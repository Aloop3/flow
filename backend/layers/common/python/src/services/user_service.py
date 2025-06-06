import uuid
from typing import Dict, Any, Optional
from src.repositories.user_repository import UserRepository
from src.models.user import User
from src.models.exercise_type import ExerciseType, ExerciseCategory


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
        weight_unit_preference: Optional[str] = "auto",
    ) -> User:
        """
        Creates a new user

        :param email: The email of the user
        :param name: The name of the user
        :param role: The role of the user
        :param weight_unit_preference: The user's weight unit preference
        :return: The created User object
        """
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
        self.user_repository.update_user(user_id, update_data)
        return self.get_user(user_id)

    def create_custom_exercise(
        self, user_id: str, exercise_name: str, exercise_category: str
    ) -> Dict[str, Any]:
        """
        Creates a custom exercise for a user

        :param user_id: The ID of the user
        :param exercise_name: Name of the custom exercise
        :param exercise_category: Category of the custom exercise
        :return: Dictionary with result or error
        """
        # Validate category exists (input should be lowercase, enum values are lowercase)
        try:
            category_enum = ExerciseCategory(exercise_category.lower())
            # Don't allow CUSTOM category for user-created exercises
            if category_enum == ExerciseCategory.CUSTOM:
                return {"error": "Cannot use CUSTOM category for user exercises"}
        except ValueError:
            valid_categories = [
                cat.value for cat in ExerciseCategory if cat != ExerciseCategory.CUSTOM
            ]
            return {
                "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            }

        # Check if exercise name conflicts with predefined exercises
        if ExerciseType.is_valid_predefined(exercise_name):
            return {
                "error": f"Exercise '{exercise_name}' already exists in predefined library"
            }

        # Get current user to check existing custom exercises
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}

        # Check for duplicate custom exercises (case-insensitive)
        normalized_name = exercise_name.lower()
        for custom_exercise in user.custom_exercises:
            if custom_exercise.get("name", "").lower() == normalized_name:
                return {"error": f"Custom exercise '{exercise_name}' already exists"}

        # Create custom exercise object (store category as uppercase enum name for consistency)
        custom_exercise = {
            "name": exercise_name,
            "category": category_enum.name,  # This stores "BODYWEIGHT" instead of "bodyweight"
        }

        # Add to user's custom exercises
        updated_custom_exercises = user.custom_exercises + [custom_exercise]

        # Update user in database
        update_result = self.user_repository.update_user(
            user_id, {"custom_exercises": updated_custom_exercises}
        )

        return {
            "message": "Custom exercise created successfully",
            "exercise": custom_exercise,
            "user": update_result,
        }
