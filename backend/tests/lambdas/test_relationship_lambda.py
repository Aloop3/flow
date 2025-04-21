import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.relationship_lambda import relationship_lambda


class TestRelationshipLambda(BaseTest):
    """Test suite for the Relationship Lambda handler"""

    def test_create_relationship_route(self):
        """Test successful routing to create_relationship function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = relationship_lambda.ROUTE_MAP["POST /relationships"]

        # Replace with our mock
        mock_response = {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "relationship_id": "rel123",
                    "coach_id": "coach456",
                    "athlete_id": "athlete789",
                    "status": "pending",
                    "created_at": "2025-03-13T12:00:00",
                }
            ),
        }
        relationship_lambda.ROUTE_MAP["POST /relationships"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/relationships",
                "body": json.dumps(
                    {"coach_id": "coach456", "athlete_id": "athlete789"}
                ),
            }
            context = {}

            # Call the Lambda handler
            response = relationship_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 201)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["relationship_id"], "rel123")
            self.assertEqual(response_body["coach_id"], "coach456")
            self.assertEqual(response_body["status"], "pending")
            relationship_lambda.ROUTE_MAP[
                "POST /relationships"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            relationship_lambda.ROUTE_MAP["POST /relationships"] = original_func

    def test_accept_relationship_route(self):
        """Test successful routing to accept_relationship function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = relationship_lambda.ROUTE_MAP[
            "POST /relationships/{relationship_id}/accept"
        ]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "relationship_id": "rel123",
                    "coach_id": "coach456",
                    "athlete_id": "athlete789",
                    "status": "active",  # Changed from pending to active
                    "created_at": "2025-03-13T12:00:00",
                }
            ),
        }
        relationship_lambda.ROUTE_MAP[
            "POST /relationships/{relationship_id}/accept"
        ] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/relationships/{relationship_id}/accept",
                "pathParameters": {"relationship_id": "rel123"},
            }
            context = {}

            # Call the Lambda handler
            response = relationship_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["status"], "active")
            relationship_lambda.ROUTE_MAP[
                "POST /relationships/{relationship_id}/accept"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            relationship_lambda.ROUTE_MAP[
                "POST /relationships/{relationship_id}/accept"
            ] = original_func

    def test_end_relationship_route(self):
        """Test successful routing to end_relationship function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = relationship_lambda.ROUTE_MAP[
            "POST /relationships/{relationship_id}/end"
        ]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "relationship_id": "rel123",
                    "coach_id": "coach456",
                    "athlete_id": "athlete789",
                    "status": "ended",  # Changed from active to ended
                    "created_at": "2025-03-13T12:00:00",
                }
            ),
        }
        relationship_lambda.ROUTE_MAP[
            "POST /relationships/{relationship_id}/end"
        ] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "POST",
                "resource": "/relationships/{relationship_id}/end",
                "pathParameters": {"relationship_id": "rel123"},
            }
            context = {}

            # Call the Lambda handler
            response = relationship_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["status"], "ended")
            relationship_lambda.ROUTE_MAP[
                "POST /relationships/{relationship_id}/end"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            relationship_lambda.ROUTE_MAP[
                "POST /relationships/{relationship_id}/end"
            ] = original_func

    def test_get_relationships_for_coach_route(self):
        """Test successful routing to get_relationships_for_coach function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = relationship_lambda.ROUTE_MAP[
            "GET /coaches/{coach_id}/relationships"
        ]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                [
                    {
                        "relationship_id": "rel1",
                        "coach_id": "coach456",
                        "athlete_id": "athlete1",
                        "status": "active",
                    },
                    {
                        "relationship_id": "rel2",
                        "coach_id": "coach456",
                        "athlete_id": "athlete2",
                        "status": "pending",
                    },
                ]
            ),
        }
        relationship_lambda.ROUTE_MAP[
            "GET /coaches/{coach_id}/relationships"
        ] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/coaches/{coach_id}/relationships",
                "pathParameters": {"coach_id": "coach456"},
                "queryStringParameters": {"status": "active"},
            }
            context = {}

            # Call the Lambda handler
            response = relationship_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["relationship_id"], "rel1")
            relationship_lambda.ROUTE_MAP[
                "GET /coaches/{coach_id}/relationships"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            relationship_lambda.ROUTE_MAP[
                "GET /coaches/{coach_id}/relationships"
            ] = original_func

    def test_get_relationship_route(self):
        """Test successful routing to get_relationship function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = relationship_lambda.ROUTE_MAP[
            "GET /relationships/{relationship_id}"
        ]

        # Replace with our mock
        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "relationship_id": "rel123",
                    "coach_id": "coach456",
                    "athlete_id": "athlete789",
                    "status": "active",
                    "created_at": "2025-03-13T12:00:00",
                }
            ),
        }
        relationship_lambda.ROUTE_MAP[
            "GET /relationships/{relationship_id}"
        ] = MagicMock(return_value=mock_response)

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/relationships/{relationship_id}",
                "pathParameters": {"relationship_id": "rel123"},
            }
            context = {}

            # Call the Lambda handler
            response = relationship_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["relationship_id"], "rel123")
            relationship_lambda.ROUTE_MAP[
                "GET /relationships/{relationship_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            relationship_lambda.ROUTE_MAP[
                "GET /relationships/{relationship_id}"
            ] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        # Setup
        event = {
            "httpMethod": "DELETE",  # Not defined in the ROUTE_MAP
            "resource": "/relationships/{relationship_id}",
        }
        context = {}

        # Call the Lambda handler
        response = relationship_lambda.handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_handler_exception(self):
        """Test exception handling in the Lambda handler"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = relationship_lambda.ROUTE_MAP[
            "GET /relationships/{relationship_id}"
        ]

        # Replace with our mock that raises an exception
        relationship_lambda.ROUTE_MAP[
            "GET /relationships/{relationship_id}"
        ] = MagicMock(side_effect=Exception("Test exception"))

        try:
            event = {
                "httpMethod": "GET",
                "resource": "/relationships/{relationship_id}",
                "pathParameters": {"relationship_id": "rel123"},
            }
            context = {}

            # Call the Lambda handler
            response = relationship_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            relationship_lambda.ROUTE_MAP[
                "GET /relationships/{relationship_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            relationship_lambda.ROUTE_MAP[
                "GET /relationships/{relationship_id}"
            ] = original_func


if __name__ == "__main__":
    unittest.main()
