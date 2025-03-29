import unittest
from unittest.mock import MagicMock, patch
from src.services.set_service import SetService
from src.models.set import Set

class TestSetService(unittest.TestCase):
    """
    Test suite for the SetService class
    """
    
    def setUp(self):
        """
        Set up test environment before each test
        """
        # Create mock repository
        self.set_repository_mock = MagicMock()
        
        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch('uuid.uuid4', return_value='test-uuid')
        self.uuid_mock = self.uuid_patcher.start()
        
        # Initialize service with mocked repository
        with patch('src.services.set_service.SetRepository', return_value=self.set_repository_mock):
            self.set_service = SetService()
    
    def tearDown(self):
        """
        Clean up after each test
        """
        self.uuid_patcher.stop()
    
    def test_get_set(self):
        """
        Test retrieving a set by ID
        """
        # Setup mock return value
        mock_set_data = {
            "set_id": "set123",
            "completed_exercise_id": "ex456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 10,
            "weight": 225.0,
            "rpe": 8,
            "notes": "Test notes",
            "completed": True
        }
        self.set_repository_mock.get_set.return_value = mock_set_data
        
        # Call the method
        result = self.set_service.get_set("set123")
        
        # Assert
        self.set_repository_mock.get_set.assert_called_once_with("set123")
        self.assertIsInstance(result, Set)
        self.assertEqual(result.set_id, "set123")
        self.assertEqual(result.completed_exercise_id, "ex456")
        self.assertEqual(result.workout_id, "workout789")
        self.assertEqual(result.set_number, 1)
        self.assertEqual(result.reps, 10)
        self.assertEqual(result.weight, 225.0)
        self.assertEqual(result.rpe, 8)
        self.assertEqual(result.notes, "Test notes")
        self.assertEqual(result.completed, True)
    
    def test_get_set_not_found(self):
        """
        Test retrieving a set that doesn't exist
        """
        # Setup mock return value
        self.set_repository_mock.get_set.return_value = None
        
        # Call the method
        result = self.set_service.get_set("nonexistent")
        
        # Assert
        self.set_repository_mock.get_set.assert_called_once_with("nonexistent")
        self.assertIsNone(result)
    
    def test_get_sets_for_exercise(self):
        """
        Test retrieving all sets for an exercise
        """
        # Setup mock return value
        mock_sets_data = [
            {
                "set_id": "set1",
                "completed_exercise_id": "ex123",
                "workout_id": "workout456",
                "set_number": 2,  # Not in order
                "reps": 10,
                "weight": 225.0
            },
            {
                "set_id": "set2",
                "completed_exercise_id": "ex123",
                "workout_id": "workout456",
                "set_number": 1,  # Should be sorted first
                "reps": 10,
                "weight": 225.0
            }
        ]
        self.set_repository_mock.get_sets_by_exercise.return_value = mock_sets_data
        
        # Call the method
        results = self.set_service.get_sets_for_exercise("ex123")
        
        # Assert
        self.set_repository_mock.get_sets_by_exercise.assert_called_once_with("ex123")
        self.assertEqual(len(results), 2)
        
        # Check that sets are sorted by set_number
        self.assertEqual(results[0].set_id, "set2")  # set_number 1
        self.assertEqual(results[1].set_id, "set1")  # set_number 2
        
        # Check all are Set objects
        for result in results:
            self.assertIsInstance(result, Set)
    
    def test_create_set(self):
        """
        Test creating a new set
        """
        # Call the method
        result = self.set_service.create_set(
            completed_exercise_id="ex123",
            workout_id="workout456",
            set_number=1,
            reps=10,
            weight=225.0,
            rpe=8,
            notes="Test notes",
            completed=True
        )
        
        # Assert
        expected_set_dict = {
            "set_id": "test-uuid",
            "completed_exercise_id": "ex123",
            "workout_id": "workout456",
            "set_number": 1,
            "reps": 10,
            "weight": 225.0,
            "rpe": 8,
            "notes": "Test notes",
            "completed": True
        }
        
        # Check UUID is used to generate ID
        self.uuid_mock.assert_called_once()
        
        # Check repository create method was called
        self.set_repository_mock.create_set.assert_called_once_with(expected_set_dict)
        
        # Check returned object
        self.assertIsInstance(result, Set)
        self.assertEqual(result.set_id, "test-uuid")
        self.assertEqual(result.completed_exercise_id, "ex123")
        self.assertEqual(result.workout_id, "workout456")
        self.assertEqual(result.set_number, 1)
        self.assertEqual(result.reps, 10)
        self.assertEqual(result.weight, 225.0)
        self.assertEqual(result.rpe, 8)
        self.assertEqual(result.notes, "Test notes")
        self.assertEqual(result.completed, True)
    
    def test_create_set_minimal(self):
        """
        Test creating a set with minimal required fields
        """
        # Call the method with minimal fields
        result = self.set_service.create_set(
            completed_exercise_id="ex123",
            workout_id="workout456",
            set_number=1,
            reps=10,
            weight=225.0
            # No optional fields
        )
        
        # Assert
        # Check repository create method was called once
        self.set_repository_mock.create_set.assert_called_once()
        
        # Get the actual dictionary passed to create_set
        actual_dict = self.set_repository_mock.create_set.call_args[0][0]
        
        # Check required fields
        self.assertEqual(actual_dict["set_id"], "test-uuid")
        self.assertEqual(actual_dict["completed_exercise_id"], "ex123")
        self.assertEqual(actual_dict["workout_id"], "workout456")
        self.assertEqual(actual_dict["set_number"], 1)
        self.assertEqual(actual_dict["reps"], 10)
        self.assertEqual(actual_dict["weight"], 225.0)
        
        # Check optional fields - they might be None or missing
        self.assertIn("rpe", actual_dict)
        self.assertIsNone(actual_dict["rpe"])
        self.assertIn("notes", actual_dict)
        self.assertIsNone(actual_dict["notes"])
        
        # Check returned object has expected values
        self.assertEqual(result.set_id, "test-uuid")
        self.assertEqual(result.completed_exercise_id, "ex123")
        self.assertEqual(result.workout_id, "workout456")
        self.assertEqual(result.set_number, 1)
        self.assertEqual(result.reps, 10)
        self.assertEqual(result.weight, 225.0)
        self.assertIsNone(result.rpe)
        self.assertIsNone(result.notes)
        self.assertIsNone(result.completed)
    
    def test_update_set(self):
        """
        Test updating an existing set
        """
        # Setup mock return values for get_set (before and after update)
        original_set_data = {
            "set_id": "set123",
            "completed_exercise_id": "ex456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 10,
            "weight": 225.0,
            "rpe": 8,
            "notes": "Original notes",
            "completed": True
        }
        
        updated_set_data = {
            "set_id": "set123",
            "completed_exercise_id": "ex456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 12,  # Updated
            "weight": 245.0,  # Updated
            "rpe": 9,  # Updated
            "notes": "Updated notes",  # Updated
            "completed": True
        }
        
        # Configure mock to return different values on successive calls
        self.set_repository_mock.get_set.side_effect = [original_set_data, updated_set_data]
        
        # Update data to pass to service
        update_data = {
            "reps": 12,
            "weight": 245.0,
            "rpe": 9,
            "notes": "Updated notes"
        }
        
        # Call the method
        result = self.set_service.update_set("set123", update_data)
        
        # Assert
        # Check repository methods were called correctly
        self.set_repository_mock.get_set.assert_any_call("set123")  # Called once before update
        self.set_repository_mock.update_set.assert_called_once_with("set123", update_data)
        self.set_repository_mock.get_set.assert_any_call("set123")  # Called again after update
        
        # Check the returned object has updated values
        self.assertIsInstance(result, Set)
        self.assertEqual(result.set_id, "set123")
        self.assertEqual(result.reps, 12)
        self.assertEqual(result.weight, 245.0)
        self.assertEqual(result.rpe, 9)
        self.assertEqual(result.notes, "Updated notes")
        
        # Check unchanged values remain the same
        self.assertEqual(result.completed_exercise_id, "ex456")
        self.assertEqual(result.workout_id, "workout789")
        self.assertEqual(result.set_number, 1)
        self.assertEqual(result.completed, True)
    
    def test_update_set_not_found(self):
        """
        Test updating a set that doesn't exist
        """
        # Configure mock to return None (set not found)
        self.set_repository_mock.get_set.return_value = None
        
        # Update data
        update_data = {"reps": 12, "weight": 245.0}
        
        # Call the method
        result = self.set_service.update_set("nonexistent", update_data)
        
        # Assert
        self.set_repository_mock.get_set.assert_called_once_with("nonexistent")
        # Update should not be called
        self.set_repository_mock.update_set.assert_not_called()
        # Result should be None
        self.assertIsNone(result)
    
    def test_delete_set(self):
        """
        Test deleting a set
        """
        # Configure mock to return a successful response
        self.set_repository_mock.delete_set.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        
        # Call the method
        result = self.set_service.delete_set("set123")
        
        # Assert
        self.set_repository_mock.delete_set.assert_called_once_with("set123")
        self.assertTrue(result)
    
    def test_delete_set_unsuccessful(self):
        """
        Test deleting a set that fails
        """
        # Configure mock to return an empty response (unsuccessful)
        self.set_repository_mock.delete_set.return_value = {}
        
        # Call the method
        result = self.set_service.delete_set("set123")
        
        # Assert
        self.set_repository_mock.delete_set.assert_called_once_with("set123")
        self.assertFalse(result)
    
    def test_delete_sets_for_exercise(self):
        """
        Test deleting all sets for an exercise
        """
        # Configure mock to return number of deleted sets
        self.set_repository_mock.delete_sets_by_exercise.return_value = 5
        
        # Call the method
        result = self.set_service.delete_sets_for_exercise("ex123")
        
        # Assert
        self.set_repository_mock.delete_sets_by_exercise.assert_called_once_with("ex123")
        self.assertEqual(result, 5)

if __name__ == "__main__": # pragma: no cover
    unittest.main()