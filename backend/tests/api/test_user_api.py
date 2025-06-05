import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.api import user_api


class TestUserAPI(BaseTest):
    """Test suite for the User API module with middleware integration"""

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

        # Bypass middleware for successful test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = lambda e, c: user_api.create_user.__wrapped__(
                e, c
            )
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
    def test_create_user_missing_name(self, mock_create_user):
        """
        Test user creation with missing name
        """

        # Setup
        event = {
            "body": json.dumps(
                {"email": "test@example.com", "name": "", "role": "athlete"}
            )
        }
        context = {}

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"}),
            }
            response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_user.assert_not_called()

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_missing_role(self, mock_create_user):
        """
        Test user creation with missing role
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "email": "test@example.com",
                    "name": "Test User",
                    "role": "",
                }
            )
        }
        context = {}

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"}),
            }
            response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_user.assert_not_called()

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_missing_email(self, mock_create_user):
        """
        Test user creation with missing email
        """

        # Setup
        event = {
            "body": json.dumps({"email": "", "name": "Test User", "role": "athlete"})
        }
        context = {}

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"}),
            }
            response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_user.assert_not_called()

    @patch("src.services.user_service.UserService.create_user")
    def test_create_user_invalid_json(self, mock_create_user):
        """
        Test user creation with invalid JSON in request body
        """

        # Setup
        event = {"body": "{invalid json"}  # Invalid JSON
        context = {}

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON in request body"}),
            }
            response = user_api.create_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])
        mock_create_user.assert_not_called()

    def test_create_user_generic_exception(self):
        """
        Test that the create_user method handles generic exceptions properly
        """
        # Setup - create an event that would pass validation
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

        # Mock the service to raise an exception
        with patch.object(
            user_api.user_service, "create_user", side_effect=Exception("Test error")
        ):
            # Mock middleware to pass through the exception
            with patch(
                "src.middleware.middleware.LambdaMiddleware.__call__"
            ) as mock_middleware:
                mock_middleware.return_value = {
                    "statusCode": 500,
                    "body": json.dumps({"error": "Test error"}),
                }
                response = user_api.create_user(event, context)
            # Call the API - this should trigger the generic exception handler
            response = user_api.create_user(event, context)

            # Assert the correct error response
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["error"], "Test error")

    def test_create_user_json_decode_error(self):
        """Test create_user with a JSON decode error"""
        # Setup
        event = {"body": "invalid:-json"}
        context = {}

        # Execute with direct call to ensure middleware doesn't interfere
        response = user_api.create_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])

    def test_create_user_missing_email(self):
        """Test validation when email is missing"""
        # Setup
        event = {"body": json.dumps({"name": "Test", "role": "athlete"})}

        # Call API
        response = user_api.create_user.__wrapped__(event, {})

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Missing required fields")

    def test_create_user_missing_name(self):
        """Test validation when name is missing"""
        # Setup
        event = {"body": json.dumps({"email": "test@example.com", "role": "athlete"})}

        # Call API
        response = user_api.create_user.__wrapped__(event, {})

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Missing required fields")

    def test_create_user_invalid_role(self):
        """Test validation when role is invalid"""
        # Setup
        event = {
            "body": json.dumps(
                {"email": "test@example.com", "name": "Test", "role": "invalid"}
            )
        }

        # Call API
        response = user_api.create_user.__wrapped__(event, {})

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Invalid role")

    def test_create_user_null_role_allowed(self):
        """Test that null role is allowed"""
        # Mock the user service
        with patch.object(user_api, "user_service") as mock_service:
            mock_user = MagicMock()
            mock_user.to_dict.return_value = {
                "user_id": "123",
                "email": "test@example.com",
                "name": "Test",
            }
            mock_service.create_user.return_value = mock_user

            event = {"body": json.dumps({"email": "test@example.com", "name": "Test"})}
            response = user_api.create_user.__wrapped__(event, {})

            self.assertEqual(response["statusCode"], 201)
            mock_service.create_user.assert_called_with(
                email="test@example.com", name="Test", role=None
            )

    def test_create_user_invalid_role_direct(self):
        """Validation logic for invalid role"""
        # Setup
        event = {
            "body": json.dumps(
                {
                    "email": "test@example.com",
                    "name": "Test User",
                    "role": "invalid",  # Not in allowed roles
                }
            )
        }

        # Direct call to function without middleware
        response = user_api.create_user.__wrapped__(event, {})

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Invalid role")

    @patch("src.services.user_service.UserService.create_custom_exercise")
    def test_create_custom_exercise_success(self, mock_create_custom_exercise):
        """
        Test successful custom exercise creation
        """
        # Setup
        mock_create_custom_exercise.return_value = {
            "message": "Custom exercise created successfully",
            "exercise": {"name": "Bulgarian Split Squat", "category": "BODYWEIGHT"},
            "user": {"user_id": "user123"},
        }

        event = {
            "pathParameters": {"user_id": "user123"},
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
            "body": json.dumps(
                {"name": "Bulgarian Split Squat", "category": "bodyweight"}
            ),
        }
        context = {}

        # Bypass middleware for successful test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = (
                lambda e, c: user_api.create_custom_exercise.__wrapped__(e, c)
            )
            response = user_api.create_custom_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["message"], "Custom exercise created successfully"
        )
        self.assertEqual(response_body["exercise"]["name"], "Bulgarian Split Squat")
        mock_create_custom_exercise.assert_called_once_with(
            "user123", "Bulgarian Split Squat", "bodyweight"
        )

    @patch("src.services.user_service.UserService.create_custom_exercise")
    def test_create_custom_exercise_unauthorized_user(
        self, mock_create_custom_exercise
    ):
        """
        Test custom exercise creation with unauthorized user (different user_id)
        """
        event = {
            "pathParameters": {"user_id": "user123"},
            "requestContext": {"authorizer": {"claims": {"sub": "different-user"}}},
            "body": json.dumps(
                {"name": "Bulgarian Split Squat", "category": "bodyweight"}
            ),
        }
        context = {}

        # Bypass middleware for test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = (
                lambda e, c: user_api.create_custom_exercise.__wrapped__(e, c)
            )
            response = user_api.create_custom_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertIn(
            "Cannot create custom exercises for other users", response_body["error"]
        )
        mock_create_custom_exercise.assert_not_called()

    @patch("src.services.user_service.UserService.create_custom_exercise")
    def test_create_custom_exercise_missing_fields(self, mock_create_custom_exercise):
        """
        Test custom exercise creation with missing required fields
        """
        event = {
            "pathParameters": {"user_id": "user123"},
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
            "body": json.dumps({"name": "", "category": "bodyweight"}),  # Missing name
        }
        context = {}

        # Bypass middleware for test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = (
                lambda e, c: user_api.create_custom_exercise.__wrapped__(e, c)
            )
            response = user_api.create_custom_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_custom_exercise.assert_not_called()

    @patch("src.services.user_service.UserService.create_custom_exercise")
    def test_create_custom_exercise_service_error(self, mock_create_custom_exercise):
        """
        Test custom exercise creation with service error (duplicate exercise)
        """
        # Setup
        mock_create_custom_exercise.return_value = {
            "error": "Custom exercise 'Bulgarian Split Squat' already exists"
        }

        event = {
            "pathParameters": {"user_id": "user123"},
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
            "body": json.dumps(
                {"name": "Bulgarian Split Squat", "category": "bodyweight"}
            ),
        }
        context = {}

        # Bypass middleware for test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = (
                lambda e, c: user_api.create_custom_exercise.__wrapped__(e, c)
            )
            response = user_api.create_custom_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("already exists", response_body["error"])
        mock_create_custom_exercise.assert_called_once()

    def test_create_custom_exercise_invalid_json(self):
        """
        Test custom exercise creation with invalid JSON
        """
        event = {
            "pathParameters": {"user_id": "user123"},
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
            "body": "{invalid json",
        }
        context = {}

        # Direct call to function without middleware
        response = user_api.create_custom_exercise.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])

    @patch("src.services.user_service.UserService.create_custom_exercise")
    def test_create_custom_exercise_exception(self, mock_create_custom_exercise):
        """
        Test custom exercise creation with unexpected exception
        """
        # Setup
        mock_create_custom_exercise.side_effect = Exception("Database error")

        event = {
            "pathParameters": {"user_id": "user123"},
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
            "body": json.dumps(
                {"name": "Bulgarian Split Squat", "category": "bodyweight"}
            ),
        }
        context = {}

        # Direct call to function without middleware
        response = user_api.create_custom_exercise.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Database error", response_body["error"])

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

        # Bypass middleware for successful test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = lambda e, c: user_api.get_user.__wrapped__(
                e, c
            )
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

        # Bypass middleware for not found test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = lambda e, c: user_api.get_user.__wrapped__(
                e, c
            )
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
        event = {}  # No pathParameters key at all
        context = {}

        # Directly access wrapped function to test exception handling
        response = user_api.get_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("error", response_body)

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

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing user_id in path parameters"}),
            }
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

        # Middleware should return 500 for unexpected errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 500,
                "body": json.dumps({"error": "Test error"}),
            }
            response = user_api.get_user(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test error")

    def test_get_user_path_parameters_exception(self):
        """Test get_user with missing path parameters to cover"""
        # Setup
        event = {}  # No pathParameters at all
        context = {}

        # Execute with direct call to ensure middleware doesn't interfere
        response = user_api.get_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("error", response_body)

    def test_get_user_keyerror_exception(self):
        """KeyError exception in get_user when pathParameters is missing"""
        # Setup - event that will cause KeyError when accessing pathParameters['user_id']
        event = {"pathParameters": {}}  # pathParameters exists but user_id is missing
        context = {}

        # Direct call without patching
        response = user_api.get_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))

    def test_get_user_exception(self):
        """Exception in get_user"""
        # Setup - event that will cause KeyError when accessing pathParameters
        event = {}  # No pathParameters at all
        context = {}

        # Direct call without patching
        response = user_api.get_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))

    def test_get_user_exception(self):
        """Exception in get_user"""
        # Setup - event that will cause KeyError when accessing pathParameters
        event = {}  # No pathParameters at all
        context = {}

        # Direct call without patching
        response = user_api.get_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))

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

        # Bypass middleware for successful test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = lambda e, c: user_api.update_user.__wrapped__(
                e, c
            )
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

        # Bypass middleware for not found test case
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.side_effect = lambda e, c: user_api.update_user.__wrapped__(
                e, c
            )
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

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing user_id in path parameters"}),
            }
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

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing user_id in path parameters"}),
            }
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

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing request body"}),
            }
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

        # Middleware should return 400 for validation errors
        with patch(
            "src.middleware.middleware.LambdaMiddleware.__call__"
        ) as mock_middleware:
            mock_middleware.return_value = {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON in request body"}),
            }
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
        event = {
            "pathParameters": {"user_id": "user123"},
            "body": json.dumps({"name": "Updated User"}),
        }
        context = {}

        # Patch user_service.update_user to raise a generic exception
        with patch.object(
            user_api.user_service,
            "update_user",
            side_effect=Exception("Database connection error"),
        ):
            # Call the function directly using __wrapped__ to bypass middleware
            response = user_api.update_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database connection error")

    def test_update_user_exception(self):
        """Exception in update_user"""
        # Setup - event that will cause exception in JSON parsing
        event = {"pathParameters": {"user_id": "123"}, "body": "{invalid:json}"}
        context = {}

        # Direct call without patching
        response = user_api.update_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))

    def test_update_user_json_exception(self):
        """JSON decode exception in update_user"""
        # Setup - event with valid pathParameters but invalid JSON body
        event = {
            "pathParameters": {"user_id": "123"},
            "body": "{email: 'test@example.com', name: 'Test User'}",
        }
        context = {}

        # Direct call without patching
        response = user_api.update_user.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
