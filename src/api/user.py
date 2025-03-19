import json
import logging
from src.services.user_service import UserService
from src.utils.response import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

user_service = UserService()

def create_user(event, context):
    """
    Handle POST /users request to create a new user
    """
    try:
        body = json.loads(event["body"])

        # Extract user details from request
        email = body.get("email", None)
        name = body.get("name", None)
        role = body.get("role", None)

        logger.debug(f"Extracted fields - email {email}, name: {name}, role: {role}")

        # Validate required fields
        if not email or not name or not role:
            logger.info("Validation failed: Missing required fields")
            return create_response(400, {"error": "Missing required fields"})
        
        # Validate role
        if role not in ["athlete", "coach", "both"]:
            logger.info(f"Validation failed: Invalid role {role}")
            return create_response(400, {"error": "Invalid role"})
        
        # Create user
        user = user_service.create_user(email=email, name=name, role=role)

        return create_response(201, user.to_dict())
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return create_response(500, {"error": str(e)})

def get_user(event, context):
    """
    Handle GET /users/{user_id} request to get a user by ID
    """
    try:
        if not event.get("pathParameters") or not event["pathParameters"].get("user_id"):
            return create_response(400, {"error": "Missing user_id in path parameters"})

        user_id = event["pathParameters"]["user_id"]

        user = user_service.get_user(user_id)

        if not user:
            return create_response(404, {"error": "User not found"})
        
        return create_response(200, user.to_dict())
    
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return create_response(500, {"error": str(e)})

def update_user(event, context):
    """
    Handle PUT /users/{user_id} request to update a user by ID
    """
    try:
        if not event.get("pathParameters") or not event["pathParameters"].get("user_id"):
            return create_response(400, {"error": "Missing user_id in path parameters"})
        
        if not event.get("body"):
            return create_response(400, {"error": "Missing request body"})

        user_id = event["pathParameters"]["user_id"]
        body = json.loads(event["body"])

        # Update user
        update_user = user_service.update_user(user_id, body)

        if not update_user:
            return create_response(404, {"error": "User not found"})
        
        return create_response(200, update_user.to_dict())
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return create_response(500, {"error": str(e)})
    