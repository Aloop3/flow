import json
import logging
from src.services.exercise_service import ExerciseService
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

exercise_service = ExerciseService()

def create_exercise(event, context):
    """
    Handle POST /exercises request to create a new exercise
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
            return create_response(400, {"error": "Missing required fields"})
        
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
        
        return create_response(201, exercise.to_dict())
    
    except Exception as e:
        logger.error(f"Error creating exercise: {str(e)}")
        return create_response(500, {"error": str(e)})

def get_exercises_for_day(event, context):
    """
    Handle GET /days/{day_id}/exercises request to get all exercises for a training day
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]

        # Get exercises 
        exercises = exercise_service.get_exercises_for_day(day_id)

        return create_response(200, [exercise.to_dict() for exercise in exercises])
    
    except Exception as e:
        logger.error(f"Error getting exercises for day: {str(e)}")
        return create_response(500, {"error": str(e)})

def update_exercise(event, context):
    """
    Handle PUT /exercises/{exercise_id} request to update an exercise
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        body = json.loads(event["body"])

        # Update exercise
        updated_exercise = exercise_service.update_exercise(exercise_id, body)

        if not updated_exercise:
            return create_response(404, {"error": "Exercise not found"})
        
        return create_response(200, updated_exercise.to_dict())
    
    except Exception as e:
        logger.error(f"Error updating exercise: {str(e)}")
        return create_response(500, {"error": str(e)})

def delete_exercise(event, context):
    """
    Handle DELETE /exercises/{exercise_id} request to delete an exercise
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]

        # Delete exercise
        delete_exercise = exercise_service.delete_exercise(exercise_id)

        if not delete_exercise:
            return create_response(404, {"error": "Exercise not found"})
        
        return create_response(204, {})
    
    except Exception as e:
        logger.error(f"Error deleting exercise: {str(e)}")
        return create_response(500, {"error": str(e)})

def reorder_exercises(event, context):
    """
    Handle POST /exercises/reorder request to reorder exercises
    """
    try:
        body = json.loads(event["body"])

        # Extract parameters
        day_id = body.get("day_id")
        exercise_order = body.get("exercise_order", [])

        # Validate required fields
        if not day_id or not exercise_order:
            return create_response(400, {"error": "Missing required fields"})
        
        # Reorder exercises
        reorder_exercises = exercise_service.reorder_exercises(day_id, exercise_order)

        return create_response(200, [exercise.to_dict() for exercise in reorder_exercises])
    
    except Exception as e:
        logger.error(f"Error reordering exercises: {str(e)}")
        return create_response(500, {"error": str(e)})
    