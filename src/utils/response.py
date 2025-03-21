import json
from typing import Dict, Any, Union
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def create_response(status_code: int, body: Union[Dict[str, Any], list]) -> Dict[str, Any]:
    """
    Create a standardized API response
    
    :param status_code: The HTTP status code
    :param body: The response body content
    :return: A dictionary representing the API response
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control_Allow-Methods": "OPTIONS,GET,POST,PUT,DELTE",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }