import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import exercise_api
from src.api import exercise_type_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /exercises": exercise_api.create_exercise,
    "GET /days/{day_id}/exercises": exercise_api.get_exercises_for_workout,
    "GET /exercises/types": exercise_type_api.get_exercise_types,
    "PUT /exercises/{exercise_id}": exercise_api.update_exercise,
    "DELETE /exercises/{exercise_id}": exercise_api.delete_exercise,
    "POST /exercises/reorder": exercise_api.reorder_exercises,
    "POST /exercises/{exercise_id}/complete": exercise_api.complete_exercise,
    "POST /exercises/{exercise_id}/sets/{set_number}": exercise_api.track_set,
    "DELETE /exercises/{exercise_id}/sets/{set_number}": exercise_api.delete_exercise_set,
}


def handler(event, context):
    """
    Lambda handler for exercise-related API endpoints.
    Maps API Gateway requests to the appropriate exercise API function.
    """
    # Handle OPTIONS requests for CORS
    if event.get("httpMethod") == "OPTIONS":
        return add_cors_headers(
            {"statusCode": 200, "body": json.dumps({"message": "OK"})}
        )

    try:
        # Extract route information
        method = event.get("httpMethod")
        resource = event.get("resource")
        route_key = f"{method} {resource}"

        logger.info(f"Processing {route_key} request")

        # Find the appropriate handler function
        handler_func = ROUTE_MAP.get(route_key)

        if handler_func:
            response = handler_func(event, context)
            return add_cors_headers(response)
        else:
            return add_cors_headers(
                {"statusCode": 404, "body": json.dumps({"error": "Route not found"})}
            )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return add_cors_headers(
            {
                "statusCode": 500,
                "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
            }
        )
