import unittest
from unittest.mock import MagicMock, patch
import json
from src.api.notification_api import get_notifications, mark_notification_as_read
from src.models.notification import Notification


class TestNotificationAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with consistent test data"""
        # Mock coach and athlete IDs
        self.coach_id = "test-coach-123"
        self.athlete_id = "test-athlete-456"
        self.notification_id = "test-notification-789"

        # Sample notification for testing
        self.sample_notification = Notification(
            notification_id=self.notification_id,
            coach_id=self.coach_id,
            athlete_id=self.athlete_id,
            athlete_name="Test Athlete",
            workout_id="workout-123",
            day_info="Day 3 (2024-06-25)",
            workout_data={"workout_id": "workout-123", "status": "completed"},
            created_at="2024-06-25T10:30:00Z",
            is_read=False,
            notification_type="workout_completion",
        )

        # Standard event structure
        self.base_event = {
            "requestContext": {"authorizer": {"claims": {"sub": self.coach_id}}},
            "queryStringParameters": None,
            "pathParameters": None,
        }

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_success_default_params(self, mock_service):
        """Test successful GET /notifications with default parameters"""
        # Arrange
        mock_service.get_notifications_for_coach.return_value = [
            self.sample_notification
        ]

        event = self.base_event.copy()
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0]["notification_id"], self.notification_id)

        # Verify service called with correct parameters
        mock_service.get_notifications_for_coach.assert_called_once_with(
            self.coach_id, None, False
        )

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_with_limit_parameter(self, mock_service):
        """Test GET /notifications with limit parameter"""
        # Arrange
        mock_service.get_notifications_for_coach.return_value = [
            self.sample_notification
        ]

        event = self.base_event.copy()
        event["queryStringParameters"] = {"limit": "10"}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_service.get_notifications_for_coach.assert_called_once_with(
            self.coach_id, 10, False
        )

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_unread_only_true(self, mock_service):
        """Test GET /notifications with unread_only=true"""
        # Arrange
        mock_service.get_notifications_for_coach.return_value = [
            self.sample_notification
        ]

        event = self.base_event.copy()
        event["queryStringParameters"] = {"unread_only": "true"}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_service.get_notifications_for_coach.assert_called_once_with(
            self.coach_id, None, True
        )

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_grouped_by_athlete(self, mock_service):
        """Test GET /notifications with grouped=true parameter"""
        # Arrange
        grouped_notifications = {self.athlete_id: [self.sample_notification]}
        mock_service.get_notifications_grouped_by_athlete.return_value = (
            grouped_notifications
        )

        event = self.base_event.copy()
        event["queryStringParameters"] = {"grouped": "true"}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertIn(self.athlete_id, response_body)
        self.assertEqual(len(response_body[self.athlete_id]), 1)

        mock_service.get_notifications_grouped_by_athlete.assert_called_once_with(
            self.coach_id, None
        )

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_combined_parameters(self, mock_service):
        """Test GET /notifications with multiple parameters"""
        # Arrange
        mock_service.get_notifications_for_coach.return_value = []

        event = self.base_event.copy()
        event["queryStringParameters"] = {"limit": "25", "unread_only": "true"}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_service.get_notifications_for_coach.assert_called_once_with(
            self.coach_id, 25, True
        )

    def test_get_notifications_missing_auth(self):
        """Test GET /notifications without authentication"""
        # Arrange
        event = {"requestContext": {}, "queryStringParameters": None}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized")

    def test_get_notifications_invalid_limit(self):
        """Test GET /notifications with invalid limit parameter"""
        # Arrange
        event = self.base_event.copy()
        event["queryStringParameters"] = {"limit": "invalid"}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Invalid limit parameter")

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_service_exception(self, mock_service):
        """Test GET /notifications when service throws exception"""
        # Arrange
        mock_service.get_notifications_for_coach.side_effect = Exception(
            "Database error"
        )

        event = self.base_event.copy()
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database error")

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_empty_result(self, mock_service):
        """Test GET /notifications when no notifications exist"""
        # Arrange
        mock_service.get_notifications_for_coach.return_value = []

        event = self.base_event.copy()
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body, [])

    @patch("src.api.notification_api.notification_service")
    def test_mark_notification_as_read_success(self, mock_service):
        """Test successful PATCH /notifications/{id}/read"""
        # Arrange
        mock_service.get_notification.return_value = self.sample_notification
        mock_service.mark_notification_as_read.return_value = True

        event = self.base_event.copy()
        event["pathParameters"] = {"notification_id": self.notification_id}
        context = {}

        # Act
        response = mark_notification_as_read(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Notification marked as read")

        # Verify service calls
        mock_service.get_notification.assert_called_once_with(self.notification_id)
        mock_service.mark_notification_as_read.assert_called_once_with(
            self.notification_id
        )

    def test_mark_notification_as_read_missing_auth(self):
        """Test PATCH /notifications/{id}/read without authentication"""
        # Arrange
        event = {
            "requestContext": {},
            "pathParameters": {"notification_id": self.notification_id},
        }
        context = {}

        # Act
        response = mark_notification_as_read(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 401)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Unauthorized")

    @patch("src.api.notification_api.notification_service")
    def test_mark_notification_as_read_not_found(self, mock_service):
        """Test PATCH /notifications/{id}/read when notification doesn't exist"""
        # Arrange
        mock_service.get_notification.return_value = None

        event = self.base_event.copy()
        event["pathParameters"] = {"notification_id": self.notification_id}
        context = {}

        # Act
        response = mark_notification_as_read(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Notification not found")

        # Verify get_notification was called but mark_as_read was not
        mock_service.get_notification.assert_called_once_with(self.notification_id)
        mock_service.mark_notification_as_read.assert_not_called()

    @patch("src.api.notification_api.notification_service")
    def test_mark_notification_as_read_wrong_coach(self, mock_service):
        """Test PATCH /notifications/{id}/read when notification belongs to different coach"""
        # Arrange
        different_coach_notification = Notification(
            notification_id=self.notification_id,
            coach_id="different-coach-id",
            athlete_id=self.athlete_id,
            athlete_name="Test Athlete",
            workout_id="workout-123",
            day_info="Day 3 (2024-06-25)",
            workout_data={"workout_id": "workout-123"},
            is_read=False,
        )
        mock_service.get_notification.return_value = different_coach_notification

        event = self.base_event.copy()
        event["pathParameters"] = {"notification_id": self.notification_id}
        context = {}

        # Act
        response = mark_notification_as_read(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Forbidden")

        # Verify authorization check prevented marking as read
        mock_service.get_notification.assert_called_once_with(self.notification_id)
        mock_service.mark_notification_as_read.assert_not_called()

    @patch("src.api.notification_api.notification_service")
    def test_mark_notification_as_read_service_failure(self, mock_service):
        """Test PATCH /notifications/{id}/read when service fails to mark as read"""
        # Arrange
        mock_service.get_notification.return_value = self.sample_notification
        mock_service.mark_notification_as_read.return_value = False

        event = self.base_event.copy()
        event["pathParameters"] = {"notification_id": self.notification_id}
        context = {}

        # Act
        response = mark_notification_as_read(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Failed to mark notification as read")

    @patch("src.api.notification_api.notification_service")
    def test_mark_notification_as_read_service_exception(self, mock_service):
        """Test PATCH /notifications/{id}/read when service throws exception"""
        # Arrange
        mock_service.get_notification.side_effect = Exception("Database error")

        event = self.base_event.copy()
        event["pathParameters"] = {"notification_id": self.notification_id}
        context = {}

        # Act
        response = mark_notification_as_read(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database error")

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_case_insensitive_boolean_params(self, mock_service):
        """Test GET /notifications with case-insensitive boolean parameters"""
        # Arrange
        mock_service.get_notifications_for_coach.return_value = []

        test_cases = [
            ("TRUE", True),
            ("True", True),
            ("false", False),
            ("FALSE", False),
            ("invalid", False),  # Invalid values default to False
        ]

        for param_value, expected_bool in test_cases:
            with self.subTest(param_value=param_value):
                event = self.base_event.copy()
                event["queryStringParameters"] = {"unread_only": param_value}
                context = {}

                # Act
                response = get_notifications(event, context)

                # Assert
                self.assertEqual(response["statusCode"], 200)
                mock_service.get_notifications_for_coach.assert_called_with(
                    self.coach_id, None, expected_bool
                )

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_multiple_notifications(self, mock_service):
        """Test GET /notifications with multiple notifications"""
        # Arrange
        notification2 = Notification(
            notification_id="test-notification-890",
            coach_id=self.coach_id,
            athlete_id="another-athlete",
            athlete_name="Another Athlete",
            workout_id="workout-456",
            day_info="Day 1 (2024-06-24)",
            workout_data={"workout_id": "workout-456"},
            is_read=True,
        )

        mock_service.get_notifications_for_coach.return_value = [
            self.sample_notification,
            notification2,
        ]

        event = self.base_event.copy()
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)

        # Verify both notifications are properly serialized
        notification_ids = [n["notification_id"] for n in response_body]
        self.assertIn(self.notification_id, notification_ids)
        self.assertIn("test-notification-890", notification_ids)

    @patch("src.api.notification_api.notification_service")
    def test_get_notifications_grouped_multiple_athletes(self, mock_service):
        """Test GET /notifications grouped by athlete with multiple athletes"""
        # Arrange
        athlete2_id = "athlete-789"
        notification2 = Notification(
            notification_id="notification-456",
            coach_id=self.coach_id,
            athlete_id=athlete2_id,
            athlete_name="Second Athlete",
            workout_id="workout-456",
            day_info="Day 2 (2024-06-24)",
            workout_data={"workout_id": "workout-456"},
            is_read=False,
        )

        grouped_notifications = {
            self.athlete_id: [self.sample_notification],
            athlete2_id: [notification2],
        }
        mock_service.get_notifications_grouped_by_athlete.return_value = (
            grouped_notifications
        )

        event = self.base_event.copy()
        event["queryStringParameters"] = {"grouped": "true", "limit": "10"}
        context = {}

        # Act
        response = get_notifications(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Verify grouping structure
        self.assertEqual(len(response_body), 2)
        self.assertIn(self.athlete_id, response_body)
        self.assertIn(athlete2_id, response_body)
        self.assertEqual(len(response_body[self.athlete_id]), 1)
        self.assertEqual(len(response_body[athlete2_id]), 1)

        # Verify service called with limit
        mock_service.get_notifications_grouped_by_athlete.assert_called_once_with(
            self.coach_id, 10
        )


if __name__ == "__main__":
    unittest.main()
