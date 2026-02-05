import json
import logging
from src.services.workout_service import WorkoutService
from src.repositories.workout_repository import WorkoutRepository
from src.services.day_service import DayService
from src.services.week_service import WeekService
from src.services.block_service import BlockService
from src.services.relationship_service import RelationshipService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors
from .exercise_api import (
    convert_exercise_weights_for_display,
    get_user_weight_preference,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

workout_service = WorkoutService()
day_service = DayService()
week_service = WeekService()
block_service = BlockService()
relationship_service = RelationshipService()


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
        exercises = body.get("exercises", [])
        notes = body.get("notes")
        status = body.get("status")

        # Validate required fields
        if not athlete_id or not day_id or not date:
            return create_response(400, {"error": "Missing required fields"})

        # Create a Workout
        workout = workout_service.create_workout(
            athlete_id=athlete_id,
            day_id=day_id,
            date=date,
            exercises=exercises,
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
        current_user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Get the day to determine the actual athlete
        day = day_service.get_day(day_id)
        if not day:
            return create_response(404, {"error": "Day not found"})

        # Get the week to find the block
        week = week_service.get_week(day.week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})

        # Get the block to find the actual athlete
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})

        # Use the block's athlete_id, not the current user's ID
        athlete_id = block.athlete_id

        # Verify the current user has permission (either is the athlete or their coach)
        if current_user_id != athlete_id:
            # Check if current user is the coach
            relationship = relationship_service.get_active_relationship(
                coach_id=current_user_id, athlete_id=athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized to create workout for this athlete"}
                )

        # Use the day's date from the database to ensure consistency
        date = day.date

        # Extract exercise data
        exercises = body.get("exercises", [])

        if not exercises:
            return create_response(400, {"error": "No exercises provided"})

        # Transform exercises to format expected by workout_service
        transformed_exercises = []
        for exercise in exercises:
            transformed_exercise = {
                "exercise_type": exercise.get("exerciseType"),
                "sets": exercise.get("sets", 1),
                "reps": exercise.get("reps", 1),
                "weight": exercise.get("weight", 0),
                "rpe": exercise.get("rpe"),
                "notes": exercise.get("notes", ""),
            }

            if "sets_data" in exercise:
                transformed_exercise["sets_data"] = exercise.get("sets_data")

            transformed_exercises.append(transformed_exercise)

        # Create the workout with the athlete_id
        workout = workout_service.create_workout(
            athlete_id=athlete_id,
            day_id=day_id,
            date=date,
            exercises=transformed_exercises,
            status="not_started",
        )

        # Get user preference for weight conversion
        user_preference = get_user_weight_preference(current_user_id)

        # Convert workout to dict and process exercises
        workout_dict = workout.to_dict()

        # Convert exercise weights to display units
        if "exercises" in workout_dict and workout_dict["exercises"]:
            converted_exercises = []
            for exercise in workout_dict["exercises"]:
                converted_exercise = convert_exercise_weights_for_display(
                    exercise,
                    user_preference,
                    exercise.get("exercise_type"),
                    exercise.get("exercise_category"),
                )
                converted_exercises.append(converted_exercise)
            workout_dict["exercises"] = converted_exercises

        return create_response(201, workout_dict)
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

        # Get user preference for weight conversion
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        user_preference = get_user_weight_preference(user_id)

        # Convert workout to dict and process exercises
        workout_dict = workout.to_dict()

        # Convert exercise weights to display units
        if "exercises" in workout_dict and workout_dict["exercises"]:
            converted_exercises = []
            for exercise in workout_dict["exercises"]:
                converted_exercise = convert_exercise_weights_for_display(
                    exercise,
                    user_preference,
                    exercise.get("exercise_type"),
                    exercise.get("exercise_category"),
                )
                converted_exercises.append(converted_exercise)
            workout_dict["exercises"] = converted_exercises

        return create_response(200, workout_dict)
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

        # Extract current user info from cognito claims
        current_user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Get the source day to determine the actual athlete
        day_service = DayService()
        source_day = day_service.get_day(source_day_id)
        if not source_day:
            return create_response(404, {"error": "Source day not found"})

        # Get the week to find the block
        week = week_service.get_week(source_day.week_id)
        if not week:
            return create_response(404, {"error": "Week not found"})

        # Get the block to find the actual athlete
        block = block_service.get_block(week.block_id)
        if not block:
            return create_response(404, {"error": "Block not found"})

        # Use the block's athlete_id, not the current user's ID
        athlete_id = block.athlete_id

        # Verify the current user has permission (either is the athlete or their coach)
        if current_user_id != athlete_id:
            # Check if current user is the coach
            relationship = relationship_service.get_active_relationship(
                coach_id=current_user_id, athlete_id=athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized to copy workout for this athlete"}
                )

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
            exercise_data = {
                "exercise_id": exercise.exercise_id,
                "exercise_type": exercise.exercise_type,
                "sets": exercise.sets,
                "reps": exercise.reps,
                "weight": exercise.weight,
                "notes": exercise.notes,
            }

            # Include sets_data if it exists to preserve individual set details (without completion data)
            if hasattr(exercise, "sets_data") and exercise.sets_data:
                cleaned_sets_data = []
                for set_data in exercise.sets_data:
                    cleaned_set = {
                        "set_number": set_data.get("set_number"),
                        "weight": set_data.get("weight"),
                        "reps": set_data.get("reps"),
                        "rpe": set_data.get("rpe"),
                        "completed": False,  # Reset completion status
                    }
                    cleaned_sets_data.append(cleaned_set)
                exercise_data["sets_data"] = cleaned_sets_data

            exercises_to_copy.append(exercise_data)

        # Create new workout for target day
        new_workout = workout_service.create_workout(
            athlete_id=athlete_id,
            day_id=target_day_id,
            date=target_day.date,
            exercises=exercises_to_copy,
            status="not_started",
        )

        # Get user preference for weight conversion
        user_preference = get_user_weight_preference(current_user_id)

        # Convert workout to dict and process exercises
        workout_dict = new_workout.to_dict()

        # Convert exercise weights to display units
        if "exercises" in workout_dict and workout_dict["exercises"]:
            converted_exercises = []
            for exercise in workout_dict["exercises"]:
                converted_exercise = convert_exercise_weights_for_display(
                    exercise,
                    user_preference,
                    exercise.get("exercise_type"),
                    exercise.get("exercise_category"),
                )
                converted_exercises.append(converted_exercise)
            workout_dict["exercises"] = converted_exercises

        return create_response(201, workout_dict)

    except Exception as e:
        logger.error(f"Error copying workout: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def start_workout_session(event, context):
    """
    Handle POST /workouts/{workout_id}/start request to start workout timing
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Extract user info from cognito claims
        current_user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Get the workout to validate it exists and check permissions
        workout = workout_service.get_workout(workout_id)
        if not workout:
            return create_response(404, {"error": "Workout not found"})

        # Verify the current user has permission (either is the athlete or their coach)
        if current_user_id != workout.athlete_id:
            # Check if current user is the coach
            relationship = relationship_service.get_active_relationship(
                coach_id=current_user_id, athlete_id=workout.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized to start timing for this workout"}
                )

        # Start the workout session
        updated_workout = workout_service.start_workout_session(workout_id)

        if not updated_workout:
            return create_response(500, {"error": "Failed to start workout session"})

        return create_response(200, updated_workout.to_dict())

    except ValueError as e:
        return create_response(400, {"error": str(e)})
    except Exception as e:
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def finish_workout_session(event, context):
    """
    Handle POST /workouts/{workout_id}/finish request to finish workout timing
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Extract user info from cognito claims
        current_user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Get the workout to validate it exists and check permissions
        workout = workout_service.get_workout(workout_id)
        if not workout:
            return create_response(404, {"error": "Workout not found"})

        # Verify the current user has permission (either is the athlete or their coach)
        if current_user_id != workout.athlete_id:
            # Check if current user is the coach
            relationship = relationship_service.get_active_relationship(
                coach_id=current_user_id, athlete_id=workout.athlete_id
            )
            if not relationship:
                return create_response(
                    403, {"error": "Unauthorized to finish timing for this workout"}
                )

        # Finish the workout session
        updated_workout = workout_service.finish_workout_session(workout_id)

        if not updated_workout:
            return create_response(
                400,
                {
                    "error": "Cannot finish workout session - session not started or already finished"
                },
            )

        return create_response(200, updated_workout.to_dict())

    except ValueError as e:
        return create_response(400, {"error": str(e)})
    except Exception as e:
        return create_response(500, {"error": str(e)})
