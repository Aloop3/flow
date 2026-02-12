import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import day after the mocks are set up in BaseTest
with patch("boto3.resource"):
    from src.api import day_api


class TestDayAPI(BaseTest):
    """
    Test suite for the Day API module
    """

    def _mock_ownership_chain(self, mock_get_week, mock_get_block):
        """Helper to set up week→block ownership mocks"""
        mock_week = MagicMock()
        mock_week.block_id = "block456"
        mock_get_week.return_value = mock_week

        mock_block = MagicMock()
        mock_block.athlete_id = "athlete456"
        mock_block.coach_id = "coach789"
        mock_get_block.return_value = mock_block

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_success(self, mock_create_day, mock_get_week, mock_get_block):
        """Test successful day creation"""
        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_day = MagicMock()
        mock_day.to_dict.return_value = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
            "focus": "squat",
            "notes": "Heavy squat day",
        }
        mock_create_day.return_value = mock_day

        event = {
            "body": json.dumps(
                {
                    "week_id": "week456",
                    "day_number": 1,
                    "date": "2025-03-15",
                    "focus": "squat",
                    "notes": "Heavy squat day",
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.create_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["day_id"], "day123")
        self.assertEqual(response_body["week_id"], "week456")
        self.assertEqual(response_body["day_number"], 1)
        self.assertEqual(response_body["date"], "2025-03-15")
        mock_create_day.assert_called_once_with(
            week_id="week456",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="Heavy squat day",
        )

    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_missing_fields(self, mock_create_day):
        """
        Test day creation with missing required fields
        """
        # Setup
        event = {
            "body": json.dumps(
                {
                    "week_id": "week456",
                    # Missing day_number
                    "date": "2025-03-15",
                }
            )
        }
        context = {}

        # Call API
        response = day_api.create_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_day.assert_not_called()

    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_invalid_json(self, mock_create_day):
        """
        Test day creation with invalid JSON
        """
        event = {"body": "invalid json"}
        context = {}

        # Call API
        response = day_api.create_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])
        mock_create_day.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_service_exception(
        self, mock_create_day, mock_get_week, mock_get_block
    ):
        """Test day creation when the service layer raises an exception"""
        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_create_day.side_effect = Exception("DynamoDB throttling occurred")

        event = {
            "body": json.dumps(
                {
                    "week_id": "week456",
                    "day_number": 1,
                    "date": "2025-03-15",
                    "focus": "squat",
                    "notes": "Heavy squat day",
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.create_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "DynamoDB throttling occurred")
        mock_create_day.assert_called_once_with(
            week_id="week456",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="Heavy squat day",
        )

    def test_create_day_direct_json_decode_error(self):
        """
        Test the JSONDecodeError handler in create_day (line 41)
        """
        # Setup - create event with invalid JSON
        event = {"body": "{invalid-json"}
        context = {}

        # Call the function directly using __wrapped__ to bypass middleware
        response = day_api.create_day.__wrapped__(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Invalid JSON in request body")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_unauthorized(
        self, mock_create_day, mock_get_week, mock_get_block, mock_get_relationship
    ):
        """Test day creation by unauthorized user"""
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_get_relationship.return_value = None

        event = {
            "body": json.dumps(
                {
                    "week_id": "week456",
                    "day_number": 1,
                    "date": "2025-03-15",
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = day_api.create_day(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_create_day.assert_not_called()

    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_week_not_found(self, mock_create_day, mock_get_week):
        """Test day creation when week not found"""
        mock_get_week.return_value = None

        event = {
            "body": json.dumps(
                {"week_id": "week456", "day_number": 1, "date": "2025-03-15"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.create_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Week not found", json.loads(response["body"])["error"])
        mock_create_day.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.create_day")
    def test_create_day_block_not_found(
        self, mock_create_day, mock_get_week, mock_get_block
    ):
        """Test day creation when block not found"""
        mock_week = MagicMock()
        mock_week.block_id = "block456"
        mock_get_week.return_value = mock_week
        mock_get_block.return_value = None

        event = {
            "body": json.dumps(
                {"week_id": "week456", "day_number": 1, "date": "2025-03-15"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.create_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])
        mock_create_day.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_get_day_success(self, mock_get_day, mock_get_week, mock_get_block):
        """Test successful day retrieval"""
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_day = MagicMock()
        mock_day.week_id = "week456"
        mock_day.to_dict.return_value = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
        }
        mock_get_day.return_value = mock_day

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        response = day_api.get_day(event, context)

        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["day_id"], "day123")

    @patch("src.services.day_service.DayService.get_day")
    def test_get_day_not_found(self, mock_get_day):
        """Test day retrieval when day not found"""
        mock_get_day.return_value = None

        event = {
            "pathParameters": {"day_id": "nonexistent"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.get_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Day not found", response_body["error"])

    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_get_day_week_not_found(self, mock_get_day, mock_get_week):
        """Test day retrieval when week not found during ownership check"""
        mock_day = MagicMock()
        mock_day.week_id = "week456"
        mock_get_day.return_value = mock_day
        mock_get_week.return_value = None

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.get_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Week not found", json.loads(response["body"])["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_get_day_block_not_found(self, mock_get_day, mock_get_week, mock_get_block):
        """Test day retrieval when block not found during ownership check"""
        mock_day = MagicMock()
        mock_day.week_id = "week456"
        mock_get_day.return_value = mock_day

        mock_week = MagicMock()
        mock_week.block_id = "block456"
        mock_get_week.return_value = mock_week
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.get_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

    @patch("src.services.day_service.DayService.get_day")
    def test_get_day_exception(self, mock_get_day):
        """Test exception handling in get_day"""
        mock_get_day.side_effect = Exception("Unexpected error")

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.get_day(event, context)

        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Unexpected error", response_body["error"])

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_get_day_unauthorized(
        self, mock_get_day, mock_get_week, mock_get_block, mock_get_relationship
    ):
        """Test day retrieval by unauthorized user"""
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_get_relationship.return_value = None

        mock_day = MagicMock()
        mock_day.week_id = "week456"
        mock_get_day.return_value = mock_day

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = day_api.get_day(event, context)

        self.assertEqual(response["statusCode"], 403)

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_days_for_week")
    def test_get_days_for_week_success(
        self, mock_get_days, mock_get_week, mock_get_block
    ):
        """
        Test successful retrieval of days for a week
        """

        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_day1 = MagicMock()
        mock_day1.to_dict.return_value = {
            "day_id": "day1",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
        }
        mock_day2 = MagicMock()
        mock_day2.to_dict.return_value = {
            "day_id": "day2",
            "week_id": "week456",
            "day_number": 2,
            "date": "2025-03-16",
        }
        mock_get_days.return_value = [mock_day1, mock_day2]

        event = {
            "pathParameters": {"week_id": "week456"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.get_days_for_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["day_id"], "day1")
        self.assertEqual(response_body[1]["day_id"], "day2")
        mock_get_days.assert_called_once_with("week456")

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_days_for_week")
    def test_get_days_for_week_exception(
        self, mock_get_days, mock_get_week, mock_get_block
    ):
        """
        Test exception handling in get_days_for_week
        """
        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_get_days.side_effect = Exception("Test exception")

        event = {
            "pathParameters": {"week_id": "week456"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.get_days_for_week(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch("src.services.week_service.WeekService.get_week")
    def test_get_days_for_week_week_not_found(self, mock_get_week):
        """Test getting days when week not found"""
        mock_get_week.return_value = None

        event = {
            "pathParameters": {"week_id": "week456"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.get_days_for_week(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Week not found", json.loads(response["body"])["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    def test_get_days_for_week_block_not_found(self, mock_get_week, mock_get_block):
        """Test getting days when block not found"""
        mock_week = MagicMock()
        mock_week.block_id = "block456"
        mock_get_week.return_value = mock_week
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"week_id": "week456"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.get_days_for_week(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_days_for_week")
    def test_get_days_for_week_unauthorized(
        self, mock_get_days, mock_get_week, mock_get_block, mock_get_relationship
    ):
        """Test retrieving days for week by unauthorized user"""
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"week_id": "week456"},
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = day_api.get_days_for_week(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_get_days.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.day_service.DayService.update_day")
    def test_update_day_success(
        self, mock_update_day, mock_get_day, mock_get_week, mock_get_block
    ):
        """
        Test successful day update
        """

        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        mock_day = MagicMock()
        mock_day.to_dict.return_value = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
            "focus": "deadlift",
            "notes": "Updated notes",
        }
        mock_update_day.return_value = mock_day

        event = {
            "pathParameters": {"day_id": "day123"},
            "body": json.dumps({"focus": "deadlift", "notes": "Updated notes"}),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.update_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["day_id"], "day123")
        self.assertEqual(response_body["focus"], "deadlift")
        self.assertEqual(response_body["notes"], "Updated notes")
        mock_update_day.assert_called_once_with(
            "day123", {"focus": "deadlift", "notes": "Updated notes"}
        )

    @patch("src.services.day_service.DayService.get_day")
    def test_update_day_not_found(self, mock_get_day):
        """
        Test day update when day not found during ownership check
        """

        # Setup
        mock_get_day.return_value = None

        event = {
            "pathParameters": {"day_id": "nonexistent"},
            "body": json.dumps({"focus": "deadlift"}),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        # Call API
        response = day_api.update_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Day not found", response_body["error"])

    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_update_day_week_not_found(self, mock_get_day, mock_get_week):
        """Test day update when week not found during ownership check"""
        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing
        mock_get_week.return_value = None

        event = {
            "pathParameters": {"day_id": "day123"},
            "body": json.dumps({"focus": "deadlift"}),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.update_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Week not found", json.loads(response["body"])["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_update_day_block_not_found(
        self, mock_get_day, mock_get_week, mock_get_block
    ):
        """Test day update when block not found during ownership check"""
        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        mock_week = MagicMock()
        mock_week.block_id = "block456"
        mock_get_week.return_value = mock_week
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"day_id": "day123"},
            "body": json.dumps({"focus": "deadlift"}),
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.update_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.day_service.DayService.update_day")
    def test_update_day_exception(
        self, mock_update_day, mock_get_day, mock_get_week, mock_get_block
    ):
        """
        Test exception handling in update_day
        """
        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        mock_update_day.side_effect = Exception("Test exception")

        event = {
            "pathParameters": {"day_id": "day123"},
            "body": json.dumps({"focus": "deadlift"}),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.update_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.day_service.DayService.update_day")
    def test_update_day_unauthorized(
        self,
        mock_update_day,
        mock_get_day,
        mock_get_week,
        mock_get_block,
        mock_get_relationship,
    ):
        """Test day update by unauthorized user"""
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_get_relationship.return_value = None

        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        event = {
            "pathParameters": {"day_id": "day123"},
            "body": json.dumps({"focus": "deadlift"}),
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = day_api.update_day(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_update_day.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.day_service.DayService.delete_day")
    def test_delete_day_success(
        self, mock_delete_day, mock_get_day, mock_get_week, mock_get_block
    ):
        """
        Test successful day deletion
        """

        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        mock_delete_day.return_value = True

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.delete_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_day.assert_called_once_with("day123")

    @patch("src.services.day_service.DayService.get_day")
    def test_delete_day_not_found(self, mock_get_day):
        """
        Test day deletion when day not found during ownership check
        """
        # Setup
        mock_get_day.return_value = None

        event = {
            "pathParameters": {"day_id": "nonexistent"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        # Call API
        response = day_api.delete_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Day not found", response_body["error"])

    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_delete_day_week_not_found(self, mock_get_day, mock_get_week):
        """Test day deletion when week not found during ownership check"""
        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing
        mock_get_week.return_value = None

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.delete_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Week not found", json.loads(response["body"])["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_delete_day_block_not_found(
        self, mock_get_day, mock_get_week, mock_get_block
    ):
        """Test day deletion when block not found during ownership check"""
        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        mock_week = MagicMock()
        mock_week.block_id = "block456"
        mock_get_week.return_value = mock_week
        mock_get_block.return_value = None

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "some-user"}}},
        }
        context = {}

        response = day_api.delete_day(event, context)

        self.assertEqual(response["statusCode"], 404)
        self.assertIn("Block not found", json.loads(response["body"])["error"])

    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.day_service.DayService.delete_day")
    def test_delete_day_exception(
        self, mock_delete_day, mock_get_day, mock_get_week, mock_get_block
    ):
        """
        Test exception handling in delete_day
        """
        # Setup
        self._mock_ownership_chain(mock_get_week, mock_get_block)

        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        mock_delete_day.side_effect = Exception("Test exception")

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = day_api.delete_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.day_service.DayService.delete_day")
    def test_delete_day_unauthorized(
        self,
        mock_delete_day,
        mock_get_day,
        mock_get_week,
        mock_get_block,
        mock_get_relationship,
    ):
        """Test day deletion by unauthorized user"""
        self._mock_ownership_chain(mock_get_week, mock_get_block)
        mock_get_relationship.return_value = None

        mock_existing = MagicMock()
        mock_existing.week_id = "week456"
        mock_get_day.return_value = mock_existing

        event = {
            "pathParameters": {"day_id": "day123"},
            "requestContext": {"authorizer": {"claims": {"sub": "other-user"}}},
        }
        context = {}

        response = day_api.delete_day(event, context)

        self.assertEqual(response["statusCode"], 403)
        mock_delete_day.assert_not_called()


if __name__ == "__main__":
    unittest.main()
