import json
import logging
from src.services.exercise_service import ExerciseService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

exercise_service = ExerciseService()

def create_exercise(event, context):
    """
    Lambda function to create a new exercise
    """
    try:
        body = json.loads(event["body"])

        # Extract exercise data from the request
        day_id = body.get("day_id")
        exercise_type = body.get("exercise_type")
        exercise_category = body.get("exercise_category")
        sets = body.get("sets")
        reps = body.get("reps")
        weight = body.get("weight")
        rpe = body.get("rpe")
        notes = body.get("notes")
        order = body.get("order")

        # Validate required fields
        if not day_id or not exercise_type or sets is None or reps is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Create exercise
        exercise = exercise_service.create_exercise(
            day_id=day_id, 
            exercise_type=exercise_type, 
            exercise_category=exercise_category, 
            sets=sets, 
            reps=reps, 
            weight=weight, 
            rpe=rpe, 
            notes=notes, 
            order=order)
        
        return {
            "statusCode": 201,
            "body": json.dumps(exercise.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error creating exercise: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_exercises_for_day(event, context):
    """
    Lambda function to get all exercises for a training day
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]

        # Get exercises 
        exercises = exercise_service.get_exercises_for_day(day_id)

        return {
            "statusCode": 200,
            "body": json.dumps([exercise.to_dict() for exercise in exercises])
        }
    
    except Exception as e:
        logger.error(f"Error getting exercises for day: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def update_exercise(event, context):
    """
    Lambda function to update an exercise
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        body = json.loads(event["body"])

        # Update exercise
        update_exercise = exercise_service.update_exercise(exercise_id, body)

        if not update_exercise:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Exercise not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(update_exercise.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error updating exercise: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def delete_exercise(event, context):
    """
    Lambda function to delete an exercise
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]

        # Delete exercise
        delete_exercise = exercise_service.delete_exercise(exercise_id)

        if not delete_exercise:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Exercise not found"})
            }
        
        return {
            "statusCode": 204,
            "body": ""
        }
    
    except Exception as e:
        logger.error(f"Error deleting exercise: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def reorder_exercises(event, context):
    """
    Lambda function to reorder exercises
    """
    try:
        body = json.loads(event["body"])

        # Extract parameters
        day_id = body.get("day_id")
        exercise_order = body.get("exercise_order", [])

        # Validate required fields
        if not day_id or not exercise_order:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Reorder exercises
        reorder_exercises = exercise_service.reorder_exercises(day_id, exercise_order)

        return {
            "statusCode": 200,
            "body": json.dumps([exercise.to_dict() for exercise in reorder_exercises])
        }
    
    except Exception as e:
        logger.error(f"Error reordering exercises: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    