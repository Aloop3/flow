import json
import logging
from src.services.block_service import BlockService
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

block_service = BlockService()


def create_block(event, context):
    """
    Handle POST /blocks request to create a new training block
    """
    try:
        # Extract block details from request
        body = json.loads(event["body"])

        # Extract block details from request
        athlete_id = body.get("athlete_id")
        title = body.get("title")
        description = body.get("description")
        start_date = body.get("start_date")
        end_date = body.get("end_date")
        coach_id = body.get("coach_id")
        status = body.get("status")

        # Validate required fields
        if not athlete_id or not title or not start_date or not end_date:
            return create_response(400, {"error": "Missing required fields"})

        # Create block
        block = block_service.create_block(
            athlete_id=athlete_id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            coach_id=coach_id,
            status=status,
        )

        return create_response(201, block.to_dict())

    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error creating block: {str(e)}")
        return create_response(500, {"error": str(e)})


def get_block(event, context):
    """
    Handle GET /blocks/{block_id} request to get a block by ID
    """
    # Validate required parameters upfront
    if not event.get("pathParameters") or not event["pathParameters"].get("block_id"):
        return create_response(400, {"error": "Missing block_id parameter"})

    try:
        # Extract block_id from path parameters
        block_id = event["pathParameters"]["block_id"]

        # Get block
        block = block_service.get_block(block_id)

        # Handle not found case
        if not block:
            return create_response(404, {"error": "Block not found"})

        # Return successful response
        return create_response(200, block.to_dict())

    except Exception as e:
        logger.error(f"Error getting block: {str(e)}")
        return create_response(500, {"error": f"Internal server error: {str(e)}"})


def get_blocks_by_athlete(event, context):
    """
    Handle GET/athletes/{athlete_id}/blocks request to get blocks by athlete ID
    """
    try:
        if not event.get("pathParameters") or not event["pathParameters"].get(
            "athlete_id"
        ):
            return create_response(400, {"error": "Missing athlete_id parameter"})

        # Extract athlete_id from path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Get blocks
        blocks = block_service.get_blocks_for_athlete(athlete_id)

        return create_response(200, [block.to_dict() for block in blocks])

    except Exception as e:
        logger.error(f"Error getting blocks: {str(e)}")
        return create_response(500, {"error": str(e)})


def update_block(event, context):
    """
    Handle PUT /blocks/{block_id} request to update a block by ID
    """
    # Validate required parameters upfront
    if not event.get("pathParameters") or not event["pathParameters"].get("block_id"):
        return create_response(400, {"error": "Missing block_id parameter"})

    if not event.get("body"):
        return create_response(400, {"error": "Missing request body"})

    try:
        # Extract block_id from path parameters
        block_id = event["pathParameters"]["block_id"]

        # Parse JSON body
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return create_response(400, {"error": "Invalid JSON in request body"})

        # Update block
        updated_block = block_service.update_block(block_id, body)

        # Handle not found case
        if not updated_block:
            return create_response(404, {"error": "Block not found"})

        # Return successful response
        return create_response(200, updated_block.to_dict())

    except Exception as e:
        logger.error(f"Error updating block: {str(e)}")
        return create_response(500, {"error": f"Internal server error: {str(e)}"})


def delete_block(event, context):
    """
    Handle DELETE /blocks/{block_id} request to delete a block by ID
    """
    try:
        if not event.get("pathParameters") or not event["pathParameters"].get(
            "block_id"
        ):
            return create_response(400, {"error": "Missing block_id parameter"})

        # Extract block_id from path parameters
        block_id = event["pathParameters"]["block_id"]

        # Delete block
        delete_block = block_service.delete_block(block_id)

        if not delete_block:
            return create_response(404, {"error": "Block not found"})

        return create_response(204, {})

    except Exception as e:
        logger.error(f"Error deleting block: {str(e)}")
        return create_response(500, {"error": str(e)})
