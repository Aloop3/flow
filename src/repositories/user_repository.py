from typing import Dict, Any, Optional
from .base_repository import BaseRepository
import os


class UserRepository(BaseRepository):
    """
    Repository class for handling user-related database operations in DynamoDB.

    Extends BaseRepository to provide methods for retrieving, creating, and updating user data.
    """
    def __init__(self):
        super().__init__(os.environ.get("USERS_TABLE"))
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user from the database using their unique user ID.

        :param user_id: The unique identifier of the user.
        :return: A dictionary containing user details if found, else None.
        """
        return self.get_by_id("user_id", user_id)
    
    def create_user(self, user_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new user in the database

        :param user_dict: A dictionary containing the user's details.
        :return: The response from the create operation
        """
        return self.create(user_dict)
    
    def update_user(self, user_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing user in the database.

        :param user_id: The unique identifier of the user to update.
        :param update_dict: A dictionary containing the attributes to update.
        :return: The response from the update operation.
        """
        update_expression = "set "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in update_dict.items():
            attribute_placeholder = f"#{key}"
            value_placeholder = f":{key}"

            update_expression += f"{attribute_placeholder} = {value_placeholder}, "
            expression_attribute_values[value_placeholder] = value
            expression_attribute_names[attribute_placeholder] = key

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        response = self.table.update_item(
            Key={"user_id": user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )

        return response.get("Attributes", {})