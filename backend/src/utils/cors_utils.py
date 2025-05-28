def add_cors_headers(response, event=None):
    """
    Minimal response headers - API Gateway handles all CORS
    """
    if "headers" not in response:
        response["headers"] = {}
    
    # Only ensure Content-Type exists
    if "Content-Type" not in response["headers"]:
        response["headers"]["Content-Type"] = "application/json"
    
    return response
