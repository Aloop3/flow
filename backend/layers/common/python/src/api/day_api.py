import json
import logging
from src.services.day_service import DayService
from src.services.week_service import WeekService
from src.services.block_service import BlockService
from src.services.relationship_service import RelationshipService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

day_service = DayService()
week_service = WeekService()
block_service = BlockService()
relationship_service = RelationshipService()


@with_middleware([log_request, handle_errors])
def create_day(event, context):
    """
    Handle POST /days request to create a new day
    """
    try:
        body = json.loads(event["body"])

        # Extract day details from request
        week_id = body.get("week_id")
        day_number = body.get("day_number")
        date = body.get("date")
        focus = body.get("focus")
        notes = body.get("notes")

        # Validate required fields
        if not week_id or day_number is None or not date:
            return create_response(400, {"error": "Missing required fields"})

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        week = week_service.get_week(week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this week"}
                )

        # Create day
        day = day_service.create_day(
            week_id=week_id, day_number=day_number, date=date, focus=focus, notes=notes
        )

        return create_response(201, day.to_dict())

    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error creating day: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_day(event, context):
    """
    Handle GET /days/{day_id} request to get a day by ID
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]

        # Get day
        day = day_service.get_day(day_id)

        if not day:
            return create_response(404, {"error": "Day not found"})

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        week = week_service.get_week(day.week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this day"}
                )

        return create_response(200, day.to_dict())

    except Exception as e:
        logger.error(f"Error getting day: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_days_for_week(event, context):
    """
    Handle GET /weeks/{week_id}/days request to get all days for a training week
    """
    try:
        # Extract week_id from path parameters
        week_id = event["pathParameters"]["week_id"]

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        week = week_service.get_week(week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this week"}
                )

        # Get days
        days = day_service.get_days_for_week(week_id)

        return create_response(200, [day.to_dict() for day in days])

    except Exception as e:
        logger.error(f"Error getting days for week: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def update_day(event, context):
    """
    Lambda function to update a day by ID
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]
        body = json.loads(event["body"])

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        existing_day = day_service.get_day(day_id)
        if not existing_day:
            return create_response(404, {"error": "Day not found"})
        week = week_service.get_week(existing_day.week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this day"}
                )

        # Update day
        updated_day = day_service.update_day(day_id, body)

        if not updated_day:
            return create_response(404, {"error": "Day not found"})

        return create_response(200, updated_day.to_dict())

    except Exception as e:
        logger.error(f"Error updating day: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def delete_day(event, context):
    """
    Handle DELETE /days/{day_id} request to delete day
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        existing_day = day_service.get_day(day_id)
        if not existing_day:
            return create_response(404, {"error": "Day not found"})
        week = week_service.get_week(existing_day.week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this day"}
                )

        # Delete day
        day_service.delete_day(day_id)

        return create_response(204, {})

    except Exception as e:
        logger.error(f"Error deleting day: {str(e)}")
        return create_response(500, {"error": str(e)})
