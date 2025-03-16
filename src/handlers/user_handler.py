import json
import logging
from src.services.user_service import UserService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

user_service = UserService()

def create_user(event, context):
    """
    Lambda function to create a new user
    """
    try:
        body = json.loads(event["body"])

        # Extract user details from request
        email = body["email"]
        name = body["name"]
        role = body["role"]

        # Validate required fields
        if not email or not name or not role:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }
        
        # Validate role
        if role not in ["athlete", "coach", "both"]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid role"})
            }
        
        # Create user
        user = user_service.create_user(email=email, name=name, role=role)

        return {
            "statusCode": 201,
            "body": json.dumps(user.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def get_user(event, context):
    """
    Lambda function to get a user by ID
    """
    try:
        user_id = event["pathParameters"]["user_id"]

        # Get user
        user = user_service.get_user(user_id)

        if not user:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(user.to_dict())
        }
    
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def update_user(event, context):
    """
    Lambda function to update a user by ID
    """
    try:
        user_id = event["pathParameters"]["user_id"]
        body = json.loads(event["body"])

        # Update user
        update_user = user_service.update_user(user_id, body)

        if not update_user:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }
        
        return {
            "statusCode": 200,
            "body": json.dumps(update_user.to_dict())
        }

    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
