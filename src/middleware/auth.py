import os
import json
import logging
from functools import wraps
from typing import Callable, Dict, Any, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def require_auth(handler_function: Callable) -> Callable:
    """
    Decorator to enforce authentication using Cognito token

    :param handler_function: Lambda handler function to wrap
    :return Callable: Wrapped handler function with auth check
    """

    @wraps(handler_function)
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        # Auth is handled by the API Gateway Authorizer

        # Check if we have auth claims from Cognito
        if (
            "requestContext" not in event
            or "authorizer" not in event["requestContext"]
            or "claims" not in event["requestContext"]["authorizer"]
        ):
            logger.error("No auth claims found in event")
            return {"statusCode": 401, "body": json.dumps({"message": "Unauthorized"})}

        # Continue with the handler
        return handler_function(event, context)

    return wrapper
