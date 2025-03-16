import json
import logging
from src.services.workout_service import WorkoutService
from src.repositories.workout_repository import WorkoutRepository

logger = logging.getLogger()
logger.setLevel(logging.INFO)

workout_service = WorkoutService()

def create_workout(event, context):
    """
    Lambda function to create a new workout
    """
    try: 
        body = json.loads(event["body"])

        # Extract workout details from request
        athlete_id = body.get("athlete_id")
        day_id = body.get("day_id")
        date = body.get("date")
        completed_exercises = body.get("exercises", [])
        notes = body.get("notes")
        status = body.get("status")

        # Validate required fields
        if not athlete_id or not day_id or not date or not completed_exercises:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing required fields"})
            }
        
        # Log workout
        workout = workout_service.log_workout(
            athlete_id=athlete_id, 
            day_id=day_id,
            date=date,
            completed_exercises=completed_exercises,
            notes=notes,
            status=status
        )

        return {
            "statusCode": 201,
            "body": json.dumps(workout.to_dict())
        }
    except Exception as e:
        logger.error(f"Error creating workout: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_workout(event, context):
    """
    Lambda function to get a workout by ID
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Get workout
        workout = workout_service.get_workout(workout_id)

        if not workout:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Workout not found"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(workout.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error getting workout: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_workouts_by_athlete(event, context):
    """
    Lambda function to get workouts by athlete ID
    """
    try:
        # Extract athlete_id from path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Use workout repository directly since the service doesn't expose this method
        workout_repo = WorkoutRepository()

        workouts = workout_repo.get_workouts_by_athlete(athlete_id)

        return {
            "statusCode": 200,
            "body": json.dumps(workouts)
        }
    
    except Exception as e:
        logger.error(f"Error getting workouts: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
def update_workout(event, context):
    """
    Lambda fucntion to get workouts by athlete ID
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]
        body = json.loads(event["body"])

        # Update workout
        workout = workout_service.update_workout(workout_id, body)

        if not workout:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Workout not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(workout.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error updating workout: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def delete_workout(event, context):
    """
    Lambda function to delete a workout by ID
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Delete workout
        result =  workout_service.delete_workout(workout_id)

        if not result:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Workout not found"})
            }
        
        return {
            "statusCode": 204,
            "body": ""
        }
    
    except Exception as e:
        logger.error(f"Error deleting workout: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }