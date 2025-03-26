import unittest
from unittest.mock import MagicMock, patch, call
from src.repositories.workout_repository import WorkoutRepository

class TestWorkoutRepository(unittest.TestCase):
    """
    Test suite for the WorkoutRepository class with set-level support
    """
    
    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.mock_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table
        
        # Mock SetRepository
        self.mock_set_repository = MagicMock()
        
        # Patch boto3 resource and SetRepository in constructor
        with patch('boto3.resource', return_value=self.mock_dynamodb), \
             patch('src.repositories.workout_repository.SetRepository', return_value=self.mock_set_repository):
            self.workout_repository = WorkoutRepository()
    
    def test_get_workout_with_sets(self):
        """
        Test retrieving a workout with its sets
        """
        # Mock data for a workout with exercises
        mock_workout = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "exercise1",
                    "exercise_type": "Squat",
                    "actual_sets": 3
                },
                {
                    "completed_id": "exercise2",
                    "exercise_type": "Bench Press",
                    "actual_sets": 3
                }
            ]
        }
        
        # Mock data for sets
        mock_sets = [
            {
                "set_id": "set1",
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123",
                "set_number": 1,
                "actual_reps": 5,
                "actual_weight": 315.0
            },
            {
                "set_id": "set2",
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123",
                "set_number": 2,
                "actual_reps": 5,
                "actual_weight": 315.0
            },
            {
                "set_id": "set3",
                "completed_exercise_id": "exercise2",
                "workout_id": "workout123",
                "set_number": 1,
                "actual_reps": 8,
                "actual_weight": 225.0
            }
        ]
        
        # Configure mocks
        self.mock_table.get_item.return_value = {"Item": mock_workout}
        self.mock_set_repository.get_sets_by_workout.return_value = mock_sets
        
        # Call the method
        result = self.workout_repository.get_workout("workout123")
        
        # Assert get_item was called with correct args
        self.mock_table.get_item.assert_called_once_with(
            Key={"workout_id": "workout123"}
        )
        
        # Assert get_sets_by_workout was called with correct workout ID
        self.mock_set_repository.get_sets_by_workout.assert_called_once_with("workout123")
        
        # Assert the result contains the workout data
        self.assertEqual(result["workout_id"], "workout123")
        self.assertEqual(result["athlete_id"], "athlete456")
        
        # Assert the sets were added to the correct exercises
        self.assertEqual(len(result["exercises"]), 2)
        
        # First exercise should have 2 sets
        exercise1 = result["exercises"][0]
        self.assertEqual(exercise1["completed_id"], "exercise1")
        self.assertTrue("sets" in exercise1)
        self.assertEqual(len(exercise1["sets"]), 2)
        
        # Second exercise should have 1 set
        exercise2 = result["exercises"][1]
        self.assertEqual(exercise2["completed_id"], "exercise2")
        self.assertTrue("sets" in exercise2)
        self.assertEqual(len(exercise2["sets"]), 1)
    
    def test_create_workout_with_sets(self):
        """
        Test creating a workout with sets
        """
        # Test data with exercises and sets
        workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "exercise1",
                    "exercise_type": "Squat",
                    "sets": [
                        {
                            "set_id": "set1",
                            "set_number": 1,
                            "actual_reps": 5,
                            "actual_weight": 315.0
                        },
                        {
                            "set_id": "set2",
                            "set_number": 2,
                            "actual_reps": 5,
                            "actual_weight": 315.0
                        }
                    ]
                },
                {
                    "completed_id": "exercise2",
                    "exercise_type": "Bench Press",
                    "sets": [
                        {
                            "set_id": "set3",
                            "set_number": 1,
                            "actual_reps": 8,
                            "actual_weight": 225.0
                        }
                    ]
                }
            ]
        }
        
        # Expected workout data after sets are removed
        expected_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "exercise1",
                    "exercise_type": "Squat"
                },
                {
                    "completed_id": "exercise2",
                    "exercise_type": "Bench Press"
                }
            ]
        }
        
        # Call the method
        self.workout_repository.create_workout(workout_data)
        
        # Assert that put_item was called on the workout table
        self.mock_table.put_item.assert_called_once()
        
        # Assert that create_set was called for each set
        self.assertEqual(self.mock_set_repository.create_set.call_count, 3)
        
        # Verify the calls to create_set
        set1 = {
            "set_id": "set1",
            "set_number": 1,
            "actual_reps": 5,
            "actual_weight": 315.0,
            "completed_exercise_id": "exercise1",
            "workout_id": "workout123"
        }
        
        set2 = {
            "set_id": "set2",
            "set_number": 2,
            "actual_reps": 5,
            "actual_weight": 315.0,
            "completed_exercise_id": "exercise1",
            "workout_id": "workout123"
        }
        
        set3 = {
            "set_id": "set3",
            "set_number": 1,
            "actual_reps": 8,
            "actual_weight": 225.0,
            "completed_exercise_id": "exercise2",
            "workout_id": "workout123"
        }
        
        self.mock_set_repository.create_set.assert_any_call(set1)
        self.mock_set_repository.create_set.assert_any_call(set2)
        self.mock_set_repository.create_set.assert_any_call(set3)
    
    def test_update_workout_with_sets(self):
        """
        Test updating a workout with sets
        """
        # Test data for update
        workout_id = "workout123"
        update_data = {
            "date": "2025-03-16",  # Updated date
            "exercises": [
                {
                    "completed_id": "exercise1",
                    "sets": [
                        {
                            "set_id": "existing_set1",
                            "set_number": 1,
                            "actual_reps": 6,  # Updated reps
                            "actual_weight": 325.0  # Updated weight
                        },
                        {
                            "set_number": 2,  # New set (no set_id)
                            "actual_reps": 6,
                            "actual_weight": 325.0
                        }
                    ]
                }
            ]
        }
        
        # Mock existing sets
        existing_sets = [
            {
                "set_id": "existing_set1",
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123",
                "set_number": 1,
                "actual_reps": 5,
                "actual_weight": 315.0
            },
            {
                "set_id": "existing_set2",
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123",
                "set_number": 2,
                "actual_reps": 5,
                "actual_weight": 315.0
            }
        ]
        
        # Configure mocks
        self.mock_set_repository.get_sets_by_exercise.return_value = existing_sets
        
        # Call the method
        self.workout_repository.update_workout(workout_id, update_data)
        
        # Assert get_sets_by_exercise was called
        self.mock_set_repository.get_sets_by_exercise.assert_called_with("exercise1")
        
        # Assert update_set was called for the existing set
        self.mock_set_repository.update_set.assert_called_with(
            "existing_set1",
            {
                "set_id": "existing_set1",
                "set_number": 1,
                "actual_reps": 6,
                "actual_weight": 325.0
            }
        )
        
        # Assert create_set was called for the new set
        self.mock_set_repository.create_set.assert_called_with({
            "set_number": 2,
            "actual_reps": 6,
            "actual_weight": 325.0,
            "completed_exercise_id": "exercise1",
            "workout_id": "workout123"
        })
        
        # Assert delete_set was called for the set that wasn't in the update
        self.mock_set_repository.delete_set.assert_called_with("existing_set2")
        
        # Assert update was called on the workout itself
        self.mock_table.update_item.assert_called_once()
    
    def test_delete_workout_with_sets(self):
        """
        Test deleting a workout and its sets
        """
        # Mock response data
        mock_response = {
            "Attributes": {
                "workout_id": "workout123",
                "athlete_id": "athlete456"
            }
        }
        
        # Configure mock
        self.mock_table.delete_item.return_value = mock_response
        
        # Call the method
        result = self.workout_repository.delete_workout("workout123")
        
        # Assert delete_sets_by_workout was called first
        self.mock_set_repository.delete_sets_by_workout.assert_called_once_with("workout123")
        
        # Assert delete_item was called on the workout
        self.mock_table.delete_item.assert_called_once_with(
            Key={"workout_id": "workout123"},
            ReturnValues="ALL_OLD"
        )
        
        # Assert the result matches our mock response
        self.assertEqual(result, mock_response.get("Attributes"))


if __name__ == "__main__": # pragma: no cover
    unittest.main()