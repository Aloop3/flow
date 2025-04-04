import json
import logging
from src.api import exercise_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /exercises": exercise_api.create_exercise,
    "GET /days/{day_id}/exercises": exercise_api.get_exercises_for_workout,
    "PUT /exercises/{exercise_id}": exercise_api.update_exercise,
    "DELETE /exercises/{exercise_id}": exercise_api.delete_exercise,
    "POST /exercises/reorder": exercise_api.reorder_exercises,
}


def handler(event, context):
    """
    Lambda handler for exercise-related API endpoints.
    Maps API Gateway requests to the appropriate exercise API function.
    """
    try:
        # Extract route information
        method = event.get("httpMethod")
        resource = event.get("resource")
        route_key = f"{method} {resource}"

        logger.info(f"Processing {route_key} request")

        # Find the appropriate handler function
        handler_func = ROUTE_MAP.get(route_key)

        if handler_func:
            return handler_func(event, context)
        else:
            return {"statusCode": 404, "body": json.dumps({"error": "Route not found"})}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }
