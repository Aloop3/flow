import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas import set_lambda


class TestSetLambda(BaseTest):
    """Test suite for the Set Lambda handler"""

    def test_get_set_route(self):
        """Test successful routing to get_set function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = set_lambda.ROUTE_MAP["GET /sets/{set_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "set_id": "set123",
                    "completed_exercise_id": "exercise456",
                    "workout_id": "workout789",
                    "set_number": 1,
                    "reps": 5,
                    "weight": 225.0,
                    "rpe": 8.5,
                }
            ),
        }
        set_lambda.ROUTE_MAP["GET /sets/{set_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/sets/{set_id}",
                "pathParameters": {"set_id": "set123"},
            }
            context = {}

            # Call the Lambda handler
            response = set_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["set_id"], "set123")
            self.assertEqual(response_body["reps"], 5)
            set_lambda.ROUTE_MAP["GET /sets/{set_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            set_lambda.ROUTE_MAP["GET /sets/{set_id}"] = original_func

    def test_get_sets_for_exercise_route(self):
        """Test successful routing to get_sets_for_exercise function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = set_lambda.ROUTE_MAP["GET /exercises/{exercise_id}/sets"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "exercise_id": "exercise456",
                    "sets": [
                        {"set_id": "set1", "set_number": 1, "reps": 5, "weight": 225.0},
                        {"set_id": "set2", "set_number": 2, "reps": 5, "weight": 230.0},
                    ],
                }
            ),
        }
        set_lambda.ROUTE_MAP["GET /exercises/{exercise_id}/sets"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/exercises/{exercise_id}/sets",
                "pathParameters": {"exercise_id": "exercise456"},
            }
            context = {}

            # Call the Lambda handler
            response = set_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["exercise_id"], "exercise456")
            self.assertEqual(len(response_body["sets"]), 2)
            self.assertEqual(response_body["sets"][0]["set_id"], "set1")
            set_lambda.ROUTE_MAP[
                "GET /exercises/{exercise_id}/sets"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            set_lambda.ROUTE_MAP["GET /exercises/{exercise_id}/sets"] = original_func

    def test_create_set_route(self):
        """Test successful routing to create_set function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = set_lambda.ROUTE_MAP["POST /exercises/{exercise_id}/sets"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "set_id": "newset123",
                    "completed_exercise_id": "exercise456",
                    "workout_id": "workout789",
                    "set_number": 3,
                    "reps": 5,
                    "weight": 245.0,
                    "rpe": 8.5,
                }
            ),
        }
        set_lambda.ROUTE_MAP["POST /exercises/{exercise_id}/sets"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/exercises/{exercise_id}/sets",
                "pathParameters": {"exercise_id": "exercise456"},
                "body": json.dumps(
                    {
                        "workout_id": "workout789",
                        "set_number": 3,
                        "reps": 5,
                        "weight": 245.0,
                        "rpe": 8.5,
                    }
                ),
            }
            context = {}

            # Call the Lambda handler
            response = set_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["set_id"], "newset123")
            self.assertEqual(response_body["reps"], 5)
            self.assertEqual(response_body["weight"], 245.0)
            set_lambda.ROUTE_MAP[
                "POST /exercises/{exercise_id}/sets"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            set_lambda.ROUTE_MAP["POST /exercises/{exercise_id}/sets"] = original_func

    def test_update_set_route(self):
        """Test successful routing to update_set function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = set_lambda.ROUTE_MAP["PUT /sets/{set_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "set_id": "set123",
                    "completed_exercise_id": "exercise456",
                    "workout_id": "workout789",
                    "set_number": 1,
                    "reps": 6,  # Updated from 5 to 6
                    "weight": 235.0,  # Updated weight
                    "rpe": 9.0,  # Updated RPE
                }
            ),
        }
        set_lambda.ROUTE_MAP["PUT /sets/{set_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/sets/{set_id}",
                "pathParameters": {"set_id": "set123"},
                "body": json.dumps({"reps": 6, "weight": 235.0, "rpe": 9.0}),
            }
            context = {}

            # Call the Lambda handler
            response = set_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["reps"], 6)
            self.assertEqual(response_body["weight"], 235.0)
            self.assertEqual(response_body["rpe"], 9.0)
            set_lambda.ROUTE_MAP["PUT /sets/{set_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            set_lambda.ROUTE_MAP["PUT /sets/{set_id}"] = original_func

    def test_delete_set_route(self):
        """Test successful routing to delete_set function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = set_lambda.ROUTE_MAP["DELETE /sets/{set_id}"]

        # Replace with our mock
        mock_response = {"statusCode": 204, "body": json.dumps({})}
        set_lambda.ROUTE_MAP["DELETE /sets/{set_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "DELETE",
                "resource": "/sets/{set_id}",
                "pathParameters": {"set_id": "set123"},
            }
            context = {}

            # Call the Lambda handler
            response = set_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 204)
            set_lambda.ROUTE_MAP["DELETE /sets/{set_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            set_lambda.ROUTE_MAP["DELETE /sets/{set_id}"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "PATCH",  # Not defined in the ROUTE_MAP
            "resource": "/sets/{set_id}",
        }
        context = {}

        # Call the Lambda handler
        response = set_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = set_lambda.ROUTE_MAP["GET /sets/{set_id}"]

        # Replace with our mock that raises an exception
        set_lambda.ROUTE_MAP["GET /sets/{set_id}"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/sets/{set_id}",
                "pathParameters": {"set_id": "set123"},
            }
            context = {}

            # Call the Lambda handler
            response = set_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            set_lambda.ROUTE_MAP["GET /sets/{set_id}"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            set_lambda.ROUTE_MAP["GET /sets/{set_id}"] = original_func


if __name__ == "__main__":
    unittest.main()
