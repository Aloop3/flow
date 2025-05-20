import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import relationship_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /relationships": relationship_api.create_relationship,
    "POST /relationships/{relationship_id}/accept": relationship_api.accept_relationship,
    "POST /relationships/{relationship_id}/end": relationship_api.end_relationship,
    "GET /coaches/{coach_id}/relationships": relationship_api.get_relationships_for_coach,
    "GET /relationships/{relationship_id}": relationship_api.get_relationship,
    "POST /coaches/{coach_id}/invitation": relationship_api.generate_invitation_code,
    "POST /athletes/{athlete_id}/accept-invitation": relationship_api.accept_invitation_code,
}


def handler(event, context):
    """
    Lambda handler for relationship-related API endpoints.
    Maps API Gateway requests to the appropriate relationship API function.
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
