import json
import logging
from src.services.day_service import DayService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

day_service = DayService()

def create_day(event, context):
    """
    Lambda function to create a new day
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
        if not week_id or not day_number is None or not date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Create day
        day = day_service.create_day(week_id=week_id, day_number=day_number, date=date, focus=focus, notes=notes)
        
        return {
            "statusCode": 201,
            "body": json.dumps(day.to_dict())
        }

    except Exception as e:
        logger.error(f"Error creating day: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_days_for_week(event, context):
    """
    Lambda function to get all days for a training week
    """
    try:
        # Extract week_id from path parameters
        week_id = event["pathParameters"]["week_id"]

        # Get days 
        days = day_service.get_days_for_week(week_id)

        return {
            "statusCode": 200,
            "body": json.dumps([day.to_dict() for day in days])
        }
    
    except Exception as e:
        logger.error(f"Error getting days for week: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def update_day(event, context):
    """
    Lambda function to update a day by ID
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]
        body = json.loads(event["body"])

        # Update day 
        update_day = day_service.update_day(day_id, body)

        if not update_day:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Day not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(update_day.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error updating day: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def delete_day(event, context):
    """
    Lambda function to delete day
    """
    try: 
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]

        # Delete day
        delete_day = day_service.delete_day(day_id)

        if not delete_day:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Day not found"})
            }
        
        return {
            "statusCode": 204,
            "body": ""
        }
    
    except Exception as e:
        logger.error(f"Error deleting day: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
