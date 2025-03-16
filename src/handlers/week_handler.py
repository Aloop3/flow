import json
import logging
from src.services.week_service import WeekService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

week_service = WeekService()

def create_week(event, context):
    """
    Lambda function to create a new week in a training block
    """
    try:
        body = json.loads(event["body"])

        # Extract week details from request
        block_id = body.get("block_id")
        week_number = body.get("week_number")
        notes = body.get("notes")

        # Validate required fields
        if not block_id or not week_number:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Create week
        week = week_service.create_week(block_id=block_id, week_number=week_number, notes=notes)

        return {
            "statusCode": 201,
            "body": json.dumps(week.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error creating week: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_weeks_for_block(event, context):
    """
    Lambda function to get all weeks for a training block
    """
    try:
        block_id = event["pathParameters"]["block_id"]

        # Get weeks
        weeks = week_service.get_weeks_for_block(block_id)

        return {
            "statusCode": 200,
            "body": json.dumps(weeks.to_dict() for week in weeks)
        }
    
    except Exception as e:
        logger.error(f"Error getting weeks for block: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
def update_week(event, context):
    """
    Lambda function to update a week by ID
    """
    try:
        week_id = event["pathParameters"]["week_id"]
        body = json.loads(event["body"])

        # Update week
        update_week = week_service.update_week(week_id, body)

        if not update_week:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Week not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(update_week.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error updating week: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def delete_week(event, context):
    """
    Lambda function to delete a week by ID
    """
    try:
        week_id = event["pathParameters"]["week_id"]

        # Delete week
        delete_week = week_service.delete_week(week_id)

        if not delete_week:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Week not found"})
            }
        
        return {
            "statusCode": 204,
            "body": ""
        }
    
    except Exception as e:
        logger.error(f"Error deleting week: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
