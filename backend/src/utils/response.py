import json
import os
from typing import Dict, Any, Union
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def create_response(
    status_code: int, body: Union[Dict[str, Any], list]
) -> Dict[str, Any]:
    """
    Create a standardized API response

    :param status_code: The HTTP status code
    :param body: The response body content
    :return: A dictionary representing the API response
    """
    # Get CORS origin from environment variable, fallback to '*' for dev
    cors_origin = os.environ.get("CORS_ORIGIN", "*")

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }
