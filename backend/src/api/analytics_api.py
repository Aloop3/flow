import logging
from src.services.analytics_service import AnalyticsService
from src.services.user_service import UserService
from src.services.relationship_service import RelationshipService
from src.services.block_service import BlockService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

analytics_service = AnalyticsService()
user_service = UserService()
relationship_service = RelationshipService()
block_service = BlockService()


def validate_athlete_access(user_id: str, athlete_id: str) -> bool:
    """
    Validate that the current user has access to the athlete's data.
    User can access their own data or their athletes' data if they're a coach.

    :param user_id: Current user's ID from Cognito claims
    :param athlete_id: Target athlete's ID
    :return: True if access is allowed, False otherwise
    """
    try:
        # User can always access their own data
        if user_id == athlete_id:
            return True

        # Check if user is a coach with active relationship to this athlete
        from src.services.relationship_service import RelationshipService

        relationship_service = RelationshipService()
        relationship = relationship_service.get_active_relationship(
            coach_id=user_id, athlete_id=athlete_id
        )

        # Return True only if active relationship exists
        return relationship is not None and relationship.status == "active"

    except Exception as e:
        logger.warning(
            f"Error validating athlete access for user {user_id} -> athlete {athlete_id}: {str(e)}"
        )
        return False


def validate_date_format(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@with_middleware([log_request, handle_errors])
def get_max_weight_history(event, context):
    """
    Handle GET /analytics/max-weight/{athlete_id} request
    Query parameters: exercise_type (required), start_date, end_date
    """
    try:
        # Extract path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Extract query parameters
        query_params = event.get("queryStringParameters") or {}
        exercise_type = query_params.get("exercise_type")
        start_date = query_params.get("start_date")
        end_date = query_params.get("end_date")

        # Validate required parameters
        if not exercise_type:
            return create_response(
                400, {"error": "exercise_type query parameter is required"}
            )

        # Validate date formats if provided
        if start_date and not validate_date_format(start_date):
            return create_response(
                400, {"error": "start_date must be in YYYY-MM-DD format"}
            )

        if end_date and not validate_date_format(end_date):
            return create_response(
                400, {"error": "end_date must be in YYYY-MM-DD format"}
            )

        # Validate user access
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if not validate_athlete_access(user_id, athlete_id):
            return create_response(
                403, {"error": "Unauthorized access to athlete data"}
            )

        # Get max weight history
        max_weight_data = analytics_service.get_max_weight_history(
            athlete_id, exercise_type
        )

        # Filter by date range if provided
        if start_date or end_date:
            filtered_data = []
            for data_point in max_weight_data:
                point_date = data_point.get("date")
                if point_date:
                    if start_date and point_date < start_date:
                        continue
                    if end_date and point_date > end_date:
                        continue
                    filtered_data.append(data_point)
            max_weight_data = filtered_data

        return create_response(
            200,
            {
                "athlete_id": athlete_id,
                "exercise_type": exercise_type,
                "start_date": start_date,
                "end_date": end_date,
                "data": max_weight_data,
            },
        )

    except Exception as e:
        logger.error(f"Error getting max weight history: {str(e)}")
        return create_response(500, {"error": "Internal server error"})


@with_middleware([log_request, handle_errors])
def get_volume_calculation(event, context):
    """
    Handle GET /analytics/volume/{athlete_id} request
    Query parameters: time_period (week/month/year/all), start_date, end_date
    """
    try:
        # Extract path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Extract query parameters
        query_params = event.get("queryStringParameters") or {}
        time_period = query_params.get("time_period", "month")
        start_date = query_params.get("start_date")
        end_date = query_params.get("end_date")

        # Validate time_period
        valid_periods = ["week", "month", "year", "all"]
        if time_period not in valid_periods:
            return create_response(
                400,
                {"error": f"time_period must be one of: {', '.join(valid_periods)}"},
            )

        # Validate date formats if provided
        if start_date and not validate_date_format(start_date):
            return create_response(
                400, {"error": "start_date must be in YYYY-MM-DD format"}
            )

        if end_date and not validate_date_format(end_date):
            return create_response(
                400, {"error": "end_date must be in YYYY-MM-DD format"}
            )

        # Validate user access
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if not validate_athlete_access(user_id, athlete_id):
            return create_response(
                403, {"error": "Unauthorized access to athlete data"}
            )

        # Calculate volume
        volume_data = analytics_service.calculate_volume(athlete_id, time_period)

        # Filter by date range if provided
        if start_date or end_date:
            filtered_data = []
            for data_point in volume_data:
                point_date = data_point.get("date")
                if point_date:
                    if start_date and point_date < start_date:
                        continue
                    if end_date and point_date > end_date:
                        continue
                    filtered_data.append(data_point)
            volume_data = filtered_data

        return create_response(
            200,
            {
                "athlete_id": athlete_id,
                "time_period": time_period,
                "start_date": start_date,
                "end_date": end_date,
                "data": volume_data,
            },
        )

    except Exception as e:
        logger.error(f"Error calculating volume: {str(e)}")
        return create_response(500, {"error": "Internal server error"})


@with_middleware([log_request, handle_errors])
def get_exercise_frequency(event, context):
    """
    Handle GET /analytics/frequency/{athlete_id} request
    Query parameters: exercise_type (required), time_period (week/month/year)
    """
    try:
        # Extract path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Extract query parameters
        query_params = event.get("queryStringParameters") or {}
        exercise_type = query_params.get("exercise_type")
        time_period = query_params.get("time_period", "month")

        # Validate required parameters
        if not exercise_type:
            return create_response(
                400, {"error": "exercise_type query parameter is required"}
            )

        # Validate time_period
        valid_periods = ["week", "month", "year"]
        if time_period not in valid_periods:
            return create_response(
                400,
                {"error": f"time_period must be one of: {', '.join(valid_periods)}"},
            )

        # Validate user access
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if not validate_athlete_access(user_id, athlete_id):
            return create_response(
                403, {"error": "Unauthorized access to athlete data"}
            )

        # Get exercise frequency
        frequency_data = analytics_service.get_exercise_frequency(
            athlete_id, exercise_type, time_period
        )

        return create_response(200, frequency_data)

    except Exception as e:
        logger.error(f"Error getting exercise frequency: {str(e)}")
        return create_response(500, {"error": "Internal server error"})


@with_middleware([log_request, handle_errors])
def get_block_analysis(event, context):
    """
    Handle GET /analytics/block-analysis/{athlete_id}/{block_id} request
    """
    try:
        # Extract path parameters
        athlete_id = event["pathParameters"]["athlete_id"]
        block_id = event["pathParameters"]["block_id"]

        # Validate user access
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if not validate_athlete_access(user_id, athlete_id):
            return create_response(
                403, {"error": "Unauthorized access to athlete data"}
            )

        # Verify block belongs to athlete
        from src.services.block_service import BlockService

        block_service = BlockService()
        block = block_service.get_block(block_id)

        if not block:
            return create_response(404, {"error": "Block not found"})

        if block.athlete_id != athlete_id:
            return create_response(
                403, {"error": "Block does not belong to specified athlete"}
            )

        # Calculate block volume analysis
        block_analysis = analytics_service.calculate_block_volume(block_id)

        # Check for service errors
        if "error" in block_analysis:
            return create_response(400, block_analysis)

        return create_response(200, block_analysis)

    except Exception as e:
        logger.error(f"Error getting block analysis: {str(e)}")
        return create_response(500, {"error": "Internal server error"})


@with_middleware([log_request, handle_errors])
def get_block_comparison(event, context):
    """
    Handle GET /analytics/block-comparison/{athlete_id} request
    Query parameters: block_id1 (required), block_id2 (required)
    """
    try:
        # Extract path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Extract query parameters
        query_params = event.get("queryStringParameters") or {}
        block_id1 = query_params.get("block_id1")
        block_id2 = query_params.get("block_id2")

        # Validate required parameters
        if not block_id1 or not block_id2:
            return create_response(
                400,
                {"error": "Both block_id1 and block_id2 query parameters are required"},
            )

        if block_id1 == block_id2:
            return create_response(400, {"error": "Cannot compare a block with itself"})

        # Validate user access
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        if not validate_athlete_access(user_id, athlete_id):
            return create_response(
                403, {"error": "Unauthorized access to athlete data"}
            )

        # Verify both blocks belong to athlete
        from src.services.block_service import BlockService

        block_service = BlockService()

        block1 = block_service.get_block(block_id1)
        block2 = block_service.get_block(block_id2)

        if not block1:
            return create_response(404, {"error": f"Block {block_id1} not found"})
        if not block2:
            return create_response(404, {"error": f"Block {block_id2} not found"})

        if block1.athlete_id != athlete_id:
            return create_response(
                403,
                {"error": f"Block {block_id1} does not belong to specified athlete"},
            )
        if block2.athlete_id != athlete_id:
            return create_response(
                403,
                {"error": f"Block {block_id2} does not belong to specified athlete"},
            )

        # Compare blocks
        comparison_data = analytics_service.compare_blocks(block_id1, block_id2)

        # Check for service errors
        if "error" in comparison_data:
            return create_response(400, comparison_data)

        return create_response(200, comparison_data)

    except Exception as e:
        logger.error(f"Error comparing blocks: {str(e)}")
        return create_response(500, {"error": "Internal server error"})
