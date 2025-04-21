import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.week_lambda import week_lambda


class TestWeekLambda(BaseTest):
    """Test suite for the Week Lambda handler"""

    def test_create_week_route(self):
        """Test successful routing to create_week function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = week_lambda.ROUTE_MAP["POST /weeks"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {"week_id": "week123", "block_id": "block456", "week_number": 1}
            ),
        }
        week_lambda.ROUTE_MAP["POST /weeks"] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/weeks",
                "body": json.dumps(
                    {"block_id": "block456", "week_number": 1, "notes": "Test week"}
                ),
            }
            context = {}

            # Call the Lambda handler
            response = week_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["week_id"], "week123")
            week_lambda.ROUTE_MAP["POST /weeks"].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            week_lambda.ROUTE_MAP["POST /weeks"] = original_func

    def test_get_weeks_for_block_route(self):
        """Test successful routing to get_weeks_for_block function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = week_lambda.ROUTE_MAP["GET /blocks/{block_id}/weeks"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [
                    {"week_id": "week1", "week_number": 1},
                    {"week_id": "week2", "week_number": 2},
                ]
            ),
        }
        week_lambda.ROUTE_MAP["GET /blocks/{block_id}/weeks"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/blocks/{block_id}/weeks",
                "pathParameters": {"block_id": "block456"},
            }
            context = {}

            # Call the Lambda handler
            response = week_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["week_id"], "week1")
            week_lambda.ROUTE_MAP[
                "GET /blocks/{block_id}/weeks"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            week_lambda.ROUTE_MAP["GET /blocks/{block_id}/weeks"] = original_func

    def test_update_week_route(self):
        """Test successful routing to update_week function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = week_lambda.ROUTE_MAP["PUT /weeks/{week_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "week_id": "week123",
                    "block_id": "block456",
                    "week_number": 1,
                    "notes": "Updated notes",
                }
            ),
        }
        week_lambda.ROUTE_MAP["PUT /weeks/{week_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/weeks/{week_id}",
                "pathParameters": {"week_id": "week123"},
                "body": json.dumps({"notes": "Updated notes"}),
            }
            context = {}

            # Call the Lambda handler
            response = week_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["notes"], "Updated notes")
            week_lambda.ROUTE_MAP["PUT /weeks/{week_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            week_lambda.ROUTE_MAP["PUT /weeks/{week_id}"] = original_func

    def test_delete_week_route(self):
        """Test successful routing to delete_week function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = week_lambda.ROUTE_MAP["DELETE /weeks/{week_id}"]

        # Replace with our mock
        mock_response = {"statusCode": 204, "body": json.dumps({})}
        week_lambda.ROUTE_MAP["DELETE /weeks/{week_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "DELETE",
                "resource": "/weeks/{week_id}",
                "pathParameters": {"week_id": "week123"},
            }
            context = {}

            # Call the Lambda handler
            response = week_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 204)
            week_lambda.ROUTE_MAP["DELETE /weeks/{week_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            week_lambda.ROUTE_MAP["DELETE /weeks/{week_id}"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "PATCH",  # Not defined in the ROUTE_MAP
            "resource": "/weeks/{week_id}",
        }
        context = {}

        # Call the Lambda handler
        response = week_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = week_lambda.ROUTE_MAP["GET /blocks/{block_id}/weeks"]

        # Replace with our mock that raises an exception
        week_lambda.ROUTE_MAP["GET /blocks/{block_id}/weeks"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/blocks/{block_id}/weeks",
                "pathParameters": {"block_id": "block456"},
            }
            context = {}

            # Call the Lambda handler
            response = week_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            week_lambda.ROUTE_MAP[
                "GET /blocks/{block_id}/weeks"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            week_lambda.ROUTE_MAP["GET /blocks/{block_id}/weeks"] = original_func


if __name__ == "__main__":
    unittest.main()
