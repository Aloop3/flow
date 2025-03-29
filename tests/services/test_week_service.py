import unittest
from unittest.mock import MagicMock, patch
from src.models.week import Week
from src.services.week_service import WeekService


class TestWeekService(unittest.TestCase):
    """
    Test suite for the WeekService class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.week_repository_mock = MagicMock()
        self.day_repository_mock = MagicMock()
        
        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch('uuid.uuid4', return_value='test-uuid')
        self.uuid_mock = self.uuid_patcher.start()
        
        # Initialize service with mocked repositories
        with patch('src.services.week_service.WeekRepository', return_value=self.week_repository_mock), \
             patch('src.services.week_service.DayRepository', return_value=self.day_repository_mock):
            self.week_service = WeekService()
    
    def tearDown(self):
        """
        Clean up after each test method
        """
        self.uuid_patcher.stop()
    
    def test_get_week_found(self):
        """
        Test retrieving a week by ID when the week exists
        """
        # Mock data that would be returned from the repository
        mock_week_data = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Test week"
        }
        
        # Configure mock to return our test data
        self.week_repository_mock.get_week.return_value = mock_week_data
        
        # Call the service method
        result = self.week_service.get_week("week123")
        
        # Assert repository was called with correct ID
        self.week_repository_mock.get_week.assert_called_once_with("week123")
        
        # Assert the result is a Week instance with correct data
        self.assertIsInstance(result, Week)
        self.assertEqual(result.week_id, "week123")
        self.assertEqual(result.block_id, "block456")
        self.assertEqual(result.week_number, 1)
        self.assertEqual(result.notes, "Test week")
    
    def test_get_week_not_found(self):
        """
        Test retrieving a non-existent week returns None
        """
        # Configure mock to return None (week not found)
        self.week_repository_mock.get_week.return_value = None
        
        # Call the service method
        result = self.week_service.get_week("nonexistent")
        
        # Assert repository was called with correct ID
        self.week_repository_mock.get_week.assert_called_once_with("nonexistent")
        
        # Assert the result is None
        self.assertIsNone(result)
    
    def test_get_weeks_for_block(self):
        """
        Test retrieving all weeks for a block
        """
        # Mock data for weeks
        mock_weeks_data = [
            {
                "week_id": "week1",
                "block_id": "block123",
                "week_number": 1,
                "notes": "Week 1 notes"
            },
            {
                "week_id": "week2",
                "block_id": "block123",
                "week_number": 2,
                "notes": "Week 2 notes"
            }
        ]
        
        # Configure mock to return our test data
        self.week_repository_mock.get_weeks_by_block.return_value = mock_weeks_data
        
        # Call the service method
        result = self.week_service.get_weeks_for_block("block123")
        
        # Assert repository was called with correct block ID
        self.week_repository_mock.get_weeks_by_block.assert_called_once_with("block123")
        
        # Assert the result is a list of Week objects
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Week)
        self.assertEqual(result[0].week_id, "week1")
        self.assertEqual(result[0].block_id, "block123")
        self.assertEqual(result[1].week_id, "week2")
        self.assertEqual(result[1].week_number, 2)
    
    def test_get_weeks_for_block_empty(self):
        """
        Test retrieving weeks for a block that has no weeks
        """
        # Configure mock to return an empty list
        self.week_repository_mock.get_weeks_by_block.return_value = []
        
        # Call the service method
        result = self.week_service.get_weeks_for_block("empty-block")
        
        # Assert repository was called with correct block ID
        self.week_repository_mock.get_weeks_by_block.assert_called_once_with("empty-block")
        
        # Assert the result is an empty list
        self.assertEqual(result, [])
    
    def test_create_week(self):
        """
        Test creating a new week
        """
        # Call the service method
        result = self.week_service.create_week(
            block_id="block123",
            week_number=1,
            notes="Test week notes"
        )
        
        # Assert the UUID function was called
        self.uuid_mock.assert_called()
        
        # Assert repository create method was called with correct data
        expected_week_dict = {
            "week_id": "test-uuid",
            "block_id": "block123",
            "week_number": 1,
            "notes": "Test week notes"
        }
        
        self.week_repository_mock.create_week.assert_called_once()
        actual_arg = self.week_repository_mock.create_week.call_args[0][0]
        
        # Check that all keys match the expected values
        for key, value in expected_week_dict.items():
            self.assertEqual(actual_arg[key], value)
        
        # Assert the returned object is a Week with correct data
        self.assertIsInstance(result, Week)
        self.assertEqual(result.week_id, "test-uuid")
        self.assertEqual(result.block_id, "block123")
        self.assertEqual(result.week_number, 1)
        self.assertEqual(result.notes, "Test week notes")
    
    def test_create_week_without_notes(self):
        """
        Test creating a week without providing notes
        """
        # Call the service method without notes
        result = self.week_service.create_week(
            block_id="block123",
            week_number=1
        )
        
        # Assert repository create method was called with correct data
        expected_week_dict = {
            "week_id": "test-uuid",
            "block_id": "block123",
            "week_number": 1,
            "notes": ""  # Default empty string from Week model
        }
        
        self.week_repository_mock.create_week.assert_called_once()
        actual_arg = self.week_repository_mock.create_week.call_args[0][0]
        
        # Check that all keys match the expected values
        for key, value in expected_week_dict.items():
            self.assertEqual(actual_arg[key], value)
        
        # Assert the returned object has correct data
        self.assertEqual(result.notes, "")
    
    def test_update_week(self):
        """
        Test updating a week
        """
        # Mock data for the updated week
        updated_week_data = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Updated notes"  # Changed from original
        }
        
        # Configure mocks
        self.week_repository_mock.update_week.return_value = {"Attributes": {"notes": "Updated notes"}}
        self.week_repository_mock.get_week.return_value = updated_week_data
        
        # Data to update
        update_data = {
            "notes": "Updated notes"
        }
        
        # Call the service method
        result = self.week_service.update_week("week123", update_data)
        
        # Assert repository methods were called correctly
        self.week_repository_mock.update_week.assert_called_once_with("week123", update_data)
        self.week_repository_mock.get_week.assert_called_once_with("week123")
        
        # Assert the returned object is a Week with updated data
        self.assertIsInstance(result, Week)
        self.assertEqual(result.notes, "Updated notes")
        self.assertEqual(result.week_id, "week123")
    
    def test_update_week_not_found(self):
        """
        Test updating a week that doesn't exist
        """
        # Configure mock to return None after update (week not found)
        self.week_repository_mock.update_week.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        self.week_repository_mock.get_week.return_value = None
        
        # Call the service method with update data
        result = self.week_service.update_week("nonexistent", {"notes": "Updated notes"})
        
        # Assert repository methods were called
        self.week_repository_mock.update_week.assert_called_once_with("nonexistent", {"notes": "Updated notes"})
        self.week_repository_mock.get_week.assert_called_once_with("nonexistent")
        
        # Assert the result is None (week not found)
        self.assertIsNone(result)
    
    def test_delete_week(self):
        """
        Test deleting a week
        """
        # Configure mock to return a success response for delete_week
        self.week_repository_mock.delete_week.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        
        # Configure mock for cascade delete of days
        self.day_repository_mock.delete_days_by_week.return_value = 3  # 3 days deleted
        
        # Call the service method
        result = self.week_service.delete_week("week123")
        
        # Assert cascade delete of days was called first
        self.day_repository_mock.delete_days_by_week.assert_called_once_with("week123")
        
        # Assert week deletion was called
        self.week_repository_mock.delete_week.assert_called_once_with("week123")
        
        # Assert the result is True (successful deletion)
        self.assertTrue(result)
    
    def test_delete_week_failure(self):
        """
        Test deletion failure when the week doesn't exist
        """
        # Configure mock to return None (unsuccessful deletion)
        self.week_repository_mock.delete_week.return_value = None
        
        # Configure mock for cascade delete of days
        self.day_repository_mock.delete_days_by_week.return_value = 0  # No days deleted
        
        # Call the service method
        result = self.week_service.delete_week("nonexistent")
        
        # Assert cascade delete of days was still called
        self.day_repository_mock.delete_days_by_week.assert_called_once_with("nonexistent")
        
        # Assert week deletion was called
        self.week_repository_mock.delete_week.assert_called_once_with("nonexistent")
        
        # Assert the result is False (unsuccessful deletion)
        self.assertFalse(result)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()