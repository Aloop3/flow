import unittest
from unittest.mock import MagicMock, patch
from src.models.user import User
from src.services.user_service import UserService


class TestUserService(unittest.TestCase):
    """
    Test suite for the UserService class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.user_repository_mock = MagicMock()

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value="test-uuid")
        self.uuid_mock = self.uuid_patcher.start()

        # Initialize service with mocked repository
        with patch(
            "src.services.user_service.UserRepository",
            return_value=self.user_repository_mock,
        ):
            self.user_service = UserService()

    def tearDown(self):
        """
        Clean up after each test method
        """
        self.uuid_patcher.stop()

    def test_get_user_found(self):
        """
        Test retrieving a user by ID when the user exists
        """
        # Mock data that would be returned from the repository
        mock_user_data = {
            "user_id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
        }

        # Configure mock to return our test data
        self.user_repository_mock.get_user.return_value = mock_user_data

        # Call the service method
        result = self.user_service.get_user("user123")

        # Assert repository was called with correct ID
        self.user_repository_mock.get_user.assert_called_once_with("user123")

        # Assert the result is a User instance with correct data
        self.assertIsInstance(result, User)
        self.assertEqual(result.user_id, "user123")
        self.assertEqual(result.email, "test@example.com")
        self.assertEqual(result.name, "Test User")
        self.assertEqual(result.role, "athlete")

    def test_get_user_not_found(self):
        """
        Test retrieving a non-existent user returns None
        """
        # Configure mock to return None (user not found)
        self.user_repository_mock.get_user.return_value = None

        # Call the service method
        result = self.user_service.get_user("nonexistent")

        # Assert repository was called with correct ID
        self.user_repository_mock.get_user.assert_called_once_with("nonexistent")

        # Assert the result is None
        self.assertIsNone(result)

    def test_create_user(self):
        """
        Test creating a new user
        """
        # Call the service method
        result = self.user_service.create_user(
            email="new@example.com", name="New User", role="coach"
        )

        # Assert the UUID function was called
        self.uuid_mock.assert_called()

        # Assert repository create method was called with correct data
        expected_user_dict = {
            "user_id": "test-uuid",
            "email": "new@example.com",
            "name": "New User",
            "role": "coach",
        }

        self.user_repository_mock.create_user.assert_called_once()
        actual_arg = self.user_repository_mock.create_user.call_args[0][0]

        # Check that all keys match the expected values
        for key, value in expected_user_dict.items():
            self.assertEqual(actual_arg[key], value)

        # Assert the returned object is a User with correct data
        self.assertIsInstance(result, User)
        self.assertEqual(result.user_id, "test-uuid")
        self.assertEqual(result.email, "new@example.com")
        self.assertEqual(result.name, "New User")
        self.assertEqual(result.role, "coach")

    def test_create_user_with_both_role(self):
        """
        Test creating a user with 'both' role
        """
        # Call the service method
        result = self.user_service.create_user(
            email="both@example.com", name="Both User", role="both"
        )

        # Assert repository create method was called with correct data
        self.user_repository_mock.create_user.assert_called_once()
        actual_arg = self.user_repository_mock.create_user.call_args[0][0]

        # Check role is correctly set
        self.assertEqual(actual_arg["role"], "both")

        # Assert the returned object has correct role
        self.assertEqual(result.role, "both")

    def test_update_user(self):
        """
        Test updating a user
        """
        # Mock data for the updated user
        updated_user_data = {
            "user_id": "user123",
            "email": "updated@example.com",  # Changed email
            "name": "Updated User",  # Changed name
            "role": "coach",  # Changed role
        }

        # Configure mocks
        self.user_repository_mock.update_user.return_value = {
            "Attributes": {
                "email": "updated@example.com",
                "name": "Updated User",
                "role": "coach",
            }
        }
        self.user_repository_mock.get_user.return_value = updated_user_data

        # Data to update
        update_data = {
            "email": "updated@example.com",
            "name": "Updated User",
            "role": "coach",
        }

        # Call the service method
        result = self.user_service.update_user("user123", update_data)

        # Assert repository methods were called correctly
        self.user_repository_mock.update_user.assert_called_once_with(
            "user123", update_data
        )
        self.user_repository_mock.get_user.assert_called_once_with("user123")

        # Assert the returned object is a User with updated data
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, "updated@example.com")
        self.assertEqual(result.name, "Updated User")
        self.assertEqual(result.role, "coach")
        self.assertEqual(result.user_id, "user123")  # ID should remain the same

    def test_update_user_not_found(self):
        """
        Test updating a user that doesn't exist
        """
        # Configure mock to return None after update (user not found)
        self.user_repository_mock.update_user.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        self.user_repository_mock.get_user.return_value = None

        # Call the service method with update data
        result = self.user_service.update_user("nonexistent", {"name": "Updated Name"})

        # Assert repository methods were called
        self.user_repository_mock.update_user.assert_called_once_with(
            "nonexistent", {"name": "Updated Name"}
        )
        self.user_repository_mock.get_user.assert_called_once_with("nonexistent")

        # Assert the result is None (user not found)
        self.assertIsNone(result)

    def test_create_custom_exercise_success(self):
        """
        Test successful custom exercise creation
        """
        # Arrange
        mock_user_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
            "weight_unit_preference": "auto",
            "custom_exercises": [],
        }

        self.user_repository_mock.update_user.return_value = mock_user_data
        mock_user = User(**mock_user_data)
        self.user_service.get_user = MagicMock(return_value=mock_user)

        # Act
        result = self.user_service.create_custom_exercise(
            "test-user-id", "Bulgarian Split Squat", "bodyweight"
        )

        # Assert
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Custom exercise created successfully")
        self.assertEqual(result["exercise"]["name"], "Bulgarian Split Squat")
        self.assertEqual(result["exercise"]["category"], "BODYWEIGHT")

        # Verify repository was called with correct data
        self.user_repository_mock.update_user.assert_called_once()
        update_call_args = self.user_repository_mock.update_user.call_args[0]
        self.assertEqual(update_call_args[0], "test-user-id")
        self.assertEqual(len(update_call_args[1]["custom_exercises"]), 1)

    def test_create_custom_exercise_invalid_category(self):
        """
        Test custom exercise creation with invalid category
        """
        # Arrange
        mock_user_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
            "weight_unit_preference": "auto",
            "custom_exercises": [],
        }
        mock_user = User(**mock_user_data)
        self.user_service.get_user = MagicMock(return_value=mock_user)

        # Act
        result = self.user_service.create_custom_exercise(
            "test-user-id", "Some Exercise", "INVALID_CATEGORY"
        )

        # Assert
        self.assertIn("error", result)
        self.assertIn("Invalid category", result["error"])

    def test_create_custom_exercise_custom_category_blocked(self):
        """
        Test that CUSTOM category is blocked for user exercises
        """
        # Arrange
        mock_user_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
            "weight_unit_preference": "auto",
            "custom_exercises": [],
        }
        mock_user = User(**mock_user_data)
        self.user_service.get_user = MagicMock(return_value=mock_user)

        # Act
        result = self.user_service.create_custom_exercise(
            "test-user-id", "Some Exercise", "custom"
        )

        # Assert
        self.assertIn("error", result)
        self.assertEqual(
            result["error"], "Cannot use CUSTOM category for user exercises"
        )

    def test_create_custom_exercise_predefined_conflict(self):
        """
        Test that predefined exercise names are blocked
        """
        # Arrange
        mock_user_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
            "weight_unit_preference": "auto",
            "custom_exercises": [],
        }
        mock_user = User(**mock_user_data)
        self.user_service.get_user = MagicMock(return_value=mock_user)

        # Act - try to create custom exercise with predefined name
        result = self.user_service.create_custom_exercise(
            "test-user-id", "Squat", "barbell"  # This is a predefined exercise
        )

        # Assert
        self.assertIn("error", result)
        self.assertIn("already exists in predefined library", result["error"])

    def test_create_custom_exercise_duplicate_custom(self):
        """
        Test that duplicate custom exercise names are blocked
        """
        # Arrange
        mock_user_data = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
            "weight_unit_preference": "auto",
            "custom_exercises": [
                {"name": "Bulgarian Split Squat", "category": "BODYWEIGHT"}
            ],
        }
        mock_user = User(**mock_user_data)
        self.user_service.get_user = MagicMock(return_value=mock_user)

        # Act - try to create duplicate
        result = self.user_service.create_custom_exercise(
            "test-user-id",
            "bulgarian split squat",  # Case-insensitive duplicate
            "dumbbell",
        )

        # Assert
        self.assertIn("error", result)
        self.assertIn("already exists", result["error"])

    def test_create_custom_exercise_user_not_found(self):
        """
        Test custom exercise creation when user not found
        """
        # Arrange
        self.user_service.get_user = MagicMock(return_value=None)

        # Act
        result = self.user_service.create_custom_exercise(
            "nonexistent-user", "Some Exercise", "bodyweight"
        )

        # Assert
        self.assertIn("error", result)
        self.assertEqual(result["error"], "User not found")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
