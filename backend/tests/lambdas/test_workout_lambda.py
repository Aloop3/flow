import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.workout_lambda import workout_lambda


class TestWorkoutLambda(BaseTest):
    """Test suite for the Workout Lambda handler"""

    def test_create_workout_route(self):
        """Test successful routing to create_workout function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP["POST /workouts"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "workout_id": "workout123",
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                    "status": "completed",
                    "exercises": [
                        {
                            "completed_id": "comp1",
                            "exercise_id": "ex1",
                            "actual_sets": 5,
                            "actual_reps": 5,
                            "actual_weight": 315.0,
                        }
                    ],
                }
            ),
        }
        workout_lambda.ROUTE_MAP["POST /workouts"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/workouts",
                "body": json.dumps(
                    {
                        "athlete_id": "athlete456",
                        "day_id": "day789",
                        "date": "2025-03-15",
                        "status": "completed",
                        "exercises": [
                            {
                                "exercise_id": "ex1",
                                "actual_sets": 5,
                                "actual_reps": 5,
                                "actual_weight": 315.0,
                            }
                        ],
                    }
                ),
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["workout_id"], "workout123")
            self.assertEqual(len(response_body["exercises"]), 1)
            workout_lambda.ROUTE_MAP["POST /workouts"].assert_called_once_with(
                event, context
            )
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP["POST /workouts"] = original_func

    def test_get_workout_route(self):
        """Test successful routing to get_workout function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP["GET /workouts/{workout_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "workout_id": "workout123",
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                    "status": "completed",
                }
            ),
        }
        workout_lambda.ROUTE_MAP["GET /workouts/{workout_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/workouts/{workout_id}",
                "pathParameters": {"workout_id": "workout123"},
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["workout_id"], "workout123")
            workout_lambda.ROUTE_MAP[
                "GET /workouts/{workout_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP["GET /workouts/{workout_id}"] = original_func

    def test_get_workouts_by_athlete_route(self):
        """Test successful routing to get_workouts_by_athlete function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP["GET /athletes/{athlete_id}/workouts"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [
                    {"workout_id": "w1", "date": "2025-03-15"},
                    {"workout_id": "w2", "date": "2025-03-16"},
                ]
            ),
        }
        workout_lambda.ROUTE_MAP["GET /athletes/{athlete_id}/workouts"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/athletes/{athlete_id}/workouts",
                "pathParameters": {"athlete_id": "athlete456"},
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["workout_id"], "w1")
            workout_lambda.ROUTE_MAP[
                "GET /athletes/{athlete_id}/workouts"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP[
                "GET /athletes/{athlete_id}/workouts"
            ] = original_func

    def test_get_workout_by_day_route(self):
        """Test successful routing to get_workout_by_day function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP[
            "GET /athletes/{athlete_id}/days/{day_id}/workout"
        ]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "workout_id": "workout123",
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                }
            ),
        }
        workout_lambda.ROUTE_MAP[
            "GET /athletes/{athlete_id}/days/{day_id}/workout"
        ] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/athletes/{athlete_id}/days/{day_id}/workout",
                "pathParameters": {"athlete_id": "athlete456", "day_id": "day789"},
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["workout_id"], "workout123")
            workout_lambda.ROUTE_MAP[
                "GET /athletes/{athlete_id}/days/{day_id}/workout"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP[
                "GET /athletes/{athlete_id}/days/{day_id}/workout"
            ] = original_func

    def test_update_workout_route(self):
        """Test successful routing to update_workout function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP["PUT /workouts/{workout_id}"]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "workout_id": "workout123",
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                    "notes": "Updated notes",  # Added notes
                    "status": "partial",  # Changed from completed to partial
                }
            ),
        }
        workout_lambda.ROUTE_MAP["PUT /workouts/{workout_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "PUT",
                "resource": "/workouts/{workout_id}",
                "pathParameters": {"workout_id": "workout123"},
                "body": json.dumps({"notes": "Updated notes", "status": "partial"}),
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["notes"], "Updated notes")
            self.assertEqual(response_body["status"], "partial")
            workout_lambda.ROUTE_MAP[
                "PUT /workouts/{workout_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP["PUT /workouts/{workout_id}"] = original_func

    def test_delete_workout_route(self):
        """Test successful routing to delete_workout function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP["DELETE /workouts/{workout_id}"]

        # Replace with our mock
        mock_response = {"statusCode": 204, "body": json.dumps({})}
        workout_lambda.ROUTE_MAP["DELETE /workouts/{workout_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "DELETE",
                "resource": "/workouts/{workout_id}",
                "pathParameters": {"workout_id": "workout123"},
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 204)
            workout_lambda.ROUTE_MAP[
                "DELETE /workouts/{workout_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP["DELETE /workouts/{workout_id}"] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "PATCH",  # Not defined in the ROUTE_MAP
            "resource": "/workouts/{workout_id}",
        }
        context = {}

        # Call the Lambda handler
        response = workout_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = workout_lambda.ROUTE_MAP["GET /workouts/{workout_id}"]

        # Replace with our mock that raises an exception
        workout_lambda.ROUTE_MAP["GET /workouts/{workout_id}"] = MagicMock(
            side_effect=Exception("Test exception")
        )

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/workouts/{workout_id}",
                "pathParameters": {"workout_id": "workout123"},
            }
            context = {}

            # Call the Lambda handler
            response = workout_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            workout_lambda.ROUTE_MAP[
                "GET /workouts/{workout_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            workout_lambda.ROUTE_MAP["GET /workouts/{workout_id}"] = original_func


if __name__ == "__main__":
    unittest.main()
