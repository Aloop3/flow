import logging
import os
import boto3
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table(os.environ["USERS_TABLE"])


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda trigger for Cognito post confirmation event.
    Creates user in DynamoDB after successful registration.
    """
    try:
        # Extract user attributes
        user_attributes = event["request"]["userAttributes"]

        # Create user in DynamoDB directly (skip API validation)
        user_item = {
            "user_id": user_attributes["sub"],
            "email": user_attributes["email"],
            "name": user_attributes.get("name", user_attributes["email"].split("@")[0]),
            "role": None,  # User will select role later
        }

        users_table.put_item(Item=user_item)
        logger.info(f"Created user in DynamoDB: {user_attributes['sub']}")

        
        return event

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        # Still return event to avoid blocking user registration
        return event
