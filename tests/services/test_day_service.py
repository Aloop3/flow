import unittest
from unittest.mock import MagicMock, patch
from src.models.day import Day
from src.services.day_service import DayService


class TestDayService(unittest.TestCase):
    """Test suite for the DayService"""

    def setUp(self):
        """Set up test environment before each test method"""
        self.day_repository_mock = MagicMock()
        self.exercise_repository_mock = MagicMock()

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value="test-uuid")
        self.uuid_mock = self.uuid_patcher.start()

        # Initialize service with mocked repositories
        with patch(
            "src.services.day_service.DayRepository",
            return_value=self.day_repository_mock,
        ), patch(
            "src.services.day_service.ExerciseRepository",
            return_value=self.exercise_repository_mock,
        ):
            self.day_service = DayService()

    def tearDown(self):
        """Clean up after each test method"""
        self.uuid_patcher.stop()

    def test_get_day(self):
        """Test retrieving a day by ID"""
        # Mock data that would be returned from the repository
        mock_day_data = {
            "day_id": "day123",
            "week_id": 456,
            "day_number": 1,
            "date": "2025-03-15",
            "focus": "squat",
            "notes": "Heavy squat day",
        }

        # Configure mock to return our test data
        self.day_repository_mock.get_day.return_value = mock_day_data

        # Call the service method
        result = self.day_service.get_day("day123")

        # Assert repository was called with correct ID
        self.day_repository_mock.get_day.assert_called_once_with("day123")

        # Assert the result is a Day instance with correct data
        self.assertIsInstance(result, Day)
        self.assertEqual(result.day_id, "day123")
        self.assertEqual(result.week_id, 456)
        self.assertEqual(result.day_number, 1)
        self.assertEqual(result.date, "2025-03-15")
        self.assertEqual(result.focus, "squat")
        self.assertEqual(result.notes, "Heavy squat day")

    def test_get_day_not_found(self):
        """Test retrieving a non-existent day returns None"""
        # Configure mock to return None (day not found)
        self.day_repository_mock.get_day.return_value = None

        # Call the service method
        result = self.day_service.get_day("nonexistent")

        # Assert repository was called with correct ID
        self.day_repository_mock.get_day.assert_called_once_with("nonexistent")

        # Assert the result is None
        self.assertIsNone(result)

    def test_get_days_for_week(self):
        """Test retrieving all days for a week"""
        # Mock data that would be returned from the repository
        mock_days_data = [
            {
                "day_id": "day1",
                "week_id": 123,
                "day_number": 1,
                "date": "2025-03-15",
                "focus": "squat",
                "notes": "Heavy squat day",
            },
            {
                "day_id": "day2",
                "week_id": 123,
                "day_number": 2,
                "date": "2025-03-16",
                "focus": "bench",
                "notes": "Volume bench day",
            },
        ]

        # Configure mock to return our test data
        self.day_repository_mock.get_days_by_week.return_value = mock_days_data

        # Call the service method
        result = self.day_service.get_days_for_week(123)

        # Assert repository was called with correct week ID
        self.day_repository_mock.get_days_by_week.assert_called_once_with(123)

        # Assert the result is a list of Day instances with correct data
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Day)
        self.assertEqual(result[0].day_id, "day1")
        self.assertEqual(result[0].focus, "squat")
        self.assertEqual(result[1].day_id, "day2")
        self.assertEqual(result[1].focus, "bench")

    def test_create_day(self):
        """Test creating a new day"""
        # Call the service method
        result = self.day_service.create_day(
            week_id=123,
            day_number=3,
            date="2025-03-17",
            focus="deadlift",
            notes="Max effort deadlift day",
        )

        # Assert the UUID function was called
        self.uuid_mock.assert_called()

        # Assert repository create method was called with correct data
        expected_day_dict = {
            "day_id": "test-uuid",
            "week_id": 123,
            "day_number": 3,
            "date": "2025-03-17",
            "focus": "deadlift",
            "notes": "Max effort deadlift day",
        }

        self.day_repository_mock.create_day.assert_called_once()
        actual_arg = self.day_repository_mock.create_day.call_args[0][0]

        # Check that all keys match the expected values
        for key, value in expected_day_dict.items():
            self.assertEqual(actual_arg[key], value)

        # Assert the returned object is a Day with correct data
        self.assertIsInstance(result, Day)
        self.assertEqual(result.day_id, "test-uuid")
        self.assertEqual(result.week_id, 123)
        self.assertEqual(result.day_number, 3)
        self.assertEqual(result.date, "2025-03-17")
        self.assertEqual(result.focus, "deadlift")
        self.assertEqual(result.notes, "Max effort deadlift day")

    def test_create_day_minimal(self):
        """Test creating a day with minimal information"""
        # Call the service method with only required fields
        result = self.day_service.create_day(
            week_id=123, day_number=4, date="2025-03-18"
        )

        # Check repository was called with correct data
        self.day_repository_mock.create_day.assert_called_once()
        actual_arg = self.day_repository_mock.create_day.call_args[0][0]

        # Check the optional fields have default values
        self.assertEqual(actual_arg["focus"], "")
        self.assertEqual(actual_arg["notes"], "")

        # Assert the returned object has the correct data
        self.assertEqual(result.week_id, 123)
        self.assertEqual(result.day_number, 4)
        self.assertEqual(result.date, "2025-03-18")
        self.assertEqual(result.focus, "")
        self.assertEqual(result.notes, "")

    def test_update_day(self):
        """Test updating a day"""
        # Mock data for the updated day
        updated_day_data = {
            "day_id": "day123",
            "week_id": 456,
            "day_number": 1,
            "date": "2025-03-15",
            "focus": "squat",
            "notes": "Updated notes for squat day",
        }

        # Configure mocks
        self.day_repository_mock.update_day.return_value = {
            "Attributes": {"notes": "Updated notes for squat day"}
        }
        self.day_repository_mock.get_day.return_value = updated_day_data

        # Data to update
        update_data = {"notes": "Updated notes for squat day"}

        # Call the service method
        result = self.day_service.update_day("day123", update_data)

        # Assert repository methods were called correctly
        self.day_repository_mock.update_day.assert_called_once_with(
            "day123", update_data
        )
        self.day_repository_mock.get_day.assert_called_once_with("day123")

        # Assert the returned object has the updated values
        self.assertIsInstance(result, Day)
        self.assertEqual(result.notes, "Updated notes for squat day")

        # Assert the other values remain unchanged
        self.assertEqual(result.day_id, "day123")
        self.assertEqual(result.focus, "squat")

    def test_delete_day(self):
        """Test deleting a day and its exercises (cascading delete)"""
        # Configure mock responses
        self.exercise_repository_mock.delete_exercises_by_day.return_value = 3
        self.day_repository_mock.delete_day.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        # Call the service method
        result = self.day_service.delete_day("day123")

        # Assert repository methods were called in the correct order with correct ID
        self.exercise_repository_mock.delete_exercises_by_day.assert_called_once_with(
            "day123"
        )
        self.day_repository_mock.delete_day.assert_called_once_with("day123")

        # Assert the result is True (successful deletion)
        self.assertTrue(result)

    def test_get_days_for_week_empty(self):
        """Test retrieving days for a week that has no days"""
        # Configure mock to return an empty list
        self.day_repository_mock.get_days_by_week.return_value = []

        # Call the service method
        result = self.day_service.get_days_for_week(999)

        # Assert repository was called with correct week ID
        self.day_repository_mock.get_days_by_week.assert_called_once_with(999)

        # Assert the result is an empty list
        self.assertEqual(result, [])

    def test_update_day_not_found(self):
        """Test updating a day that doesn't exist"""
        # Configure mock to return None after update (day not found)
        self.day_repository_mock.update_day.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }
        self.day_repository_mock.get_day.return_value = None

        # Call the service method
        result = self.day_service.update_day("nonexistent", {"notes": "Updated notes"})

        # Assert repository methods were called
        self.day_repository_mock.update_day.assert_called_once()
        self.day_repository_mock.get_day.assert_called_once_with("nonexistent")

        # Assert the result is None (day not found)
        self.assertIsNone(result)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
