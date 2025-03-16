import json
import logging
from src.services.block_service import BlockService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

block_service = BlockService()

def create_block(event, context):
    """
    Lambda function to create a new block
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

        # Valudate required fields
        if not athlete_id or not title or not start_date or not end_date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Create block
        block = block_service.create_block(
            athlete_id=athlete_id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            coach_id=coach_id,
            status=status
        )

        return {
            "statusCode": 201,
            "body": json.dumps(block.to_dict())
        
        }
    
    except Exception as e:
        logger.error(f"Error creating block: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_block(event, context):
    """
    Lambda function to get a block by ID
    """
    try:
        # Extract block_id from path parameters
        block_id = event["pathParameters"]["block_id"]

        # Get block
        block = block_service.get_block(block_id)

        if not block:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Block not found"})
            }
        
    except Exception as e:
        logger.error(f"Error getting block: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_blocks_by_athlete(event, context):
    """
    Lambda function to get blocks by athlete ID
    """
    try:
        # Extract athlete_id from path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Get blocks
        blocks = block_service.get_blocks_for_athlete(athlete_id)

        return {
            "statusCode": 200,
            "body": json.dumps([block.to_dict() for block in blocks])
        }
    
    except Exception as e:
        logger.error(f"Error getting blocks: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def update_block(event, context):
    """
    Lambda function to update a block by ID
    """
    try:
        # Extract block_id from path parameters
        block_id = event["pathParameters"]["block_id"]
        body = json.loads(event["body"])

        # Update block
        update_block = block_service.update_block(block_id, body)

        if not update_block:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Block not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(update_block.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error updating block: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def delete_block(event, context):
    """
    Lambda function to delete a block by ID
    """
    try:
        # Extract block_id from path parameters
        block_id = event["pathParameters"]["block_id"]

        # Delete block
        delete_block = block_service.delete_block(block_id)

        if not delete_block:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Block not found"})
            }
        
        return {
            "statusCode": 204,
            "body": ""
        }
    
    except Exception as e:
        logger.error(f"Error deleting block: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
