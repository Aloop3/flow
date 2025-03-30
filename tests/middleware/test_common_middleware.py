import unittest
from unittest.mock import MagicMock, patch
import json


# Import middleware after patching
with patch("boto3.resource"):
    from src.middleware.common_middleware import (
        validate_auth,
        log_request,
        handle_errors,
    )


class TestCommonMiddleware(unittest.TestCase):
    """
    Test suite for common middleware functions
    """

    def test_handle_errors_with_invalid_json(self):
        """
        Test that handle_errors detects invalid JSON in the body
        """
        event = {"body": "{invalid json"}
        context = MagicMock()

        # handle_errors should raise an exception for invalid JSON
        with self.assertRaises(Exception) as cm:
            handle_errors(event, context)

        # Check that the exception message mentions invalid JSON
        self.assertIn("Invalid JSON", str(cm.exception))

    def test_handle_errors_with_valid_json(self):
        """
        Test that handle_errors accepts valid JSON
        """
        event = {"body": json.dumps({"key": "value"})}
        context = MagicMock()

        # handle_errors should not raise an exception for valid JSON
        result = handle_errors(event, context)

        # Check that the event is returned with errors array
        self.assertEqual(result, event)
        self.assertIn("errors", result)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_with_missing_path_parameters(self):
        """
        Test that handle_errors detects missing path parameters
        """
        # Test for GET /users/{user_id} without user_id
        event = {
            "httpMethod": "GET",
            "path": "/users/123",
            "pathParameters": {},  # Empty path parameters
        }
        context = MagicMock()

        # handle_errors should raise an exception for missing path parameter
        with self.assertRaises(Exception) as cm:
            handle_errors(event, context)

        # Check that the exception message mentions the missing parameter
        self.assertIn("Missing path parameter", str(cm.exception))

    def test_handle_errors_with_valid_path_parameters(self):
        """
        Test that handle_errors accepts valid path parameters
        """
        event = {
            "httpMethod": "GET",
            "path": "/users/123",
            "pathParameters": {"user_id": "123"},
        }
        context = MagicMock()

        # handle_errors should not raise an exception for valid path parameters
        result = handle_errors(event, context)

        # Check that the event is returned with errors array
        self.assertEqual(result, event)
        self.assertIn("errors", result)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_with_missing_query_parameters(self):
        """
        Test that handle_errors detects missing query parameters
        """
        # Test for GET /athletes/{athlete_id}/progress without time_period
        event = {
            "httpMethod": "GET",
            "path": "/athletes/123/progress",
            "pathParameters": {"athlete_id": "123"},
            "queryStringParameters": {},  # Empty query parameters
        }
        context = MagicMock()

        # handle_errors should add error to the errors array
        result = handle_errors(event, context)

        # Check that the error was added to the errors array
        self.assertIn("errors", result)
        self.assertGreater(len(result["errors"]), 0)
        self.assertTrue(
            any("Missing query parameter" in error for error in result["errors"])
        )

    def test_handle_errors_with_valid_query_parameters(self):
        """
        Test that handle_errors accepts valid query parameters
        """
        event = {
            "httpMethod": "GET",
            "path": "/athletes/123/progress",
            "pathParameters": {"athlete_id": "123"},
            "queryStringParameters": {"time_period": "week"},
        }
        context = MagicMock()

        # handle_errors should not add errors for valid query parameters
        result = handle_errors(event, context)

        # Check that the errors array is empty
        self.assertIn("errors", result)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_with_missing_body_for_post(self):
        """
        Test that handle_errors detects missing body for POST requests
        """
        event = {
            "httpMethod": "POST",
            "path": "/users",
            # Missing body
        }
        context = MagicMock()

        # handle_errors should add error to the errors array
        result = handle_errors(event, context)

        # Check that the error was added to the errors array
        self.assertIn("errors", result)
        self.assertGreater(len(result["errors"]), 0)
        self.assertTrue(
            any("Request body is required" in error for error in result["errors"])
        )

    def test_handle_errors_with_valid_body_for_post(self):
        """
        Test that handle_errors accepts valid body for POST requests
        """
        event = {
            "httpMethod": "POST",
            "path": "/users",
            "body": json.dumps({"key": "value"}),
        }
        context = MagicMock()

        # handle_errors should not add errors for valid body
        result = handle_errors(event, context)

        # Check that the errors array is empty
        self.assertIn("errors", result)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_with_body_exception_endpoints(self):
        """
        Test that handle_errors allows missing body for exception endpoints
        """
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/accept",
            "pathParameters": {"relationship_id": "123"}
            # Missing body is allowed for this endpoint
        }
        context = MagicMock()

        # handle_errors should not add errors for this endpoint
        result = handle_errors(event, context)

        # Check that the errors array is empty
        self.assertIn("errors", result)
        self.assertEqual(result["errors"], [])

    def test_validate_auth_with_valid_claims(self):
        """
        Test validate_auth with valid authentication claims
        """
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user123"}}}}
        context = MagicMock()

        # validate_auth should not raise an exception
        result = validate_auth(event, context)

        # Check that the event is returned unchanged
        self.assertEqual(result, event)

    def test_validate_auth_with_missing_claims(self):
        """
        Test validate_auth with missing authentication claims
        """
        # Test with missing requestContext
        event1 = {}
        context = MagicMock()

        with self.assertRaises(Exception) as cm:
            validate_auth(event1, context)

        self.assertIn("Unauthorized", str(cm.exception))

        # Test with missing authorizer
        event2 = {"requestContext": {}}

        with self.assertRaises(Exception) as cm:
            validate_auth(event2, context)

        self.assertIn("Unauthorized", str(cm.exception))

        # Test with missing claims
        event3 = {"requestContext": {"authorizer": {}}}

        with self.assertRaises(Exception) as cm:
            validate_auth(event3, context)

        self.assertIn("Unauthorized", str(cm.exception))

    @patch("logging.Logger.info")
    def test_log_request(self, mock_logger_info):
        """
        Test log_request middleware
        """
        event = {
            "path": "/users",
            "httpMethod": "GET",
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
        }
        context = MagicMock()
        context.aws_request_id = "req123"

        # Call middleware
        result = log_request(event, context)

        # Check that logging was called
        mock_logger_info.assert_called_once()

        # Check that the first argument to info() contains the expected data
        log_arg = mock_logger_info.call_args[0][0]
        self.assertIn("req123", log_arg)  # Contains request ID
        self.assertIn("/users", log_arg)  # Contains path
        self.assertIn("GET", log_arg)  # Contains method

        # Check that the event was returned unchanged
        self.assertEqual(result, event)

    def test_log_request_with_missing_data(self):
        """
        Test log_request with missing event data
        """
        # Test with minimal event
        event = {}
        context = MagicMock()

        # log_request should not raise exceptions for missing data
        result = log_request(event, context)

        # Check that the event was returned unchanged
        self.assertEqual(result, event)


if __name__ == "__main__":
    unittest.main()
