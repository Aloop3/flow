import unittest
from unittest.mock import patch
from src.models.notification import Notification


class TestNotification(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock datetime.now() to return consistent timestamps
        self.test_timestamp = "2024-06-25T10:30:00Z"
        self.test_notification_data = {
            "notification_id": "test-notification-123",
            "coach_id": "coach-456",
            "athlete_id": "athlete-789",
            "athlete_name": "John Athlete",
            "workout_id": "workout-abc",
            "day_info": "Day 5 (2024-06-25)",
            "workout_data": {
                "workout_id": "workout-abc",
                "exercises": [
                    {"exercise_type": "Squat", "sets": 3, "reps": 5, "weight": 225}
                ],
                "duration_minutes": 90,
            },
            "created_at": self.test_timestamp,
            "is_read": False,
            "notification_type": "workout_completion",
        }

    @patch("src.models.notification.datetime")
    def test_notification_creation_with_all_parameters(self, mock_datetime):
        """Test creating a notification with all parameters explicitly provided."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-06-25T10:30:00"

        notification = Notification(
            notification_id="test-notification-123",
            coach_id="coach-456",
            athlete_id="athlete-789",
            athlete_name="John Athlete",
            workout_id="workout-abc",
            day_info="Day 5 (2024-06-25)",
            workout_data={"test": "data"},
            created_at="2024-06-25T10:30:00Z",
            is_read=True,
            notification_type="workout_completion",
        )

        self.assertEqual(notification.notification_id, "test-notification-123")
        self.assertEqual(notification.coach_id, "coach-456")
        self.assertEqual(notification.athlete_id, "athlete-789")
        self.assertEqual(notification.athlete_name, "John Athlete")
        self.assertEqual(notification.workout_id, "workout-abc")
        self.assertEqual(notification.day_info, "Day 5 (2024-06-25)")
        self.assertEqual(notification.workout_data, {"test": "data"})
        self.assertEqual(notification.created_at, "2024-06-25T10:30:00Z")
        self.assertTrue(notification.is_read)
        self.assertEqual(notification.notification_type, "workout_completion")

    @patch("src.models.notification.datetime")
    def test_notification_creation_with_default_values(self, mock_datetime):
        """Test creating a notification with default values for optional parameters."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-06-25T10:30:00"

        notification = Notification(
            notification_id="test-notification-123",
            coach_id="coach-456",
            athlete_id="athlete-789",
            athlete_name="John Athlete",
            workout_id="workout-abc",
            day_info="Day 5 (2024-06-25)",
            workout_data={"test": "data"},
        )

        # Check defaults are applied
        self.assertFalse(notification.is_read)  # Default False
        self.assertEqual(
            notification.notification_type, "workout_completion"
        )  # Default type
        self.assertEqual(
            notification.created_at, "2024-06-25T10:30:00Z"
        )  # Auto-generated timestamp

    def test_to_dict_conversion(self):
        """Test converting notification object to dictionary."""
        notification = Notification(**self.test_notification_data)
        result_dict = notification.to_dict()

        # Verify all fields are present
        expected_keys = {
            "notification_id",
            "coach_id",
            "athlete_id",
            "athlete_name",
            "workout_id",
            "day_info",
            "workout_data",
            "created_at",
            "is_read",
            "notification_type",
        }
        self.assertEqual(set(result_dict.keys()), expected_keys)

        # Verify values match
        self.assertEqual(result_dict["notification_id"], "test-notification-123")
        self.assertEqual(result_dict["coach_id"], "coach-456")
        self.assertEqual(result_dict["athlete_id"], "athlete-789")
        self.assertEqual(result_dict["athlete_name"], "John Athlete")
        self.assertEqual(result_dict["workout_id"], "workout-abc")
        self.assertEqual(result_dict["day_info"], "Day 5 (2024-06-25)")
        self.assertFalse(result_dict["is_read"])
        self.assertEqual(result_dict["notification_type"], "workout_completion")

    def test_from_dict_conversion(self):
        """Test creating notification object from dictionary."""
        notification = Notification.from_dict(self.test_notification_data)

        self.assertEqual(notification.notification_id, "test-notification-123")
        self.assertEqual(notification.coach_id, "coach-456")
        self.assertEqual(notification.athlete_id, "athlete-789")
        self.assertEqual(notification.athlete_name, "John Athlete")
        self.assertEqual(notification.workout_id, "workout-abc")
        self.assertEqual(notification.day_info, "Day 5 (2024-06-25)")
        self.assertEqual(
            notification.workout_data, self.test_notification_data["workout_data"]
        )
        self.assertEqual(notification.created_at, self.test_timestamp)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, "workout_completion")

    @patch("src.models.notification.datetime")
    def test_from_dict_with_missing_optional_fields(self, mock_datetime):
        """Test from_dict handles missing optional fields gracefully."""
        mock_datetime.now.return_value.isoformat.return_value = "2024-06-25T10:30:00"

        minimal_data = {
            "notification_id": "test-notification-123",
            "coach_id": "coach-456",
            "athlete_id": "athlete-789",
            "athlete_name": "John Athlete",
            "workout_id": "workout-abc",
            "day_info": "Day 5 (2024-06-25)",
            "workout_data": {"test": "data"},
        }

        notification = Notification.from_dict(minimal_data)

        # Should use defaults for missing fields
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, "workout_completion")
        self.assertEqual(
            notification.created_at, "2024-06-25T10:30:00Z"
        )  # Auto-generated when missing

    def test_to_dict_from_dict_roundtrip(self):
        """Test that to_dict and from_dict are inverse operations."""
        original_notification = Notification(**self.test_notification_data)

        # Convert to dict and back
        dict_data = original_notification.to_dict()
        reconstructed_notification = Notification.from_dict(dict_data)

        # Should be identical
        self.assertEqual(
            original_notification.notification_id,
            reconstructed_notification.notification_id,
        )
        self.assertEqual(
            original_notification.coach_id, reconstructed_notification.coach_id
        )
        self.assertEqual(
            original_notification.athlete_id, reconstructed_notification.athlete_id
        )
        self.assertEqual(
            original_notification.athlete_name, reconstructed_notification.athlete_name
        )
        self.assertEqual(
            original_notification.workout_id, reconstructed_notification.workout_id
        )
        self.assertEqual(
            original_notification.day_info, reconstructed_notification.day_info
        )
        self.assertEqual(
            original_notification.workout_data, reconstructed_notification.workout_data
        )
        self.assertEqual(
            original_notification.created_at, reconstructed_notification.created_at
        )
        self.assertEqual(
            original_notification.is_read, reconstructed_notification.is_read
        )
        self.assertEqual(
            original_notification.notification_type,
            reconstructed_notification.notification_type,
        )

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification(**self.test_notification_data)

        # Initially unread
        self.assertFalse(notification.is_read)

        # Mark as read
        notification.mark_as_read()

        # Should now be read
        self.assertTrue(notification.is_read)

    def test_complex_workout_data_storage(self):
        """Test that complex workout data is stored and retrieved correctly."""
        complex_workout_data = {
            "workout_id": "workout-abc",
            "athlete_id": "athlete-789",
            "exercises": [
                {
                    "exercise_id": "ex-1",
                    "exercise_type": "Squat",
                    "sets": 3,
                    "reps": 5,
                    "weight": 225,
                    "sets_data": [
                        {
                            "reps": 5,
                            "weight": 225,
                            "completed": True,
                            "notes": "Good depth",
                        },
                        {"reps": 5, "weight": 225, "completed": True, "notes": ""},
                        {
                            "reps": 4,
                            "weight": 225,
                            "completed": True,
                            "notes": "Failed last rep",
                        },
                    ],
                }
            ],
            "start_time": "2024-06-25T10:00:00Z",
            "finish_time": "2024-06-25T11:30:00Z",
            "duration_minutes": 90,
            "notes": "Great session overall",
        }

        data = self.test_notification_data.copy()
        data["workout_data"] = complex_workout_data

        notification = Notification.from_dict(data)

        # Verify complex data is preserved
        self.assertEqual(notification.workout_data, complex_workout_data)
        self.assertEqual(
            notification.workout_data["exercises"][0]["sets_data"][0]["notes"],
            "Good depth",
        )
        self.assertEqual(notification.workout_data["duration_minutes"], 90)

    def test_notification_immutability_after_to_dict(self):
        """Test that modifying the dict returned by to_dict doesn't affect the original notification."""
        notification = Notification(**self.test_notification_data)
        result_dict = notification.to_dict()

        # Modify the returned dict
        result_dict["coach_id"] = "modified-coach"
        result_dict["workout_data"]["new_field"] = "new_value"

        # Original notification should be unchanged
        self.assertEqual(notification.coach_id, "coach-456")
        self.assertNotIn("new_field", notification.workout_data)


if __name__ == "__main__":
    unittest.main()
