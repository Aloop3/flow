import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import week after the mocks are set up in BaseTest
with patch("boto3.resource"):
    from src.api import week_api


class TestWeekAPI(BaseTest):
    """
    Test suite for the Week API module
    """

    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_success(self, mock_create_week):
        """
        Test successful week creation
        """

        # Setup
        mock_week = MagicMock()
        mock_week.to_dict.return_value = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Test week",
        }
        mock_create_week.return_value = mock_week

        event = {
            "body": json.dumps(
                {"block_id": "block456", "week_number": 1, "notes": "Test week"}
            )
        }
        context = {}

        # Call API
        response = week_api.create_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["week_id"], "week123")
        self.assertEqual(response_body["block_id"], "block456")
        self.assertEqual(response_body["week_number"], 1)
        mock_create_week.assert_called_once_with(
            block_id="block456", week_number=1, notes="Test week"
        )

    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_missing_fields(self, mock_create_week):
        """
        Test week creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    # Missing block_id
                    "week_number": 1
                }
            )
        }
        context = {}

        # Call API
        response = week_api.create_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_week.assert_not_called()

    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_invalid_json(self, mock_create_week):
        """
        Test week creation with invalid JSON
        """
        event = {"body": "{invalid_json}"}
        context = {}

        # Call API
        response = week_api.create_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("error", json.loads(response["body"]))

    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_service_exception(self, mock_create_week):
        """
        Test exception handling in create_week
        """
        # Setup - make the service throw an exception
        mock_create_week.side_effect = Exception("Service error")

        event = {
            "body": json.dumps(
                {"block_id": "block456", "week_number": 1, "notes": "Test week"}
            )
        }
        context = {}

        # Call API directly with __wrapped__ to bypass middleware
        response = week_api.create_week.__wrapped__(event, context)

        # Assert that the exception was caught and a 500 response was returned
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Service error")

        # Verify that the service was called with the right parameters
        mock_create_week.assert_called_once_with(
            block_id="block456", week_number=1, notes="Test week"
        )

    @patch("src.services.week_service.WeekService.get_weeks_for_block")
    def test_get_weeks_for_block_success(self, mock_get_weeks):
        """
        Test successful retrieval of weeks for a block
        """

        # Setup
        mock_week1 = MagicMock()
        mock_week1.to_dict.return_value = {
            "week_id": "week1",
            "block_id": "block456",
            "week_number": 1,
        }
        mock_week2 = MagicMock()
        mock_week2.to_dict.return_value = {
            "week_id": "week2",
            "block_id": "block456",
            "week_number": 2,
        }
        mock_get_weeks.return_value = [mock_week1, mock_week2]

        event = {"pathParameters": {"block_id": "block456"}}
        context = {}

        # Call API
        response = week_api.get_weeks_for_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["week_id"], "week1")
        self.assertEqual(response_body[1]["week_id"], "week2")
        mock_get_weeks.assert_called_once_with("block456")

    @patch("src.services.week_service.WeekService.get_weeks_for_block")
    def test_get_weeks_for_block_no_path_param(self, mock_get_weeks):
        """
        Test get_weeks_for_block with missing path parameter
        """
        event = {}  # No pathParameters
        context = {}

        # Call API
        response = week_api.get_weeks_for_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))

    @patch("src.services.week_service.WeekService.update_week")
    def test_update_week_success(self, mock_update_week):
        """
        Test successful week update
        """

        # Setup
        mock_week = MagicMock()
        mock_week.to_dict.return_value = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Updated notes",
        }
        mock_update_week.return_value = mock_week

        event = {
            "pathParameters": {"week_id": "week123"},
            "body": json.dumps({"notes": "Updated notes"}),
        }
        context = {}

        # Call API
        response = week_api.update_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["week_id"], "week123")
        self.assertEqual(response_body["notes"], "Updated notes")
        mock_update_week.assert_called_once_with("week123", {"notes": "Updated notes"})

    @patch("src.services.week_service.WeekService.update_week")
    def test_update_week_not_found(self, mock_update_week):
        """
        Test week update when week not found
        """

        # Setup
        mock_update_week.return_value = None

        event = {
            "pathParameters": {"week_id": "nonexistent"},
            "body": json.dumps({"notes": "Updated notes"}),
        }
        context = {}

        # Call API
        response = week_api.update_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Week not found", response_body["error"])

    @patch("src.services.week_service.WeekService.update_week")
    def test_update_week_missing_path_param(self, mock_update_week):
        """
        Test update_week with missing path parameter
        """
        event = {"body": json.dumps({"notes": "Updated"})}  # No pathParameters

        context = {}

        # Call API
        response = week_api.update_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))

    @patch("src.services.week_service.WeekService.delete_week")
    def test_delete_week_success(self, mock_delete_week):
        """
        Test successful week deletion
        """

        # Setup
        mock_delete_week.return_value = True

        event = {"pathParameters": {"week_id": "week123"}}
        context = {}

        # Call API
        response = week_api.delete_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_week.assert_called_once_with("week123")

    @patch("src.services.week_service.WeekService.delete_week")
    def test_delete_week_not_found(self, mock_delete_week):
        """
        Test week deletion when week not found
        """

        # Setup
        mock_delete_week.return_value = False

        event = {"pathParameters": {"week_id": "nonexistent"}}
        context = {}

        # Call API
        response = week_api.delete_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Week not found", response_body["error"])

    @patch("src.services.week_service.WeekService.delete_week")
    def test_delete_week_missing_path_param(self, mock_delete_week):
        """
        Test delete_week with missing path parameter
        """
        event = {}  # No pathParameters
        context = {}

        # Call API
        response = week_api.delete_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error", json.loads(response["body"]))


if __name__ == "__main__":
    unittest.main()
