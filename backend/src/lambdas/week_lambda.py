import json
import logging
from src.api import week_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /weeks": week_api.create_week,
    "GET /blocks/{block_id}/weeks": week_api.get_weeks_for_block,
    "PUT /weeks/{week_id}": week_api.update_week,
    "DELETE /weeks/{week_id}": week_api.delete_week,
}


def handler(event, context):
    """
    Lambda handler for week-related API endpoints.
    Maps API Gateway requests to the appropriate week API function.
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
