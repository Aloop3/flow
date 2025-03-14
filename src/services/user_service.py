import uuid
from typing import Dict, Any, Optional
from src.repositories.user_repository import UserRepository
from src.models.user import User

class UserService:
    def __init__(self):
        self.user_repository: UserRepository = UserRepository()

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Retrieves a user by user_id

        :param user_id: The ID of the user to retrieve
        :return: The User object if found, else None
        """
        user_data = self.user_repository.get_user(user_id)
        if user_data:
            return User(**user_data)
        return None
    
    def create_user(self, email: str, name: str, role: str) -> User:
        """
        Creates a new user

        :param email: The email of the user
        :param name: The name of the user
        :param role: The role of the user
        :return: The created User object
        """
        user = User(
            user_id=str(uuid.uuid4()),
            email=email,
            name=name,
            role=role
        )

        self.user_repository.create_user(user.to_dict())

        return user
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """
        Updates a user by user_id

        :param user_id: The ID of the user to update
        :param update_data: The data to update the user with
        :return: The updated User object if found, else None
        """
        self.user_repository.update_user(user_id, update_data)
        return self.get_user(user_id)