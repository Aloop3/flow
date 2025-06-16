import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.lambdas.analytics_lambda import analytics_lambda


class TestAnalyticsLambda(BaseTest):
    """Test suite for the Analytics Lambda handler"""

    def setUp(self):
        """Set up test dependencies"""
        # Patch uuid for consistent test IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value=MagicMock(hex="test-uuid"))
        self.mock_uuid = self.uuid_patcher.start()

    def tearDown(self):
        """Clean up patches"""
        self.uuid_patcher.stop()

    def test_max_weight_history_route(self):
        """Test successful routing to max weight history function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = analytics_lambda.ROUTE_MAP[
            "GET /analytics/max-weight/{athlete_id}"
        ]

        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "athlete_id": "athlete123",
                    "exercise_type": "squat",
                    "data": [{"date": "2025-03-01", "max_weight": 225}],
                }
            ),
        }
        analytics_lambda.ROUTE_MAP[
            "GET /analytics/max-weight/{athlete_id}"
        ] = MagicMock(return_value=mock_response)

        try:
            event = self.create_api_gateway_event(
                method="GET",
                path="/analytics/max-weight/athlete123",
                path_parameters={"athlete_id": "athlete123"},
                query_parameters={"exercise_type": "squat"},
                auth_claims={"sub": "test-user-id"},
            )
            event[
                "resource"
            ] = "/analytics/max-weight/{athlete_id}"  # Manual addition required
            context = self.create_lambda_context()

            # Call the Lambda handler
            response = analytics_lambda.handler(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["athlete_id"], "athlete123")
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/max-weight/{athlete_id}"
            ].assert_called_once_with(event, context)
        finally:
            # Restore the original function
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/max-weight/{athlete_id}"
            ] = original_func

    def test_volume_calculation_route(self):
        """Test successful routing to volume calculation function"""
        # Setup - Mock the function in the ROUTE_MAP directly
        original_func = analytics_lambda.ROUTE_MAP["GET /analytics/volume/{athlete_id}"]

        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "athlete_id": "athlete123",
                    "time_period": "month",
                    "data": [{"date": "2025-03", "volume": 15000}],
                }
            ),
        }
        analytics_lambda.ROUTE_MAP["GET /analytics/volume/{athlete_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = self.create_api_gateway_event(
                method="GET",
                path="/analytics/volume/athlete123",
                path_parameters={"athlete_id": "athlete123"},
                query_parameters={"time_period": "month"},
                auth_claims={"sub": "test-user-id"},
            )
            event["resource"] = "/analytics/volume/{athlete_id}"
            context = self.create_lambda_context()

            response = analytics_lambda.handler(event, context)

            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["athlete_id"], "athlete123")
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/volume/{athlete_id}"
            ].assert_called_once_with(event, context)
        finally:
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/volume/{athlete_id}"
            ] = original_func

    def test_exercise_frequency_route(self):
        """Test successful routing to exercise frequency function"""
        original_func = analytics_lambda.ROUTE_MAP[
            "GET /analytics/frequency/{athlete_id}"
        ]

        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "athlete_id": "athlete123",
                    "exercise_type": "squat",
                    "frequency_per_week": 3,
                }
            ),
        }
        analytics_lambda.ROUTE_MAP["GET /analytics/frequency/{athlete_id}"] = MagicMock(
            return_value=mock_response
        )

        try:
            event = self.create_api_gateway_event(
                method="GET",
                path="/analytics/frequency/athlete123",
                path_parameters={"athlete_id": "athlete123"},
                query_parameters={"exercise_type": "squat", "time_period": "month"},
                auth_claims={"sub": "test-user-id"},
            )
            event["resource"] = "/analytics/frequency/{athlete_id}"
            context = self.create_lambda_context()

            response = analytics_lambda.handler(event, context)

            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["athlete_id"], "athlete123")
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/frequency/{athlete_id}"
            ].assert_called_once_with(event, context)
        finally:
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/frequency/{athlete_id}"
            ] = original_func

    def test_block_analysis_route(self):
        """Test successful routing to block analysis function"""
        original_func = analytics_lambda.ROUTE_MAP[
            "GET /analytics/block-analysis/{athlete_id}/{block_id}"
        ]

        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "athlete_id": "athlete123",
                    "block_id": "block456",
                    "total_volume": 45000,
                    "exercise_breakdown": {},
                }
            ),
        }
        analytics_lambda.ROUTE_MAP[
            "GET /analytics/block-analysis/{athlete_id}/{block_id}"
        ] = MagicMock(return_value=mock_response)

        try:
            event = self.create_api_gateway_event(
                method="GET",
                path="/analytics/block-analysis/athlete123/block456",
                path_parameters={"athlete_id": "athlete123", "block_id": "block456"},
                auth_claims={"sub": "test-user-id"},
            )
            event["resource"] = "/analytics/block-analysis/{athlete_id}/{block_id}"
            context = self.create_lambda_context()

            response = analytics_lambda.handler(event, context)

            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["athlete_id"], "athlete123")
            self.assertEqual(response_body["block_id"], "block456")
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/block-analysis/{athlete_id}/{block_id}"
            ].assert_called_once_with(event, context)
        finally:
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/block-analysis/{athlete_id}/{block_id}"
            ] = original_func

    def test_block_comparison_route(self):
        """Test successful routing to block comparison function"""
        original_func = analytics_lambda.ROUTE_MAP[
            "GET /analytics/block-comparison/{athlete_id}"
        ]

        mock_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "athlete_id": "athlete123",
                    "block1_id": "block456",
                    "block2_id": "block789",
                    "comparison": {"volume_change": "+15%"},
                }
            ),
        }
        analytics_lambda.ROUTE_MAP[
            "GET /analytics/block-comparison/{athlete_id}"
        ] = MagicMock(return_value=mock_response)

        try:
            event = self.create_api_gateway_event(
                method="GET",
                path="/analytics/block-comparison/athlete123",
                path_parameters={"athlete_id": "athlete123"},
                query_parameters={"block_id1": "block456", "block_id2": "block789"},
                auth_claims={"sub": "test-user-id"},
            )
            event["resource"] = "/analytics/block-comparison/{athlete_id}"
            context = self.create_lambda_context()

            response = analytics_lambda.handler(event, context)

            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["athlete_id"], "athlete123")
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/block-comparison/{athlete_id}"
            ].assert_called_once_with(event, context)
        finally:
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/block-comparison/{athlete_id}"
            ] = original_func

    def test_route_not_found(self):
        """Test handling of non-existent route"""
        event = self.create_api_gateway_event(
            method="GET", path="/analytics/invalid-endpoint"
        )
        event["resource"] = "/analytics/invalid-endpoint"
        context = self.create_lambda_context()

        response = analytics_lambda.handler(event, context)

        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_non_get_method_returns_404(self):
        """Test that non-GET methods return 404"""
        event = self.create_api_gateway_event(
            method="POST", path="/analytics/max-weight/athlete123"
        )
        event["resource"] = "/analytics/max-weight/{athlete_id}"
        context = self.create_lambda_context()

        response = analytics_lambda.handler(event, context)

        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Route not found", response_body["error"])

    def test_options_request_handling(self):
        """Test OPTIONS request handling for CORS"""
        event = self.create_api_gateway_event(
            method="OPTIONS", path="/analytics/max-weight/athlete123"
        )
        event["resource"] = "/analytics/max-weight/{athlete_id}"
        context = self.create_lambda_context()

        response = analytics_lambda.handler(event, context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "OK")

    def test_handler_exception_handling(self):
        """Test exception handling in the Lambda handler"""
        original_func = analytics_lambda.ROUTE_MAP[
            "GET /analytics/max-weight/{athlete_id}"
        ]

        # Replace with mock that raises an exception
        analytics_lambda.ROUTE_MAP[
            "GET /analytics/max-weight/{athlete_id}"
        ] = MagicMock(side_effect=Exception("Test exception"))

        try:
            event = self.create_api_gateway_event(
                method="GET",
                path="/analytics/max-weight/athlete123",
                path_parameters={"athlete_id": "athlete123"},
                query_parameters={"exercise_type": "squat"},
                auth_claims={"sub": "test-user-id"},
            )
            event["resource"] = "/analytics/max-weight/{athlete_id}"
            context = self.create_lambda_context()

            response = analytics_lambda.handler(event, context)

            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertIn("Internal server error", response_body["error"])
            self.assertIn("Test exception", response_body["error"])
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/max-weight/{athlete_id}"
            ].assert_called_once_with(event, context)
        finally:
            analytics_lambda.ROUTE_MAP[
                "GET /analytics/max-weight/{athlete_id}"
            ] = original_func

    def test_handler_logging(self):
        """Test handler logs incoming requests"""
        with patch(
            "src.lambdas.analytics_lambda.analytics_lambda.logger"
        ) as mock_logger:
            event = self.create_api_gateway_event(
                method="GET", path="/analytics/invalid-endpoint"
            )
            event["resource"] = "/analytics/invalid-endpoint"
            context = self.create_lambda_context()

            analytics_lambda.handler(event, context)

            # Verify request was logged
            mock_logger.info.assert_called()
            logged_message = mock_logger.info.call_args[0][0]
            self.assertIn(
                "Processing GET /analytics/invalid-endpoint request", logged_message
            )

    def test_handler_warning_for_invalid_route(self):
        """Test handler logs warning for invalid routes"""
        with patch(
            "src.lambdas.analytics_lambda.analytics_lambda.logger"
        ) as mock_logger:
            event = self.create_api_gateway_event(
                method="GET", path="/analytics/invalid-route"
            )
            event["resource"] = "/analytics/invalid-route"
            context = self.create_lambda_context()

            analytics_lambda.handler(event, context)

            # Verify warning was logged
            mock_logger.warning.assert_called()
            warning_message = mock_logger.warning.call_args[0][0]
            self.assertIn(
                "No route found for GET /analytics/invalid-route", warning_message
            )

    def test_handler_route_map_coverage(self):
        """Test that all routes in ROUTE_MAP are properly handled"""
        from src.lambdas.analytics_lambda.analytics_lambda import ROUTE_MAP

        expected_routes = [
            "GET /analytics/max-weight/{athlete_id}",
            "GET /analytics/volume/{athlete_id}",
            "GET /analytics/frequency/{athlete_id}",
            "GET /analytics/block-analysis/{athlete_id}/{block_id}",
            "GET /analytics/block-comparison/{athlete_id}",
        ]

        # Verify all expected routes are in ROUTE_MAP
        for route in expected_routes:
            self.assertIn(route, ROUTE_MAP, f"Route {route} missing from ROUTE_MAP")

        # Verify ROUTE_MAP only contains expected routes
        self.assertEqual(
            len(ROUTE_MAP), len(expected_routes), "ROUTE_MAP contains unexpected routes"
        )

    def test_handler_missing_http_method(self):
        """Test handler handles missing httpMethod gracefully"""
        event = self.create_api_gateway_event(
            method="GET", path="/analytics/max-weight/athlete123"
        )
        del event["httpMethod"]  # Remove httpMethod
        event["resource"] = "/analytics/max-weight/{athlete_id}"
        context = self.create_lambda_context()

        response = analytics_lambda.handler(event, context)

        # Should handle gracefully and return 404
        self.assertEqual(response["statusCode"], 404)

    def test_handler_missing_resource(self):
        """Test handler handles missing resource gracefully"""
        event = self.create_api_gateway_event(
            method="GET", path="/analytics/max-weight/athlete123"
        )
        # Note: create_api_gateway_event() doesn't include "resource" by default
        # So this event naturally has no "resource" field
        context = self.create_lambda_context()

        response = analytics_lambda.handler(event, context)

        # Should handle gracefully and return 404
        self.assertEqual(response["statusCode"], 404)

    def test_handler_route_case_sensitivity(self):
        """Test that route matching is case-sensitive"""
        event = self.create_api_gateway_event(
            method="GET", path="/Analytics/Max-Weight/athlete123"  # Different case
        )
        event["resource"] = "/Analytics/Max-Weight/{athlete_id}"
        context = self.create_lambda_context()

        response = analytics_lambda.handler(event, context)

        # Should return 404 for case mismatch
        self.assertEqual(response["statusCode"], 404)


if __name__ == "__main__":
    unittest.main()
