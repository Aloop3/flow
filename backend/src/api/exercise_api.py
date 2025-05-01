import json
import logging
from src.services.exercise_service import ExerciseService
from src.services.workout_service import WorkoutService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

exercise_service = ExerciseService()
workout_service = WorkoutService()


@with_middleware([log_request, handle_errors])
def create_exercise(event, context):
    """
    Handle POST /exercises request to create a new exercise
    """
    try:
        body = json.loads(event["body"])

        # Extract exercise data from the request
        workout_id = body.get("workout_id")
        exercise_type = body.get("exercise_type")
        exercise_category = body.get("exercise_category")
        sets = body.get("sets")
        reps = body.get("reps")
        weight = body.get("weight")
        rpe = body.get("rpe")
        notes = body.get("notes")
        order = body.get("order")

        # Validate required fields
        if not workout_id or not exercise_type or sets is None or reps is None:
            return create_response(400, {"error": "Missing required fields"})

        # Create exercise
        exercise = exercise_service.create_exercise(
            workout_id=workout_id,
            exercise_type=exercise_type,
            exercise_category=exercise_category,
            sets=sets,
            reps=reps,
            weight=weight,
            rpe=rpe,
            notes=notes,
            order=order,
        )

        return create_response(201, exercise.to_dict())

    except Exception as e:
        logger.error(f"Error creating exercise: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_exercises_for_workout(event, context):
    """
    Handle GET /workouts/{workout_id}/exercises request to get all exercises for a training workout
    """
    try:
        # Extract workout_id from path parameters
        workout_id = event["pathParameters"]["workout_id"]

        # Get exercises
        exercises = exercise_service.get_exercises_for_workout(workout_id)

        return create_response(200, [exercise.to_dict() for exercise in exercises])

    except Exception as e:
        logger.error(f"Error getting exercises for workout: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
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


@with_middleware([log_request, handle_errors])
def complete_exercise(event, context):
    """
    Handle POST /exercises/{exercise_id}/complete request to complete an exercise
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        body = json.loads(event["body"])

        # Extract completion data
        sets = body.get("sets")
        reps = body.get("reps")
        weight = body.get("weight")
        rpe = body.get("rpe")
        notes = body.get("notes")

        # Validate required fields
        if sets is None or reps is None or weight is None:
            return create_response(400, {"error": "Missing required fields"})

        # Complete the exercise
        updated_exercise = workout_service.complete_exercise(
            exercise_id=exercise_id,
            sets=sets,
            reps=reps,
            weight=weight,
            rpe=rpe,
            notes=notes,
        )

        if not updated_exercise:
            return create_response(404, {"error": "Exercise not found"})

        return create_response(200, updated_exercise.to_dict())

    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error completing exercise: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
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


@with_middleware([log_request, handle_errors])
def reorder_exercises(event, context):
    """
    Handle POST /exercises/reorder request to reorder exercises
    """
    try:
        body = json.loads(event["body"])

        # Extract parameters
        workout_id = body.get("workout_id")
        exercise_order = body.get("exercise_order", [])

        # Validate required fields
        if not workout_id or not exercise_order:
            return create_response(400, {"error": "Missing required fields"})

        # Reorder exercises
        reorder_exercises = exercise_service.reorder_exercises(
            workout_id, exercise_order
        )

        return create_response(
            200, [exercise.to_dict() for exercise in reorder_exercises]
        )

    except Exception as e:
        logger.error(f"Error reordering exercises: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def track_set(event, context):
    """
    Handle POST /exercises/{exercise_id}/sets/{set_number} request to track a set
    """
    try:
        # Extract parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        set_number = int(event["pathParameters"]["set_number"])
        body = json.loads(event["body"])

        # Extract set data
        reps = body.get("reps")
        weight = body.get("weight")
        rpe = body.get("rpe")
        completed = body.get("completed", True)
        notes = body.get("notes")

        # Validate required fields
        if reps is None or weight is None:
            return create_response(
                400, {"error": "Missing required fields: reps and weight"}
            )

        # Create service and call method
        service = ExerciseService()

        # First check if exercise exists to avoid TypeError
        exercise = service.get_exercise(exercise_id)
        if not exercise:
            return create_response(404, {"error": "Exercise not found"})

        # If exercise exists, track the set
        updated_exercise = service.track_set(
            exercise_id=exercise_id,
            set_number=set_number,
            reps=reps,
            weight=weight,
            rpe=rpe,
            completed=completed,
            notes=notes,
        )

        # Convert to dict and return
        response_data = updated_exercise.to_dict()
        return create_response(200, response_data)

    except ValueError as e:
        return create_response(400, {"error": f"Invalid parameters: {str(e)}"})
    except Exception as e:
        logger.error(f"Error tracking set: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return create_response(500, {"error": f"Server error: {str(e)}"})


@with_middleware([log_request, handle_errors])
def delete_exercise_set(event, context):
    """
    Handle DELETE /exercises/{exercise_id}/sets/{set_number} request to delete a set
    """
    try:
        # Extract parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        set_number = int(event["pathParameters"]["set_number"])

        # Create service and call method
        service = ExerciseService()

        # First check if exercise exists
        exercise = service.get_exercise(exercise_id)
        if not exercise:
            return create_response(404, {"error": "Exercise not found"})

        # Delete the set
        updated_exercise = service.delete_set(exercise_id, set_number)

        if not updated_exercise:
            return create_response(404, {"error": "Set not found or already deleted"})

        # Return the updated exercise
        return create_response(200, updated_exercise.to_dict())

    except ValueError as e:
        return create_response(400, {"error": f"Invalid parameters: {str(e)}"})
    except Exception as e:
        logger.error(f"Error deleting set: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return create_response(500, {"error": f"Server error: {str(e)}"})
