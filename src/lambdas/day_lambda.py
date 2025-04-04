import json
import logging
from src.api import day_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /days": day_api.create_day,
    "GET /weeks/{week_id}/days": day_api.get_days_for_week,
    "PUT /days/{day_id}": day_api.update_day,
    "DELETE /days/{day_id}": day_api.delete_day,
}


def handler(event, context):
    """
    Lambda handler for day-related API endpoints.
    Maps API Gateway requests to the appropriate day API function.
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
