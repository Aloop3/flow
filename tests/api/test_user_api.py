import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.api import user_api


class TestUserAPI(BaseTest):
    """Test suite for the User API module"""

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_success(self, mock_create_user):
        """
        Test successful user creation
        """

        # Setup
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "user_id": "test-uuid",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
        }
        mock_create_user.return_value = mock_user

        event = {
            "body": json.dumps(
                {"email": "test@example.com", "name": "Test User", "role": "athlete"}
            )
        }
        context = {}

        # Call API
        response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["user_id"], "test-uuid")
        self.assertEqual(response_body["email"], "test@example.com")
        mock_create_user.assert_called_once_with(
            email="test@example.com", name="Test User", role="athlete"
        )

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_missing_fields(self, mock_create_user):
        """
        Test user creation with missing fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "email": "test@example.com",
                    # Missing name
                    "role": "athlete",
                }
            )
        }
        context = {}

        # Call API
        response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_user.assert_not_called()

    def test_create_user_invalid_role(self, mock_create_user):
        """
        Test user creation with invalid role
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "email": "test@example.com",
                    "name": "Test User",
                    "role": "invalid_role",  # Invalid role
                }
            )
        }
        context = {}

        # Call API
        response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid role", response_body["error"])

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_invalid_role(self, mock_create_user):
        """
        Test user creation with invalid role
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "email": "test@example.com",
                    "name": "Test User",
                    "role": "invalid_role",  # Invalid role
                }
            )
        }
        context = {}

        # Call API
        response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid role", response_body["error"])
        mock_create_user.assert_not_called()

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_invalid_json(self, mock_create_user):
        """
        Test user creation with invalid JSON in request body
        """

        # Setup
        event = {"body": "{invalid json"}  # Invalid JSON
        context = {}

        # Call API
        response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])
        mock_create_user.assert_not_called()

    def test_create_user_generic_exception(self):
        """
        Test that the create_user method handles generic exceptions properly
        This specifically targets lines 43-45 in user_api.py
        """
        # Setup - Note that the specific patch target and method are critical for coverage
        with patch.object(
            user_api.user_service, "create_user", side_effect=Exception("Test error")
        ):
            # Create a valid event object that will pass all validation
            event = {
                "body": json.dumps(
                    {
                        "email": "test@example.com",
                        "name": "Test User",
                        "role": "athlete",
                    }
                )
            }
            context = {}

            # Call the API - this should trigger the generic exception handler
            response = user_api.create_user(event, context)

            # Assert the correct error response
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["error"], "Test error")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_user_success(self, mock_get_user):
        """
        Test successful user retrieval
        """

        # Setup
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "user_id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete",
        }
        mock_get_user.return_value = mock_user

        event = {"pathParameters": {"user_id": "user123"}}
        context = {}

        # Call API
        response = user_api.get_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["user_id"], "user123")
        mock_get_user.assert_called_once_with("user123")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_user_not_found(self, mock_get_user):
        """
        Test user retrieval when user not found
        """

        # Setup
        mock_get_user.return_value = None

        event = {"pathParameters": {"user_id": "nonexistent"}}
        context = {}

        # Call API
        response = user_api.get_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("User not found", response_body["error"])

    def test_get_user_missing_path_parameters(self):
        """
        Test user retrieval with missing path parameters
        """

        # Setup
        event = {
            # Missing pathParameters
        }
        context = {}

        # Call API
        response = user_api.get_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing user_id", response_body["error"])

    def test_get_user_missing_user_id(self):
        """
        Test user retrieval with missing user_id in path parameters
        """

        # Setup
        event = {
            "pathParameters": {
                # Missing user_id
            }
        }
        context = {}

        # Call API
        response = user_api.get_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing user_id", response_body["error"])

    @patch("src.services.user_service.UserService.get_user")
    def test_get_user_generic_exception(self, mock_get_user):
        """
        Test user retrieval with a generic exception from the service
        """

        # Setup
        mock_get_user.side_effect = Exception("Test error")

        event = {"pathParameters": {"user_id": "user123"}}
        context = {}

        # Call API
        response = user_api.get_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test error")

    @patch("src.services.user_service.UserService.update_user")
    def test_update_user_success(self, mock_update_user):
        """
        Test successful user update
        """

        # Setup
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "user_id": "user123",
            "email": "updated@example.com",
            "name": "Updated User",
            "role": "coach",
        }
        mock_update_user.return_value = mock_user

        event = {
            "pathParameters": {"user_id": "user123"},
            "body": json.dumps(
                {
                    "email": "updated@example.com",
                    "name": "Updated User",
                    "role": "coach",
                }
            ),
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["email"], "updated@example.com")
        mock_update_user.assert_called_once()

    @patch("src.services.user_service.UserService.update_user")
    def test_update_user_not_found(self, mock_update_user):
        """
        Test user update when user not found
        """

        # Setup
        mock_update_user.return_value = None

        event = {
            "pathParameters": {"user_id": "nonexistent"},
            "body": json.dumps({"name": "Updated User"}),
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("User not found", response_body["error"])

    def test_update_user_missing_path_parameters(self):
        """
        Test user update with missing path parameters
        """

        # Setup
        event = {
            # Missing pathParameters
            "body": json.dumps({"name": "Updated User"})
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing user_id", response_body["error"])

    def test_update_user_missing_user_id(self):
        """
        Test user update with missing user_id in path parameters
        """

        # Setup
        event = {
            "pathParameters": {
                # Missing user_id
            },
            "body": json.dumps({"name": "Updated User"}),
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing user_id", response_body["error"])

    def test_update_user_missing_body(self):
        """
        Test user update with missing request body
        """

        # Setup
        event = {
            "pathParameters": {"user_id": "user123"}
            # Missing body
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing request body", response_body["error"])

    @patch("src.services.user_service.UserService.update_user")
    def test_update_user_invalid_json(self, mock_update_user):
        """
        Test user update with invalid JSON in request body
        """

        # Setup
        event = {
            "pathParameters": {"user_id": "user123"},
            "body": "{invalid json",  # Invalid JSON
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])
        mock_update_user.assert_not_called()

    @patch("src.services.user_service.UserService.update_user")
    def test_update_user_generic_exception(self, mock_update_user):
        """
        Test user update with a generic exception from the service
        """

        # Setup
        mock_update_user.side_effect = Exception("Test error")

        event = {
            "pathParameters": {"user_id": "user123"},
            "body": json.dumps({"name": "Updated User"}),
        }
        context = {}

        # Call API
        response = user_api.update_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test error")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
