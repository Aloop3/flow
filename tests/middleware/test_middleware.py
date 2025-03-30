import unittest
from unittest.mock import MagicMock, patch
import json
from src.utils.response import create_response

# Import the middleware after patching
with patch("boto3.resource"):
    from src.middleware.middleware import LambdaMiddleware, with_middleware
    from src.middleware.common_middleware import (
        validate_auth,
        log_request,
        handle_errors,
    )


class TestLambdaMiddleware(unittest.TestCase):
    """
    Test suite for Lambda middleware functionality
    """

    def test_middleware_composition(self):
        """
        Test that middleware functions are composed correctly
        """
        # Create mock handler and middleware
        handler = MagicMock(return_value=create_response(200, {"message": "Success"}))
        middleware1 = MagicMock(return_value={"key1": "value1"})
        middleware2 = MagicMock(return_value={"key2": "value2"})

        # Create middleware chain
        middleware = LambdaMiddleware(handler)
        middleware.add_middleware(middleware1)
        middleware.add_middleware(middleware2)

        # Check that middlewares were added correctly
        self.assertEqual(len(middleware.middlewares), 2)
        self.assertEqual(middleware.middlewares[0], middleware1)
        self.assertEqual(middleware.middlewares[1], middleware2)

    def test_middleware_execution(self):
        """
        Test that middleware functions are executed in the correct order
        """
        # Create mock handler
        handler = MagicMock(return_value=create_response(200, {"message": "Success"}))

        # Create middleware that modifies the event
        def middleware1(event, context):
            event["middleware1_executed"] = True
            return event

        def middleware2(event, context):
            event["middleware2_executed"] = True
            return event

        # Create middleware chain
        middleware = LambdaMiddleware(handler)
        middleware.add_middleware(middleware1)
        middleware.add_middleware(middleware2)

        # Execute middleware
        event = {}
        context = MagicMock()
        middleware(event, context)

        # Check that the middlewares were executed
        self.assertTrue(event.get("middleware1_executed"))
        self.assertTrue(event.get("middleware2_executed"))

        # Check that the handler was called with the modified event
        handler.assert_called_once_with(event, context)

    def test_middleware_error_handling(self):
        """
        Test that errors in middleware are handled correctly
        """
        # Create mock handler
        handler = MagicMock(return_value=create_response(200, {"message": "Success"}))

        # Create middleware that raises an error
        def error_middleware(event, context):
            raise Exception("Middleware error")

        # Create middleware chain
        middleware = LambdaMiddleware(handler)
        middleware.add_middleware(error_middleware)

        # Execute middleware
        event = {}
        context = MagicMock()
        response = middleware(event, context)

        # Check that the response indicates an error
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Middleware error")

        # Check that the handler was not called
        handler.assert_not_called()

    def test_handler_error_handling(self):
        """
        Test that errors in the handler are handled correctly
        """
        # Create mock handler that raises an error
        handler = MagicMock(side_effect=Exception("Handler error"))

        # Create middleware chain
        middleware = LambdaMiddleware(handler)

        # Execute middleware
        event = {}
        context = MagicMock()
        response = middleware(event, context)

        # Check that the response indicates an error
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Handler error")

    def test_validate_auth_middleware(self):
        """
        Test the validate_auth middleware function
        """
        # Create event with auth claims
        event = {"requestContext": {"authorizer": {"claims": {"sub": "user123"}}}}
        context = MagicMock()

        # Call middleware
        result = validate_auth(event, context)

        # Check that the event was returned unchanged
        self.assertEqual(result, event)

        # Create event without auth claims
        event_no_auth = {}

        # Call middleware and expect an exception
        with self.assertRaises(Exception) as context:
            validate_auth(event_no_auth, context)
            self.assertTrue("Unauthorized" in str(context.exception))

    @patch("logging.Logger.info")
    def test_log_request_middleware(self, mock_logger_info):
        """
        Test the log_request middleware function
        """
        # Create event and context
        event = {
            "path": "/users",
            "httpMethod": "GET",
            "requestContext": {"authorizer": {"claims": {"sub": "user123"}}},
        }
        context = MagicMock()
        context.aws_request_id = "req123"

        # Call middleware
        result = log_request(event, context)

        # Check that the event was returned unchanged
        self.assertEqual(result, event)

        # Check that logging was called
        mock_logger_info.assert_called_once()

    def test_handle_errors_middleware(self):
        """
        Test the handle_errors middleware function
        """
        # Create event
        event = {}
        context = MagicMock()

        # Call middleware
        result = handle_errors(event, context)

        # Check that the event was returned
        self.assertEqual(result, event)

    def test_with_middleware_decorator(self):
        """
        Test the with_middleware decorator
        """
        # Create mock handler
        handler = MagicMock(return_value=create_response(200, {"message": "Success"}))

        # Create middleware that modifies the event
        def middleware1(event, context):
            event["middleware1_executed"] = True
            return event

        def middleware2(event, context):
            event["middleware2_executed"] = True
            return event

        # Apply decorator
        decorated_handler = with_middleware([middleware1, middleware2])(handler)

        # Call decorated handler
        event = {}
        context = MagicMock()
        decorated_handler(event, context)

        # Check that the middlewares were executed
        self.assertTrue(event.get("middleware1_executed"))
        self.assertTrue(event.get("middleware2_executed"))

        # Check that the handler was called with the modified event
        handler.assert_called_once_with(event, context)

    def test_with_middleware_decorator_no_middlewares(self):
        """
        Test the with_middleware decorator with no middlewares
        """
        # Create mock handler
        handler = MagicMock(return_value=create_response(200, {"message": "Success"}))

        # Apply decorator with no middlewares
        decorated_handler = with_middleware()(handler)

        # Call decorated handler
        event = {}
        context = MagicMock()
        decorated_handler(event, context)

        # Check that the handler was called with the event
        handler.assert_called_once_with(event, context)


if __name__ == "__main__":
    unittest.main()
