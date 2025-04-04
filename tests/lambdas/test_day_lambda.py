import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas import day_lambda


class TestDayLambda(BaseTest):
    """Test suite for the Day Lambda handler"""

    def test_create_day_route(self):
        """Test successful routing to create_day function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = day_lambda.ROUTE_MAP["POST /days"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "day_id": "day123",
                    "week_id": "week456",
                    "day_number": 1,
                    "date": "2025-03-15",
                    "focus": "squat",
                }
            ),
        }
        day_lambda.ROUTE_MAP["POST /days"] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/days",
                "body": json.dumps(
                    {
                        "week_id": "week456",
                        "day_number": 1,
                        "date": "2025-03-15",
                        "focus": "squat",
                    }
                ),
            }
            context = {}

            # Call the Lambda handler
            response = day_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["day_id"], "day123")
            day_lambda.ROUTE_MAP["POST /days"].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            day_lambda.ROUTE_MAP["POST /days"] = original_func

    def test_get_days_for_week_route(self):
        """Test successful routing to get_days_for_week function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [
                    {"day_id": "day1", "day_number": 1, "date": "2025-03-15"},
                    {"day_id": "day2", "day_number": 2, "date": "2025-03-16"},
                ]
            ),
        }
        day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/weeks/{week_id}/days",
                "pathParameters": {"week_id": "week456"},
            }
            context = {}

            # Call the Lambda handler
            response = day_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["day_id"], "day1")
            day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"] = original_func

    def test_update_day_route(self):
        """Test successful routing to update_day function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = day_lambda.ROUTE_MAP["PUT /days/{day_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "day_id": "day123",
                    "week_id": "week456",
                    "day_number": 1,
                    "date": "2025-03-15",
                    "focus": "deadlift",  # Updated focus
                    "notes": "Heavy day",  # Added notes
                }
            ),
        }
        day_lambda.ROUTE_MAP["PUT /days/{day_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/days/{day_id}",
                "pathParameters": {"day_id": "day123"},
                "body": json.dumps({"focus": "deadlift", "notes": "Heavy day"}),
            }
            context = {}

            # Call the Lambda handler
            response = day_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["focus"], "deadlift")
            self.assertEqual(response_body["notes"], "Heavy day")
            day_lambda.ROUTE_MAP["PUT /days/{day_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            day_lambda.ROUTE_MAP["PUT /days/{day_id}"] = original_func

    def test_delete_day_route(self):
        """Test successful routing to delete_day function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = day_lambda.ROUTE_MAP["DELETE /days/{day_id}"]

        # Replace with our mock
        mock_response = {"statusCode": 204, "body": json.dumps({})}
        day_lambda.ROUTE_MAP["DELETE /days/{day_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "DELETE",
                "resource": "/days/{day_id}",
                "pathParameters": {"day_id": "day123"},
            }
            context = {}

            # Call the Lambda handler
            response = day_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 204)
            day_lambda.ROUTE_MAP["DELETE /days/{day_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            day_lambda.ROUTE_MAP["DELETE /days/{day_id}"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "PATCH",  # Not defined in the ROUTE_MAP
            "resource": "/days/{day_id}",
        }
        context = {}

        # Call the Lambda handler
        response = day_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"]

        # Replace with our mock that raises an exception
        day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/weeks/{week_id}/days",
                "pathParameters": {"week_id": "week456"},
            }
            context = {}

            # Call the Lambda handler
            response = day_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            day_lambda.ROUTE_MAP["GET /weeks/{week_id}/days"] = original_func


if __name__ == "__main__":
    unittest.main()
