import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import analytics_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "GET /analytics/max-weight/{athlete_id}": analytics_api.get_max_weight_history,
    "GET /analytics/volume/{athlete_id}": analytics_api.get_volume_calculation,
    "GET /analytics/frequency/{athlete_id}": analytics_api.get_exercise_frequency,
    "GET /analytics/block-analysis/{athlete_id}/{block_id}": analytics_api.get_block_analysis,
    "GET /analytics/block-comparison/{athlete_id}": analytics_api.get_block_comparison,
}


def handler(event, context):
    """
    Lambda handler for analytics-related API endpoints.
    Maps API Gateway requests to the appropriate analytics API function.
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
            logger.warning(f"No route found for {route_key}")
            return add_cors_headers(
                {"statusCode": 404, "body": json.dumps({"error": "Route not found"})}
            )
    except Exception as e:
        logger.error(f"Error processing analytics request: {str(e)}")
        return add_cors_headers(
            {
                "statusCode": 500,
                "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
            }
        )
