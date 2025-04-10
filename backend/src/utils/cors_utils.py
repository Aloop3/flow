import os

CORS_ALLOWED_ORIGIN = os.environ.get("CORS_ALLOWED_ORIGIN", "http://localhost:5173")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": CORS_ALLOWED_ORIGIN,
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS,PATCH",
    "Access-Control-Allow-Credentials": "true",
}


def add_cors_headers(response):
    """
    Adds CORS headers to the response
    """
    if "headers" not in response:
        response["headers"] = {}

    response["headers"].update(CORS_HEADERS)
    return response
