import unittest
from unittest.mock import patch, MagicMock
import json
import os

os.environ["USERS_TABLE"] = "test-users-table"
os.environ["BLOCKS_TABLE"] = "test-blocks-table"
os.environ["WEEKS_TABLE"] = "test-weeks-table"
os.environ["DAYS_TABLE"] = "test-days-table"
os.environ["EXERCISES_TABLE"] = "test-exercises-table"
os.environ["WORKOUTS_TABLE"] = "test-workouts-table"
os.environ["COMPLETED_EXERCISES_TABLE"] = "test-completed-exercises-table"
os.environ["RELATIONSHIPS_TABLE"] = "test-relationships-table"

with patch("boto3.resource"):
    import handler


class TestHandler(unittest.TestCase):
    """
    Test suite for the main Lambda handler
    """

    @patch("handler.ROUTE_CONFIG", new_callable=dict)
    def test_route_to_create_user(self, mock_route_config):
        """Test that POST /users routes to the create_user function"""
        # Setup
        mock_create_user = MagicMock(return_value={"statusCode": 201})
        mock_route_config["POST /users"] = mock_create_user
        event = {
            "httpMethod": "POST",
            "resource": "/users",
            "path": "/users",
            "body": json.dumps(
                {"email": "test@example.com", "name": "Test User", "role": "athlete"}
            ),
        }
        context = {}

        # Call handler
        result = handler.lambda_handler(event, context)

        # Assert
        mock_create_user.assert_called_once_with(event, context)
        self.assertEqual(result, {"statusCode": 201})

    @patch("handler.ROUTE_CONFIG", new_callable=dict)
    def test_route_to_get_block(self, mock_route_config):
        """
        Test that GET /blocks/{block_id} routes to the get_block function
        """
        # Setup
        mock_get_block = MagicMock(return_value={"statusCode": 200})
        mock_route_config["GET /blocks/{block_id}"] = mock_get_block
        event = {
            "httpMethod": "GET",
            "resource": "/blocks/{block_id}",
            "path": "/blocks/123",
            "pathParameters": {"block_id": "123"},
        }
        context = {}

        # Call handler
        result = handler.lambda_handler(event, context)

        # Assert
        mock_get_block.assert_called_once_with(event, context)
        self.assertEqual(result, {"statusCode": 200})

    @patch("handler.ROUTE_CONFIG", new_callable=dict)
    def test_route_not_found(self, mock_route_config):
        """
        Test that a non-existent route returns 404
        """
        # Setup
        mock_get_block = MagicMock(return_value={"statusCode": 200})
        mock_route_config["GET /blocks/{block_id}"] = mock_get_block

        event = {
            "httpMethod": "GET",
            "resource": "/non-existent",
            "path": "/non-existent",
        }
        context = {}

        # Call handler
        result = handler.lambda_handler(event, context)

        # Assert
        self.assertEqual(result["statusCode"], 404)
        self.assertIn("Not Found", result["body"])

    @patch("handler.find_handler")
    def test_handler_exception(self, mock_find_handler):
        """
        Test that exceptions in handlers are caught and return 500
        """
        # Setup
        mock_handler = MagicMock()
        mock_handler.side_effect = Exception("Test exception")
        mock_find_handler.return_value = mock_handler

        event = {
            "httpMethod": "GET",
            "resource": "/users/123",
            "path": "/users/123",
            "pathParameters": {"user_id": "123"},
        }
        context = {}

        # Call handler
        result = handler.lambda_handler(event, context)

        # Assert
        self.assertEqual(result["statusCode"], 500)
        self.assertIn("Internal server error", result["body"])

    def test_get_route_key(self):
        """Test get_route_key function"""
        # Setup
        method = "GET"
        path = "/users/123"

        # Call function
        result = handler.get_route_key(method, path)

        # Assert
        self.assertEqual(result, "GET /users/123")

    def test_replace_path_parameters(self):
        """Test replace_path_parameters function"""
        # Setup
        path_template = "/users/{user_id}/workouts/{workout_id}"
        path_parameters = {"user_id": "123", "workout_id": "456"}

        # Call function
        result = handler.replace_path_parameters(path_template, path_parameters)

        # Assert
        self.assertEqual(result, "/users/123/workouts/456")

    def test_find_handler_with_complex_matching(self):
        """Test find_handler function with complex path matching"""
        # Setup
        method = "GET"
        path = "/users/123/workouts/456"
        resource_path = "/users/{user_id}/workouts/{workout_id}"
        path_parameters = {"user_id": "123", "workout_id": "456"}

        # Create mock handler function
        mock_handler = MagicMock()

        # Add the route to ROUTE_CONFIG temporarily
        original_config = handler.ROUTE_CONFIG.copy()
        handler.ROUTE_CONFIG[
            "GET /users/{user_id}/workouts/{workout_id}"
        ] = mock_handler

        try:
            # Call function
            result = handler.find_handler(method, path, resource_path, path_parameters)

            # Assert
            self.assertEqual(result, mock_handler)

            # Test method mismatch
            result = handler.find_handler("POST", path, resource_path, path_parameters)
            self.assertIsNone(result)

            # Test path length mismatch by adding a non-matching route
            handler.ROUTE_CONFIG.clear()
            handler.ROUTE_CONFIG[
                "GET /users/{user_id}/workouts/{workout_id}"
            ] = mock_handler
            different_path = "/users/123"  # Different number of segments
            different_resource = "/users/{user_id}"

            result = handler.find_handler(
                method, different_path, different_resource, {"user_id": "123"}
            )
            self.assertIsNone(result)

            # Test path parts mismatch
            handler.ROUTE_CONFIG.clear()
            handler.ROUTE_CONFIG[
                "GET /users/{user_id}/workouts/{workout_id}"
            ] = mock_handler
            mismatched_path = (
                "/users/123/orders/456"  # Different path segment (orders vs workouts)
            )
            mismatched_resource = "/users/{user_id}/orders/{order_id}"

            result = handler.find_handler(
                method,
                mismatched_path,
                mismatched_resource,
                {"user_id": "123", "order_id": "456"},
            )
            self.assertIsNone(result)
        finally:
            # Restore original ROUTE_CONFIG
            handler.ROUTE_CONFIG = original_config

    def test_lambda_handler_with_null_path_parameters(self):
        """Test lambda_handler when pathParameters is None"""
        # Setup
        mock_handler = MagicMock(return_value={"statusCode": 200})

        event = {
            "httpMethod": "GET",
            "resource": "/users",
            "path": "/users",
            "pathParameters": None,  # Explicitly None to test the fallback
        }
        context = {}

        # Add the route to ROUTE_CONFIG temporarily
        original_config = handler.ROUTE_CONFIG.copy()

        # Clear first to avoid interference
        handler.ROUTE_CONFIG.clear()
        handler.ROUTE_CONFIG["GET /users"] = mock_handler

        try:
            # Call handler
            result = handler.lambda_handler(event, context)

            # Assert
            mock_handler.assert_called_once_with(event, context)
            self.assertEqual(result, {"statusCode": 200})
        finally:
            # Restore original ROUTE_CONFIG
            handler.ROUTE_CONFIG = original_config

    def test_find_handler_complex_path_match(self):
        """Test the path matching in find_handler more thoroughly"""
        method = "GET"
        path = "/workouts/123/exercises"
        resource_path = "/workouts/{workout_id}/exercises"
        path_parameters = {"workout_id": "123"}

        mock_handler = MagicMock()

        # Save original config
        original_config = handler.ROUTE_CONFIG.copy()
        handler.ROUTE_CONFIG.clear()
        handler.ROUTE_CONFIG["GET /workouts/{workout_id}/exercises"] = mock_handler

        try:
            # Test successful match with path parameters
            result = handler.find_handler(method, path, resource_path, path_parameters)
            self.assertEqual(result, mock_handler)

            # Test with a different template but same path parts structure
            handler.ROUTE_CONFIG.clear()
            handler.ROUTE_CONFIG["GET /blocks/{block_id}/weeks"] = mock_handler
            result = handler.find_handler(
                "GET",
                "/blocks/456/weeks",
                "/blocks/{block_id}/weeks",
                {"block_id": "456"},
            )
            self.assertEqual(result, mock_handler)

            # Test with a regular path (no parameters)
            handler.ROUTE_CONFIG.clear()
            handler.ROUTE_CONFIG["GET /health"] = mock_handler
            result = handler.find_handler("GET", "/health", "/health", {})
            self.assertEqual(result, mock_handler)

            # Test the final match condition in find_handler
            # This specifically tests the if match: return handler branch
            handler.ROUTE_CONFIG.clear()
            handler.ROUTE_CONFIG["GET /users/{user_id}/profile"] = mock_handler
            actual_path = "/users/789/profile"
            result = handler.find_handler(
                "GET", actual_path, "/any/different/resource", {"user_id": "789"}
            )
            self.assertEqual(result, mock_handler)
        finally:
            # Restore original config
            handler.ROUTE_CONFIG = original_config


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
