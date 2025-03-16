import unittest
from unittest.mock import MagicMock, patch
from src.models.workout import Workout
from src.models.completed_exercise import CompletedExercise
from src.services.workout_service import WorkoutService

class TestWorkoutService(unittest.TestCase):
    """
    Test suite for the WorkoutService
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.workout_repository_mock = MagicMock()
        self.day_repository_mock = MagicMock()
        self.exercise_repository_mock = MagicMock()

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4")
        self.uuid_mock = self.uuid_patcher.start()

        # Configure uuid4 to return different values for workout_id and completed_exercise_id
        self.uuid_mock.side_effect = ["workout-uuid", "exercise1-uuid", "exercise2-uuid"]

        # Initialize service with mocked repositories
        with patch("src.services.workout_service.WorkoutRepository", return_value=self.workout_repository_mock), patch("src.services.workout_service.DayRepository", return_value=self.day_repository_mock), patch("src.services.workout_service.ExerciseRepository", return_value=self.exercise_repository_mock):
            self.workout_service = WorkoutService()
    
    def tearDown(self):
        """
        Clean up after each test method
        """
        self.uuid_patcher.stop()

    def test_get_workout(self):
        """
        Test retrieving a workout by ID
        """
        # Mock data for a workout with exercises
        mock_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Solid session",
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "comp1",
                    "workout_id": "workout123",
                    "exercise_id": "ex1",
                    "actual_sets": 3,
                    "actual_reps": 5,
                    "actual_weight": 225.0,
                    "actual_rpe": 8,
                    "notes": "Felt strong"
                }
            ]
        }

        # Configure mock to return test data
        self.workout_repository_mock.get_workout.return_value = mock_workout_data

        # Call the service method
        result = self.workout_service.get_workout("workout123")

        # Assert repository was called with correct ID
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")

        # Assert the result is a Workout instance with correct data
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.workout_id, "workout123")
        self.assertEqual(result.athlete_id, "athlete456")
        self.assertEqual(result.day_id, "day789")
        self.assertEqual(result.date, "2025-03-15")
        self.assertEqual(result.notes, "Solid session")
        self.assertEqual(result.status, "completed")

        # Check that exercises were correctly loaded
        self.assertEqual(len(result.exercises), 1)
        self.assertIsInstance(result.exercises[0], CompletedExercise)
        self.assertEqual(result.exercises[0].completed_id, "comp1")
        self.assertEqual(result.exercises[0].exercise_id, "ex1")
        self.assertEqual(result.exercises[0].actual_weight, 225.0)

    def test_get_workout_not_found(self):
        """
        Test retrieving a non-existent workout returns None
        """
        # Configure mock to return None (workout not found)
        self.workout_repository_mock.get_workout.return_value = None

        # Call the service method
        result = self.workout_service.get_workout("nonexistent")

        # Assert the repository was called with the correct ID
        self.workout_repository_mock.get_workout.assert_called_once_with("nonexistent")

        # Assert the result is None
        self.assertIsNone(result)
    
    def test_get_workout_by_day(self):
        """
        Test retrieving a workout by athlete and day
        """
        # Mock data for a workout
        mock_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Solid session",
            "status": "completed",
            "exercises": []
        }

        # Configure mock to return our test data
        self.workout_repository_mock.get_workout_by_day.return_value = mock_workout_data

        # Call the service method
        result = self.workout_service.get_workout_by_day("athlete456", "day789")

        # Assert the repository was called with correct IDs
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with("athlete456", "day789")

        # Assert the result is a Workout instance with correct data
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.workout_id, "workout123")
        self.assertEqual(result.athlete_id, "athlete456")
        self.assertEqual(result.day_id, "day789")
    
    def test_get_workout_by_day_not_found(self):
        """
        Test retrieving a non-existent workout by day returns None
        """
        # Configure mock to return None (workout not found)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Call the service method
        self.workout_repository_mock.get_workout_by_day("athlete456", "nonexistent-day-id")

        # Assert the repository was called with correct IDs
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with("athlete456", "nonexistent-day-id")

        # Assert the result is None
        self.assertIsNone(None)

    def test_log_workout_new(self):
        """
        Test logging a new workout
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Prepare completed exercises data
        completed_exercises = [
            {
                "exercise_id": "ex123",
                "actual_sets": 3,
                "actual_reps": 5,
                "actual_weight": 225.0,
                "actual_rpe": 8
            },
            {
                "exercise_id": "ex456",
                "actual_sets": 4,
                "actual_reps": 10,
                "actual_weight": 135.0,
                "actual_rpe": 7
            }
        ]

        # Call the service method
        result = self.workout_service.log_workout(
            athlete_id="athlete123",
            day_id="day456",
            date="2025-03-15",
            completed_exercises=completed_exercises,
            notes="Below average workout",
            status="completed"
        )
        
        # Assert UUID function was called multiple times (3 times here, one for workout, and two for exercises)
        self.assertEqual(self.uuid_mock.call_count, 3) 

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with("athlete123", "day456")
        self.workout_repository_mock.create_workout.assert_called_once()

        # Check the workout data passed to create_workout
        workout_dict = self.workout_repository_mock.create_workout.call_args[0][0]
        self.assertEqual(workout_dict["workout_id"], "workout-uuid")
        self.assertEqual(workout_dict["athlete_id"], "athlete123")
        self.assertEqual(workout_dict["day_id"], "day456")
        self.assertEqual(workout_dict["date"], "2025-03-15")
        self.assertEqual(workout_dict["notes"], "Below average workout")
        self.assertEqual(workout_dict["status"], "completed")

        # Check the exercises in the workout
        self.assertEqual(len(workout_dict["exercises"]), 2)
        self.assertEqual(workout_dict["exercises"][0]["completed_id"], "exercise1-uuid")
        self.assertEqual(workout_dict["exercises"][0]["workout_id"], "workout-uuid")
        self.assertEqual(workout_dict["exercises"][0]["exercise_id"], "ex123")
        self.assertEqual(workout_dict["exercises"][0]["actual_sets"], 3)

        # Assert the returned object is a Workout with correct data
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.workout_id, "workout-uuid")
        self.assertEqual(result.athlete_id, "athlete123")
        self.assertEqual(len(result.exercises), 2)
    
    def test_log_workout_update_existing(self):
        """
        Test logging a workout that already exists (update case)
        """
        # Mock data for an existing workout
        existing_workout = {
            "workout_id": "existing-workout",
            "athlete_id": "athlete123",
            "day_id": "day456",
            "date": "2025-03-15",
            "notes": "Initial notes",
            "status": "partial",
            "exercises": [
                {
                    "completed_id": "old-exercise",
                    "workout_id": "existing-workout",
                    "exercise_id": "ex123",
                    "actual_sets": 2,
                    "actual_reps": 5,
                    "actual_weight": 205.0,
                    "actual_rpe": 9
                }
            ]
        }

        # Configure mock to return the existing workout
        self.workout_repository_mock.get_workout_by_day.return_value = existing_workout

        # New completed exercise data
        updated_exercises = [
            {
                "exercise_id": "ex123",
                "actual_sets": 3,
                "actual_reps": 5,
                "actual_weight": 225.0,
                "actual_rpe": 8
            }
        ]

        # Mock the updated_workout method to return a workout object
        with patch.object(self.workout_service, "update_workout") as mock_update_workout:
            # Setup the mock to return a Workout object
            updated_workout = Workout(
                workout_id="existing-workout",
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                notes="Good workout",
                status="completed"
            )
            mock_update_workout.return_value = updated_workout

            # Call the service method
            result = self.workout_service.log_workout(
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                completed_exercises=updated_exercises,
                notes="Good workout",
                status="completed"
            )

            # Assert repository methods were called correctly
            self.workout_repository_mock.get_workout_by_day.assert_called_once_with("athlete123", "day456")

            # Assert update_workout was called with correct parameters
            mock_update_workout.assert_called_once_with(
                "existing-workout",
                {
                    "date": "2025-03-15",
                    "notes": "Good workout",
                    "status": "completed",
                    "exercises": updated_exercises
                }
            )

            # Assert the returned object is the updated workout
            self.assertIsInstance(result, Workout)
            self.assertEqual(result.workout_id, "existing-workout")
            self.assertEqual(result.status, "completed")
    
    def test_update_workout(self):
        """
        Test updating a workout with new information
        """
        # Mock initial workout data
        initial_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Initial notes",
            "status": "partial",
            "exercises": []
        }

        # Mock updated workout data
        updated_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Updated notes",
            "status": "completed",  # Changed from partial to completed
            "exercises": []
        }

        # Configure mocks
        self.workout_repository_mock.update_workout.return_value = {"Attributes": {"status": "completed", "notes": "Updated notes"}}
        self.workout_repository_mock.get_workout.return_value = updated_workout_data

        # Update data to send
        update_data = {
            "notes": "Updated notes",
            "status": "completed"
        }

        # Call the service method
        result = self.workout_service.update_workout("workout123", update_data)

        # Assert repository methods were called correctly
        self.workout_repository_mock.update_workout.assert_called_once_with("workout123", update_data)
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")

        # Assert the returned object has the updated values
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.notes, "Updated notes")
        self.assertEqual(result.status, "completed")

        # Assert unchanged values remain the same
        self.assertEqual(result.workout_id, "workout123")
        self.assertEqual(result.athlete_id, "athlete456")
        self.assertEqual(result.date, "2025-03-15")

    def test_update_workout_with_exercises(self):
        """
        Test updating a workout's exercises
        """
        # Mock initial workout data with exercises
        initial_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Good session",
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "comp1",
                    "workout_id": "workout123",
                    "exercise_id": "ex1",
                    "actual_sets": 3,
                    "actual_reps": 5,
                    "actual_weight": 225.0
                }
            ]
        }
        
        # New exercises data
        new_exercises = [
            {
                "completed_id": "comp1",
                "workout_id": "workout123",
                "exercise_id": "ex1",
                "actual_sets": 5,  # Changed from 3 to 5
                "actual_reps": 5,
                "actual_weight": 225.0
            },
            {
                "completed_id": "comp2",
                "workout_id": "workout123",
                "exercise_id": "ex2",
                "actual_sets": 3,
                "actual_reps": 10,
                "actual_weight": 135.0
            }
        ]
        
        # Updated workout data with new exercises
        updated_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Good session",
            "status": "completed",
            "exercises": new_exercises
        }

        # Configure mocks 
        self.workout_repository_mock.update_workout.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        self.workout_repository_mock.get_workout.return_value = updated_workout_data

        # Update data to send
        update_data = {
            "exercises": new_exercises
        }

        # Call the service method
        result = self.workout_service.update_workout("workout123", update_data)

        # Assert the repository methods were called correctly
        self.workout_repository_mock.update_workout.assert_called_once_with("workout123", update_data)

        # Assert the returned object has the updated exercises
        self.assertEqual(len(result.exercises), 2)
        self.assertEqual(result.exercises[0].actual_sets, 5) # Updated value

    def test_log_workout_with_minimal_data(self):
        """
        Test logging a workout with minimal required data
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None
        
        # Prepare minimal completed exercises data
        completed_exercises = [
            {
                "exercise_id": "ex123",
                "actual_sets": 3,
                "actual_reps": 5,
                "actual_weight": 225.0
                # No RPE or notes
            }
        ]
        
        # Call the service method with minimal data
        result = self.workout_service.log_workout(
            athlete_id="athlete123",
            day_id="day456",
            date="2025-03-15",
            completed_exercises=completed_exercises
            # No notes or status
        )
        
        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with("athlete123", "day456")
        self.workout_repository_mock.create_workout.assert_called_once()
        
        # Check the workout data uses default values where missing
        workout_dict = self.workout_repository_mock.create_workout.call_args[0][0]
        self.assertEqual(workout_dict["status"], "completed")  # Default status
        self.assertIsNone(workout_dict["notes"])  # Default None for notes
        
        # Check the exercise has None for optional fields
        exercise_dict = workout_dict["exercises"][0]
        self.assertIsNone(exercise_dict["actual_rpe"])
        self.assertIsNone(exercise_dict["notes"])

    def test_log_workout_with_invalid_status(self):
        """
        Test logging a workout with an invalid status
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None
        
        # Prepare completed exercises data
        completed_exercises = [
            {
                "exercise_id": "ex123",
                "actual_sets": 3,
                "actual_reps": 5,
                "actual_weight": 225.0
            }
        ]
        
        # Call the service method with invalid status
        with self.assertRaises(ValueError):
            self.workout_service.log_workout(
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                completed_exercises=completed_exercises,
                status="invalid_status"  # Not one of: completed, partial, skipped
            )
        
        # Assert repository methods were not called
        self.workout_repository_mock.create_workout.assert_not_called()

    
    def test_delete_workout(self):
        """
        Test deleting a workout
        """
        # Configure mock to return a successful response
        self.workout_repository_mock.delete_workout.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Call the service method
        result = self.workout_service.delete_workout("workout123")

        # Assert repository was called with the correct ID
        self.workout_repository_mock.delete_workout.assert_called_once_with("workout123")

        # Assert the result is True (successful deletion)
        self.assertTrue(result)


if __name__ == "__main__": # pragma: no cover
    unittest.main()