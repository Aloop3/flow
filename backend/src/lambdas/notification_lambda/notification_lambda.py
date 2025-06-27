import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import notification_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "GET /notifications": notification_api.get_notifications,
    "PATCH /notifications/{notification_id}/read": notification_api.mark_notification_as_read,
}


def handler(event, context):
    """
    Lambda handler for notification-related API endpoints.
    Maps API Gateway requests to the appropriate notification API function.
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
            logger.warning(f"No handler found for {route_key}")
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
