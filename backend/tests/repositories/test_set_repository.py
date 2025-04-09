import unittest
from unittest.mock import MagicMock, patch
from src.repositories.set_repository import SetRepository
from src.config.set_config import SetConfig


class TestSetRepository(unittest.TestCase):
    """
    Test suite for the SetRepository class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.mock_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

        with patch("boto3.resource", return_value=self.mock_dynamodb):
            self.set_repository = SetRepository()

    def test_get_set(self):
        """
        Test retrieving a set by ID
        """
        # Mock data that would be returned from DynamoDB
        mock_set_data = {
            "set_id": "set123",
            "completed_exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 1,
            "actual_reps": 8,
            "actual_weight": 225.0,
            "actual_rpe": 8.5,
        }

        # Configure mock to return our test data
        self.mock_table.get_item.return_value = {"Item": mock_set_data}

        # Call the method
        result = self.set_repository.get_set("set123")

        # Assert table was called with correct args
        self.mock_table.get_item.assert_called_once_with(Key={"set_id": "set123"})

        # Assert the result matches our mock data
        self.assertEqual(result, mock_set_data)

    def test_get_set_not_found(self):
        """
        Test retrieving a non-existent set returns None
        """
        # Configure mock to return empty response (no Item)
        self.mock_table.get_item.return_value = {}

        # Call the method
        result = self.set_repository.get_set("nonexistent")

        # Assert the result is None
        self.assertIsNone(result)

    def test_get_sets_by_exercise(self):
        """
        Test retrieving sets by exercise ID
        """
        # Mock data that would be returned from DynamoDB
        mock_sets = [
            {
                "set_id": "set1",
                "completed_exercise_id": "exercise123",
                "workout_id": "workout456",
                "set_number": 1,
                "actual_reps": 8,
                "actual_weight": 225.0,
            },
            {
                "set_id": "set2",
                "completed_exercise_id": "exercise123",
                "workout_id": "workout456",
                "set_number": 2,
                "actual_reps": 8,
                "actual_weight": 225.0,
            },
        ]

        # Configure mock to return our test data
        self.mock_table.query.return_value = {"Items": mock_sets}

        # Call the method
        result = self.set_repository.get_sets_by_exercise("exercise123")

        # Assert query was called with correct args
        self.mock_table.query.assert_called_once_with(
            IndexName=SetConfig.EXERCISE_INDEX,
            KeyConditionExpression=unittest.mock.ANY,
            Limit=20,
        )

        # Assert the result matches our mock data
        self.assertEqual(result, mock_sets)

    def test_get_sets_by_workout(self):
        """
        Test retrieving sets by workout ID
        """
        # Mock data that would be returned from DynamoDB
        mock_sets = [
            {
                "set_id": "set1",
                "completed_exercise_id": "exercise123",
                "workout_id": "workout456",
                "set_number": 1,
                "actual_reps": 8,
                "actual_weight": 225.0,
            },
            {
                "set_id": "set2",
                "completed_exercise_id": "exercise789",
                "workout_id": "workout456",
                "set_number": 1,
                "actual_reps": 12,
                "actual_weight": 135.0,
            },
        ]

        # Configure mock to return our test data
        self.mock_table.query.return_value = {"Items": mock_sets}

        # Call the method
        result = self.set_repository.get_sets_by_workout("workout456")

        # Assert query was called with correct args
        self.mock_table.query.assert_called_once_with(
            IndexName=SetConfig.WORKOUT_INDEX,
            KeyConditionExpression=unittest.mock.ANY,
            Limit=20,
        )

        # Assert the result matches our mock data
        self.assertEqual(result, mock_sets)

    def test_create_set(self):
        """
        Test creating a new set
        """
        # Test data to create
        set_data = {
            "set_id": "newset123",
            "completed_exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 1,
            "actual_reps": 8,
            "actual_weight": 225.0,
            "actual_rpe": 8.5,
        }

        # Call the method
        result = self.set_repository.create_set(set_data)

        # Assert put_item was called with correct args
        self.mock_table.put_item.assert_called_once_with(Item=set_data)

        # Assert the result matches our input data
        self.assertEqual(result, set_data)

    def test_update_set(self):
        """
        Test updating an existing set
        """
        # Test data for update
        set_id = "set123"
        update_data = {"actual_reps": 10, "actual_weight": 235.0, "actual_rpe": 9.0}

        # Mock response data
        mock_response = {
            "Attributes": {
                "set_id": set_id,
                "completed_exercise_id": "exercise456",
                "workout_id": "workout789",
                "set_number": 1,
                "actual_reps": 10,
                "actual_weight": 235.0,
                "actual_rpe": 9.0,
            }
        }

        # Configure mock to return our response
        self.mock_table.update_item.return_value = mock_response

        # Call the method
        result = self.set_repository.update_set(set_id, update_data)

        # Assert update_item was called
        self.mock_table.update_item.assert_called_once()

        # Assert the result matches our mock response
        self.assertEqual(result, mock_response.get("Attributes"))

    def test_delete_set(self):
        """
        Test deleting a set
        """
        # Mock response data
        mock_response = {
            "Attributes": {
                "set_id": "set123",
                "completed_exercise_id": "exercise456",
                "workout_id": "workout789",
            }
        }

        # Configure mock to return our response
        self.mock_table.delete_item.return_value = mock_response

        # Call the method
        result = self.set_repository.delete_set("set123")

        # Assert delete_item was called with correct args
        self.mock_table.delete_item.assert_called_once_with(
            Key={"set_id": "set123"}, ReturnValues="ALL_OLD"
        )

        # Assert the result matches our mock response
        self.assertEqual(result, mock_response.get("Attributes"))

    def test_delete_sets_by_exercise(self):
        """
        Test deleting all sets for a specific exercise
        """
        # Mock data for get_sets_by_exercise
        mock_sets = [
            {"set_id": "set1", "completed_exercise_id": "exercise123"},
            {"set_id": "set2", "completed_exercise_id": "exercise123"},
        ]

        # Create a batch writer mock
        mock_batch_writer = MagicMock()
        mock_batch_context = MagicMock()
        mock_batch_context.__enter__.return_value = mock_batch_writer
        self.mock_table.batch_writer.return_value = mock_batch_context

        # Mock get_sets_by_exercise to return our mock sets
        with patch.object(
            self.set_repository, "get_sets_by_exercise", return_value=mock_sets
        ):
            # Call the method
            result = self.set_repository.delete_sets_by_exercise("exercise123")

            # Assert batch_writer was called
            self.mock_table.batch_writer.assert_called_once()

            # Assert delete_item was called for each set
            self.assertEqual(mock_batch_writer.delete_item.call_count, 2)
            mock_batch_writer.delete_item.assert_any_call(Key={"set_id": "set1"})
            mock_batch_writer.delete_item.assert_any_call(Key={"set_id": "set2"})

            # Assert the result is the number of sets deleted
            self.assertEqual(result, 2)

    def test_delete_sets_by_workout(self):
        """
        Test deleting all sets for a specific workout
        """
        # Mock data for get_sets_by_workout
        mock_sets = [
            {"set_id": "set1", "workout_id": "workout123"},
            {"set_id": "set2", "workout_id": "workout123"},
            {"set_id": "set3", "workout_id": "workout123"},
        ]

        # Create a batch writer mock
        mock_batch_writer = MagicMock()
        mock_batch_context = MagicMock()
        mock_batch_context.__enter__.return_value = mock_batch_writer
        self.mock_table.batch_writer.return_value = mock_batch_context

        # Mock get_sets_by_workout to return our mock sets
        with patch.object(
            self.set_repository, "get_sets_by_workout", return_value=mock_sets
        ):
            # Call the method
            result = self.set_repository.delete_sets_by_workout("workout123")

            # Assert batch_writer was called
            self.mock_table.batch_writer.assert_called_once()

            # Assert delete_item was called for each set
            self.assertEqual(mock_batch_writer.delete_item.call_count, 3)
            mock_batch_writer.delete_item.assert_any_call(Key={"set_id": "set1"})
            mock_batch_writer.delete_item.assert_any_call(Key={"set_id": "set2"})
            mock_batch_writer.delete_item.assert_any_call(Key={"set_id": "set3"})

            # Assert the result is the number of sets deleted
            self.assertEqual(result, 3)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
