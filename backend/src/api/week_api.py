import json
import logging
from src.services.week_service import WeekService
from src.services.block_service import BlockService
from src.services.relationship_service import RelationshipService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

week_service = WeekService()
block_service = BlockService()
relationship_service = RelationshipService()


@with_middleware([log_request, handle_errors])
def create_week(event, context):
    """
    Handle POST /weeks request to create a new week in a training block
    """
    try:
        body = json.loads(event["body"])

        # Extract week details from request
        block_id = body.get("block_id")
        week_number = body.get("week_number")
        notes = body.get("notes")

        # Validate required fields
        if not block_id or not week_number:
            return create_response(400, {"error": "Missing required fields"})

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        block = block_service.get_block(block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this block"}
                )

        # Create week
        week = week_service.create_week(
            block_id=block_id, week_number=week_number, notes=notes
        )

        return create_response(201, week.to_dict())

    except Exception as e:
        logger.error(f"Error creating week: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_weeks_for_block(event, context):
    """
    Handle GET /blocks/{block_id}/weeks request to get all weeks for a training block
    """
    try:
        block_id = event["pathParameters"]["block_id"]

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        block = block_service.get_block(block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})
        if user_id != block.athlete_id and user_id != block.coach_id:
            relationship = relationship_service.get_active_relationship(
                coach_id=user_id, athlete_id=block.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized access to this block"}
                )

        # Get weeks
        weeks = week_service.get_weeks_for_block(block_id)

        return create_response(200, [week.to_dict() for week in weeks])

    except Exception as e:
        logger.error(f"Error getting weeks for block: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def update_week(event, context):
    """
    Handle PUT /weeks/{week_id} request to update a week by ID
    """
    try:
        week_id = event["pathParameters"]["week_id"]
        body = json.loads(event["body"])

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        existing_week = week_service.get_week(week_id)
        if not existing_week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(existing_week.block_id)
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

        # Update week
        updated_week = week_service.update_week(week_id, body)

        if not updated_week:
            return create_response(404, {"error": "Week not found"})

        return create_response(200, updated_week.to_dict())

    except Exception as e:
        logger.error(f"Error updating week: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def delete_week(event, context):
    """
    Handle DELETE /weeks/{week_id} request to delete a week by ID
    """
    try:
        week_id = event["pathParameters"]["week_id"]

        # Verify ownership
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        existing_week = week_service.get_week(week_id)
        if not existing_week:
            return create_response(404, {"error": "Week not found"})
        block = block_service.get_block(existing_week.block_id)
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

        # Delete week
        week_service.delete_week(week_id)

        return create_response(204, {})

    except Exception as e:
        logger.error(f"Error deleting week: {str(e)}")
        return create_response(500, {"error": str(e)})
