import json
import os
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.client"):
    from src.lambdas.feedback_lambda import feedback_lambda


class TestFeedbackLambda(BaseTest):
    """Test suite for the Feedback Lambda handler"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        super().setUp()
        self.valid_event = {
            "httpMethod": "POST",
            "resource": "/feedback",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "test@example.com",
                        "name": "Test User",
                        "sub": "test-user-id",
                    }
                }
            },
            "body": json.dumps(
                {
                    "category": "bug",
                    "message": "Test feedback message",
                    "pageUrl": "https://example.com/test-page",
                }
            ),
            "headers": {"User-Agent": "Mozilla/5.0 Test Browser"},
        }
        self.context = MagicMock()
        self.context.invoked_function_arn = (
            "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        )

    def test_options_request_cors(self):
        """Test successful CORS handling for OPTIONS request"""
        # Setup
        event = {"httpMethod": "OPTIONS"}

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "OK")
        # Verify proper CORS headers are present
        self.assertIn("headers", response)
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertIn("Access-Control-Allow-Methods", response["headers"])
        self.assertIn("Access-Control-Allow-Headers", response["headers"])

    def test_successful_feedback_submission(self):
        """Test successful feedback submission with SNS publish"""
        # Setup - Mock SNS client
        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            # Call the Lambda handler
            response = feedback_lambda.handler(self.valid_event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(
                response_body["message"], "Feedback submitted successfully"
            )
            self.assertEqual(response_body["feedback_id"], "test-message-id")

            # Verify CORS headers are present
            self.assertIn("headers", response)
            self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")

            # Verify SNS publish was called
            mock_sns.publish.assert_called_once()
            call_args = mock_sns.publish.call_args
            self.assertIn("TopicArn", call_args.kwargs)
            self.assertIn("[FLOW BETA] BUG:", call_args.kwargs["Subject"])
            self.assertIn("Test feedback message", call_args.kwargs["Message"])

    def test_sns_failure_fallback_logging(self):
        """Test fallback to logging when SNS publish fails"""
        # Setup - Mock SNS client to raise exception
        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.side_effect = Exception("SNS error")

            # Call the Lambda handler
            response = feedback_lambda.handler(self.valid_event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(
                response_body["message"], "Feedback submitted successfully (logged)"
            )
            self.assertTrue(response_body["feedback_id"].startswith("logged-"))

    def test_missing_auth_claims(self):
        """Test handling of missing authentication claims"""
        # Setup - Remove auth claims
        event = self.valid_event.copy()
        event["requestContext"] = {}

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertIn("Unauthorized", response_body["error"])
        # Verify CORS headers are present (note: this path uses add_cors_headers, not add_feedback_cors_headers)
        self.assertIn("headers", response)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")

    def test_missing_request_body(self):
        """Test handling of missing request body"""
        # Setup - Remove body
        event = self.valid_event.copy()
        del event["body"]

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Request body is required")

    def test_invalid_json_body(self):
        """Test handling of invalid JSON in request body"""
        # Setup - Invalid JSON
        event = self.valid_event.copy()
        event["body"] = "invalid json"

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Invalid JSON in request body")

    def test_missing_authorizer(self):
        """Test handling when authorizer is missing"""
        # Setup - requestContext without authorizer
        event = self.valid_event.copy()
        event["requestContext"] = {"some_key": "some_value"}

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized - no authorizer")

        # Updated assertion - now CORS headers ARE present
        self.assertIn("headers", response)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        # CORS headers should now be present
        self.assertIn("Access-Control-Allow-Origin", response["headers"])
        # Should use environment CORS_ORIGIN or default to "*"
        expected_origin = os.environ.get("CORS_ORIGIN", "*")
        self.assertEqual(
            response["headers"]["Access-Control-Allow-Origin"], expected_origin
        )

    def test_missing_claims(self):
        """Test handling when claims are missing - ensures add_cors_headers path is tested"""
        # Setup - authorizer without claims
        event = self.valid_event.copy()
        event["requestContext"] = {
            "authorizer": {"some_key": "some_value"}  # Valid dict but no claims
        }

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized - no claims")
        self.assertIn("headers", response)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")

        # CORS headers should now be present
        self.assertIn("Access-Control-Allow-Origin", response["headers"])
        expected_origin = os.environ.get("CORS_ORIGIN", "*")
        self.assertEqual(
            response["headers"]["Access-Control-Allow-Origin"], expected_origin
        )

    def test_invalid_category(self):
        """Test handling of invalid feedback category"""
        # Setup - Invalid category
        event = self.valid_event.copy()
        event["body"] = json.dumps(
            {"category": "invalid-category", "message": "Test feedback message"}
        )

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid category", response_body["error"])
        self.assertIn(
            "bug, suggestion, question, feature-request", response_body["error"]
        )

    def test_valid_categories(self):
        """Test all valid feedback categories"""
        valid_categories = ["bug", "suggestion", "question", "feature-request"]

        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            for category in valid_categories:
                with self.subTest(category=category):
                    # Setup
                    event = self.valid_event.copy()
                    event["body"] = json.dumps(
                        {"category": category, "message": f"Test {category} message"}
                    )

                    # Call the Lambda handler
                    response = feedback_lambda.handler(event, self.context)

                    # Assert
                    self.assertEqual(response["statusCode"], 200)
                    response_body = json.loads(response["body"])
                    self.assertEqual(
                        response_body["message"], "Feedback submitted successfully"
                    )

    def test_sns_topic_arn_construction(self):
        """Test SNS topic ARN construction for different environments"""
        test_cases = [
            ("dev", "flow-dev-feedback-alerts"),
            ("prod", "flow-prod-monitoring-alerts"),
        ]

        for environment, expected_topic_suffix in test_cases:
            with self.subTest(environment=environment):
                with patch(
                    "src.lambdas.feedback_lambda.feedback_lambda.sns"
                ) as mock_sns:
                    with patch.dict("os.environ", {"ENVIRONMENT": environment}):
                        mock_sns.publish.return_value = {"MessageId": "test-message-id"}

                        # Call the Lambda handler
                        response = feedback_lambda.handler(
                            self.valid_event, self.context
                        )

                        # Assert
                        self.assertEqual(response["statusCode"], 200)
                        call_args = mock_sns.publish.call_args
                        topic_arn = call_args.kwargs["TopicArn"]
                        self.assertIn(expected_topic_suffix, topic_arn)

    def test_user_info_extraction(self):
        """Test extraction of user information from Cognito claims"""
        # Setup - Test different user info scenarios
        test_cases = [
            {
                "claims": {
                    "email": "test@example.com",
                    "name": "Test User",
                    "sub": "user123",
                },
                "expected_email": "test@example.com",
                "expected_name": "Test User",
            },
            {
                "claims": {"email": "noreply@example.com", "sub": "user456"},
                "expected_email": "noreply@example.com",
                "expected_name": "noreply",  # Should extract from email
            },
        ]

        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            for test_case in test_cases:
                with self.subTest(claims=test_case["claims"]):
                    # Setup
                    event = self.valid_event.copy()
                    event["requestContext"]["authorizer"]["claims"] = test_case[
                        "claims"
                    ]

                    # Call the Lambda handler
                    response = feedback_lambda.handler(event, self.context)

                    # Assert
                    self.assertEqual(response["statusCode"], 200)
                    call_args = mock_sns.publish.call_args
                    message_body = call_args.kwargs["Message"]
                    self.assertIn(test_case["expected_email"], message_body)
                    self.assertIn(test_case["expected_name"], message_body)

    def test_context_information_capture(self):
        """Test capture of context information in feedback"""
        # Setup
        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            # Call the Lambda handler
            response = feedback_lambda.handler(self.valid_event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            call_args = mock_sns.publish.call_args
            message_body = call_args.kwargs["Message"]

            # Verify context information is included
            self.assertIn("https://example.com/test-page", message_body)
            self.assertIn("Mozilla/5.0 Test Browser", message_body)
            self.assertIn("Test feedback message", message_body)

    def test_missing_optional_fields(self):
        """Test handling when optional fields are missing"""
        # Setup - Remove optional fields
        event = self.valid_event.copy()
        event["body"] = json.dumps(
            {
                "category": "suggestion",
                "message": "Test feedback without optional fields",
            }
        )
        del event["headers"]

        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            call_args = mock_sns.publish.call_args
            message_body = call_args.kwargs["Message"]
            self.assertIn(
                "Not provided", message_body
            )  # Should handle missing fields gracefully

    def test_exception_handling(self):
        """Test general exception handling"""
        # Setup - Mock datetime to raise unexpected exception during processing
        with patch("src.lambdas.feedback_lambda.feedback_lambda.dt") as mock_datetime:
            mock_datetime.now.side_effect = Exception("Unexpected datetime error")

            # Call the Lambda handler
            response = feedback_lambda.handler(self.valid_event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["error"], "Internal server error")

    def test_missing_request_context(self):
        """Test auth handling when requestContext is completely missing"""
        # Setup - Remove entire requestContext
        event = self.valid_event.copy()
        del event["requestContext"]

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert - Should hit the "requestContext is missing" branch
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized - no request context")

    def test_request_context_without_get_method(self):
        """Test auth handling when requestContext lacks get method"""
        # Setup - requestContext as string instead of dict
        event = self.valid_event.copy()
        event["requestContext"] = "not-a-dict"

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert - Should hit the authorizer extraction branch
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertIn("Unauthorized", response_body["error"])

    def test_auth_exception_handling(self):
        """Test auth exception handling"""
        # Setup - Mock requestContext.get to raise exception
        event = self.valid_event.copy()
        mock_context = MagicMock()
        mock_context.get.side_effect = Exception("Context error")
        event["requestContext"] = mock_context

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized - auth error")

    def test_body_as_non_dict_non_string(self):
        """Test body parsing when body is neither string nor dict"""
        # Setup - Body as integer
        event = self.valid_event.copy()
        event["body"] = 12345

        # Call the Lambda handler
        response = feedback_lambda.handler(event, self.context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Invalid body format")

    def test_body_parsing_exception(self):
        """Test body parsing exception handling"""
        # Setup - Patch json.loads to raise a non-JSONDecodeError exception only for specific calls
        original_json_loads = json.loads

        def selective_json_loads(s):
            # If this looks like the request body, raise an exception
            if isinstance(s, str) and '"category"' in s and '"message"' in s:
                raise Exception("Unexpected JSON error")
            # Otherwise use the real json.loads (for response body parsing in the test)
            return original_json_loads(s)

        with patch(
            "src.lambdas.feedback_lambda.feedback_lambda.json.loads",
            side_effect=selective_json_loads,
        ):
            event = self.valid_event.copy()

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert - Parse response with original json.loads
            self.assertEqual(response["statusCode"], 400)
            response_body = original_json_loads(response["body"])
            self.assertEqual(response_body["error"], "Body parsing failed")

    def test_body_not_dict_like_during_validation(self):
        """Test field validation when parsed body is not dict-like"""
        # Setup - Patch json.loads to return a string instead of dict for request body
        original_json_loads = json.loads

        def selective_json_loads(s):
            # If this looks like the request body, return a string instead of dict
            if isinstance(s, str) and '"category"' in s and '"message"' in s:
                return "not-a-dict"  # Return string instead of dict
            # Otherwise use the real json.loads (for response body parsing in the test)
            return original_json_loads(s)

        with patch(
            "src.lambdas.feedback_lambda.feedback_lambda.json.loads",
            side_effect=selective_json_loads,
        ):
            event = self.valid_event.copy()

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert - Parse response with original json.loads
            self.assertEqual(response["statusCode"], 400)
            response_body = original_json_loads(response["body"])
            self.assertEqual(response_body["error"], "Invalid JSON in request body")

    def test_field_validation_exception(self):
        """Test field validation exception handling"""
        # Setup - Create a dict that passes initial validation but fails on subsequent access
        original_json_loads = json.loads

        class BadBodyDict(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.access_count = 0

            def get(self, key, default=None):
                self.access_count += 1
                # First two calls for required field validation - succeed
                if self.access_count <= 2 and key in ["category", "message"]:
                    return "bug" if key == "category" else "test message"
                # Later calls - raise exception
                raise Exception("Field access error")

    def test_user_info_extraction_exception(self):
        """Test user info extraction exception handling"""
        # Setup - Mock claims.get to raise exception
        event = self.valid_event.copy()
        mock_claims = MagicMock()
        mock_claims.get.side_effect = Exception("Claims access error")
        event["requestContext"]["authorizer"]["claims"] = mock_claims

        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert - Should succeed but use "unknown" for user info
            self.assertEqual(response["statusCode"], 200)
            call_args = mock_sns.publish.call_args
            message_body = call_args.kwargs["Message"]
            self.assertIn("unknown", message_body)

    def test_data_extraction_exception(self):
        """Test feedback data extraction exception handling"""
        # Setup - Create a dict that works for validation but fails for data extraction
        original_json_loads = json.loads

        class DataExtractionDict(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.access_count = 0

            def get(self, key, default=None):
                self.access_count += 1
                # First two calls for required field validation - succeed
                if self.access_count <= 2 and key in ["category", "message"]:
                    return "bug" if key == "category" else "test message"
                # Later calls for data extraction - raise exception
                raise Exception("Data extraction error")

    def test_header_extraction_exception(self):
        """Test header extraction exception handling"""
        # Setup - Mock headers to raise exception
        event = self.valid_event.copy()
        mock_headers = MagicMock()
        mock_headers.get.side_effect = Exception("Header access error")
        event["headers"] = mock_headers

        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert - Should succeed but use "Not provided" for user agent
            self.assertEqual(response["statusCode"], 200)
            call_args = mock_sns.publish.call_args
            message_body = call_args.kwargs["Message"]
            self.assertIn("Not provided", message_body)

    def test_double_encoded_json_body(self):
        """Test handling of double-encoded JSON body"""
        # Setup - Double encode the JSON
        inner_json = json.dumps(
            {"category": "bug", "message": "Double encoded message"}
        )
        event = self.valid_event.copy()
        event["body"] = json.dumps(inner_json)  # Double encode

        with patch("src.lambdas.feedback_lambda.feedback_lambda.sns") as mock_sns:
            mock_sns.publish.return_value = {"MessageId": "test-message-id"}

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(
                response_body["message"], "Feedback submitted successfully"
            )

    def test_json_decode_error_at_top_level(self):
        """Test JSONDecodeError handling at the top level exception handler"""
        # Setup - Mock json.loads to raise JSONDecodeError during initial body parsing
        with patch("src.lambdas.feedback_lambda.feedback_lambda.json") as mock_json:
            # Make json.loads raise JSONDecodeError during body parsing
            mock_json.loads.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
            mock_json.dumps = json.dumps  # Keep dumps working for response
            mock_json.JSONDecodeError = json.JSONDecodeError  # Keep the exception class

            event = self.valid_event.copy()

            # Call the Lambda handler
            response = feedback_lambda.handler(event, self.context)

            # Assert - Should hit the top-level JSONDecodeError handler
            self.assertEqual(response["statusCode"], 400)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["error"], "Invalid JSON in request body")


if __name__ == "__main__":
    unittest.main()
