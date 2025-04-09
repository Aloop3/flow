import json
import logging
from src.api import set_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "GET /sets/{set_id}": set_api.get_set,
    "GET /exercises/{exercise_id}/sets": set_api.get_sets_for_exercise,
    "POST /exercises/{exercise_id}/sets": set_api.create_set,
    "PUT /sets/{set_id}": set_api.update_set,
    "DELETE /sets/{set_id}": set_api.delete_set,
}


def handler(event, context):
    """
    Lambda handler for set-related API endpoints.
    Maps API Gateway requests to the appropriate set API function.
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
