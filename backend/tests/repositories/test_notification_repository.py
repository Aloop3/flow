import unittest
from unittest.mock import patch, MagicMock
from src.repositories.notification_repository import NotificationRepository
from src.config.notification_config import NotificationConfig


class TestNotificationRepository(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_notification_data = {
            "notification_id": "test-notification-123",
            "coach_id": "coach-456",
            "athlete_id": "athlete-789",
            "athlete_name": "John Athlete",
            "workout_id": "workout-abc",
            "day_info": "Day 5 (2024-06-25)",
            "workout_data": {
                "workout_id": "workout-abc",
                "exercises": [{"exercise_type": "Squat", "sets": 3}],
            },
            "created_at": "2024-06-25T10:30:00Z",
            "is_read": False,
            "notification_type": "workout_completion",
        }

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_init_creates_dynamodb_connection(self, mock_boto3):
        """Test that repository initialization creates proper DynamoDB connection."""
        # Setup mock
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_boto3.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table

        # Create repository
        repo = NotificationRepository()

        # Verify initialization
        self.assertEqual(repo.table_name, NotificationConfig.TABLE_NAME)
        mock_boto3.assert_called_once_with("dynamodb")
        mock_dynamodb.Table.assert_called_once_with(NotificationConfig.TABLE_NAME)
        self.assertEqual(repo.table, mock_table)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_create_notification_success(self, mock_boto3):
        """Test successful notification creation."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.put_item.return_value = {}

        repo = NotificationRepository()

        # Test creation
        result = repo.create_notification(self.test_notification_data)

        # Verify
        self.assertTrue(result)
        mock_table.put_item.assert_called_once_with(Item=self.test_notification_data)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_create_notification_failure(self, mock_boto3):
        """Test notification creation failure handling."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.put_item.side_effect = Exception("DynamoDB error")

        repo = NotificationRepository()

        # Test creation failure
        result = repo.create_notification(self.test_notification_data)

        # Verify
        self.assertFalse(result)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notification_success(self, mock_boto3):
        """Test successful notification retrieval."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.get_item.return_value = {"Item": self.test_notification_data}

        repo = NotificationRepository()

        # Test retrieval
        result = repo.get_notification("test-notification-123")

        # Verify
        self.assertEqual(result, self.test_notification_data)
        mock_table.get_item.assert_called_once_with(
            Key={"notification_id": "test-notification-123"}
        )

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notification_not_found(self, mock_boto3):
        """Test notification retrieval when notification doesn't exist."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.get_item.return_value = {}  # No 'Item' key when not found

        repo = NotificationRepository()

        # Test retrieval
        result = repo.get_notification("nonexistent-notification")

        # Verify
        self.assertIsNone(result)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notification_failure(self, mock_boto3):
        """Test notification retrieval failure handling."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.get_item.side_effect = Exception("DynamoDB error")

        repo = NotificationRepository()

        # Test retrieval failure
        result = repo.get_notification("test-notification-123")

        # Verify
        self.assertIsNone(result)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notifications_for_coach_success(self, mock_boto3):
        """Test successful retrieval of notifications for a coach."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.return_value = {"Items": [self.test_notification_data]}

        repo = NotificationRepository()

        # Test retrieval
        result = repo.get_notifications_for_coach("coach-456", limit=10)

        # Verify
        self.assertEqual(result, [self.test_notification_data])
        mock_table.query.assert_called_once()

        # Verify query parameters
        call_args = mock_table.query.call_args[1]
        self.assertEqual(call_args["IndexName"], NotificationConfig.COACH_INDEX)
        self.assertEqual(call_args["ScanIndexForward"], False)  # Newest first
        self.assertEqual(call_args["Limit"], 10)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notifications_for_coach_with_default_limit(self, mock_boto3):
        """Test notifications retrieval uses config default limit when none provided."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.return_value = {"Items": []}

        repo = NotificationRepository()

        # Test retrieval without limit
        repo.get_notifications_for_coach("coach-456")

        # Verify default limit is used
        call_args = mock_table.query.call_args[1]
        self.assertEqual(call_args["Limit"], NotificationConfig.MAX_ITEMS)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notifications_for_coach_unread_only(self, mock_boto3):
        """Test retrieval of only unread notifications for a coach."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.return_value = {"Items": []}

        repo = NotificationRepository()

        # Test retrieval with unread_only filter
        repo.get_notifications_for_coach("coach-456", unread_only=True)

        # Verify filter is applied
        call_args = mock_table.query.call_args[1]
        self.assertIn("FilterExpression", call_args)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_notifications_for_coach_failure(self, mock_boto3):
        """Test handling of failures when retrieving notifications for coach."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.side_effect = Exception("DynamoDB error")

        repo = NotificationRepository()

        # Test retrieval failure
        result = repo.get_notifications_for_coach("coach-456")

        # Verify
        self.assertEqual(result, [])

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_update_notification_success(self, mock_boto3):
        """Test successful notification update."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {}

        repo = NotificationRepository()

        # Test update
        update_data = {"is_read": True, "notes": "Updated notes"}
        result = repo.update_notification("test-notification-123", update_data)

        # Verify
        self.assertTrue(result)
        mock_table.update_item.assert_called_once()

        # Verify update parameters
        call_args = mock_table.update_item.call_args[1]
        self.assertEqual(call_args["Key"], {"notification_id": "test-notification-123"})
        self.assertIn("SET", call_args["UpdateExpression"])
        self.assertIn(":is_read", call_args["ExpressionAttributeValues"])
        self.assertIn(":notes", call_args["ExpressionAttributeValues"])

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_update_notification_failure(self, mock_boto3):
        """Test notification update failure handling."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.update_item.side_effect = Exception("DynamoDB error")

        repo = NotificationRepository()

        # Test update failure
        result = repo.update_notification("test-notification-123", {"is_read": True})

        # Verify
        self.assertFalse(result)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_mark_notification_as_read_success(self, mock_boto3):
        """Test successful marking notification as read."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {}

        repo = NotificationRepository()

        # Test marking as read
        result = repo.mark_notification_as_read("test-notification-123")

        # Verify
        self.assertTrue(result)
        mock_table.update_item.assert_called_once()

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_unread_count_for_coach_success(self, mock_boto3):
        """Test successful retrieval of unread count for coach."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.return_value = {"Count": 5}

        repo = NotificationRepository()

        # Test count retrieval
        result = repo.get_unread_count_for_coach("coach-456")

        # Verify
        self.assertEqual(result, 5)
        mock_table.query.assert_called_once()

        # Verify query parameters
        call_args = mock_table.query.call_args[1]
        self.assertEqual(call_args["IndexName"], NotificationConfig.COACH_INDEX)
        self.assertEqual(call_args["Select"], "COUNT")
        self.assertIn("FilterExpression", call_args)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_unread_count_for_coach_zero_count(self, mock_boto3):
        """Test unread count returns zero when no count in response."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.return_value = {}  # No 'Count' key

        repo = NotificationRepository()

        # Test count retrieval
        result = repo.get_unread_count_for_coach("coach-456")

        # Verify
        self.assertEqual(result, 0)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_get_unread_count_for_coach_failure(self, mock_boto3):
        """Test handling of failures when getting unread count."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.query.side_effect = Exception("DynamoDB error")

        repo = NotificationRepository()

        # Test count retrieval failure
        result = repo.get_unread_count_for_coach("coach-456")

        # Verify
        self.assertEqual(result, 0)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_delete_notification_success(self, mock_boto3):
        """Test successful notification deletion."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.delete_item.return_value = {}

        repo = NotificationRepository()

        # Test deletion
        result = repo.delete_notification("test-notification-123")

        # Verify
        self.assertTrue(result)
        mock_table.delete_item.assert_called_once_with(
            Key={"notification_id": "test-notification-123"}
        )

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_delete_notification_failure(self, mock_boto3):
        """Test notification deletion failure handling."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.delete_item.side_effect = Exception("DynamoDB error")

        repo = NotificationRepository()

        # Test deletion failure
        result = repo.delete_notification("test-notification-123")

        # Verify
        self.assertFalse(result)

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_dynamic_update_expression_building(self, mock_boto3):
        """Test that update expressions are built dynamically from update_data."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table
        mock_table.update_item.return_value = {}

        repo = NotificationRepository()

        # Test update with multiple fields
        update_data = {
            "is_read": True,
            "notes": "Test notes",
            "custom_field": "custom_value",
        }
        repo.update_notification("test-notification-123", update_data)

        # Verify update expression contains all fields
        call_args = mock_table.update_item.call_args[1]
        update_expression = call_args["UpdateExpression"]

        self.assertIn("is_read = :is_read", update_expression)
        self.assertIn("notes = :notes", update_expression)
        self.assertIn("custom_field = :custom_field", update_expression)

        # Verify all values are in expression attribute values
        values = call_args["ExpressionAttributeValues"]
        self.assertEqual(values[":is_read"], True)
        self.assertEqual(values[":notes"], "Test notes")
        self.assertEqual(values[":custom_field"], "custom_value")

    @patch("src.repositories.notification_repository.boto3.resource")
    def test_complex_workout_data_storage_and_retrieval(self, mock_boto3):
        """Test that complex workout data is stored and retrieved correctly."""
        # Setup mocks
        mock_table = MagicMock()
        mock_boto3.return_value.Table.return_value = mock_table

        complex_workout_data = {
            "workout_id": "workout-abc",
            "exercises": [
                {
                    "exercise_id": "ex-1",
                    "sets_data": [
                        {
                            "reps": 5,
                            "weight": 225,
                            "completed": True,
                            "notes": "Good depth",
                        }
                    ],
                }
            ],
            "duration_minutes": 90,
        }

        notification_data = self.test_notification_data.copy()
        notification_data["workout_data"] = complex_workout_data

        mock_table.put_item.return_value = {}
        mock_table.get_item.return_value = {"Item": notification_data}

        repo = NotificationRepository()

        # Test create and retrieve
        create_result = repo.create_notification(notification_data)
        retrieve_result = repo.get_notification("test-notification-123")

        # Verify complex data is preserved
        self.assertTrue(create_result)
        self.assertEqual(retrieve_result["workout_data"], complex_workout_data)


if __name__ == "__main__":
    unittest.main()
