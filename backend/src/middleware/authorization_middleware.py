import logging
from typing import Dict, Any
from src.middleware.middleware import ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_resource_ownership(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Middleware to validate user has permission to access resource.

    Validates against path parameters:
    - {user_id}: User can access own data
    - {athlete_id}: User can access own data OR coach can access athlete data
    - {block_id}, {week_id}, {day_id}, {workout_id}: Traced back to athlete ownership

    :param event: The Lambda event
    :param context: The Lambda context
    :return: The event, possibly modified
    :raises: ValidationError if access denied
    """
    # Extract current user from JWT claims
    current_user_id = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
        .get("sub")
    )

    if not current_user_id:
        logger.error("No user ID found in auth claims")
        raise ValidationError("Unauthorized - missing user ID")

    # Extract path parameters
    path_params = event.get("pathParameters", {}) or {}
    resource = event.get("resource", "")
    method = event.get("httpMethod", "")

    # Skip validation for certain endpoints that don't require ownership validation
    skip_validation_patterns = [
        "/exercises/types",  # Public exercise types
        "/relationships",  # Handled by business logic
        "/auth/",  # Auth endpoints
    ]

    if any(pattern in resource for pattern in skip_validation_patterns):
        return event

    try:
        # Validate access based on path parameters
        if "user_id" in path_params:
            _validate_user_access(current_user_id, path_params["user_id"])

        elif "athlete_id" in path_params:
            _validate_athlete_access(current_user_id, path_params["athlete_id"])

        elif "block_id" in path_params:
            athlete_id = _get_athlete_from_block(path_params["block_id"])
            _validate_athlete_access(current_user_id, athlete_id)

        elif "week_id" in path_params:
            athlete_id = _get_athlete_from_week(path_params["week_id"])
            _validate_athlete_access(current_user_id, athlete_id)

        elif "day_id" in path_params:
            athlete_id = _get_athlete_from_day(path_params["day_id"])
            _validate_athlete_access(current_user_id, athlete_id)

        elif "workout_id" in path_params:
            athlete_id = _get_athlete_from_workout(path_params["workout_id"])
            _validate_athlete_access(current_user_id, athlete_id)

        # For resource creation endpoints, validate via request body
        elif method == "POST" and event.get("body"):
            _validate_creation_access(current_user_id, event, resource)

    except ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.error(f"Error validating resource access: {str(e)}")
        raise ValidationError("Access validation failed")

    return event


def _validate_user_access(current_user_id: str, target_user_id: str) -> None:
    """Validate user can access user resource (only their own)"""
    if current_user_id != target_user_id:
        logger.warning(
            f"User {current_user_id} attempted to access user {target_user_id}"
        )
        raise ValidationError("Forbidden - cannot access other user's data")


def _validate_athlete_access(current_user_id: str, athlete_id: str) -> None:
    """Validate user can access athlete resource (own data or coach relationship)"""
    # User can always access their own data
    if current_user_id == athlete_id:
        return

    # Check if current user is coach of this athlete
    if not _is_active_coach(current_user_id, athlete_id):
        logger.warning(
            f"User {current_user_id} attempted to access athlete {athlete_id} without permission"
        )
        raise ValidationError("Forbidden - no active coach relationship")


def _validate_creation_access(
    current_user_id: str, event: Dict[str, Any], resource: str
) -> None:
    """Validate user can create resources for specified athlete"""
    import json

    try:
        body = json.loads(event.get("body", "{}"))

        # Check for athlete_id in request body for creation endpoints
        if "athlete_id" in body:
            _validate_athlete_access(current_user_id, body["athlete_id"])

        # Special handling for day workout creation
        elif "/days/" in resource and "/workout" in resource:
            day_id = event.get("pathParameters", {}).get("day_id")
            if day_id:
                athlete_id = _get_athlete_from_day(day_id)
                _validate_athlete_access(current_user_id, athlete_id)

    except json.JSONDecodeError:
        # Invalid JSON will be caught by other middleware
        pass


def _is_active_coach(coach_id: str, athlete_id: str) -> bool:
    """Check if user is active coach of athlete"""
    try:
        from src.services.relationship_service import RelationshipService

        relationship_service = RelationshipService()
        relationship = relationship_service.get_active_relationship(
            coach_id=coach_id, athlete_id=athlete_id
        )

        # Confirmed from RelationshipService: returns Relationship object or None
        # Status check: relationship.status == "active"
        return relationship is not None and relationship.status == "active"

    except Exception as e:
        logger.error(f"Error checking coach relationship: {str(e)}")
        return False


def _get_athlete_from_block(block_id: str) -> str:
    """Get athlete_id from block_id"""
    from src.services.block_service import BlockService

    block_service = BlockService()
    block = block_service.get_block(block_id)

    if not block:
        raise ValidationError("Block not found")

    return block.athlete_id


def _get_athlete_from_week(week_id: str) -> str:
    """Get athlete_id from week_id via block"""
    from src.services.week_service import WeekService

    week_service = WeekService()
    week = week_service.get_week(week_id)

    if not week:
        raise ValidationError("Week not found")

    return _get_athlete_from_block(week.block_id)


def _get_athlete_from_day(day_id: str) -> str:
    """Get athlete_id from day_id via week and block"""
    from src.services.day_service import DayService

    day_service = DayService()
    day = day_service.get_day(day_id)

    if not day:
        raise ValidationError("Day not found")

    return _get_athlete_from_week(day.week_id)


def _get_athlete_from_workout(workout_id: str) -> str:
    """Get athlete_id from workout_id"""
    from src.services.workout_service import WorkoutService

    workout_service = WorkoutService()
    workout = workout_service.get_workout(workout_id)

    if not workout:
        raise ValidationError("Workout not found")

    return workout.athlete_id
