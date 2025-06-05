import json
import logging
from src.services.user_service import UserService
from src.services.exercise_service import ExerciseService
from src.services.workout_service import WorkoutService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors
from src.utils.weight_utils import (
    convert_weight_to_kg,
    convert_weight_from_kg,
    get_exercise_default_unit,
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

user_service = UserService()
exercise_service = ExerciseService()
workout_service = WorkoutService()


def get_user_weight_preference(user_id: str) -> str:
    """
    Get user's weight preference with graceful fallback.

    :param user_id: User ID from Cognito claims
    :return: Weight preference ("auto", "kg", "lb")
    """
    try:
        user = user_service.get_user(user_id)
        return user.weight_unit_preference if user else "auto"
    except Exception as e:
        logger.warning(f"Failed to get user weight preference for {user_id}: {str(e)}")
        return "auto"


def convert_exercise_weights_for_display(exercise_dict, user_preference, exercise_type):
    """Convert exercise weights from kg (storage) to display unit"""
    display_unit = get_exercise_default_unit(exercise_type, user_preference)

    # Convert template weight
    if "weight" in exercise_dict and exercise_dict["weight"] is not None:
        exercise_dict["weight"] = convert_weight_from_kg(
            exercise_dict["weight"], display_unit
        )

    # Convert sets_data weights
    if "sets_data" in exercise_dict and exercise_dict["sets_data"]:
        for set_data in exercise_dict["sets_data"]:
            if "weight" in set_data and set_data["weight"] is not None:
                set_data["weight"] = convert_weight_from_kg(
                    set_data["weight"], display_unit
                )

    # Add display unit info
    exercise_dict["display_unit"] = display_unit
    return exercise_dict


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

        # Get user preference for weight conversion
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        user_preference = get_user_weight_preference(user_id)

        # Convert weight from display unit to kg for storage
        weight_kg = weight
        if weight is not None:
            display_unit = get_exercise_default_unit(exercise_type, user_preference)
            weight_kg = convert_weight_to_kg(weight, display_unit)

        # Create exercise
        exercise = exercise_service.create_exercise(
            workout_id=workout_id,
            exercise_type=exercise_type,
            exercise_category=exercise_category,
            sets=sets,
            reps=reps,
            weight=weight_kg,  # Use converted weight
            rpe=rpe,
            notes=notes,
            order=order,
        )

        # Convert response back to display units
        response_data = convert_exercise_weights_for_display(
            exercise.to_dict(), user_preference, exercise_type
        )
        return create_response(201, response_data)

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

        # Get user preference for weight conversion
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        user_preference = get_user_weight_preference(user_id)

        # Get exercises
        exercises = exercise_service.get_exercises_for_workout(workout_id)

        # Convert all exercise weights to display units
        converted_exercises = []
        for exercise in exercises:
            exercise_dict = exercise.to_dict()
            converted_exercise = convert_exercise_weights_for_display(
                exercise_dict, user_preference, exercise.exercise_type
            )
            converted_exercises.append(converted_exercise)

        return create_response(200, converted_exercises)

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

        # Get user preference and exercise info for weight conversion
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        user_preference = get_user_weight_preference(user_id)

        # Get exercise to determine type
        exercise = exercise_service.get_exercise(exercise_id)
        if not exercise:
            return create_response(404, {"error": "Exercise not found"})

        # Convert weight from display unit to kg
        display_unit = get_exercise_default_unit(
            exercise.exercise_type, user_preference
        )
        weight_kg = convert_weight_to_kg(weight, display_unit)

        # Complete the exercise with converted weight
        updated_exercise = workout_service.complete_exercise(
            exercise_id=exercise_id,
            sets=sets,
            reps=reps,
            weight=weight_kg,  # Use converted weight
            rpe=rpe,
            notes=notes,
        )

        if not updated_exercise:
            return create_response(404, {"error": "Exercise not found"})

        # Convert response back to display units
        response_data = convert_exercise_weights_for_display(
            updated_exercise.to_dict(), user_preference, updated_exercise.exercise_type
        )
        return create_response(200, response_data)

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
def reorder_sets(event, context):
    """
    Handle POST /exercises/{exercise_id}/reorder-sets request to reorder sets
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        body = json.loads(event["body"])

        # Extract new set order from request
        new_order = body.get("set_order", [])  # Array of set_numbers in new order

        # Validate required fields
        if not new_order:
            return create_response(400, {"error": "Missing set_order array"})

        # Create service instance
        service = ExerciseService()

        # Get exercise to verify it exists
        exercise = service.get_exercise(exercise_id)
        if not exercise:
            return create_response(404, {"error": "Exercise not found"})

        # Reorder the sets
        updated_exercise = service.reorder_sets(exercise_id, new_order)

        if not updated_exercise:
            return create_response(404, {"error": "Failed to reorder sets"})

        # Get user preference for weight conversion in response
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        user_preference = get_user_weight_preference(user_id)

        # Convert response back to display units
        response_data = convert_exercise_weights_for_display(
            updated_exercise.to_dict(), user_preference, updated_exercise.exercise_type
        )
        return create_response(200, response_data)

    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})
    except ValueError as e:
        return create_response(400, {"error": f"Invalid parameters: {str(e)}"})
    except Exception as e:
        logger.error(f"Error reordering sets: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return create_response(500, {"error": f"Server error: {str(e)}"})


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

        # Create service instance
        service = ExerciseService()

        # Get user preference and exercise info for weight conversion
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        user_preference = get_user_weight_preference(user_id)

        # Get exercise to determine type
        exercise = service.get_exercise(exercise_id)
        if not exercise:
            return create_response(404, {"error": "Exercise not found"})

        # Convert weight from display unit to kg
        display_unit = get_exercise_default_unit(
            exercise.exercise_type, user_preference
        )
        weight_kg = convert_weight_to_kg(weight, display_unit)

        # Track the set with converted weight
        updated_exercise = service.track_set(
            exercise_id=exercise_id,
            set_number=set_number,
            reps=reps,
            weight=weight_kg,
            rpe=rpe,
            completed=completed,
            notes=notes,
        )

        # Convert response back to display units for frontend
        response_data = convert_exercise_weights_for_display(
            updated_exercise.to_dict(), user_preference, updated_exercise.exercise_type
        )
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
