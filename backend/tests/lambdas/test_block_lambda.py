import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.block_lambda import block_lambda


class TestBlockLambda(BaseTest):
    """Test suite for the Block Lambda handler"""

    def test_create_block_route(self):
        """Test successful routing to create_block function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = block_lambda.ROUTE_MAP["POST /blocks"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "block_id": "block123",
                    "athlete_id": "athlete456",
                    "title": "Test Block",
                }
            ),
        }
        block_lambda.ROUTE_MAP["POST /blocks"] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/blocks",
                "body": json.dumps(
                    {
                        "athlete_id": "athlete456",
                        "title": "Test Block",
                        "start_date": "2025-03-01",
                        "end_date": "2025-04-01",
                    }
                ),
            }
            context = {}

            # Call the Lambda handler
            response = block_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["block_id"], "block123")
            block_lambda.ROUTE_MAP["POST /blocks"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            block_lambda.ROUTE_MAP["POST /blocks"] = original_func

    def test_get_block_route(self):
        """Test successful routing to get_block function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = block_lambda.ROUTE_MAP["GET /blocks/{block_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "block_id": "block123",
                    "athlete_id": "athlete456",
                    "title": "Test Block",
                }
            ),
        }
        block_lambda.ROUTE_MAP["GET /blocks/{block_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/blocks/{block_id}",
                "pathParameters": {"block_id": "block123"},
            }
            context = {}

            # Call the Lambda handler
            response = block_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["block_id"], "block123")
            block_lambda.ROUTE_MAP["GET /blocks/{block_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            block_lambda.ROUTE_MAP["GET /blocks/{block_id}"] = original_func

    def test_get_blocks_by_athlete_route(self):
        """Test successful routing to get_blocks_by_athlete function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = block_lambda.ROUTE_MAP["GET /athletes/{athlete_id}/blocks"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [
                    {"block_id": "block1", "title": "Block 1"},
                    {"block_id": "block2", "title": "Block 2"},
                ]
            ),
        }
        block_lambda.ROUTE_MAP["GET /athletes/{athlete_id}/blocks"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/athletes/{athlete_id}/blocks",
                "pathParameters": {"athlete_id": "athlete456"},
            }
            context = {}

            # Call the Lambda handler
            response = block_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["block_id"], "block1")
            block_lambda.ROUTE_MAP[
                "GET /athletes/{athlete_id}/blocks"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            block_lambda.ROUTE_MAP["GET /athletes/{athlete_id}/blocks"] = original_func

    def test_update_block_route(self):
        """Test successful routing to update_block function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = block_lambda.ROUTE_MAP["PUT /blocks/{block_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {"block_id": "block123", "title": "Updated Block", "status": "active"}
            ),
        }
        block_lambda.ROUTE_MAP["PUT /blocks/{block_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/blocks/{block_id}",
                "pathParameters": {"block_id": "block123"},
                "body": json.dumps({"title": "Updated Block", "status": "active"}),
            }
            context = {}

            # Call the Lambda handler
            response = block_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["title"], "Updated Block")
            block_lambda.ROUTE_MAP["PUT /blocks/{block_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            block_lambda.ROUTE_MAP["PUT /blocks/{block_id}"] = original_func

    def test_delete_block_route(self):
        """Test successful routing to delete_block function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = block_lambda.ROUTE_MAP["DELETE /blocks/{block_id}"]

        # Replace with our mock
        mock_response = {"statusCode": 204, "body": json.dumps({})}
        block_lambda.ROUTE_MAP["DELETE /blocks/{block_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "DELETE",
                "resource": "/blocks/{block_id}",
                "pathParameters": {"block_id": "block123"},
            }
            context = {}

            # Call the Lambda handler
            response = block_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 204)
            block_lambda.ROUTE_MAP["DELETE /blocks/{block_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            block_lambda.ROUTE_MAP["DELETE /blocks/{block_id}"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "PATCH",  # Not defined in the ROUTE_MAP
            "resource": "/blocks/{block_id}",
        }
        context = {}

        # Call the Lambda handler
        response = block_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = block_lambda.ROUTE_MAP["GET /blocks/{block_id}"]

        # Replace with our mock that raises an exception
        block_lambda.ROUTE_MAP["GET /blocks/{block_id}"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/blocks/{block_id}",
                "pathParameters": {"block_id": "block123"},
            }
            context = {}

            # Call the Lambda handler
            response = block_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            block_lambda.ROUTE_MAP["GET /blocks/{block_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            block_lambda.ROUTE_MAP["GET /blocks/{block_id}"] = original_func


if __name__ == "__main__":
    unittest.main()
