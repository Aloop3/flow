import unittest
from unittest.mock import MagicMock, patch
import json
from src.api.analytics_api import (
    get_max_weight_history,
    get_volume_calculation,
    get_exercise_frequency,
    get_block_analysis,
    get_block_comparison,
    get_all_time_1rm,
    validate_athlete_access,
    validate_date_format,
)


class TestAnalyticsAPI(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies with mocked services"""
        # Patch uuid for consistent test IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value=MagicMock(hex="test-uuid"))
        self.mock_uuid = self.uuid_patcher.start()

        # Mock services
        self.mock_analytics_service = MagicMock()
        self.mock_user_service = MagicMock()
        self.mock_relationship_service = MagicMock()
        self.mock_block_service = MagicMock()

        # Patch service imports
        self.analytics_service_patcher = patch(
            "src.api.analytics_api.analytics_service", self.mock_analytics_service
        )
        self.user_service_patcher = patch(
            "src.api.analytics_api.user_service", self.mock_user_service
        )

        self.analytics_service_patcher.start()
        self.user_service_patcher.start()

        # Mock event structure
        self.base_event = {
            "pathParameters": {"athlete_id": "test-athlete-id"},
            "queryStringParameters": {},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }

        self.context = MagicMock()

    def tearDown(self):
        """Clean up patches"""
        self.uuid_patcher.stop()
        self.analytics_service_patcher.stop()
        self.user_service_patcher.stop()

    def test_validate_date_format_valid_dates(self):
        """Test validate_date_format with valid date strings"""
        valid_dates = ["2024-01-01", "2023-12-31", "2024-02-29"]

        for date_str in valid_dates:
            with self.subTest(date=date_str):
                result = validate_date_format(date_str)
                self.assertTrue(result, f"Should validate {date_str} as valid")

    def test_validate_date_format_invalid_dates(self):
        """Test validate_date_format with invalid date strings"""
        invalid_dates = [
            "2024-13-01",
            "2024-01-32",
            "24-01-01",
            "2024/01/01",
            "invalid",
        ]

        for date_str in invalid_dates:
            with self.subTest(date=date_str):
                result = validate_date_format(date_str)
                self.assertFalse(result, f"Should validate {date_str} as invalid")

    @patch("src.api.analytics_api.RelationshipService")
    def test_validate_athlete_access_same_user(self, mock_relationship_service_class):
        """Test validate_athlete_access when user accesses their own data"""
        user_id = "test-user-id"
        athlete_id = "test-user-id"

        result = validate_athlete_access(user_id, athlete_id)

        self.assertTrue(result, "User should have access to their own data")
        # Should not check relationships when accessing own data
        mock_relationship_service_class.assert_not_called()

    @patch("src.services.relationship_service.RelationshipService")
    def test_validate_athlete_access_coach_relationship_active(
        self, mock_relationship_service_class
    ):
        """Test validate_athlete_access when coach has active relationship with athlete"""
        user_id = "coach-id"
        athlete_id = "athlete-id"

        mock_service = MagicMock()
        mock_relationship_service_class.return_value = mock_service

        # Mock active relationship
        mock_relationship = MagicMock()
        mock_relationship.status = "active"
        mock_service.get_active_relationship.return_value = mock_relationship

        # Import here to ensure patch is applied
        from src.api.analytics_api import validate_athlete_access

        result = validate_athlete_access(user_id, athlete_id)

        self.assertTrue(
            result, "Coach should have access to athlete data with active relationship"
        )
        mock_service.get_active_relationship.assert_called_once_with(
            coach_id=user_id, athlete_id=athlete_id
        )

    @patch("src.api.analytics_api.RelationshipService")
    def test_validate_athlete_access_coach_relationship_pending(
        self, mock_relationship_service_class
    ):
        """Test validate_athlete_access when coach has pending relationship with athlete"""
        user_id = "coach-id"
        athlete_id = "athlete-id"

        mock_service = MagicMock()
        mock_relationship_service_class.return_value = mock_service

        # Mock pending relationship
        mock_relationship = MagicMock()
        mock_relationship.status = "pending"
        mock_service.get_active_relationship.return_value = mock_relationship

        result = validate_athlete_access(user_id, athlete_id)

        self.assertFalse(
            result, "Coach should NOT have access with pending relationship"
        )

    @patch("src.api.analytics_api.logger")
    @patch("src.api.analytics_api.RelationshipService")
    def test_validate_athlete_access_logs_with_user_details(
        self, mock_relationship_service_class, mock_logger
    ):
        """Test validate_athlete_access logs with specific user and athlete IDs on error"""
        user_id = "coach-id"
        athlete_id = "athlete-id"

        mock_service = MagicMock()
        mock_relationship_service_class.return_value = mock_service
        mock_service.get_active_relationship.side_effect = Exception("Database error")

        result = validate_athlete_access(user_id, athlete_id)

        self.assertFalse(result, "Should deny access on exception")

        # Verify specific logging with user/athlete IDs
        mock_logger.warning.assert_called_once()
        logged_message = mock_logger.warning.call_args[0][0]
        self.assertIn("coach-id", logged_message)
        self.assertIn("athlete-id", logged_message)
        self.assertIn("Error validating athlete access", logged_message)

    @patch("src.api.analytics_api.RelationshipService")
    def test_validate_athlete_access_no_relationship(
        self, mock_relationship_service_class
    ):
        """Test validate_athlete_access when no relationship exists"""
        user_id = "coach-id"
        athlete_id = "athlete-id"

        mock_service = MagicMock()
        mock_relationship_service_class.return_value = mock_service
        mock_service.get_active_relationship.return_value = None  # No relationship

        result = validate_athlete_access(user_id, athlete_id)

        self.assertFalse(result, "Should deny access when no relationship exists")

    def test_get_max_weight_history_success(self):
        """Test successful max weight history retrieval"""
        # Setup event with required parameters
        event = self.base_event.copy()
        event["queryStringParameters"] = {"exercise_type": "squat"}

        # Mock analytics service response
        mock_data = [
            {"date": "2024-01-01", "max_weight": 100},
            {"date": "2024-01-02", "max_weight": 105},
        ]
        self.mock_analytics_service.get_max_weight_history.return_value = mock_data

        # Mock athlete access validation
        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        # Verify response
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["athlete_id"], "test-athlete-id")
        self.assertEqual(response_body["exercise_type"], "squat")
        self.assertEqual(response_body["data"], mock_data)

        # Verify service called correctly
        self.mock_analytics_service.get_max_weight_history.assert_called_once_with(
            "test-athlete-id", "squat"
        )

    def test_get_block_comparison_missing_parameters(self):
        """Test block comparison with missing required parameters"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"block_id1": "block-1"}  # Missing block_id2

        response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn(
            "Both block_id1 and block_id2 query parameters are required",
            response_body["error"],
        )

    def test_get_block_comparison_same_blocks(self):
        """Test block comparison with same block IDs"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "same-block",
            "block_id2": "same-block",
        }

        response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Cannot compare a block with itself", response_body["error"])

    @patch("src.services.block_service.BlockService")
    def test_get_block_comparison_first_block_not_found(self, mock_block_service_class):
        """Test block comparison when first block doesn't exist"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "nonexistent-block",
            "block_id2": "block-2",
        }

        mock_block_service = MagicMock()
        mock_block_service_class.return_value = mock_block_service
        mock_block_service.get_block.side_effect = [
            None,
            MagicMock(),
        ]  # First block not found

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block nonexistent-block not found", response_body["error"])

    @patch("src.services.block_service.BlockService")
    def test_get_block_comparison_blocks_different_athletes(
        self, mock_block_service_class
    ):
        """Test block comparison when blocks belong to different athletes"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "block-1",
            "block_id2": "block-2",
        }

        mock_block_service = MagicMock()
        mock_block_service_class.return_value = mock_block_service

        mock_block1 = MagicMock()
        mock_block1.athlete_id = "test-athlete-id"
        mock_block2 = MagicMock()
        mock_block2.athlete_id = "different-athlete-id"  # Different athlete

        mock_block_service.get_block.side_effect = [mock_block1, mock_block2]

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertIn(
            "Block block-2 does not belong to specified athlete", response_body["error"]
        )

    def test_get_max_weight_history_service_exception(self):
        """Test max weight history when analytics service raises exception"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"exercise_type": "squat"}

        self.mock_analytics_service.get_max_weight_history.side_effect = Exception(
            "Service error"
        )

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Internal server error", response_body["error"])

    def test_get_volume_calculation_default_time_period(self):
        """Test volume calculation with default time period"""
        event = self.base_event.copy()
        # No time_period specified, should default to "month"

        self.mock_analytics_service.calculate_volume.return_value = []

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_volume_calculation(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        self.mock_analytics_service.calculate_volume.assert_called_once_with(
            "test-athlete-id", "month"  # Default value
        )

    def test_get_exercise_frequency_default_time_period(self):
        """Test exercise frequency with default time period"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"exercise_type": "squat"}
        # No time_period specified, should default to "month"

        mock_data = {
            "exercise_type": "squat",
            "time_period": "month",
            "frequency_per_week": 2.5,
        }
        self.mock_analytics_service.get_exercise_frequency.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_exercise_frequency(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        self.mock_analytics_service.get_exercise_frequency.assert_called_once_with(
            "test-athlete-id", "squat", "month"  # Default value
        )

    def test_get_max_weight_history_invalid_date_format(self):
        """Test max weight history with invalid date format"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "exercise_type": "squat",
            "start_date": "invalid-date",
        }

        response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("start_date must be in YYYY-MM-DD format", response_body["error"])

    def test_get_max_weight_history_unauthorized_access(self):
        """Test max weight history with unauthorized access"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"exercise_type": "squat"}

        with patch("src.api.analytics_api.validate_athlete_access", return_value=False):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertIn("Unauthorized access", response_body["error"])

    def test_get_max_weight_history_with_date_filtering(self):
        """Test max weight history with date range filtering"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "exercise_type": "squat",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        }

        # Mock service returning data outside date range
        mock_data = [
            {"date": "2023-12-31", "max_weight": 90},  # Before start_date
            {"date": "2024-01-15", "max_weight": 100},  # Within range
            {"date": "2024-02-01", "max_weight": 110},  # After end_date
        ]
        self.mock_analytics_service.get_max_weight_history.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should only include data within date range
        filtered_data = response_body["data"]
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data[0]["date"], "2024-01-15")

    def test_get_volume_calculation_success(self):
        """Test successful volume calculation retrieval"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"time_period": "month"}

        mock_data = [
            {"date": "2024-01-01", "volume": 5000},
            {"date": "2024-01-02", "volume": 5500},
        ]
        self.mock_analytics_service.calculate_volume.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_volume_calculation(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["time_period"], "month")
        self.assertEqual(response_body["data"], mock_data)

        self.mock_analytics_service.calculate_volume.assert_called_once_with(
            "test-athlete-id", "month"
        )

    def test_get_volume_calculation_invalid_time_period(self):
        """Test volume calculation with invalid time period"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"time_period": "invalid"}

        response = get_volume_calculation(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("time_period must be one of", response_body["error"])

    def test_get_exercise_frequency_success(self):
        """Test successful exercise frequency retrieval"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "exercise_type": "squat",
            "time_period": "month",
        }

        mock_data = {
            "exercise_type": "squat",
            "time_period": "month",
            "training_days": 12,
            "total_sets": 36,
            "frequency_per_week": 3.0,
        }
        self.mock_analytics_service.get_exercise_frequency.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_exercise_frequency(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body, mock_data)

        self.mock_analytics_service.get_exercise_frequency.assert_called_once_with(
            "test-athlete-id", "squat", "month"
        )

    def test_get_exercise_frequency_missing_exercise_type(self):
        """Test exercise frequency with missing exercise_type"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"time_period": "month"}

        response = get_exercise_frequency(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn(
            "exercise_type query parameter is required", response_body["error"]
        )

    @patch("src.services.block_service.BlockService")
    def test_get_block_analysis_success(self, mock_block_service_class):
        """Test successful block analysis retrieval"""
        event = self.base_event.copy()
        event["pathParameters"]["block_id"] = "test-block-id"

        # Mock block service
        mock_block_service = MagicMock()
        mock_block_service_class.return_value = mock_block_service

        mock_block = MagicMock()
        mock_block.athlete_id = "test-athlete-id"
        mock_block_service.get_block.return_value = mock_block

        # Mock analytics service
        mock_analysis = {
            "block_id": "test-block-id",
            "total_volume": 15000,
            "weekly_volumes": {"week1": {"volume": 5000}},
        }
        self.mock_analytics_service.calculate_block_volume.return_value = mock_analysis

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_block_analysis(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body, mock_analysis)

    @patch("src.services.block_service.BlockService")
    def test_get_block_analysis_block_not_found(self, mock_block_service_class):
        """Test block analysis with non-existent block"""
        event = self.base_event.copy()
        event["pathParameters"]["block_id"] = "nonexistent-block"

        mock_block_service = MagicMock()
        mock_block_service_class.return_value = mock_block_service
        mock_block_service.get_block.return_value = None

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_block_analysis(event, self.context)

        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block not found", response_body["error"])

    @patch("src.services.block_service.BlockService")
    def test_get_block_analysis_wrong_athlete(self, mock_block_service_class):
        """Test block analysis when block belongs to different athlete"""
        event = self.base_event.copy()
        event["pathParameters"]["block_id"] = "test-block-id"

        mock_block_service = MagicMock()
        mock_block_service_class.return_value = mock_block_service

        mock_block = MagicMock()
        mock_block.athlete_id = "different-athlete-id"  # Different athlete
        mock_block_service.get_block.return_value = mock_block

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_block_analysis(event, self.context)

        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertIn(
            "Block does not belong to specified athlete", response_body["error"]
        )

    @patch("src.services.block_service.BlockService")
    def test_analytics_service_error_response(self, mock_block_service_class):
        """Test handling of analytics service error responses"""
        event = self.base_event.copy()
        event["pathParameters"]["block_id"] = "test-block-id"

        # Mock block service to return valid block
        mock_block_service = MagicMock()
        mock_block_service_class.return_value = mock_block_service

        mock_block = MagicMock()
        mock_block.athlete_id = "test-athlete-id"
        mock_block_service.get_block.return_value = mock_block

        # Mock analytics service to return error
        error_response = {"error": "Failed to calculate block volume"}
        self.mock_analytics_service.calculate_block_volume.return_value = error_response

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_block_analysis(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body, error_response)

        # Verify the services were called correctly
        mock_block_service.get_block.assert_called_once_with("test-block-id")
        self.mock_analytics_service.calculate_block_volume.assert_called_once_with(
            "test-block-id"
        )

    def test_null_query_parameters(self):
        """Test handling of null queryStringParameters"""
        event = self.base_event.copy()
        event["queryStringParameters"] = None  # API Gateway can send null

        response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn(
            "exercise_type query parameter is required", response_body["error"]
        )

    @patch("src.api.analytics_api.logger")
    def test_error_logging(self, mock_logger):
        """Test that errors are properly logged"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"exercise_type": "squat"}

        test_exception = Exception("Test exception")
        self.mock_analytics_service.get_max_weight_history.side_effect = test_exception

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 500)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        logged_message = mock_logger.error.call_args[0][0]
        self.assertIn("Error getting max weight history", logged_message)

    def test_max_weight_history_with_date_filtering_edge_cases(self):
        """Test max weight history date filtering with edge cases"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "exercise_type": "squat",
            "start_date": "2024-01-15",
            "end_date": "2024-01-15",  # Same start and end date
        }

        # Mock service returning data with various dates
        mock_data = [
            {"date": "2024-01-14", "max_weight": 100},  # Before range
            {"date": "2024-01-15", "max_weight": 105},  # Exact match
            {"date": "2024-01-16", "max_weight": 110},  # After range
        ]
        self.mock_analytics_service.get_max_weight_history.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should only include exact date match
        self.assertEqual(len(response_body["data"]), 1)
        self.assertEqual(response_body["data"][0]["date"], "2024-01-15")

    def test_max_weight_history_data_without_date(self):
        """Test max weight history with data points missing date field"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "exercise_type": "squat",
            "start_date": "2024-01-01",
        }

        # Mock service returning data with missing date
        mock_data = [
            {"date": "2024-01-15", "max_weight": 105},
            {"max_weight": 110},  # Missing date field
            {"date": None, "max_weight": 120},  # Null date
        ]
        self.mock_analytics_service.get_max_weight_history.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should only include data with valid dates
        self.assertEqual(len(response_body["data"]), 1)
        self.assertEqual(response_body["data"][0]["date"], "2024-01-15")

    def test_volume_calculation_with_date_filtering(self):
        """Test volume calculation with date filtering"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "time_period": "week",
            "start_date": "2024-01-10",
            "end_date": "2024-01-20",
        }

        # Mock service returning data outside range
        mock_data = [
            {"date": "2024-01-05", "volume": 1000},  # Before range
            {"date": "2024-01-15", "volume": 1500},  # In range
            {"date": "2024-01-25", "volume": 2000},  # After range
        ]
        self.mock_analytics_service.calculate_volume.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_volume_calculation(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should filter to date range
        self.assertEqual(len(response_body["data"]), 1)
        self.assertEqual(response_body["data"][0]["date"], "2024-01-15")

    def test_volume_calculation_data_without_date(self):
        """Test volume calculation with data points missing date field"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "time_period": "month",
            "end_date": "2024-01-31",
        }

        # Mock service returning data with missing dates
        mock_data = [
            {"date": "2024-01-15", "volume": 1500},
            {"volume": 2000},  # Missing date field
            {"date": None, "volume": 2500},  # Null date
        ]
        self.mock_analytics_service.calculate_volume.return_value = mock_data

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_volume_calculation(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should only include data with valid dates
        self.assertEqual(len(response_body["data"]), 1)

    def test_volume_calculation_invalid_time_period_edge_cases(self):
        """Test volume calculation with various invalid time periods"""
        invalid_periods = ["day", "quarter", "decade", "", None]

        for time_period in invalid_periods:
            with self.subTest(time_period=time_period):
                event = self.base_event.copy()
                event["queryStringParameters"] = {"time_period": time_period}

                response = get_volume_calculation(event, self.context)

                self.assertEqual(response["statusCode"], 400)
                response_body = json.loads(response["body"])
                self.assertIn("time_period must be one of", response_body["error"])

    def test_exercise_frequency_invalid_time_period_edge_cases(self):
        """Test exercise frequency with various invalid time periods"""
        invalid_periods = ["day", "quarter", "all", "", None]

        for time_period in invalid_periods:
            with self.subTest(time_period=time_period):
                event = self.base_event.copy()
                event["queryStringParameters"] = {
                    "exercise_type": "squat",
                    "time_period": time_period,
                }

                response = get_exercise_frequency(event, self.context)

                self.assertEqual(response["statusCode"], 400)
                response_body = json.loads(response["body"])
                self.assertIn("time_period must be one of", response_body["error"])

    def test_block_analysis_service_exception(self):
        """Test block analysis when analytics service raises exception"""
        event = self.base_event.copy()
        event["pathParameters"]["block_id"] = "test-block-id"

        with patch(
            "src.services.block_service.BlockService"
        ) as mock_block_service_class:
            mock_block_service = MagicMock()
            mock_block_service_class.return_value = mock_block_service

            mock_block = MagicMock()
            mock_block.athlete_id = "test-athlete-id"
            mock_block_service.get_block.return_value = mock_block

            # Mock analytics service to raise exception
            self.mock_analytics_service.calculate_block_volume.side_effect = Exception(
                "Database error"
            )

            with patch(
                "src.api.analytics_api.validate_athlete_access", return_value=True
            ):
                response = get_block_analysis(event, self.context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Internal server error", response_body["error"])

    def test_block_comparison_success_path(self):
        """Test successful block comparison to cover success path"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "block-1",
            "block_id2": "block-2",
        }

        with patch(
            "src.services.block_service.BlockService"
        ) as mock_block_service_class:
            mock_block_service = MagicMock()
            mock_block_service_class.return_value = mock_block_service

            # Mock both blocks belonging to same athlete
            mock_block1 = MagicMock()
            mock_block1.athlete_id = "test-athlete-id"
            mock_block2 = MagicMock()
            mock_block2.athlete_id = "test-athlete-id"

            mock_block_service.get_block.side_effect = [mock_block1, mock_block2]

            # Mock analytics service comparison
            mock_comparison = {
                "block1": {"id": "block-1", "total_volume": 10000},
                "block2": {"id": "block-2", "total_volume": 12000},
                "comparison": {"volume_difference": 2000},
            }
            self.mock_analytics_service.compare_blocks.return_value = mock_comparison

            with patch(
                "src.api.analytics_api.validate_athlete_access", return_value=True
            ):
                response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body, mock_comparison)

    def test_block_comparison_second_block_not_found(self):
        """Test block comparison when second block doesn't exist"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "block-1",
            "block_id2": "nonexistent-block",
        }

        with patch(
            "src.services.block_service.BlockService"
        ) as mock_block_service_class:
            mock_block_service = MagicMock()
            mock_block_service_class.return_value = mock_block_service

            # First block exists, second doesn't
            mock_block1 = MagicMock()
            mock_block1.athlete_id = "test-athlete-id"
            mock_block_service.get_block.side_effect = [mock_block1, None]

            with patch(
                "src.api.analytics_api.validate_athlete_access", return_value=True
            ):
                response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block nonexistent-block not found", response_body["error"])

    def test_block_comparison_first_block_wrong_athlete(self):
        """Test block comparison when first block belongs to different athlete"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "block-1",
            "block_id2": "block-2",
        }

        with patch(
            "src.services.block_service.BlockService"
        ) as mock_block_service_class:
            mock_block_service = MagicMock()
            mock_block_service_class.return_value = mock_block_service

            # First block belongs to different athlete
            mock_block1 = MagicMock()
            mock_block1.athlete_id = "different-athlete-id"
            mock_block2 = MagicMock()
            mock_block2.athlete_id = "test-athlete-id"

            mock_block_service.get_block.side_effect = [mock_block1, mock_block2]

            with patch(
                "src.api.analytics_api.validate_athlete_access", return_value=True
            ):
                response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertIn(
            "Block block-1 does not belong to specified athlete", response_body["error"]
        )

    def test_block_comparison_analytics_service_error(self):
        """Test block comparison when analytics service returns error"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "block-1",
            "block_id2": "block-2",
        }

        with patch(
            "src.services.block_service.BlockService"
        ) as mock_block_service_class:
            mock_block_service = MagicMock()
            mock_block_service_class.return_value = mock_block_service

            # Both blocks valid
            mock_block1 = MagicMock()
            mock_block1.athlete_id = "test-athlete-id"
            mock_block2 = MagicMock()
            mock_block2.athlete_id = "test-athlete-id"

            mock_block_service.get_block.side_effect = [mock_block1, mock_block2]

            # Analytics service returns error
            error_response = {"error": "Failed to compare blocks"}
            self.mock_analytics_service.compare_blocks.return_value = error_response

            with patch(
                "src.api.analytics_api.validate_athlete_access", return_value=True
            ):
                response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body, error_response)

    def test_block_comparison_analytics_service_exception(self):
        """Test block comparison when analytics service raises exception"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "block_id1": "block-1",
            "block_id2": "block-2",
        }

        with patch(
            "src.services.block_service.BlockService"
        ) as mock_block_service_class:
            mock_block_service = MagicMock()
            mock_block_service_class.return_value = mock_block_service

            # Both blocks valid
            mock_block1 = MagicMock()
            mock_block1.athlete_id = "test-athlete-id"
            mock_block2 = MagicMock()
            mock_block2.athlete_id = "test-athlete-id"

            mock_block_service.get_block.side_effect = [mock_block1, mock_block2]

            # Analytics service raises exception
            self.mock_analytics_service.compare_blocks.side_effect = Exception(
                "Service error"
            )

            with patch(
                "src.api.analytics_api.validate_athlete_access", return_value=True
            ):
                response = get_block_comparison(event, self.context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Internal server error", response_body["error"])

    def test_exercise_frequency_service_exception(self):
        """Test exercise frequency when analytics service raises exception"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {
            "exercise_type": "squat",
            "time_period": "month",
        }

        # Mock analytics service to raise exception
        self.mock_analytics_service.get_exercise_frequency.side_effect = Exception(
            "Service error"
        )

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_exercise_frequency(event, self.context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Internal server error", response_body["error"])

    def test_volume_calculation_service_exception(self):
        """Test volume calculation when analytics service raises exception"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"time_period": "month"}

        # Mock analytics service to raise exception
        self.mock_analytics_service.calculate_volume.side_effect = Exception(
            "Service error"
        )

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_volume_calculation(event, self.context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Internal server error", response_body["error"])

    def test_max_weight_history_service_exception_detailed(self):
        """Test max weight history with detailed exception handling"""
        event = self.base_event.copy()
        event["queryStringParameters"] = {"exercise_type": "squat"}

        # Mock analytics service to raise specific exception
        self.mock_analytics_service.get_max_weight_history.side_effect = ValueError(
            "Invalid exercise type"
        )

        with patch("src.api.analytics_api.validate_athlete_access", return_value=True):
            response = get_max_weight_history(event, self.context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Internal server error", response_body["error"])

    @patch("src.services.relationship_service.RelationshipService")
    def test_validate_athlete_access_service_exception_details(
        self, mock_relationship_service_class
    ):
        """Test validate_athlete_access with detailed exception logging"""
        user_id = "coach-id"
        athlete_id = "athlete-id"

        mock_service = MagicMock()
        mock_relationship_service_class.return_value = mock_service
        mock_service.get_active_relationship.side_effect = ConnectionError(
            "Database connection failed"
        )

        with patch("src.api.analytics_api.logger") as mock_logger:
            result = validate_athlete_access(user_id, athlete_id)

        self.assertFalse(result, "Should deny access on service exception")

        # Verify detailed logging
        mock_logger.warning.assert_called_once()
        logged_message = mock_logger.warning.call_args[0][0]
        self.assertIn("coach-id", logged_message)
        self.assertIn("athlete-id", logged_message)
        self.assertIn("Database connection failed", logged_message)

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_success(self, mock_validate_access):
        """Test get_all_time_1rm with valid request and successful response"""
        # Setup
        mock_validate_access.return_value = True
        self.mock_analytics_service.get_all_time_max_weight.return_value = 150.0

        event = {
            **self.base_event,
            "queryStringParameters": {"exercise_type": "deadlift"},
        }

        # Execute
        response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 200)

        response_body = json.loads(response["body"])
        expected_body = {
            "athlete_id": "test-athlete-id",
            "exercise_type": "deadlift",
            "all_time_max_weight": 150.0,
        }
        self.assertEqual(response_body, expected_body)

        # Verify service calls
        mock_validate_access.assert_called_once_with("test-user-id", "test-athlete-id")
        self.mock_analytics_service.get_all_time_max_weight.assert_called_once_with(
            "test-athlete-id", "deadlift"
        )

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_missing_exercise_type(self, mock_validate_access):
        """Test get_all_time_1rm returns 400 when exercise_type parameter is missing"""
        # Setup - no exercise_type in query parameters
        event = {**self.base_event, "queryStringParameters": {}}

        # Execute
        response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 400)

        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["error"], "exercise_type query parameter is required"
        )

        # Should not validate access or call service
        mock_validate_access.assert_not_called()
        self.mock_analytics_service.get_all_time_max_weight.assert_not_called()

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_null_query_parameters(self, mock_validate_access):
        """Test get_all_time_1rm handles null queryStringParameters gracefully"""
        # Setup - null query parameters (API Gateway behavior)
        event = {**self.base_event, "queryStringParameters": None}

        # Execute
        response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 400)

        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["error"], "exercise_type query parameter is required"
        )

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_invalid_exercise_type(self, mock_validate_access):
        """Test get_all_time_1rm returns 400 for invalid exercise types"""
        # Split empty string test from invalid exercise types
        invalid_exercise_types = ["bicep curl", "tricep extension", "invalid_exercise"]

        for exercise_type in invalid_exercise_types:
            with self.subTest(exercise_type=exercise_type):
                event = {
                    **self.base_event,
                    "queryStringParameters": {"exercise_type": exercise_type},
                }

                # Execute
                response = get_all_time_1rm(event, self.context)

                # Verify
                self.assertEqual(response["statusCode"], 400)

                response_body = json.loads(response["body"])
                self.assertIn("exercise_type must be one of", response_body["error"])
                self.assertIn("deadlift", response_body["error"])
                self.assertIn("squat", response_body["error"])
                self.assertIn("bench press", response_body["error"])

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_valid_exercise_types_case_insensitive(
        self, mock_validate_access
    ):
        """Test get_all_time_1rm accepts valid exercise types in different cases"""
        mock_validate_access.return_value = True
        self.mock_analytics_service.get_all_time_max_weight.return_value = 100.0

        valid_exercise_types = [
            ("deadlift", "deadlift"),
            ("DEADLIFT", "DEADLIFT"),
            ("Deadlift", "Deadlift"),
            ("squat", "squat"),
            ("SQUAT", "SQUAT"),
            ("bench press", "bench press"),
            ("BENCH PRESS", "BENCH PRESS"),
            ("Bench Press", "Bench Press"),
        ]

        for input_type, expected_type in valid_exercise_types:
            with self.subTest(exercise_type=input_type):
                event = {
                    **self.base_event,
                    "queryStringParameters": {"exercise_type": input_type},
                }

                # Execute
                response = get_all_time_1rm(event, self.context)

                # Verify success
                self.assertEqual(response["statusCode"], 200)

                response_body = json.loads(response["body"])
                self.assertEqual(response_body["exercise_type"], expected_type)

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_unauthorized_access(self, mock_validate_access):
        """Test get_all_time_1rm returns 403 when user lacks access to athlete data"""
        # Setup
        mock_validate_access.return_value = False

        event = {
            **self.base_event,
            "queryStringParameters": {"exercise_type": "deadlift"},
        }

        # Execute
        response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 403)

        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized access to athlete data")

        # Should validate access but not call service
        mock_validate_access.assert_called_once_with("test-user-id", "test-athlete-id")
        self.mock_analytics_service.get_all_time_max_weight.assert_not_called()

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_zero_weight_result(self, mock_validate_access):
        """Test get_all_time_1rm handles zero weight result (no data for exercise)"""
        # Setup
        mock_validate_access.return_value = True
        self.mock_analytics_service.get_all_time_max_weight.return_value = 0.0

        event = {**self.base_event, "queryStringParameters": {"exercise_type": "squat"}}

        # Execute
        response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 200)

        response_body = json.loads(response["body"])
        expected_body = {
            "athlete_id": "test-athlete-id",
            "exercise_type": "squat",
            "all_time_max_weight": 0.0,
        }
        self.assertEqual(response_body, expected_body)

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_service_exception(self, mock_validate_access):
        """Test get_all_time_1rm handles analytics service exceptions gracefully"""
        # Setup
        mock_validate_access.return_value = True
        self.mock_analytics_service.get_all_time_max_weight.side_effect = Exception(
            "Database connection failed"
        )

        event = {
            **self.base_event,
            "queryStringParameters": {"exercise_type": "bench press"},
        }

        # Execute
        with patch("src.api.analytics_api.logger") as mock_logger:
            response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 500)

        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Internal server error")

        # Verify error logging
        mock_logger.error.assert_called_once()
        log_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("Error getting all-time 1RM", log_call_args)

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_missing_path_parameters(self, mock_validate_access):
        """Test get_all_time_1rm handles missing athlete_id in path parameters"""
        # Setup - missing pathParameters (middleware converts KeyError to 500)
        event = {
            "queryStringParameters": {"exercise_type": "deadlift"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
            # pathParameters is missing entirely
        }

        # Execute
        with patch("src.api.analytics_api.logger") as mock_logger:
            response = get_all_time_1rm(event, self.context)

        # Verify - middleware catches KeyError and returns 500
        self.assertEqual(response["statusCode"], 500)

        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Internal server error")

        # Verify error logging occurred
        mock_logger.error.assert_called_once()
        log_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("Error getting all-time 1RM", log_call_args)

        # Should not validate access or call service due to early error
        mock_validate_access.assert_not_called()
        self.mock_analytics_service.get_all_time_max_weight.assert_not_called()

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_missing_athlete_id_in_path(self, mock_validate_access):
        """Test get_all_time_1rm handles missing athlete_id key in pathParameters"""
        # Setup - pathParameters exists but athlete_id key is missing
        event = {
            "pathParameters": {"some_other_param": "value"},  # athlete_id key missing
            "queryStringParameters": {"exercise_type": "deadlift"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }

        # Execute
        with patch("src.api.analytics_api.logger") as mock_logger:
            response = get_all_time_1rm(event, self.context)

        # Verify - middleware catches KeyError and returns 500
        self.assertEqual(response["statusCode"], 500)

        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Internal server error")

        # Verify error logging occurred
        mock_logger.error.assert_called_once()
        log_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("Error getting all-time 1RM", log_call_args)

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_empty_exercise_type(self, mock_validate_access):
        """Test get_all_time_1rm returns 400 for empty exercise_type"""
        # Empty string is treated as missing parameter
        event = {**self.base_event, "queryStringParameters": {"exercise_type": ""}}

        # Execute
        response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 400)

        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["error"], "exercise_type query parameter is required"
        )

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_different_athlete_ids(self, mock_validate_access):
        """Test get_all_time_1rm with different athlete IDs in path"""
        mock_validate_access.return_value = True
        self.mock_analytics_service.get_all_time_max_weight.return_value = 200.5

        test_athlete_ids = [
            "athlete-123",
            "44823433-b385-4359-8964-16a68b1b97c7",
            "different-uuid",
        ]

        for athlete_id in test_athlete_ids:
            with self.subTest(athlete_id=athlete_id):
                event = {
                    "pathParameters": {"athlete_id": athlete_id},
                    "queryStringParameters": {"exercise_type": "deadlift"},
                    "requestContext": {
                        "authorizer": {"claims": {"sub": "test-user-id"}}
                    },
                }

                # Execute
                response = get_all_time_1rm(event, self.context)

                # Verify
                self.assertEqual(response["statusCode"], 200)

                response_body = json.loads(response["body"])
                self.assertEqual(response_body["athlete_id"], athlete_id)
                self.assertEqual(response_body["all_time_max_weight"], 200.5)

                # Verify correct service call
                self.mock_analytics_service.get_all_time_max_weight.assert_called_with(
                    athlete_id, "deadlift"
                )

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_with_decimal_weights(self, mock_validate_access):
        """Test get_all_time_1rm handles decimal weight values correctly"""
        mock_validate_access.return_value = True

        decimal_weights = [102.5, 87.75, 150.25, 99.9]

        for weight in decimal_weights:
            with self.subTest(weight=weight):
                self.mock_analytics_service.get_all_time_max_weight.return_value = (
                    weight
                )

                event = {
                    **self.base_event,
                    "queryStringParameters": {"exercise_type": "deadlift"},
                }

                # Execute
                response = get_all_time_1rm(event, self.context)

                # Verify
                self.assertEqual(response["statusCode"], 200)

                response_body = json.loads(response["body"])
                self.assertEqual(response_body["all_time_max_weight"], weight)

    @patch("src.api.analytics_api.validate_athlete_access")
    def test_get_all_time_1rm_validate_access_exception(self, mock_validate_access):
        """Test get_all_time_1rm handles validate_athlete_access exceptions"""
        # Setup
        mock_validate_access.side_effect = Exception("Auth service unavailable")

        event = {**self.base_event, "queryStringParameters": {"exercise_type": "squat"}}

        # Execute
        with patch("src.api.analytics_api.logger") as mock_logger:
            response = get_all_time_1rm(event, self.context)

        # Verify
        self.assertEqual(response["statusCode"], 500)

        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Internal server error")

        # Should not call analytics service
        self.mock_analytics_service.get_all_time_max_weight.assert_not_called()


if __name__ == "__main__":
    unittest.main()
