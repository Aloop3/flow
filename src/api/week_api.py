import json
import logging
from src.services.week_service import WeekService
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

week_service = WeekService()


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

        # Create week
        week = week_service.create_week(
            block_id=block_id, week_number=week_number, notes=notes
        )

        return create_response(201, week.to_dict())

    except Exception as e:
        logger.error(f"Error creating week: {str(e)}")
        return create_response(500, {"error": str(e)})


def get_weeks_for_block(event, context):
    """
    Handle GET /blocks/{block_id}/weeks request to get all weeks for a training block
    """
    try:
        block_id = event["pathParameters"]["block_id"]

        # Get weeks
        weeks = week_service.get_weeks_for_block(block_id)

        return create_response(200, [week.to_dict() for week in weeks])

    except Exception as e:
        logger.error(f"Error getting weeks for block: {str(e)}")
        return create_response(500, {"error": str(e)})


def update_week(event, context):
    """
    Handle PUT /weeks/{week_id} request to update a week by ID
    """
    try:
        week_id = event["pathParameters"]["week_id"]
        body = json.loads(event["body"])

        # Update week
        update_week = week_service.update_week(week_id, body)

        if not update_week:
            return create_response(404, {"error": "Week not found"})

        return create_response(200, update_week.to_dict())

    except Exception as e:
        logger.error(f"Error updating week: {str(e)}")
        return create_response(500, {"error": str(e)})


def delete_week(event, context):
    """
    Handle DELETE /weeks/{week_id} request to delete a week by ID
    """
    try:
        week_id = event["pathParameters"]["week_id"]

        # Delete week
        delete_week = week_service.delete_week(week_id)

        if not delete_week:
            return create_response(404, {"error": "Week not found"})

        return create_response(204, {})

    except Exception as e:
        logger.error(f"Error deleting week: {str(e)}")
        return create_response(500, {"error": str(e)})
