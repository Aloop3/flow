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

    def create_user(
        self,
        email: str,
        name: str,
        role: Optional[str] = None,
        weight_unit_preference: Optional[str] = "lb",
    ) -> User:
        """
        Creates a new user with optional weight preference

        :param email: The email of the user
        :param name: The name of the user
        :param role: The role of the user
        :param weight_unit_preference: The user's preferred weight unit ('kg' or 'lb')
        :return: The created User object
        """
        # Validate weight unit preference
        if weight_unit_preference and weight_unit_preference not in ["kg", "lb"]:
            weight_unit_preference = "lb"

        user = User(
            user_id=str(uuid.uuid4()),
            email=email,
            name=name,
            role=role,
            weight_unit_preference=weight_unit_preference,
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
        # Validate weight_unit_preference if it's being updated
        if "weight_unit_preference" in update_data:
            weight_pref = update_data["weight_unit_preference"]
            if weight_pref and weight_pref not in ["kg", "lb"]:
                update_data["weight_unit_preference"] = "lb"

        self.user_repository.update_user(user_id, update_data)
        return self.get_user(user_id)

    def get_user_weight_unit_preference(self, user_id: str) -> str:
        """
        Get user's weight unit preference, with fallback to 'lb'

        :param user_id: The ID of the user
        :return: Weight unit preference ('kg' or 'lb')
        """
        user = self.get_user(user_id)
        if user and user.weight_unit_preference:
            return user.weight_unit_preference
        return "lb"
