from .base_repository import BaseRepository
import os

class UserRepository(BaseRepository):
    """
    Repository class for handling user-related database operations in DynamoDB.

    Extends BaseRepository to provide methods for retrieving, creating, and updating user data.
    """
    def __init__(self):
        super().__init__(os.environ.get("USER_TABLE"))
    
    def get_user(self, user_id):
        """
        Retrieves a user from the database using their unique user ID.

        :param user_id: The unique identifier of the user.
        :return: A dictionary containing user details if found, else None.
        """
        return self.get_by_id("user_id", user_id)
    
    def create_user(self, user_dict):
        """
        Creates a new user in the database

        :param user_dict: A dictionary containing the user's details.
        :return: The response from the create operation
        """
        return self.create(user_dict)
    
    def update_user(self, user_id, update_dict):
        """
        Updates an existing user in the database.

        :param user_id: The unique identifier of the user to update.
        :param update_dict: A dictionary containing the attributes to update.
        :return: The response from the update operation.
        """
        update_expression = "set "
        expression_values = {}

        for key, value in update_dict.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value
        
        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update(
            {"user_id": user_id},
            update_expression,
            expression_values
        )