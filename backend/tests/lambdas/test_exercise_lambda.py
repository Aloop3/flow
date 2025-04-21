import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.exercise_lambda import exercise_lambda


class TestExerciseLambda(BaseTest):
    """Test suite for the Exercise Lambda handler"""

    def test_create_exercise_route(self):
        """Test successful routing to create_exercise function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = exercise_lambda.ROUTE_MAP["POST /exercises"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "exercise_id": "ex123",
                    "workout_id": "workout456",
                    "exercise_type": "Squat",
                    "sets": 5,
                    "reps": 5,
                    "weight": 315.0,
                }
            ),
        }
        exercise_lambda.ROUTE_MAP["POST /exercises"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/exercises",
                "body": json.dumps(
                    {
                        "workout_id": "workout456",
                        "exercise_type": "Squat",
                        "sets": 5,
                        "reps": 5,
                        "weight": 315.0,
                    }
                ),
            }
            context = {}

            # Call the Lambda handler
            response = exercise_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["exercise_id"], "ex123")
            exercise_lambda.ROUTE_MAP["POST /exercises"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            exercise_lambda.ROUTE_MAP["POST /exercises"] = original_func

    def test_get_exercises_for_workout_route(self):
        """Test successful routing to get_exercises_for_workout function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = exercise_lambda.ROUTE_MAP["GET /days/{day_id}/exercises"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [
                    {"exercise_id": "ex1", "exercise_type": "Squat", "sets": 5},
                    {"exercise_id": "ex2", "exercise_type": "Bench Press", "sets": 3},
                ]
            ),
        }
        exercise_lambda.ROUTE_MAP["GET /days/{day_id}/exercises"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/days/{day_id}/exercises",
                "pathParameters": {"day_id": "day456"},
            }
            context = {}

            # Call the Lambda handler
            response = exercise_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["exercise_id"], "ex1")
            exercise_lambda.ROUTE_MAP[
                "GET /days/{day_id}/exercises"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            exercise_lambda.ROUTE_MAP["GET /days/{day_id}/exercises"] = original_func

    def test_update_exercise_route(self):
        """Test successful routing to update_exercise function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = exercise_lambda.ROUTE_MAP["PUT /exercises/{exercise_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "exercise_id": "ex123",
                    "workout_id": "workout456",
                    "exercise_type": "Squat",
                    "sets": 3,  # Updated from 5 to 3
                    "reps": 5,
                    "weight": 335.0,  # Updated weight
                    "notes": "Use belt",  # Added notes
                }
            ),
        }
        exercise_lambda.ROUTE_MAP["PUT /exercises/{exercise_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/exercises/{exercise_id}",
                "pathParameters": {"exercise_id": "ex123"},
                "body": json.dumps({"sets": 3, "weight": 335.0, "notes": "Use belt"}),
            }
            context = {}

            # Call the Lambda handler
            response = exercise_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["sets"], 3)
            self.assertEqual(response_body["weight"], 335.0)
            self.assertEqual(response_body["notes"], "Use belt")
            exercise_lambda.ROUTE_MAP[
                "PUT /exercises/{exercise_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            exercise_lambda.ROUTE_MAP["PUT /exercises/{exercise_id}"] = original_func

    def test_delete_exercise_route(self):
        """Test successful routing to delete_exercise function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = exercise_lambda.ROUTE_MAP["DELETE /exercises/{exercise_id}"]

        # Replace with our mock
        mock_response = {"statusCode": 204, "body": json.dumps({})}
        exercise_lambda.ROUTE_MAP["DELETE /exercises/{exercise_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "DELETE",
                "resource": "/exercises/{exercise_id}",
                "pathParameters": {"exercise_id": "ex123"},
            }
            context = {}

            # Call the Lambda handler
            response = exercise_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 204)
            exercise_lambda.ROUTE_MAP[
                "DELETE /exercises/{exercise_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            exercise_lambda.ROUTE_MAP["DELETE /exercises/{exercise_id}"] = original_func

    def test_reorder_exercises_route(self):
        """Test successful routing to reorder_exercises function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = exercise_lambda.ROUTE_MAP["POST /exercises/reorder"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [{"exercise_id": "ex2", "order": 1}, {"exercise_id": "ex1", "order": 2}]
            ),
        }
        exercise_lambda.ROUTE_MAP["POST /exercises/reorder"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/exercises/reorder",
                "body": json.dumps(
                    {"workout_id": "workout456", "exercise_order": ["ex2", "ex1"]}
                ),
            }
            context = {}

            # Call the Lambda handler
            response = exercise_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["exercise_id"], "ex2")
            self.assertEqual(response_body[0]["order"], 1)
            exercise_lambda.ROUTE_MAP[
                "POST /exercises/reorder"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            exercise_lambda.ROUTE_MAP["POST /exercises/reorder"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "PATCH",  # Not defined in the ROUTE_MAP
            "resource": "/exercises/{exercise_id}",
        }
        context = {}

        # Call the Lambda handler
        response = exercise_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = exercise_lambda.ROUTE_MAP["GET /days/{day_id}/exercises"]

        # Replace with our mock that raises an exception
        exercise_lambda.ROUTE_MAP["GET /days/{day_id}/exercises"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/days/{day_id}/exercises",
                "pathParameters": {"day_id": "day456"},
            }
            context = {}

            # Call the Lambda handler
            response = exercise_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            exercise_lambda.ROUTE_MAP[
                "GET /days/{day_id}/exercises"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            exercise_lambda.ROUTE_MAP["GET /days/{day_id}/exercises"] = original_func


if __name__ == "__main__":
    unittest.main()
