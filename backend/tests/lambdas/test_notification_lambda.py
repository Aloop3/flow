import unittest
from unittest.mock import MagicMock, patch
import json
from src.lambdas.notification_lambda.notification_lambda import handler, ROUTE_MAP


class TestNotificationLambda(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with consistent test data"""
        self.context = MagicMock()
        self.context.aws_request_id = "test-request-123"

    def test_route_map_contains_expected_routes(self):
        """Test that ROUTE_MAP contains all expected notification routes"""
        # Verify expected routes exist in ROUTE_MAP
        expected_routes = [
            "GET /notifications",
            "PATCH /notifications/{notification_id}/read",
        ]

        for route in expected_routes:
            with self.subTest(route=route):
                self.assertIn(route, ROUTE_MAP)
                self.assertIsNotNone(ROUTE_MAP[route])

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    @patch("src.api.notification_api.get_notifications")
    def test_get_notifications_route_success(
        self, mock_get_notifications, mock_add_cors
    ):
        """Test successful routing to get_notifications handler"""
        # Arrange
        mock_api_response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps([]),
        }
        mock_get_notifications.return_value = mock_api_response
        mock_add_cors.return_value = mock_api_response

        event = {
            "httpMethod": "GET",
            "resource": "/notifications",
            "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
            "queryStringParameters": None,
        }

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_get_notifications.assert_called_once_with(event, self.context)
        mock_add_cors.assert_called_once_with(mock_api_response)

    def test_get_notifications_route_success(self):
        """Test successful routing to get_notifications handler"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = ROUTE_MAP["GET /notifications"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps([]),
        }
        ROUTE_MAP["GET /notifications"] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/notifications",
                "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
                "queryStringParameters": None,
            }

            # Call the Lambda handler
            response = handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            ROUTE_MAP["GET /notifications"].assert_called_once_with(event, self.context)

        finally:
            # Restore the original function
            ROUTE_MAP["GET /notifications"] = original_func

    def test_mark_notification_as_read_route_success(self):
        """Test successful routing to mark_notification_as_read handler"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = ROUTE_MAP["PATCH /notifications/{notification_id}/read"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Notification marked as read"}),
        }
        ROUTE_MAP["PATCH /notifications/{notification_id}/read"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PATCH",
                "resource": "/notifications/{notification_id}/read",
                "pathParameters": {"notification_id": "notification-123"},
                "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
            }

            # Call the Lambda handler
            response = handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            ROUTE_MAP[
                "PATCH /notifications/{notification_id}/read"
            ].assert_called_once_with(event, self.context)

        finally:
            # Restore the original function
            ROUTE_MAP["PATCH /notifications/{notification_id}/read"] = original_func

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_options_request_returns_200(self, mock_add_cors):
        """Test that OPTIONS requests return 200 for CORS preflight"""
        # Arrange
        expected_response = {"statusCode": 200, "body": json.dumps({"message": "OK"})}
        mock_add_cors.return_value = expected_response

        event = {
            "httpMethod": "OPTIONS",
            "resource": "/notifications",
            "requestContext": {},
        }

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_add_cors.assert_called_once()

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_unsupported_route_returns_404(self, mock_add_cors):
        """Test that unsupported routes return 404 with proper CORS headers"""
        # Arrange
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {
            "httpMethod": "POST",
            "resource": "/notifications/unsupported",
            "requestContext": {},
        }

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        mock_add_cors.assert_called_once()

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_unsupported_http_method_returns_404(self, mock_add_cors):
        """Test that unsupported HTTP methods return 404"""
        # Arrange
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {
            "httpMethod": "DELETE",
            "resource": "/notifications",
            "requestContext": {},
        }

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        mock_add_cors.assert_called_once()

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_missing_http_method_creates_none_route_key(self, mock_add_cors):
        """Test handling of events missing httpMethod"""
        # Arrange
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {"resource": "/notifications", "requestContext": {}}

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        mock_add_cors.assert_called_once()

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_missing_resource_creates_none_route_key(self, mock_add_cors):
        """Test handling of events missing resource path"""
        # Arrange
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {"httpMethod": "GET", "requestContext": {}}

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        mock_add_cors.assert_called_once()

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    @patch("src.lambdas.notification_lambda.notification_lambda.notification_api")
    def test_handler_exception_returns_500(self, mock_notification_api, mock_add_cors):
        """Test that unexpected exceptions return 500 with proper CORS headers"""
        # Arrange
        mock_notification_api.get_notifications.side_effect = Exception(
            "Unexpected error"
        )
        expected_response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error: Unexpected error"}),
        }
        mock_add_cors.return_value = expected_response

        event = {
            "httpMethod": "GET",
            "resource": "/notifications",
            "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
        }

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        mock_add_cors.assert_called_once()

    @patch("src.lambdas.notification_lambda.notification_lambda.logger")
    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    @patch("src.lambdas.notification_lambda.notification_lambda.notification_api")
    def test_handler_logs_requests(
        self, mock_notification_api, mock_add_cors, mock_logger
    ):
        """Test that handler logs incoming requests"""
        # Arrange
        mock_api_response = {"statusCode": 200, "headers": {}, "body": "[]"}
        mock_notification_api.get_notifications.return_value = mock_api_response
        mock_add_cors.return_value = mock_api_response

        event = {
            "httpMethod": "GET",
            "resource": "/notifications",
            "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
        }

        # Act
        handler(event, self.context)

        # Assert
        mock_logger.info.assert_called_with("Processing GET /notifications request")

    @patch("src.lambdas.notification_lambda.notification_lambda.logger")
    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_handler_logs_route_not_found(self, mock_add_cors, mock_logger):
        """Test that handler logs when route is not found"""
        # Arrange
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {
            "httpMethod": "POST",
            "resource": "/invalid-route",
            "requestContext": {},
        }

        # Act
        handler(event, self.context)

        # Assert
        mock_logger.warning.assert_called_with(
            "No handler found for POST /invalid-route"
        )

    @patch("src.lambdas.notification_lambda.notification_lambda.logger")
    def test_handler_logs_unexpected_errors(self, mock_logger):
        """Test that handler logs unexpected exceptions"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly to raise an exception
        original_func = ROUTE_MAP["GET /notifications"]
        error_message = "Database connection failed"
        ROUTE_MAP["GET /notifications"] = MagicMock(
            side_effect=Exception(error_message)
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/notifications",
                "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
            }

            # Act
            response = handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            mock_logger.error.assert_called_with(
                f"Error processing request: {error_message}"
            )

        finally:
            # Restore the original function
            ROUTE_MAP["GET /notifications"] = original_func

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_route_case_sensitivity(self, mock_add_cors):
        """Test that route matching is case sensitive for HTTP methods"""
        # Arrange - lowercase http method should not match
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {
            "httpMethod": "get",  # lowercase
            "resource": "/notifications",
            "requestContext": {},
        }

        # Act
        response = handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 404)

    def test_get_notifications_with_query_parameters(self):
        """Test GET /notifications route with query parameters"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = ROUTE_MAP["GET /notifications"]

        # Replace with our mock
        mock_response = {"statusCode": 200, "headers": {}, "body": "[]"}
        ROUTE_MAP["GET /notifications"] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/notifications",
                "queryStringParameters": {"limit": "10", "unread_only": "true"},
                "requestContext": {"authorizer": {"claims": {"sub": "coach-123"}}},
            }

            # Call the Lambda handler
            response = handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            ROUTE_MAP["GET /notifications"].assert_called_once_with(event, self.context)

        finally:
            # Restore the original function
            ROUTE_MAP["GET /notifications"] = original_func

    def test_mark_as_read_with_path_parameters(self):
        """Test PATCH route with path parameters"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = ROUTE_MAP["PATCH /notifications/{notification_id}/read"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "headers": {},
            "body": '{"message": "Success"}',
        }
        ROUTE_MAP["PATCH /notifications/{notification_id}/read"] = MagicMock(
            return_value=mock_response
        )

        try:
            notification_id = "notification-abc-123"
            event = {
                "httpMethod": "PATCH",
                "resource": "/notifications/{notification_id}/read",
                "pathParameters": {"notification_id": notification_id},
                "requestContext": {"authorizer": {"claims": {"sub": "coach-456"}}},
            }

            # Call the Lambda handler
            response = handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            ROUTE_MAP[
                "PATCH /notifications/{notification_id}/read"
            ].assert_called_once_with(event, self.context)

        finally:
            # Restore the original function
            ROUTE_MAP["PATCH /notifications/{notification_id}/read"] = original_func

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_response_structure_consistency(self, mock_add_cors):
        """Test that all responses have consistent structure"""
        # Test 404 response structure
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        event = {"httpMethod": "POST", "resource": "/invalid", "requestContext": {}}

        response = handler(event, self.context)

        # Verify required response structure
        self.assertIn("statusCode", response)
        self.assertIn("body", response)

        # Verify body is valid JSON
        json.loads(response["body"])

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_handler_preserves_response_structure(self, mock_add_cors):
        """Test that handler preserves the exact response after CORS processing"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = ROUTE_MAP["GET /notifications"]

        api_response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"custom": "data"}),
        }
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"custom": "data"}),
        }
        ROUTE_MAP["GET /notifications"] = MagicMock(return_value=api_response)
        mock_add_cors.return_value = expected_response

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/notifications",
                "requestContext": {},
            }

            # Act
            response = handler(event, self.context)

            # Assert
            self.assertEqual(response, expected_response)
            mock_add_cors.assert_called_once_with(api_response)

        finally:
            # Restore the original function
            ROUTE_MAP["GET /notifications"] = original_func

    @patch("src.lambdas.notification_lambda.notification_lambda.add_cors_headers")
    def test_multiple_route_variations(self, mock_add_cors):
        """Test various route path variations that should return 404"""
        expected_response = {
            "statusCode": 404,
            "body": json.dumps({"error": "Route not found"}),
        }
        mock_add_cors.return_value = expected_response

        test_cases = [
            ("GET", "/notification"),  # Missing 's'
            ("GET", "/notifications/"),  # Trailing slash
            ("PATCH", "/notifications/read"),  # Missing {notification_id}
            ("PUT", "/notifications/{notification_id}/read"),  # Wrong method
            ("PATCH", "/notifications/{notification_id}"),  # Missing /read
            (
                "GET",
                "/notifications/{notification_id}/read",
            ),  # Wrong method for read endpoint
        ]

        for http_method, resource_path in test_cases:
            with self.subTest(method=http_method, path=resource_path):
                event = {
                    "httpMethod": http_method,
                    "resource": resource_path,
                    "requestContext": {},
                }

                response = handler(event, self.context)

                self.assertEqual(response["statusCode"], 404)

    def test_event_context_passed_correctly(self):
        """Test that event and context are passed correctly to API handlers"""
        from src.lambdas.notification_lambda.notification_lambda import (
            handler,
            ROUTE_MAP,
        )

        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = ROUTE_MAP["GET /notifications"]

        # Replace with our mock
        mock_api_response = {"statusCode": 200, "headers": {}, "body": "{}"}
        mock_func = MagicMock(return_value=mock_api_response)
        ROUTE_MAP["GET /notifications"] = mock_func

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/notifications",
                "requestContext": {"test": "data"},
                "headers": {"Authorization": "Bearer token"},
                "queryStringParameters": {"limit": "5"},
            }

            # Act
            handler(event, self.context)

            # Assert
            mock_func.assert_called_once_with(event, self.context)

            # Verify the exact event object was passed (not modified)
            called_event = mock_func.call_args[0][0]
            self.assertEqual(called_event["httpMethod"], "GET")
            self.assertEqual(called_event["resource"], "/notifications")
            self.assertEqual(called_event["requestContext"]["test"], "data")
            self.assertEqual(called_event["headers"]["Authorization"], "Bearer token")
            self.assertEqual(called_event["queryStringParameters"]["limit"], "5")

        finally:
            # Restore the original function
            ROUTE_MAP["GET /notifications"] = original_func


if __name__ == "__main__":
    unittest.main()
