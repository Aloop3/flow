import json
import logging
from src.services.user_service import UserService
from src.utils.response import create_response
from src.middleware.middleware import with_middleware
from src.middleware.common_middleware import log_request, handle_errors

logger = logging.getLogger()
logger.setLevel(logging.INFO)

user_service = UserService()


@with_middleware([log_request, handle_errors])
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

        # Validate required fields
        if not email or not name:
            return create_response(400, {"error": "Missing required fields"})

        # Validate role
        if role is not None and role not in ["athlete", "coach"]:
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


@with_middleware([log_request, handle_errors])
def get_user(event, context):
    """
    Handle GET /users/{user_id} request to get a user by ID
    """
    try:
        user_id = event["pathParameters"]["user_id"]

        user = user_service.get_user(user_id)

        if not user:
            return create_response(404, {"error": "User not found"})

        return create_response(200, user.to_dict())

    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return create_response(500, {"error": str(e)})


@with_middleware([log_request, handle_errors])
def update_user(event, context):
    """
    Handle PUT /users/{user_id} request to update a user by ID
    """
    try:
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


@with_middleware([log_request, handle_errors])
def create_custom_exercise(event, context):
    """
    Handle POST /users/{user_id}/custom-exercises request to create a custom exercise
    """
    try:
        # Extract user_id from path and get authenticated user
        user_id = event["pathParameters"]["user_id"]
        authenticated_user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        # Verify user can only create custom exercises for themselves
        if user_id != authenticated_user_id:
            return create_response(
                403, {"error": "Cannot create custom exercises for other users"}
            )

        body = json.loads(event["body"])

        # Extract custom exercise data
        exercise_name = body.get("name", "").strip()
        exercise_category = body.get("category", "").strip()

        # Validate required fields
        if not exercise_name or not exercise_category:
            return create_response(
                400, {"error": "Missing required fields: name and category"}
            )

        # Create custom exercise
        result = user_service.create_custom_exercise(
            user_id, exercise_name, exercise_category
        )

        if result.get("error"):
            return create_response(400, {"error": result["error"]})

        return create_response(201, result)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        return create_response(400, {"error": "Invalid JSON in request body"})
    except Exception as e:
        logger.error(f"Error creating custom exercise: {str(e)}")
        return create_response(500, {"error": str(e)})
