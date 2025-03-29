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
    
    def test_get_workout_not_found(self):
        """
        Test retrieving a workout that doesn't exist
        """
        # Configure mock to return None (no item found)
        self.mock_table.get_item.return_value = {"Item": None}
        
        # Call the method
        result = self.workout_repository.get_workout("nonexistent")
        
        # Assert get_item was called
        self.mock_table.get_item.assert_called_once()
        
        # Assert get_sets_by_workout was NOT called
        self.mock_set_repository.get_sets_by_workout.assert_not_called()
        
        # Assert the result is None
        self.assertIsNone(result)
    
    def test_get_workouts_by_athlete(self):
        """
        Test retrieving all workouts for an athlete
        """
        # Mock data for workouts
        mock_workouts = [
            {
                "workout_id": "workout1",
                "athlete_id": "athlete123",
                "date": "2025-03-01",
                "exercises": [
                    {"completed_id": "ex1", "exercise_type": "Squat"}
                ]
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete123",
                "date": "2025-03-03",
                "exercises": [
                    {"completed_id": "ex2", "exercise_type": "Bench Press"}
                ]
            }
        ]
        
        # Mock data for sets
        mock_sets_workout1 = [
            {
                "set_id": "set1",
                "completed_exercise_id": "ex1",
                "workout_id": "workout1",
                "set_number": 1
            }
        ]
        
        mock_sets_workout2 = [
            {
                "set_id": "set2",
                "completed_exercise_id": "ex2",
                "workout_id": "workout2",
                "set_number": 1
            }
        ]
        
        # Configure mocks
        self.mock_table.query.return_value = {"Items": mock_workouts}
        self.mock_set_repository.get_sets_by_workout.side_effect = [
            mock_sets_workout1, mock_sets_workout2
        ]
        
        # Call the method
        result = self.workout_repository.get_workouts_by_athlete("athlete123")
        
        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once_with(
            IndexName="athlete-index",
            KeyConditionExpression=unittest.mock.ANY
        )
        
        # Assert get_sets_by_workout was called for each workout
        self.mock_set_repository.get_sets_by_workout.assert_any_call("workout1")
        self.mock_set_repository.get_sets_by_workout.assert_any_call("workout2")
        self.assertEqual(self.mock_set_repository.get_sets_by_workout.call_count, 2)
        
        # Assert correct number of workouts returned
        self.assertEqual(len(result), 2)
        
        # Assert sets were added to exercises
        self.assertTrue("sets" in result[0]["exercises"][0])
        self.assertTrue("sets" in result[1]["exercises"][0])
    
    def test_get_workout_by_day(self):
        """
        Test retrieving a workout by athlete and day
        """
        # Mock data for the workout
        mock_workout = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "exercises": [
                {"completed_id": "exercise1", "exercise_type": "Squat"}
            ]
        }
        
        # Mock data for sets
        mock_sets = [
            {
                "set_id": "set1",
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123",
                "set_number": 1
            }
        ]
        
        # Configure mocks
        self.mock_table.scan.return_value = {"Items": [mock_workout]}
        self.mock_set_repository.get_sets_by_workout.return_value = mock_sets
        
        # Call the method
        result = self.workout_repository.get_workout_by_day("athlete456", "day789")
        
        # Assert scan was called with correct filter
        self.mock_table.scan.assert_called_once()
        
        # Assert get_sets_by_workout was called
        self.mock_set_repository.get_sets_by_workout.assert_called_once_with("workout123")
        
        # Assert the result contains the workout data
        self.assertEqual(result["workout_id"], "workout123")
        self.assertEqual(result["athlete_id"], "athlete456")
        
        # Assert sets were added to exercises
        self.assertTrue("sets" in result["exercises"][0])
    
    def test_get_workout_by_day_not_found(self):
        """
        Test retrieving a workout by day when it doesn't exist
        """
        # Configure mock to return empty list
        self.mock_table.scan.return_value = {"Items": []}
        
        # Call the method
        result = self.workout_repository.get_workout_by_day("athlete456", "nonexistent-day")
        
        # Assert scan was called
        self.mock_table.scan.assert_called_once()
        
        # Assert get_sets_by_workout was NOT called
        self.mock_set_repository.get_sets_by_workout.assert_not_called()
        
        # Assert the result is None
        self.assertIsNone(result)
    
    def test_get_completed_workouts_since(self):
        """
        Test retrieving completed workouts since a date
        """
        # Mock data for completed workouts
        mock_workouts = [
            {
                "workout_id": "workout1",
                "athlete_id": "athlete123",
                "date": "2025-03-01",
                "status": "completed",
                "exercises": [
                    {"completed_id": "ex1", "exercise_type": "Squat"}
                ]
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete123",
                "date": "2025-03-03",
                "status": "completed",
                "exercises": [
                    {"completed_id": "ex2", "exercise_type": "Bench Press"}
                ]
            }
        ]
        
        # Mock data for sets
        mock_sets_workout1 = [
            {
                "set_id": "set1",
                "completed_exercise_id": "ex1",
                "workout_id": "workout1",
                "set_number": 1
            }
        ]
        
        mock_sets_workout2 = [
            {
                "set_id": "set2",
                "completed_exercise_id": "ex2",
                "workout_id": "workout2",
                "set_number": 1
            }
        ]
        
        # Configure mocks
        self.mock_table.query.return_value = {"Items": mock_workouts}
        self.mock_set_repository.get_sets_by_workout.side_effect = [
            mock_sets_workout1, mock_sets_workout2
        ]
        
        # Call the method
        result = self.workout_repository.get_completed_workouts_since("athlete123", "2025-03-01")
        
        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once()
        
        # Assert get_sets_by_workout was called for each workout
        self.mock_set_repository.get_sets_by_workout.assert_any_call("workout1")
        self.mock_set_repository.get_sets_by_workout.assert_any_call("workout2")
        
        # Assert correct number of workouts returned
        self.assertEqual(len(result), 2)
        
        # Assert sets were added to exercises
        self.assertTrue("sets" in result[0]["exercises"][0])
        self.assertTrue("sets" in result[1]["exercises"][0])
    
    def test_get_completed_exercises_by_type(self):
        """
        Test retrieving completed exercises by type
        """
        # Mock data for workouts
        mock_workouts = [
            {
                "workout_id": "workout1",
                "athlete_id": "athlete123",
                "date": "2025-03-01",
                "status": "completed",
                "exercises": [
                    {"completed_id": "ex1", "type": "Squat", "sets": []},
                    {"completed_id": "ex2", "type": "Bench Press", "sets": []}
                ]
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete123",
                "date": "2025-03-03",
                "status": "completed",
                "exercises": [
                    {"completed_id": "ex3", "type": "Squat", "sets": []},
                    {"completed_id": "ex4", "type": "Deadlift", "sets": []}
                ]
            }
        ]
        
        # Configure mock to return workouts
        with patch.object(self.workout_repository, 'get_workouts_by_athlete', return_value=mock_workouts):
            # Call the method
            result = self.workout_repository.get_completed_exercises_by_type("athlete123", "Squat")
            
            # Assert get_workouts_by_athlete was called
            self.workout_repository.get_workouts_by_athlete.assert_called_once_with("athlete123")
            
            # Assert the result contains only Squat exercises
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["type"], "Squat")
            self.assertEqual(result[1]["type"], "Squat")
            
            # Assert workout data was added to exercises
            self.assertEqual(result[0]["date"], "2025-03-01")
            self.assertEqual(result[0]["workout_status"], "completed")
            self.assertEqual(result[1]["date"], "2025-03-03")
            self.assertEqual(result[1]["workout_status"], "completed")
    
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
    
    def test_update_workout_with_exercises_list(self):
        """
        Test updating a workout with an exercises list but no sets
        """
        # Test data for update that includes an exercises list directly
        workout_id = "workout123"
        update_data = {
            "date": "2025-03-16",
            "exercises": [  # This is the direct exercises list, not exercises with sets inside
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
        self.workout_repository.update_workout(workout_id, update_data)
        
        # Assert update_item was called with correct parameters
        self.mock_table.update_item.assert_called_once()
        
        # Check that the update expression contains "exercises = :exercises"
        call_args = self.mock_table.update_item.call_args[1]
        self.assertIn("exercises = :exercises", call_args["UpdateExpression"])
        
        # Check that the expression attributes include the exercises list
        self.assertEqual(len(call_args["ExpressionAttributeValues"][":exercises"]), 2)
        self.assertEqual(call_args["ExpressionAttributeValues"][":exercises"][0]["exercise_type"], "Squat")
        self.assertEqual(call_args["ExpressionAttributeValues"][":exercises"][1]["exercise_type"], "Bench Press")
    
    def test_update_workout_with_exercises_list(self):
        """
        Test updating a workout with an exercises list but no sets
        """
        # Test data for update that includes an exercises list directly
        workout_id = "workout123"
        update_data = {
            "date": "2025-03-16",
            "exercises": [  # This is the direct exercises list, not exercises with sets inside
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
        self.workout_repository.update_workout(workout_id, update_data)

        # Assert update_item was called with correct parameters
        self.mock_table.update_item.assert_called_once()

        # Verify the update expression doesn't contain exercises
        # (because exercises are processed separately and removed from update_dict)
        call_args = self.mock_table.update_item.call_args[1]
        self.assertIn("date = :date", call_args["UpdateExpression"])
        self.assertNotIn("exercises", call_args["UpdateExpression"])
        
        # Check that set operations were not called (since there are no sets)
        self.mock_set_repository.get_sets_by_exercise.assert_not_called()
        self.mock_set_repository.update_set.assert_not_called()
        self.mock_set_repository.create_set.assert_not_called()
        self.mock_set_repository.delete_set.assert_not_called()

    def test_update_workout_without_sets(self):
        """
        Test updating a workout without modifying sets
        """
        # Test data for update (no exercises/sets)
        workout_id = "workout123"
        update_data = {
            "date": "2025-03-16",  # Updated date
            "notes": "Updated workout notes"
        }
        
        # Call the method
        self.workout_repository.update_workout(workout_id, update_data)
        
        # Assert set repository methods were NOT called
        self.mock_set_repository.get_sets_by_exercise.assert_not_called()
        self.mock_set_repository.update_set.assert_not_called()
        self.mock_set_repository.create_set.assert_not_called()
        self.mock_set_repository.delete_set.assert_not_called()
        
        # Assert update was called on the workout itself
        self.mock_table.update_item.assert_called_once()
        
        # Check update expression and values
        call_args = self.mock_table.update_item.call_args[1]
        self.assertIn("set date = :date, notes = :notes", call_args["UpdateExpression"])
        self.assertEqual(call_args["ExpressionAttributeValues"][":date"], "2025-03-16")
        self.assertEqual(call_args["ExpressionAttributeValues"][":notes"], "Updated workout notes")
    
    def test_update_workout_with_exercises_and_sets(self):
        """
        Test updating a workout with exercises that contain sets
        """
        # Test data for update that includes exercises with sets
        workout_id = "workout123"
        update_data = {
            "date": "2025-03-16",
            "exercises": [
                {
                    "completed_id": "exercise1",
                    "exercise_type": "Squat",
                    "sets": [
                        {
                            "set_id": "set1",  # Existing set to update
                            "set_number": 1,
                            "actual_reps": 6,  # Updated reps
                            "actual_weight": 325.0  # Updated weight
                        },
                        {
                            "set_id": "set_new",  # New set to create
                            "set_number": 2,
                            "actual_reps": 5,
                            "actual_weight": 325.0
                        }
                    ]
                },
                {
                    "completed_id": "exercise2",
                    "exercise_type": "Bench Press",
                    "sets": [
                        {
                            "set_id": "set3",  # Existing set to update
                            "set_number": 1,
                            "actual_reps": 10,  # Updated reps
                            "actual_weight": 235.0  # Updated weight
                        }
                    ]
                }
            ]
        }
        
        # Mock existing sets for exercise1
        existing_sets_ex1 = [
            {
                "set_id": "set1",
                "set_number": 1,
                "actual_reps": 5,
                "actual_weight": 315.0,
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123"
            },
            {
                "set_id": "set2",  # This set will be deleted as it's not in update
                "set_number": 2,
                "actual_reps": 5,
                "actual_weight": 315.0,
                "completed_exercise_id": "exercise1",
                "workout_id": "workout123"
            }
        ]
        
        # Mock existing sets for exercise2
        existing_sets_ex2 = [
            {
                "set_id": "set3",
                "set_number": 1,
                "actual_reps": 8,
                "actual_weight": 225.0,
                "completed_exercise_id": "exercise2",
                "workout_id": "workout123"
            }
        ]
        
        # Configure mock to return existing sets
        self.mock_set_repository.get_sets_by_exercise.side_effect = [
            existing_sets_ex1,  # For exercise1
            existing_sets_ex2   # For exercise2
        ]
        
        # Call the method
        self.workout_repository.update_workout(workout_id, update_data)
        
        # Assert get_sets_by_exercise was called for each exercise
        self.mock_set_repository.get_sets_by_exercise.assert_any_call("exercise1")
        self.mock_set_repository.get_sets_by_exercise.assert_any_call("exercise2")
        
        # Assert that update_set was called for existing sets
        # For set1 (exercise1)
        set1_update = {
            "set_id": "set1",
            "set_number": 1,
            "actual_reps": 6,
            "actual_weight": 325.0
        }
        self.mock_set_repository.update_set.assert_any_call("set1", set1_update)
        
        # For set3 (exercise2)
        set3_update = {
            "set_id": "set3",
            "set_number": 1,
            "actual_reps": 10,
            "actual_weight": 235.0
        }
        self.mock_set_repository.update_set.assert_any_call("set3", set3_update)
        
        # Assert that create_set was called for new sets
        new_set = {
            "set_id": "set_new",
            "set_number": 2,
            "actual_reps": 5,
            "actual_weight": 325.0,
            "completed_exercise_id": "exercise1",
            "workout_id": "workout123"
        }
        self.mock_set_repository.create_set.assert_called_once_with(new_set)
        
        # Assert that delete_set was called for sets not in update
        self.mock_set_repository.delete_set.assert_called_once_with("set2")
        
        # Assert update_item was called on the workout table
        self.mock_table.update_item.assert_called_once()
        
        # Check that "exercises" was not in the update expression
        call_args = self.mock_table.update_item.call_args[1]
        self.assertIn("date = :date", call_args["UpdateExpression"])
        self.assertNotIn("exercises", call_args["UpdateExpression"])
    
    def test_update_workout_handles_multiple_exercises(self):
        """
        Test the update_workout method handling multiple exercises
        """
        # Test data with multiple exercises but simpler structure
        workout_id = "workout123"
        update_data = {
            "notes": "Updated notes",
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
                        }
                    ]
                },
                {
                    "completed_id": "exercise2",
                    "exercise_type": "Bench Press",
                    "sets": []  # No sets for this exercise - should not cause errors
                },
                {
                    "completed_id": "exercise3",
                    "exercise_type": "Deadlift"  # No 'sets' key at all - should not cause errors
                }
            ]
        }
        
        # Mock empty existing sets
        self.mock_set_repository.get_sets_by_exercise.return_value = []
        
        # Call the method
        self.workout_repository.update_workout(workout_id, update_data)
        
        # Assert get_sets_by_exercise was called for each exercise that has sets
        self.assertEqual(self.mock_set_repository.get_sets_by_exercise.call_count, 2)
        
        # Assert create_set was called for the one new set
        self.assertEqual(self.mock_set_repository.create_set.call_count, 1)
        
        # Assert update_item was called on the workout
        self.mock_table.update_item.assert_called_once()
        
        # Check the update expression
        call_args = self.mock_table.update_item.call_args[1]
        self.assertIn("notes = :notes", call_args["UpdateExpression"])
        self.assertEqual(call_args["ExpressionAttributeValues"][":notes"], "Updated notes")
    
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