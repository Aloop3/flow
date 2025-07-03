import os


def add_cors_headers(response, event=None):
    """Add proper CORS headers"""
    if "headers" not in response:
        response["headers"] = {}

    # Get CORS origin from environment variable
    cors_origin = os.environ.get("CORS_ORIGIN", "*")

    response["headers"].update(
        {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
        }
    )

    return response


def add_feedback_cors_headers(response):
    """Add proper CORS headers for feedback endpoint"""
    if "headers" not in response:
        response["headers"] = {}

    # Get CORS origin from environment variable, fallback to '*' for dev
    cors_origin = os.environ.get("CORS_ORIGIN", "*")

    response["headers"].update(
        {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
        }
    )
    return response
