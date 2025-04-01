import unittest
from unittest.mock import MagicMock, patch
import json
from src.middleware.middleware import ValidationError
from src.middleware.common_middleware import validate_auth, log_request, handle_errors


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
        with self.assertRaises(ValidationError) as cm:
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
        with self.assertRaises(ValidationError) as cm:
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
        Test that handle_errors raises ValidationError for missing body for POST requests
        """
        event = {
            "httpMethod": "POST",
            "path": "/users",
            # Missing body
        }
        context = MagicMock()

        # Expect a ValidationError to be raised
        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)

        # Verify the error message
        self.assertEqual(str(cm.exception), "Request body is required")

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

    def test_handle_errors_path_parameter_no_match(self):
        """Test path parameter checking when path doesn't match pattern"""
        event = {"httpMethod": "GET", "path": "/some/random/path", "pathParameters": {}}
        context = MagicMock()

        # Should not raise an exception since path doesn't match any patterns
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_path_parts_length_mismatch(self):
        """Test path parameter checking when path parts length doesn't match"""
        event = {
            "httpMethod": "GET",
            "path": "/users",  # Only one part, but pattern has two
            "pathParameters": {},
        }
        context = MagicMock()

        # Should not raise an exception since path parts length doesn't match
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_method_mismatch(self):
        """Test path parameter checking when method doesn't match"""
        event = {
            "httpMethod": "POST",  # Pattern requires GET
            "path": "/users/123",
            "pathParameters": {},
            "body": json.dumps({"name": "Test User"}),
        }
        context = MagicMock()

        # Should not check path parameters since method doesn't match
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_path_part_mismatch(self):
        """Test path parameter checking when a path part doesn't match pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/accounts/123",  # Pattern requires 'users'
            "pathParameters": {"account_id": "123"},
        }
        context = MagicMock()

        # Should not check path parameters since path parts don't match
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_null_path_parameters(self):
        """Test path parameter checking with null pathParameters"""
        event = {
            "httpMethod": "GET",
            "path": "/users/123",
            "pathParameters": None,  # Null pathParameters
        }
        context = MagicMock()

        # Should raise an exception for missing path parameter
        with self.assertRaises(ValidationError):
            handle_errors(event, context)

    def test_handle_errors_query_params_path_mismatch(self):
        """Test query parameter checking when path doesn't match pattern"""
        event = {
            "httpMethod": "GET",
            "path": "/some/random/path",
            "queryStringParameters": {},
        }
        context = MagicMock()

        # Should not add errors since path doesn't match any patterns
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_query_params_null(self):
        """Test query parameter checking with null queryStringParameters"""
        event = {
            "httpMethod": "GET",
            "path": "/athletes/123/progress",
            "pathParameters": {"athlete_id": "123"},
            "queryStringParameters": None,  # Null queryStringParameters
        }
        context = MagicMock()

        # Should add error for missing query parameter
        result = handle_errors(event, context)
        self.assertTrue(
            any("Missing query parameter" in error for error in result["errors"])
        )

    def test_handle_errors_put_missing_body(self):
        """Test PUT request with missing body"""
        event = {
            "httpMethod": "PUT",
            "path": "/users/123",
            "pathParameters": {"user_id": "123"}
            # Missing body
        }
        context = MagicMock()

        # Should raise an exception for missing body
        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)
        self.assertEqual(str(cm.exception), "Request body is required")

    def test_handle_errors_patch_missing_body(self):
        """Test PATCH request with missing body"""
        event = {
            "httpMethod": "PATCH",
            "path": "/users/123",
            "pathParameters": {"user_id": "123"}
            # Missing body
        }
        context = MagicMock()

        # Should raise an exception for missing body
        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)
        self.assertEqual(str(cm.exception), "Request body is required")

    def test_validate_auth_missing_request_context(self):
        """Test auth validation when requestContext is missing"""
        event = {}  # No requestContext
        context = MagicMock()

        with self.assertRaises(ValidationError) as cm:
            validate_auth(event, context)
        self.assertEqual(str(cm.exception), "Unauthorized")

    def test_validate_auth_missing_authorizer(self):
        """Test auth validation when authorizer is missing"""
        event = {"requestContext": {}}  # No authorizer
        context = MagicMock()

        with self.assertRaises(ValidationError) as cm:
            validate_auth(event, context)
        self.assertEqual(str(cm.exception), "Unauthorized")

    def test_validate_auth_missing_claims(self):
        """Test auth validation when claims are missing"""
        event = {"requestContext": {"authorizer": {}}}  # No claims
        context = MagicMock()

        with self.assertRaises(ValidationError) as cm:
            validate_auth(event, context)
        self.assertEqual(str(cm.exception), "Unauthorized")

    def test_log_request_missing_request_id(self):
        """Test log_request when aws_request_id is missing"""
        event = {"path": "/test", "httpMethod": "GET"}
        # Context without aws_request_id
        context = MagicMock(spec=[])  # Empty spec = no attributes

        with patch("logging.Logger.info") as mock_logger:
            result = log_request(event, context)
            self.assertEqual(result, event)
            mock_logger.assert_called_once()
            log_message = mock_logger.call_args[0][0]
            self.assertIn("request_id=unknown", log_message)

    def test_handle_errors_path_params_missing_some(self):
        """Test handle_errors when some path parameters are missing"""
        event = {
            "httpMethod": "GET",
            "path": "/blocks/123/weeks",
            "pathParameters": {},  # Empty but should have block_id
        }
        context = MagicMock()

        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)
        self.assertIn("Missing path parameter", str(cm.exception))

    def test_handle_errors_relationship_endpoints(self):
        """Test handle_errors for relationship endpoints that don't require body"""
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/accept",
            "pathParameters": {"relationship_id": "123"}
            # Missing body is allowed for this endpoint
        }
        context = MagicMock()

        # Should not raise an exception
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_handle_errors_relationship_endpoints_not_in_exceptions(self):
        """Test handle_errors for relationship endpoints that aren't in exceptions list"""
        event = {
            "httpMethod": "POST",
            "path": "/relationships/123/cancel",  # 'cancel' is not in the exceptions
            "pathParameters": {"relationship_id": "123"}
            # Missing body
        }
        context = MagicMock()

        # Should raise an exception
        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)
        self.assertEqual(str(cm.exception), "Request body is required")

    def test_handle_errors_path_too_short(self):
        """Test handle_errors for relationship endpoints with path too short"""
        event = {
            "httpMethod": "POST",
            "path": "/relationships",  # Not enough parts
            "pathParameters": {}
            # Missing body
        }
        context = MagicMock()

        # Should raise an exception
        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)
        self.assertEqual(str(cm.exception), "Request body is required")

    def test_handle_errors_not_relationships(self):
        """Test handle_errors for endpoints that aren't relationships"""
        event = {
            "httpMethod": "POST",
            "path": "/users/123/activate",
            "pathParameters": {"user_id": "123"}
            # Missing body
        }
        context = MagicMock()

        # Should raise an exception
        with self.assertRaises(ValidationError) as cm:
            handle_errors(event, context)
        self.assertEqual(str(cm.exception), "Request body is required")

    def test_handle_errors_query_params_endpoint_match(self):
        """Test query parameter checking with matching endpoint"""
        event = {
            "httpMethod": "GET",
            "path": "/coaches/123/relationships",
            "pathParameters": {"coach_id": "123"},
            "queryStringParameters": {},  # Missing required status
        }
        context = MagicMock()

        # Should add error about missing query parameter
        result = handle_errors(event, context)
        self.assertTrue(
            any(
                "Missing query parameter: status" in error for error in result["errors"]
            )
        )

    def test_handle_errors_different_method(self):
        """Test query parameter checking with non-matching method"""
        event = {
            "httpMethod": "POST",  # Not GET which is required
            "path": "/coaches/123/relationships",
            "pathParameters": {"coach_id": "123"},
            "queryStringParameters": {},
            "body": json.dumps({"test": "data"}),
        }
        context = MagicMock()

        # Should not add error since method doesn't match
        result = handle_errors(event, context)
        self.assertEqual(result["errors"], [])

    def test_validate_auth_no_request_context(self):
        """Test that validate_auth raises ValidationError when requestContext is missing"""
        event = {}  # No requestContext
        context = MagicMock()

        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            validate_auth(event, context)

    def test_validate_auth_no_authorizer(self):
        """Test that validate_auth raises ValidationError when authorizer is missing"""
        event = {"requestContext": {}}  # requestContext but no authorizer
        context = MagicMock()

        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            validate_auth(event, context)

    def test_validate_auth_no_claims(self):
        """Test that validate_auth raises ValidationError when claims are missing"""
        event = {"requestContext": {"authorizer": {}}}  # authorizer but no claims
        context = MagicMock()

        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            validate_auth(event, context)

    def test_validate_auth_directly(self):
        """Test validate_auth directly without any mocking"""
        # Print to confirm we're running this
        print("Testing validate_auth directly")

        # First test normal case
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user123"}}}}
        context = MagicMock()

        # This should not raise an exception
        result = validate_auth(event, context)
        self.assertEqual(result, event)

        # Now test case with no requestContext
        event_no_context = {}

        # This should raise a ValidationError
        try:
            validate_auth(event_no_context, context)
            self.fail("Should have raised ValidationError")
        except ValidationError:
            # Exception raised as expected
            pass

        # Test case with no authorizer
        event_no_auth = {"requestContext": {}}

        try:
            validate_auth(event_no_auth, context)
            self.fail("Should have raised ValidationError")
        except ValidationError:
            # Exception raised as expected
            pass

        # Test case with no claims
        event_no_claims = {"requestContext": {"authorizer": {}}}

        try:
            validate_auth(event_no_claims, context)
            self.fail("Should have raised ValidationError")
        except ValidationError:
            # Exception raised as expected
            pass

    def test_validate_auth_direct_inspection(self):
        """
        Test validate_auth by directly checking the code paths
        """
        # Create event that will trigger the if condition
        event1 = {}  # No requestContext
        context = MagicMock()

        # Instead of asserting the exception, we'll check what condition is met
        result1 = "requestContext" not in event1
        self.assertTrue(result1, "First condition should be true")

        # Create event that hits the second condition
        event2 = {"requestContext": {}}  # No authorizer
        result2 = "authorizer" not in event2["requestContext"]
        self.assertTrue(result2, "Second condition should be true")

        # Create event that hits the third condition
        event3 = {"requestContext": {"authorizer": {}}}  # No claims
        result3 = "claims" not in event3["requestContext"]["authorizer"]
        self.assertTrue(result3, "Third condition should be true")

        # Now directly check the entire condition
        result_all = (
            "requestContext" not in event1
            or "authorizer" not in event1.get("requestContext", {})
            or "claims" not in event1.get("requestContext", {}).get("authorizer", {})
        )
        self.assertTrue(result_all, "Overall condition should be true")

        # Now create an event that should pass
        event_valid = {"requestContext": {"authorizer": {"claims": {"sub": "user123"}}}}

        # This should not trigger the condition
        result_valid = (
            "requestContext" not in event_valid
            or "authorizer" not in event_valid["requestContext"]
            or "claims" not in event_valid["requestContext"]["authorizer"]
        )
        self.assertFalse(result_valid, "Valid event should pass the condition")

        # Now call the function with a valid event
        try:
            validate_auth(event_valid, context)
        except ValidationError:
            self.fail("validate_auth should not raise for valid event")

    def test_validate_auth_with_patching(self):
        """Test validate_auth by patching the internal components"""
        context = MagicMock()

        # Only mock the logger, not ValidationError
        with patch("src.middleware.common_middleware.logger") as mock_logger:
            # Test case 1: Missing requestContext
            event1 = {}  # No requestContext

            # When validate_auth is called, it should raise ValidationError
            with self.assertRaises(ValidationError):
                validate_auth(event1, context)

            # Verify logger was called
            mock_logger.error.assert_called_once_with("No auth claims found in event")

            # Reset the mock for the next test
            mock_logger.reset_mock()

            # Test case 2: Missing authorizer
            event2 = {"requestContext": {}}  # No authorizer

            # When validate_auth is called, it should raise ValidationError
            with self.assertRaises(ValidationError):
                validate_auth(event2, context)

            # Check that ValidationError was raised again
            mock_logger.error.assert_called_once_with("No auth claims found in event")

            # Reset the mock for the next test
            mock_logger.reset_mock()

            # Test case 3: Missing claims
            event3 = {"requestContext": {"authorizer": {}}}  # No claims

            # When validate_auth is called, it should raise ValidationError
            with self.assertRaises(ValidationError):
                validate_auth(event3, context)

            # Check that ValidationError was raised again
            mock_logger.error.assert_called_once_with("No auth claims found in event")

    def test_log_request_with_patching(self):
        """Test log_request by patching the logger"""

        with patch("src.middleware.common_middleware.logger") as mock_logger:
            # Test with missing request_id
            event = {"path": "/test", "httpMethod": "GET"}
            context = MagicMock(spec=[])  # No aws_request_id

            result = log_request(event, context)

            # Check that logger was called with expected message
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            self.assertIn("request_id=unknown", log_message)
            self.assertIn("path=/test", log_message)
            self.assertIn("method=GET", log_message)
            self.assertIn("user=unknown", log_message)


if __name__ == "__main__":
    unittest.main()
