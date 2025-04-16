import json
import logging
from src.services.workout_service import WorkoutService
from src.repositories.workout_repository import WorkoutRepository
from src.services.day_service import DayService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

workout_service = WorkoutService()
day_service = DayService()


@with_middleware([log_request, handle_errors])
def create_workout(event, context):
    """
    Handle POST /workouts request to create a new workout
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
        if not athlete_id or not day_id or not date:
            return create_response(400, {"error": "Missing required fields"})

        # Log workout
        workout = workout_service.log_workout(
            athlete_id=athlete_id,
            day_id=day_id,
            date=date,
            completed_exercises=completed_exercises,
            notes=notes,
            status=status,
        )

        return create_response(201, workout.to_dict())
    except ValueError as e:
        logger.error(f"Error creating workout: {e}")
        return create_response(400, {"error": str(e)})
    except Exception as e:
        logger.error(f"Error creating workout: {e}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def create_day_workout(event, context):
    """
    Handle POST /days/{day_id}/workout request to create a workout for a specific day
    """
    try:
        # Extract day_id from path parameters
        day_id = event["pathParameters"]["day_id"]
        body = json.loads(event["body"])

        # Extract user info from cognito claims
        athlete_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Get the day to ensure it exists and get its date
        day = day_service.get_day(day_id)

        if not day:
            return create_response(404, {"error": "Day not found"})

        # Use the day's date from the database to ensure consistency
        date = day.date

        # Extract exercise data
        exercises = body.get("exercises", [])

        if not exercises:
            return create_response(400, {"error": "No exercises provided"})

        # Transform exercises to format expected by workout_service
        transformed_exercises = []
        for exercise in exercises:
            transformed_exercises.append(
                {
                    "exercise_type": exercise.get("exerciseType"),
                    "sets": exercise.get("sets", 1),
                    "reps": exercise.get("reps", 1),
                    "weight": exercise.get("weight", 0),
                    "notes": exercise.get("notes", ""),
                }
            )

        # Create the workout
        workout = workout_service.log_workout(
            athlete_id=athlete_id,
            day_id=day_id,
            date=date,
            completed_exercises=transformed_exercises,
            status="draft",
        )

        return create_response(201, workout.to_dict())
    except Exception as e:
        logger.error(f"Error creating day workout: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_workout(event, context):
    """
    Handle GET /workouts/{workout_id} request to get a workout by ID
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Get workout
        workout = workout_service.get_workout(workout_id)

        if not workout:
            return create_response(404, {"error": "Workout not found"})

        return create_response(200, workout.to_dict())

    except Exception as e:
        logger.error(f"Error getting workout: {e}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_workouts_by_athlete(event, context):
    """
    Handle GET /athletes/{athlete_id}/workouts request to get workouts by athlete ID
    """
    try:
        # Extract athlete_id from path parameters
        athlete_id = event["pathParameters"]["athlete_id"]

        # Use workout repository directly since the service doesn't expose this method
        workout_repo = WorkoutRepository()

        workouts = workout_repo.get_workouts_by_athlete(athlete_id)

        return create_response(200, workouts)

    except Exception as e:
        logger.error(f"Error getting workouts: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_workout_by_day(event, context):
    """
    Handle GET /athletes/{athlete_id}/days/{day_id}/workout request to get a workout for a specific day
    """
    try:
        # Extract parameters
        athlete_id = event["pathParameters"]["athlete_id"]
        day_id = event["pathParameters"]["day_id"]

        # Get workout
        workout = workout_service.get_workout_by_day(athlete_id, day_id)

        if not workout:
            return create_response(404, {"error": "Workout not found"})

        return create_response(200, workout.to_dict())

    except Exception as e:
        logger.error(f"Error getting workout by day: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def update_workout(event, context):
    """
    Handle PUT /workouts/{workout_id} request to update a workout
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]
        body = json.loads(event["body"])

        # Update workout
        workout = workout_service.update_workout(workout_id, body)

        if not workout:
            return create_response(404, {"error": "Workout not found"})

        return create_response(200, workout.to_dict())

    except Exception as e:
        logger.error(f"Error updating workout: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def delete_workout(event, context):
    """
    Handle DELETE /workouts/{workout_id} request to delete a workout by ID
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Delete workout
        result = workout_service.delete_workout(workout_id)

        if not result:
            return create_response(404, {"error": "Workout not found"})

        return create_response(204, {})

    except Exception as e:
        logger.error(f"Error deleting workout: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def copy_workout(event, context):
    """
    Handle POST /workouts/copy request to copy a workout from one day to another
    """
    try:
        body = json.loads(event["body"])

        # Extract parameters
        source_day_id = body.get("source_day_id")
        target_day_id = body.get("target_day_id")

        # Validate required fields
        if not source_day_id or not target_day_id:
            return create_response(
                400,
                {"error": "Missing required fields: source_day_id and target_day_id"},
            )

        # Extract user info from cognito claims
        athlete_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Get source workout
        source_workout = workout_service.get_workout_by_day(athlete_id, source_day_id)

        if not source_workout:
            return create_response(404, {"error": "Source workout not found"})

        # Get target day to ensure it exists and get its date
        day_service = DayService()
        target_day = day_service.get_day(target_day_id)

        if not target_day:
            return create_response(404, {"error": "Target day not found"})

        # Check if a workout already exists for the target day
        existing_workout = workout_service.get_workout_by_day(athlete_id, target_day_id)
        if existing_workout:
            return create_response(
                409,
                {"error": "Target day already has a workout. Delete it first to copy."},
            )

        # Extract exercises from source workout to copy (without completion data)
        exercises_to_copy = []
        for exercise in source_workout.exercises:
            exercises_to_copy.append(
                {
                    "exercise_id": exercise.exercise_id,
                    "exercise_type": exercise.exercise_type,
                    "sets": exercise.sets,
                    "reps": exercise.reps,
                    "weight": exercise.weight,
                    "notes": exercise.notes,
                }
            )

        # Create new workout for target day
        new_workout = workout_service.log_workout(
            athlete_id=athlete_id,
            day_id=target_day_id,
            date=target_day.date,
            completed_exercises=exercises_to_copy,
            status="not_started",
        )

        return create_response(201, new_workout.to_dict())

    except Exception as e:
        logger.error(f"Error copying workout: {str(e)}")
        return create_response(500, {"error": str(e)})
