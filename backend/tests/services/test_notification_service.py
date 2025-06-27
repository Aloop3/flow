import unittest
from unittest.mock import patch, MagicMock
from src.services.notification_service import NotificationService
from src.models.workout import Workout
from src.models.notification import Notification


class TestNotificationService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock uuid.uuid4 to return consistent test UUIDs
        self.uuid_patcher = patch("src.services.notification_service.uuid.uuid4")
        self.mock_uuid = self.uuid_patcher.start()
        self.mock_uuid.return_value = MagicMock()
        self.mock_uuid.return_value.__str__ = MagicMock(
            return_value="test-notification-uuid"
        )

        # Create mock repositories
        self.mock_notification_repo = MagicMock()
        self.mock_user_repo = MagicMock()

        # Test data
        self.test_workout = Workout(
            workout_id="workout-123",
            athlete_id="athlete-456",
            day_id="day-789",
            date="2024-06-25",
            notes="Test workout",
            status="completed",
        )

        self.test_athlete_data = {
            "user_id": "athlete-456",
            "name": "John Athlete",
            "email": "john@example.com",
            "coach_id": "coach-789",
        }

        self.test_coach_data = {
            "user_id": "coach-789",
            "name": "Sarah Coach",
            "email": "sarah@example.com",
            "role": "coach",
        }

        self.test_notification_data = {
            "notification_id": "test-notification-uuid",
            "coach_id": "coach-789",
            "athlete_id": "athlete-456",
            "athlete_name": "John Athlete",
            "workout_id": "workout-123",
            "day_info": "Day day-789 (2024-06-25)",
            "workout_data": self.test_workout.to_dict(),
            "created_at": "2024-06-25T10:30:00Z",
            "is_read": False,
            "notification_type": "workout_completion",
        }

    def tearDown(self):
        """Clean up after each test method."""
        self.uuid_patcher.stop()

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_init_creates_repositories(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test that service initialization creates repository instances."""
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        service = NotificationService()

        self.assertEqual(service.notification_repository, self.mock_notification_repo)
        self.assertEqual(service.user_repository, self.mock_user_repo)

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_create_workout_completion_notification_success(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test successful notification creation."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        # Mock athlete and coach data
        self.mock_user_repo.get_user.side_effect = [
            self.test_athlete_data,  # First call for athlete
            self.test_coach_data,  # Second call for coach
        ]

        # Mock active relationship found
        relationship_data = {
            "coach_id": "coach-123",
            "athlete_id": "athlete-456",
            "status": "active",
        }
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            relationship_data
        )

        # Mock notification repository
        self.mock_notification_repo.create_notification.return_value = True

        service = NotificationService()

        # Test notification creation
        result = service.create_workout_completion_notification(self.test_workout)

        # Verify success
        self.assertTrue(result)

        # Verify calls
        self.assertEqual(self.mock_user_repo.get_user.call_count, 2)
        self.mock_user_repo.get_user.assert_any_call("athlete-456")
        self.mock_user_repo.get_user.assert_any_call("coach-123")

        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.assert_called_once_with(
            "athlete-456"
        )
        self.mock_notification_repo.create_notification.assert_called_once()

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_create_workout_completion_notification_athlete_not_found(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test notification creation when athlete is not found."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_user_repo.get_user.return_value = None  # Athlete not found

        service = NotificationService()

        # Test notification creation
        result = service.create_workout_completion_notification(self.test_workout)

        # Verify
        self.assertFalse(result)
        self.mock_user_repo.get_user.assert_called_once_with("athlete-456")
        self.mock_notification_repo.create_notification.assert_not_called()

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_create_workout_completion_notification_no_coach(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test notification creation when athlete has no coach assigned."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        # Mock athlete data (no coach_id field needed anymore)
        athlete_data = self.test_athlete_data.copy()
        self.mock_user_repo.get_user.return_value = athlete_data

        # Mock no active relationship found
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            None
        )

        service = NotificationService()

        # Test notification creation
        result = service.create_workout_completion_notification(self.test_workout)

        # Verify - should return True but not create notification
        self.assertTrue(result)
        self.mock_user_repo.get_user.assert_called_once_with("athlete-456")
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.assert_called_once_with(
            "athlete-456"
        )
        self.mock_notification_repo.create_notification.assert_not_called()

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_create_workout_completion_notification_coach_not_found(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test notification creation when coach is not found."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        # Mock athlete found, coach not found
        self.mock_user_repo.get_user.side_effect = [
            self.test_athlete_data,  # First call for athlete
            None,  # Second call for coach returns None
        ]

        # Mock successful relationship lookup
        relationship_data = {
            "coach_id": "coach-123",
            "athlete_id": "athlete-456",
            "status": "active",
        }
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            relationship_data
        )

        service = NotificationService()

        # Test notification creation
        result = service.create_workout_completion_notification(self.test_workout)

        # Verify - should return False when coach not found
        self.assertFalse(result)
        self.assertEqual(self.mock_user_repo.get_user.call_count, 2)
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.assert_called_once_with(
            "athlete-456"
        )
        self.mock_notification_repo.create_notification.assert_not_called()

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_create_workout_completion_notification_repository_failure(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test notification creation when repository fails."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        # Mock successful user and relationship lookups
        self.mock_user_repo.get_user.side_effect = [
            self.test_athlete_data,  # First call for athlete
            self.test_coach_data,  # Second call for coach
        ]

        # Mock successful relationship lookup
        relationship_data = {
            "coach_id": "coach-123",
            "athlete_id": "athlete-456",
            "status": "active",
        }
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            relationship_data
        )

        # Mock repository failure
        self.mock_notification_repo.create_notification.return_value = False

        service = NotificationService()

        # Test notification creation
        result = service.create_workout_completion_notification(self.test_workout)

        # Verify failure is handled gracefully
        self.assertFalse(result)

        # Verify calls were made
        self.assertEqual(self.mock_user_repo.get_user.call_count, 2)
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.assert_called_once_with(
            "athlete-456"
        )
        self.mock_notification_repo.create_notification.assert_called_once()

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_notifications_for_coach_success(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test successful retrieval of notifications for coach."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.get_notifications_for_coach.return_value = [
            self.test_notification_data
        ]

        service = NotificationService()

        # Test retrieval
        result = service.get_notifications_for_coach(
            "coach-789", limit=10, unread_only=True
        )

        # Verify
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Notification)
        self.assertEqual(result[0].coach_id, "coach-789")
        self.mock_notification_repo.get_notifications_for_coach.assert_called_once_with(
            "coach-789", 10, True
        )

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_notifications_for_coach_invalid_data(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test handling of invalid notification data."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        invalid_data = {"invalid": "data"}
        self.mock_notification_repo.get_notifications_for_coach.return_value = [
            self.test_notification_data,
            invalid_data,  # This should be skipped
            self.test_notification_data,
        ]

        service = NotificationService()

        # Test retrieval
        result = service.get_notifications_for_coach("coach-789")

        # Verify - should skip invalid data and return only valid notifications
        self.assertEqual(len(result), 2)
        for notification in result:
            self.assertIsInstance(notification, Notification)

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_notifications_grouped_by_athlete(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test retrieval of notifications grouped by athlete."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        # Create notifications for different athletes
        notification_data_1 = self.test_notification_data.copy()
        notification_data_2 = self.test_notification_data.copy()
        notification_data_2["athlete_id"] = "athlete-999"
        notification_data_2["athlete_name"] = "Jane Athlete"

        self.mock_notification_repo.get_notifications_for_coach.return_value = [
            notification_data_1,
            notification_data_2,
        ]

        service = NotificationService()

        # Test grouped retrieval
        result = service.get_notifications_grouped_by_athlete("coach-789", limit=20)

        # Verify
        self.assertIn("athlete-456", result)
        self.assertIn("athlete-999", result)
        self.assertEqual(len(result["athlete-456"]), 1)
        self.assertEqual(len(result["athlete-999"]), 1)
        self.mock_notification_repo.get_notifications_for_coach.assert_called_once_with(
            "coach-789", 20, False
        )

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_mark_notification_as_read_success(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test successful marking of notification as read."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.mark_notification_as_read.return_value = True

        service = NotificationService()

        # Test marking as read
        result = service.mark_notification_as_read("test-notification-uuid")

        # Verify
        self.assertTrue(result)
        self.mock_notification_repo.mark_notification_as_read.assert_called_once_with(
            "test-notification-uuid"
        )

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_mark_notification_as_read_failure(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test handling of failure when marking notification as read."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.mark_notification_as_read.return_value = False

        service = NotificationService()

        # Test marking as read failure
        result = service.mark_notification_as_read("test-notification-uuid")

        # Verify
        self.assertFalse(result)

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_unread_count_for_coach(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test retrieval of unread count for coach."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.get_unread_count_for_coach.return_value = 5

        service = NotificationService()

        # Test count retrieval
        result = service.get_unread_count_for_coach("coach-789")

        # Verify
        self.assertEqual(result, 5)
        self.mock_notification_repo.get_unread_count_for_coach.assert_called_once_with(
            "coach-789"
        )

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_notification_success(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test successful retrieval of specific notification."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.get_notification.return_value = (
            self.test_notification_data
        )

        service = NotificationService()

        # Test notification retrieval
        result = service.get_notification("test-notification-uuid")

        # Verify
        self.assertIsInstance(result, Notification)
        self.assertEqual(result.notification_id, "test-notification-uuid")
        self.mock_notification_repo.get_notification.assert_called_once_with(
            "test-notification-uuid"
        )

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_notification_not_found(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test retrieval of notification that doesn't exist."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.get_notification.return_value = None

        service = NotificationService()

        # Test notification retrieval
        result = service.get_notification("nonexistent-notification")

        # Verify
        self.assertIsNone(result)

    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_get_notification_invalid_data(
        self, mock_user_repo_class, mock_notification_repo_class
    ):
        """Test retrieval of notification with invalid data."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo

        self.mock_notification_repo.get_notification.return_value = {"invalid": "data"}

        service = NotificationService()

        # Test notification retrieval
        result = service.get_notification("test-notification-uuid")

        # Verify
        self.assertIsNone(result)

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_day_info_formatting_with_day_id_and_date(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test that day_info is formatted correctly with both day_id and date."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        self.mock_user_repo.get_user.side_effect = [
            self.test_athlete_data,
            self.test_coach_data,
        ]

        # Mock successful relationship lookup
        relationship_data = {
            "coach_id": "coach-123",
            "athlete_id": "athlete-456",
            "status": "active",
        }
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            relationship_data
        )

        self.mock_notification_repo.create_notification.return_value = True
        service = NotificationService()

        # Test with workout that has no date
        workout_no_date = Workout(
            workout_id="workout-123",
            athlete_id="athlete-456",
            day_id="day-789",
            date=None,
            notes="Test workout",
            status="completed",
        )
        result = service.create_workout_completion_notification(workout_no_date)

        # Verify notification creation was called with correct day_info
        call_args = self.mock_notification_repo.create_notification.call_args[0][0]
        expected_day_info = "Day day-789"
        self.assertEqual(call_args["day_info"], expected_day_info)

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_day_info_formatting_without_day_id(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test that day_info is formatted correctly without day_id."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        self.mock_user_repo.get_user.side_effect = [
            self.test_athlete_data,
            self.test_coach_data,
        ]

        # Mock successful relationship lookup
        relationship_data = {
            "coach_id": "coach-123",
            "athlete_id": "athlete-456",
            "status": "active",
        }
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            relationship_data
        )

        self.mock_notification_repo.create_notification.return_value = True
        service = NotificationService()

        # Test with workout that has no day_id
        workout_no_day_id = Workout(
            workout_id="workout-123",
            athlete_id="athlete-456",
            day_id=None,
            date="2024-06-25",
            notes="Test workout",
            status="completed",
        )
        result = service.create_workout_completion_notification(workout_no_day_id)

        # Verify notification creation was called with correct day_info
        call_args = self.mock_notification_repo.create_notification.call_args[0][0]
        expected_day_info = "Workout (2024-06-25)"
        self.assertEqual(call_args["day_info"], expected_day_info)

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_workout_data_storage_in_notification(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test that full workout data is stored in notification."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        self.mock_user_repo.get_user.side_effect = [
            self.test_athlete_data,
            self.test_coach_data,
        ]

        # Mock successful relationship lookup
        relationship_data = {
            "coach_id": "coach-123",
            "athlete_id": "athlete-456",
            "status": "active",
        }
        mock_relationship_service.relationship_repository.get_active_relationship_for_athlete.return_value = (
            relationship_data
        )

        self.mock_notification_repo.create_notification.return_value = True
        service = NotificationService()

        # Test notification creation
        result = service.create_workout_completion_notification(self.test_workout)

        # Verify workout data is stored
        call_args = self.mock_notification_repo.create_notification.call_args[0][0]
        self.assertIn("workout_data", call_args)
        self.assertEqual(call_args["workout_data"], self.test_workout.to_dict())

    @patch("src.services.notification_service.RelationshipService")
    @patch("src.services.notification_service.NotificationRepository")
    @patch("src.services.notification_service.UserRepository")
    def test_notification_sorting_in_grouped_by_athlete(
        self,
        mock_user_repo_class,
        mock_notification_repo_class,
        mock_relationship_service_class,
    ):
        """Test that notifications are sorted by creation time within athlete groups."""
        # Setup mocks
        mock_notification_repo_class.return_value = self.mock_notification_repo
        mock_user_repo_class.return_value = self.mock_user_repo
        mock_relationship_service = MagicMock()
        mock_relationship_service_class.return_value = mock_relationship_service

        # Create notifications with different timestamps for same athlete
        notification_1 = self.test_notification_data.copy()
        notification_1["created_at"] = "2024-06-25T10:00:00Z"
        notification_1["notification_id"] = "notification-1"

        notification_2 = self.test_notification_data.copy()
        notification_2["created_at"] = "2024-06-25T12:00:00Z"
        notification_2["notification_id"] = "notification-2"

        notification_3 = self.test_notification_data.copy()
        notification_3["created_at"] = "2024-06-25T11:00:00Z"
        notification_3["notification_id"] = "notification-3"

        self.mock_notification_repo.get_notifications_for_coach.return_value = [
            notification_1,
            notification_2,
            notification_3,
        ]

        service = NotificationService()

        # Test grouped retrieval
        result = service.get_notifications_grouped_by_athlete("coach-789")

        # Verify sorting (newest first)
        athlete_notifications = result["athlete-456"]
        self.assertEqual(len(athlete_notifications), 3)
        self.assertEqual(
            athlete_notifications[0].notification_id, "notification-2"
        )  # 12:00 - newest
        self.assertEqual(
            athlete_notifications[1].notification_id, "notification-3"
        )  # 11:00 - middle
        self.assertEqual(
            athlete_notifications[2].notification_id, "notification-1"
        )  # 10:00 - oldest


if __name__ == "__main__":
    unittest.main()
