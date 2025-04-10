import os

def add_cors_headers(response):
    """Add CORS headers to response"""
    if "headers" not in response:
        response["headers"] = {}
    
    response["headers"].update({
        "Access-Control-Allow-Origin": os.environ.get("CORS_ALLOWED_ORIGIN", "http://localhost:5173"),
        "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS,PATCH",
        "Access-Control-Allow-Credentials": "true"
    })
    return response