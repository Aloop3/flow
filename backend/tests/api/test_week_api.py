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

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_success(self, mock_create_week, mock_get_block):
        """
        Test successful week creation
        """

        # Setup
        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block

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
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
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

    @patch("src.services.block_service.BlockService.get_block")
    def test_create_week_block_not_found(self, mock_get_block):
        """Test week creation when block not found"""
        mock_get_block.return_value = None

        event = {
            "body": json.dumps(
                {"block_id": "block456", "week_number": 1, "notes": "Test week"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = week_api.create_week(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

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

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_service_exception(self, mock_create_week, mock_get_block):
        """
        Test exception handling in create_week
        """
        # Setup
        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block
        mock_create_week.side_effect = Exception("Service error")

        event = {
            "body": json.dumps(
                {"block_id": "block456", "week_number": 1, "notes": "Test week"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
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

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.create_week")
    def test_create_week_unauthorized(
        self, mock_create_week, mock_get_block, mock_get_relationship
    ):
        """Test week creation by unauthorized user"""
        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block
        mock_get_relationship.return_value = None

        event = {
            "body": json.dumps(
                {"block_id": "block456", "week_number": 1, "notes": "Test week"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = week_api.create_week(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_create_week.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_weeks_for_block")
    def test_get_weeks_for_block_success(self, mock_get_weeks, mock_get_block):
        """
        Test successful retrieval of weeks for a block
        """

        # Setup
        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block

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

        event = {
            "pathParameters": {"block_id": "block456"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
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

    @patch("src.services.block_service.BlockService.get_block")
    def test_get_weeks_for_block_block_not_found(self, mock_get_block):
        """Test getting weeks when block not found"""
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"block_id": "block456"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = week_api.get_weeks_for_block(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

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

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_weeks_for_block")
    def test_get_weeks_for_block_unauthorized(
        self, mock_get_weeks, mock_get_block, mock_get_relationship
    ):
        """Test retrieving weeks for block by unauthorized user"""
        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"block_id": "block456"},
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = week_api.get_weeks_for_block(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_get_weeks.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.week_service.WeekService.update_week")
    def test_update_week_success(self, mock_update_week, mock_get_week, mock_get_block):
        """
        Test successful week update
        """

        # Setup
        mock_existing = MagicMock()
        mock_existing.block_id = "block456"
        mock_get_week.return_value = mock_existing

        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block

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
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
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

    @patch("src.services.week_service.WeekService.get_week")
    def test_update_week_not_found(self, mock_get_week):
        """
        Test week update when week not found during ownership check
        """

        # Setup
        mock_get_week.return_value = None

        event = {
            "pathParameters": {"week_id": "nonexistent"},
            "body": json.dumps({"notes": "Updated notes"}),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        # Call API
        response = week_api.update_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Week not found", response_body["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    def test_update_week_block_not_found(self, mock_get_week, mock_get_block):
        """Test week update when block not found"""
        mock_existing = MagicMock()
        mock_existing.block_id = "block456"
        mock_get_week.return_value = mock_existing
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"week_id": "week123"},
            "body": json.dumps({"notes": "Updated notes"}),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = week_api.update_week(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

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

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.week_service.WeekService.update_week")
    def test_update_week_unauthorized(
        self, mock_update_week, mock_get_week, mock_get_block, mock_get_relationship
    ):
        """Test week update by unauthorized user"""
        mock_existing = MagicMock()
        mock_existing.block_id = "block456"
        mock_get_week.return_value = mock_existing

        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"week_id": "week123"},
            "body": json.dumps({"notes": "Updated notes"}),
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = week_api.update_week(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_update_week.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.week_service.WeekService.delete_week")
    def test_delete_week_success(self, mock_delete_week, mock_get_week, mock_get_block):
        """
        Test successful week deletion
        """

        # Setup
        mock_existing = MagicMock()
        mock_existing.block_id = "block456"
        mock_get_week.return_value = mock_existing

        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block

        mock_delete_week.return_value = True

        event = {
            "pathParameters": {"week_id": "week123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = week_api.delete_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_week.assert_called_once_with("week123")

    @patch("src.services.week_service.WeekService.get_week")
    def test_delete_week_not_found(self, mock_get_week):
        """
        Test week deletion when week not found during ownership check
        """

        # Setup
        mock_get_week.return_value = None

        event = {
            "pathParameters": {"week_id": "nonexistent"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        # Call API
        response = week_api.delete_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Week not found", response_body["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    def test_delete_week_block_not_found(self, mock_get_week, mock_get_block):
        """Test week deletion when block not found"""
        mock_existing = MagicMock()
        mock_existing.block_id = "block456"
        mock_get_week.return_value = mock_existing
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"week_id": "week123"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = week_api.delete_week(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

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

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.week_service.WeekService.delete_week")
    def test_delete_week_unauthorized(
        self, mock_delete_week, mock_get_week, mock_get_block, mock_get_relationship
    ):
        """Test week deletion by unauthorized user"""
        mock_existing = MagicMock()
        mock_existing.block_id = "block456"
        mock_get_week.return_value = mock_existing

        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"week_id": "week123"},
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = week_api.delete_week(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_delete_week.assert_not_called()


if __name__ == "__main__":
    unittest.main()
