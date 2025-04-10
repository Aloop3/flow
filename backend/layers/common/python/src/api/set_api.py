import json
import logging
from src.services.set_service import SetService
from src.services.workout_service import WorkoutService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

set_service = SetService()
workout_service = WorkoutService()


@with_middleware([log_request, handle_errors])
def get_set(event, context):
    """
    Handle GET /sets/{set_id} request to get a set by ID
    """
    try:
        # Extract set_id from path parameters
        set_id = event["pathParameters"]["set_id"]

        # Get set
        exercise_set = set_service.get_set(set_id)

        if not exercise_set:
            return create_response(404, {"error": "Set not found"})

        return create_response(200, exercise_set.to_dict())

    except Exception as e:
        logger.error(f"Error getting set: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def get_sets_for_exercise(event, context):
    """
    Handle GET /exercises/{exercise_id}/sets request to get all sets for an exercise
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]

        # Get sets
        sets = set_service.get_sets_for_exercise(exercise_id)

        return create_response(
            200, {"exercise_id": exercise_id, "sets": [s.to_dict() for s in sets]}
        )

    except Exception as e:
        logger.error(f"Error getting sets for exercise: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def create_set(event, context):
    """
    Handle POST /exercises/{exercise_id}/sets request to create a new set
    """
    try:
        # Extract exercise_id from path parameters
        exercise_id = event["pathParameters"]["exercise_id"]
        body = json.loads(event["body"])

        # Validate required fields
        required_fields = ["workout_id", "reps", "weight"]
        for field in required_fields:
            if field not in body:
                return create_response(
                    400, {"error": f"Missing required field: {field}"}
                )

        # Extract set data
        set_data = {
            "set_number": body.get("set_number"),
            "reps": body.get("reps"),
            "weight": body.get("weight"),
            "rpe": body.get("rpe"),
            "notes": body.get("notes"),
            "completed": body.get("completed", True),
        }

        # Create set
        exercise_set = workout_service.add_set_to_exercise(
            workout_id=body.get("workout_id"),
            exercise_id=exercise_id,
            set_data=set_data,
        )

        if not exercise_set:
            return create_response(400, {"error": "Failed to create set"})

        return create_response(201, exercise_set.to_dict())

    except ValueError as e:
        logger.error(f"Error creating set: {str(e)}")
        return create_response(400, {"error": str(e)})
    except Exception as e:
        logger.error(f"Error creating set: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def update_set(event, context):
    """
    Handle PUT /sets/{set_id} request to update a set
    """
    try:
        # Extract set_id from path parameters
        set_id = event["pathParameters"]["set_id"]
        body = json.loads(event["body"])

        # Update set
        updated_set = workout_service.update_set(set_id, body)

        if not updated_set:
            return create_response(404, {"error": "Set not found"})

        return create_response(200, updated_set.to_dict())

    except Exception as e:
        logger.error(f"Error updating set: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def delete_set(event, context):
    """
    Handle DELETE /sets/{set_id} request to delete a set
    """
    try:
        # Extract set_id from path parameters
        set_id = event["pathParameters"]["set_id"]

        # Delete set
        success = workout_service.delete_set(set_id)

        if not success:
            return create_response(404, {"error": "Set not found"})

        return create_response(204, {})

    except Exception as e:
        logger.error(f"Error deleting set: {str(e)}")
        return create_response(500, {"error": str(e)})
