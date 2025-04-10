import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import user_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /users": user_api.create_user,
    "GET /users/{user_id}": user_api.get_user,
    "PUT /users/{user_id}": user_api.update_user,
}


def handler(event, context):
    """
    Lambda handler for user-related API endpoints.
    Maps API Gateway requests to the appropriate user API function.
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
