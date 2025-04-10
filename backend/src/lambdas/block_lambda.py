import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import block_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /blocks": block_api.create_block,
    "GET /blocks/{block_id}": block_api.get_block,
    "GET /athletes/{athlete_id}/blocks": block_api.get_blocks_by_athlete,
    "PUT /blocks/{block_id}": block_api.update_block,
    "DELETE /blocks/{block_id}": block_api.delete_block,
}


def handler(event, context):
    """
    Lambda handler for block-related API endpoints.
    Maps API Gateway requests to the appropriate block API function.
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
