import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.user_lambda import user_lambda


class TestUserLambda(BaseTest):
    """Test suite for the User Lambda handler"""

    def test_create_user_route(self):
        """Test successful routing to create_user function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = user_lambda.ROUTE_MAP["POST /users"]

        # Replace with our mock
        mock_response = {"statusCode": 201, "body": json.dumps({"user_id": "test123"})}
        user_lambda.ROUTE_MAP["POST /users"] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/users",
                "body": json.dumps(
                    {
                        "email": "test@example.com",
                        "name": "Test User",
                        "role": "athlete",
                    }
                ),
            }
            context = {}

            # Call the Lambda handler
            response = user_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["user_id"], "test123")
            user_lambda.ROUTE_MAP["POST /users"].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            user_lambda.ROUTE_MAP["POST /users"] = original_func

    def test_get_user_route(self):
        """Test successful routing to get_user function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = user_lambda.ROUTE_MAP["GET /users/{user_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps({"user_id": "user123", "email": "test@example.com"}),
        }
        user_lambda.ROUTE_MAP["GET /users/{user_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/users/{user_id}",
                "pathParameters": {"user_id": "user123"},
            }
            context = {}

            # Call the Lambda handler
            response = user_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["user_id"], "user123")
            user_lambda.ROUTE_MAP["GET /users/{user_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            user_lambda.ROUTE_MAP["GET /users/{user_id}"] = original_func

    def test_update_user_route(self):
        """Test successful routing to update_user function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = user_lambda.ROUTE_MAP["PUT /users/{user_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps({"user_id": "user123", "email": "updated@example.com"}),
        }
        user_lambda.ROUTE_MAP["PUT /users/{user_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/users/{user_id}",
                "pathParameters": {"user_id": "user123"},
                "body": json.dumps({"email": "updated@example.com"}),
            }
            context = {}

            # Call the Lambda handler
            response = user_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["email"], "updated@example.com")
            user_lambda.ROUTE_MAP["PUT /users/{user_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            user_lambda.ROUTE_MAP["PUT /users/{user_id}"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "DELETE",  # Not defined in the ROUTE_MAP
            "resource": "/users/{user_id}",
        }
        context = {}

        # Call the Lambda handler
        response = user_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = user_lambda.ROUTE_MAP["GET /users/{user_id}"]

        # Replace with our mock that raises an exception
        user_lambda.ROUTE_MAP["GET /users/{user_id}"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/users/{user_id}",
                "pathParameters": {"user_id": "user123"},
            }
            context = {}

            # Call the Lambda handler
            response = user_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            user_lambda.ROUTE_MAP["GET /users/{user_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            user_lambda.ROUTE_MAP["GET /users/{user_id}"] = original_func

    def test_missing_route_information(self):
        """Test handling of missing route information"""
        # Setup - missing httpMethod and resource
        event = {}
        context = {}

        # Call the Lambda handler
        response = user_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])


if __name__ == "__main__":
    unittest.main()
