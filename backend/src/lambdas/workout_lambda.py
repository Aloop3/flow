import json
import logging
from src.utils.cors_utils import add_cors_headers
from src.api import workout_api
from src.api import exercise_type_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Map routes to handler functions
ROUTE_MAP = {
    "POST /workouts": workout_api.create_workout,
    "GET /workouts/{workout_id}": workout_api.get_workout,
    "GET /athletes/{athlete_id}/workouts": workout_api.get_workouts_by_athlete,
    "GET /athletes/{athlete_id}/days/{day_id}/workout": workout_api.get_workout_by_day,
    "PUT /workouts/{workout_id}": workout_api.update_workout,
    "DELETE /workouts/{workout_id}": workout_api.delete_workout,
    "POST /workouts/copy": workout_api.copy_workout,
    "POST /days/{day_id}/workout": workout_api.create_day_workout,
    "GET /exercises/types": exercise_type_api.get_exercise_types,
}


def handler(event, context):
    """
    Lambda handler for workout-related API endpoints.
    Maps API Gateway requests to the appropriate workout API function.
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
