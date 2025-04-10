import json
import logging
from typing import Dict, Any
from src.middleware.middleware import ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_auth(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Middleware to validate authentication information in the request.

    :param event: The Lambda event
    :param context: The Lambda context
    :return: The event, possibly modified
    :raises: ValidationError if authentication fails
    """
    if (
        "requestContext" not in event
        or "authorizer" not in event["requestContext"]
        or "claims" not in event["requestContext"]["authorizer"]
    ):
        logger.error("No auth claims found in event")
        raise ValidationError("Unauthorized")

    return event


def log_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Middleware to log request details.

    :param event: The Lambda event
    :param context: The Lambda context
    :return: The event, unchanged
    """
    # Create a log-safe representation of the request
    request_id = "unknown"
    if hasattr(context, "aws_request_id"):
        request_id = context.aws_request_id

    log_data = {
        "request_id": request_id,
        "path": event.get("path", "unknown"),
        "method": event.get("httpMethod", "unknown"),
        "user": event.get("requestContext", {})
        .get("authorizer", {})
        .get("claims", {})
        .get("sub", "unknown"),
    }

    # Use string formatting instead of json.dumps to avoid serialization issues with mock objects
    logger.info(
        f"Request: path={log_data['path']}, method={log_data['method']}, request_id={log_data['request_id']}, user={log_data['user']}"
    )

    return event


def handle_errors(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Checks for:
    - Missing path parameters
    - Invalid JSON in request body
    - Missing required query parameters

    :param event: The Lambda event
    :param context: The Lambda context
    :return: The event, possibly with added error information
    :raises: ValidationError for common errors with appropriate message
    """
    # Initialize an errors object in the event if it doesn't exist
    if "errors" not in event:
        event["errors"] = []

    # Check if body exists and is valid JSON
    if "body" in event and event["body"]:
        try:
            json.loads(event["body"])
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            raise ValidationError(f"Invalid JSON in request body: {str(e)}")

    # Check if required path parameters exist
    method = event.get("httpMethod", "").upper()
    path = event.get("path", "")

    # Map of endpoints that require specific path parameters
    path_param_requirements = {
        "GET /users/{user_id}": ["user_id"],
        "GET /blocks/{block_id}": ["block_id"],
        "GET /blocks/{block_id}/weeks": ["block_id"],
        "GET /weeks/{week_id}/days": ["week_id"],
        "GET /workouts/{workout_id}": ["workout_id"],
        "PUT /users/{user_id}": ["user_id"],
        "PUT /blocks/{block_id}": ["block_id"],
        "PUT /weeks/{week_id}": ["week_id"],
        "PUT /days/{day_id}": ["day_id"],
        "DELETE /blocks/{block_id}": ["block_id"],
        "DELETE /weeks/{week_id}": ["week_id"],
        "DELETE /days/{day_id}": ["day_id"],
        "DELETE /workouts/{workout_id}": ["workout_id"],
    }

    # Check if the current endpoint has path parameter requirements
    for pattern, required_params in path_param_requirements.items():
        # Skip if method doesn't match
        if not pattern.startswith(method):
            continue

        # Extract the path pattern (remove the method)
        path_pattern = pattern[len(method) + 1 :]

        # Check if the path matches the pattern
        path_parts = path.split("/")
        pattern_parts = path_pattern.split("/")

        if len(path_parts) != len(pattern_parts):
            continue

        # Check if path matches pattern
        matches = True
        for i, (path_part, pattern_part) in enumerate(zip(path_parts, pattern_parts)):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                # This is a parameter part, no need to match exactly
                continue
            elif path_part != pattern_part:
                matches = False
                break

        if matches:
            # This pattern matches our path, check required parameters
            path_parameters = event.get("pathParameters", {}) or {}

            for param in required_params:
                if not path_parameters or param not in path_parameters:
                    logger.error(f"Missing path parameter: {param}")
                    raise ValidationError(f"Missing path parameter: {param}")

    # Check if required query parameters exist for specific endpoints
    query_param_requirements = {
        "GET /coaches/{coach_id}/relationships": ["status"],
        "GET /athletes/{athlete_id}/progress": ["time_period"],
    }

    # Similar check as for path parameters
    for pattern, required_params in query_param_requirements.items():
        if not pattern.startswith(method):
            continue

        path_pattern = pattern[len(method) + 1 :]
        path_parts = path.split("/")
        pattern_parts = path_pattern.split("/")

        if len(path_parts) != len(pattern_parts):
            continue

        matches = True
        for i, (path_part, pattern_part) in enumerate(zip(path_parts, pattern_parts)):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                continue
            elif path_part != pattern_part:
                matches = False
                break

        if matches:
            query_parameters = event.get("queryStringParameters", {}) or {}

            for param in required_params:
                if not query_parameters or param not in query_parameters:
                    event["errors"].append(f"Missing query parameter: {param}")

    # Check if body is required for specific methods
    body_required_methods = ["POST", "PUT", "PATCH"]

    if method in body_required_methods and ("body" not in event or not event["body"]):
        # Check if current path is in the exception list
        path_parts = path.split("/")

        # Check for exception endpoints
        is_exception = False

        # Check for relationship endpoints like "/relationships/123/accept"
        if (
            len(path_parts) >= 4
            and path_parts[1] == "relationships"
            and path_parts[3] in ["accept", "end"]
        ):
            is_exception = True

        if not is_exception:
            raise ValidationError("Request body is required")

    return event
