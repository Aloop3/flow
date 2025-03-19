import json
import logging
from src.services.day_service import DayService
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

day_service = DayService()

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
        
        # Create day
        day = day_service.create_day(week_id=week_id, day_number=day_number, date=date, focus=focus, notes=notes)
        
        return create_response(201, day.to_dict())

    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error creating day: {str(e)}")
        return create_response(500, {"error": str(e)})

def get_days_for_week(event, context):
    """
    Handle GET /weeks/{week_id}/days request to get all days for a training week
    """
    try:
        # Extract week_id from path parameters
        week_id = event["pathParameters"]["week_id"]

        # Get days 
        days = day_service.get_days_for_week(week_id)

        return create_response(200, [day.to_dict() for day in days])
    
    except Exception as e:
        logger.error(f"Error getting days for week: {str(e)}")
        return create_response(500, {"error": str(e)})

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
            return create_response(404, {"error": "Day not found"})
        
        return create_response(200, update_day.to_dict())
    
    except Exception as e:
        logger.error(f"Error updating day: {str(e)}")
        return create_response(500, {"error": str(e)})

def delete_day(event, context):
    """
    Handle DELETE /days/{day_id} request to delete day
    """
    try: 
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]

        # Delete day
        delete_day = day_service.delete_day(day_id)

        if not delete_day:
            return create_response(404, {"error": "Day not found"})
        
        return create_response(204, {})
    
    except Exception as e:
        logger.error(f"Error deleting day: {str(e)}")
        return create_response(500, {"error": str(e)})
