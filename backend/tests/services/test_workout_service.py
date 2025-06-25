import unittest
from unittest.mock import MagicMock, patch
from src.models.workout import Workout
from src.models.exercise import Exercise
from src.services.workout_service import WorkoutService
from src.services.exercise_service import ExerciseService
import datetime as dt


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
        self.exercise_service_mock = MagicMock()

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4")
        self.uuid_mock = self.uuid_patcher.start()

        # Configure uuid4 to return different values
        self.uuid_mock.side_effect = [
            "workout-uuid",
            "exercise1-uuid",
            "exercise2-uuid",
            "set1-uuid",
            "set2-uuid",
            "set3-uuid",
        ]

        # Initialize service with mocked repositories
        with patch(
            "src.services.workout_service.WorkoutRepository",
            return_value=self.workout_repository_mock,
        ), patch(
            "src.services.workout_service.DayRepository",
            return_value=self.day_repository_mock,
        ), patch(
            "src.services.workout_service.ExerciseRepository",
            return_value=self.exercise_repository_mock,
        ), patch(
            "src.services.workout_service.ExerciseService",
            return_value=self.exercise_service_mock,
        ):
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
                    "exercise_id": "ex1",
                    "workout_id": "workout123",
                    "exercise_type": "Bench Press",
                    "sets": 3,
                    "reps": 5,
                    "weight": 225.0,
                    "status": "completed",
                    "rpe": 8.0,
                    "notes": "Good form",
                }
            ],
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
        self.assertEqual(result.notes, "Solid session")
        self.assertEqual(result.status, "completed")

        # Check that exercises were correctly loaded
        self.assertEqual(len(result.exercises), 1)
        self.assertIsInstance(result.exercises[0], Exercise)
        self.assertEqual(result.exercises[0].exercise_id, "ex1")
        self.assertEqual(result.exercises[0].exercise_type, "Bench Press")
        self.assertEqual(result.exercises[0].sets, 3)
        self.assertEqual(result.exercises[0].reps, 5)
        self.assertEqual(result.exercises[0].weight, 225.0)
        self.assertEqual(result.exercises[0].rpe, 8.0)
        self.assertEqual(result.exercises[0].notes, "Good form")

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
            "exercises": [],
        }

        # Configure mock to return our test data
        self.workout_repository_mock.get_workout_by_day.return_value = mock_workout_data

        # Call the service method
        result = self.workout_service.get_workout_by_day("athlete456", "day789")

        # Assert the repository was called with correct IDs
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete456", "day789"
        )

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
        result = self.workout_service.get_workout_by_day(
            "athlete456", "nonexistent-day-id"
        )

        # Assert the repository was called with correct IDs
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete456", "nonexistent-day-id"
        )

        # Assert the result is None
        self.assertIsNone(result)

    def test_create_workout_new(self):
        """
        Test creating a new workout with exercises
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Prepare exercises data
        exercises = [
            {
                "exercise_type": "Bench Press",
                "sets": 3,
                "reps": 5,
                "weight": 225.0,
                "status": "planned",
                "rpe": 8.0,
            },
            {
                "exercise_type": "Squat",
                "sets": 3,
                "reps": 5,
                "weight": 315.0,
                "status": "planned",
                "notes": "Hard work",
            },
        ]

        # Call the service method
        result = self.workout_service.create_workout(
            athlete_id="athlete123",
            day_id="day456",
            date="2025-03-15",
            exercises=exercises,
            notes="Good workout",
            status="not_started",
        )

        # Check UUIDs were generated
        self.assertEqual(self.uuid_mock.call_count, 3)  # 1 workout + 2 exercises

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete123", "day456"
        )
        self.workout_repository_mock.create_workout.assert_called_once()

        # Check the workout data passed to create_workout (no exercises in dict)
        workout_dict = self.workout_repository_mock.create_workout.call_args[0][0]
        self.assertEqual(workout_dict["workout_id"], "workout-uuid")
        self.assertEqual(workout_dict["athlete_id"], "athlete123")
        self.assertEqual(workout_dict["day_id"], "day456")
        self.assertEqual(workout_dict["date"], "2025-03-15")
        self.assertEqual(workout_dict["notes"], "Good workout")
        self.assertEqual(workout_dict["status"], "not_started")
        self.assertNotIn("exercises", workout_dict)  # Exercises not in the workout dict

        # Check that exercises were created separately in the exercise repository
        self.assertEqual(self.exercise_repository_mock.create_exercise.call_count, 2)

        # Check the first exercise creation call
        first_exercise_call = (
            self.exercise_repository_mock.create_exercise.call_args_list[0][0][0]
        )
        self.assertEqual(first_exercise_call["exercise_id"], "exercise1-uuid")
        self.assertEqual(first_exercise_call["workout_id"], "workout-uuid")
        self.assertEqual(first_exercise_call["exercise_type"], "Bench Press")
        self.assertEqual(first_exercise_call["sets"], 3)
        self.assertEqual(first_exercise_call["reps"], 5)
        self.assertEqual(first_exercise_call["weight"], 225.0)
        self.assertEqual(first_exercise_call["status"], "planned")

    def test_create_workout_update_existing(self):
        """
        Test creating a workout that already exists (update case)
        """
        # Mock data for an existing workout
        existing_workout = {
            "workout_id": "existing-workout",
            "athlete_id": "athlete123",
            "day_id": "day456",
            "date": "2025-03-15",
            "notes": "Initial notes",
            "status": "not_started",
            "exercises": [
                {
                    "exercise_id": "ex123",
                    "workout_id": "existing-workout",
                    "exercise_type": "Bench Press",
                    "sets": 3,
                    "reps": 5,
                    "weight": 205.0,
                    "status": "planned",
                    "notes": "Initial effort",
                }
            ],
        }

        # Configure mock to return the existing workout
        self.workout_repository_mock.get_workout_by_day.return_value = existing_workout

        # New exercise data
        updated_exercises = [
            {
                "exercise_type": "Bench Press",
                "sets": 3,
                "reps": 5,
                "weight": 225.0,
                "status": "completed",
                "notes": "Improved effort",
            }
        ]

        # Mock the updated_workout method to return a workout object
        with patch.object(
            self.workout_service, "update_workout"
        ) as mock_update_workout:
            # Setup the mock to return a Workout object
            updated_workout = Workout(
                workout_id="existing-workout",
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                notes="Good workout",
                status="completed",
            )

            # Add an exercise to the workout
            exercise = Exercise(
                exercise_id="ex123",
                workout_id="existing-workout",
                exercise_type="Bench Press",
                sets=3,
                reps=5,
                weight=225.0,
                status="completed",
                notes="Improved effort",
            )

            updated_workout.add_exercise(exercise)
            mock_update_workout.return_value = updated_workout

            # Call the service method
            result = self.workout_service.create_workout(
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                exercises=updated_exercises,
                notes="Good workout",
                status="completed",
            )

            # Assert repository methods were called correctly
            self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
                "athlete123", "day456"
            )

            # Assert update_workout was called with correct parameters
            mock_update_workout.assert_called_once_with(
                "existing-workout",
                {
                    "date": "2025-03-15",
                    "notes": "Good workout",
                    "status": "completed",
                    "exercises": updated_exercises,
                },
            )

            # Assert the returned object is the updated workout
            self.assertIsInstance(result, Workout)
            self.assertEqual(result.workout_id, "existing-workout")
            self.assertEqual(result.status, "completed")

            # Check that exercises were correctly updated
            self.assertEqual(len(result.exercises), 1)
            self.assertEqual(result.exercises[0].notes, "Improved effort")
            self.assertEqual(result.exercises[0].status, "completed")

    def test_complete_exercise(self):
        """
        Test completing an exercise by updating its status and values
        """
        # Mock exercise data
        exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout123",
            "exercise_type": "Bench Press",
            "sets": 3,
            "reps": 5,
            "weight": 225.0,
            "status": "planned",
        }

        # Mock updated exercise data
        updated_exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout123",
            "exercise_type": "Bench Press",
            "sets": 3,
            "reps": 8,  # Completed more reps than planned
            "weight": 235.0,  # Used more weight than planned
            "status": "completed",
            "rpe": 9.0,
        }

        # Configure mocks
        self.exercise_repository_mock.get_exercise.return_value = exercise_data
        self.exercise_repository_mock.update_exercise.return_value = (
            updated_exercise_data
        )

        # Call the service method
        result = self.workout_service.complete_exercise(
            exercise_id="ex123", sets=3, reps=8, weight=235.0, rpe=9.0
        )

        # Assert repository methods were called correctly
        self.exercise_repository_mock.get_exercise.assert_called_once_with("ex123")
        self.exercise_repository_mock.update_exercise.assert_called_once_with(
            "ex123",
            {"status": "completed", "sets": 3, "reps": 8, "weight": 235.0, "rpe": 9.0},
        )

        # Verify the workout status was updated
        self.assertTrue(hasattr(self.workout_service, "_update_workout_status"))

        # Assert result is the updated exercise
        self.assertEqual(result.exercise_id, "ex123")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.reps, 8)
        self.assertEqual(result.weight, 235.0)
        self.assertEqual(result.rpe, 9.0)

    def test_update_workout_status(self):
        """
        Test updating workout status based on exercise completion
        """
        # Mock workout data with exercises
        workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "not_started",
            "exercises": [
                {
                    "exercise_id": "ex1",
                    "workout_id": "workout123",
                    "exercise_type": "Bench Press",
                    "sets": 3,
                    "reps": 5,
                    "weight": 225.0,
                    "status": "planned",
                },
                {
                    "exercise_id": "ex2",
                    "workout_id": "workout123",
                    "exercise_type": "Squat",
                    "sets": 3,
                    "reps": 5,
                    "weight": 315.0,
                    "status": "planned",
                },
            ],
        }

        # Configure mock to return workout
        self.workout_repository_mock.get_workout.return_value = workout_data

        # Call the private method
        self.workout_service._update_workout_status("workout123")

        # Status should remain "not_started" since no exercises are completed
        self.workout_repository_mock.update_workout.assert_not_called()

        # Now change one exercise to completed and test again
        workout_data["exercises"][0]["status"] = "completed"

        # Call the method again
        self.workout_service._update_workout_status("workout123")

        # Status should be updated to "in_progress"
        self.workout_repository_mock.update_workout.assert_called_once_with(
            "workout123", {"status": "in_progress"}
        )

        # Reset the mock and update all exercises to completed
        self.workout_repository_mock.update_workout.reset_mock()
        workout_data["exercises"][1]["status"] = "completed"

        # Call the method again
        self.workout_service._update_workout_status("workout123")

        # Status should be updated to "completed"
        self.workout_repository_mock.update_workout.assert_called_once_with(
            "workout123", {"status": "completed"}
        )

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
            "exercises": [],
        }

        # Mock updated workout data
        updated_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Updated notes",
            "status": "completed",  # Changed from partial to completed
            "exercises": [],
        }

        # Configure mocks
        self.workout_repository_mock.get_workout.side_effect = [
            initial_workout_data,  # First call to check if workout exists
            updated_workout_data,  # Second call to get updated workout
        ]
        self.workout_repository_mock.update_workout.return_value = {
            "Attributes": {"status": "completed", "notes": "Updated notes"}
        }

        # Update data to send
        update_data = {"notes": "Updated notes", "status": "completed"}

        # Call the service method
        result = self.workout_service.update_workout("workout123", update_data)

        # Assert repository methods were called correctly
        self.workout_repository_mock.update_workout.assert_called_once_with(
            "workout123", update_data
        )
        self.assertEqual(self.workout_repository_mock.get_workout.call_count, 2)

        # Assert the returned object has the updated values
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.notes, "Updated notes")
        self.assertEqual(result.status, "completed")

        # Assert unchanged values remain the same
        self.assertEqual(result.workout_id, "workout123")
        self.assertEqual(result.athlete_id, "athlete456")
        self.assertEqual(result.date, "2025-03-15")

    def test_create_workout_with_minimal_data(self):
        """
        Test creating a workout with minimal required data
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Prepare minimal exercises data
        exercises = [
            {
                "exercise_type": "Bench Press",
                "sets": 3,
                "reps": 5,
                "weight": 225.0
                # No status, rpe or notes
            }
        ]

        # Call the service method with minimal data
        result = self.workout_service.create_workout(
            athlete_id="athlete123",
            day_id="day456",
            date="2025-03-15",
            exercises=exercises
            # No notes or status
        )

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete123", "day456"
        )
        self.workout_repository_mock.create_workout.assert_called_once()

        # Check the workout data uses default values where missing
        workout_dict = self.workout_repository_mock.create_workout.call_args[0][0]
        self.assertEqual(workout_dict["status"], "not_started")  # Default status
        self.assertIsNone(workout_dict["notes"])  # Default None for notes
        self.assertNotIn("exercises", workout_dict)  # Exercises not in the workout dict

        # Check that exercise was created separately in the exercise repository
        self.assertEqual(self.exercise_repository_mock.create_exercise.call_count, 1)

        # Check the exercise creation call
        exercise_call = self.exercise_repository_mock.create_exercise.call_args[0][0]
        self.assertEqual(exercise_call["status"], "planned")  # Default status
        self.assertIsNone(exercise_call.get("notes"))
        self.assertIsNone(exercise_call.get("rpe"))

    def test_create_workout_with_invalid_status(self):
        """
        Test creating a workout with an invalid status
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Prepare exercises data
        exercises = [
            {"exercise_type": "Bench Press", "sets": 3, "reps": 5, "weight": 225.0}
        ]

        # Call the service method with invalid status
        with self.assertRaises(ValueError):
            self.workout_service.create_workout(
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                exercises=exercises,
                status="invalid_status",  # Not one of: not_started, in_progress, completed, skipped
            )

        # Assert repository methods were not called
        self.workout_repository_mock.create_workout.assert_not_called()

    def test_delete_workout(self):
        """
        Test deleting a workout
        """
        # Configure mock to return a successful response
        self.workout_repository_mock.delete_workout.return_value = {
            "Attributes": {"workout_id": "workout123"}
        }

        # Call the service method
        result = self.workout_service.delete_workout("workout123")

        # Assert repository was called with the correct ID
        self.workout_repository_mock.delete_workout.assert_called_once_with(
            "workout123"
        )

        # Assert the result is True (successful deletion)
        self.assertTrue(result)

    def test_update_workout_with_exercises(self):
        """
        Test updating a workout with exercises (both existing and new)
        """
        # Mock the existing workout with exercises
        existing_workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            status="not_started",
        )

        # Add an existing exercise
        existing_exercise = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            status="planned",
            notes="Initial notes",
        )

        existing_workout.add_exercise(existing_exercise)

        # Mock get_workout to return the existing workout first, then updated workout
        self.workout_repository_mock.get_workout.side_effect = [
            # First call when checking if workout exists
            {
                "workout_id": "workout123",
                "athlete_id": "athlete456",
                "day_id": "day789",
                "date": "2025-03-15",
                "status": "not_started",
                "exercises": [
                    {
                        "exercise_id": "ex1",
                        "workout_id": "workout123",
                        "exercise_type": "Squat",
                        "sets": 3,
                        "reps": 5,
                        "weight": 315.0,
                        "status": "planned",
                        "notes": "Initial notes",
                    }
                ],
            },
            # Second call after update
            {
                "workout_id": "workout123",
                "athlete_id": "athlete456",
                "day_id": "day789",
                "date": "2025-03-15",
                "status": "in_progress",
                "exercises": [
                    {
                        "exercise_id": "ex1",
                        "workout_id": "workout123",
                        "exercise_type": "Squat",
                        "sets": 3,
                        "reps": 6,  # Updated
                        "weight": 325.0,  # Updated
                        "status": "completed",  # Updated
                        "notes": "Updated notes",
                    },
                    {
                        "exercise_id": "ex2",
                        "workout_id": "workout123",
                        "exercise_type": "Bench Press",
                        "sets": 3,
                        "reps": 8,
                        "weight": 225.0,
                        "status": "planned",
                        "notes": "New exercise",
                    },
                ],
            },
        ]

        # Update data to send
        update_data = {
            "status": "in_progress",
            "exercises": [
                {
                    "exercise_id": "ex1",
                    "exercise_type": "Squat",
                    "sets": 3,
                    "reps": 6,  # Updated
                    "weight": 325.0,  # Updated
                    "status": "completed",  # Updated
                    "notes": "Updated notes",
                },
                {
                    "exercise_id": "ex2",
                    "exercise_type": "Bench Press",
                    "sets": 3,
                    "reps": 8,
                    "weight": 225.0,
                    "status": "planned",
                    "notes": "New exercise",
                },
            ],
        }

        # Call the service method
        result = self.workout_service.update_workout("workout123", update_data)

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called()
        self.workout_repository_mock.update_workout.assert_called()

        # Assert the result is a Workout with updated data
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.status, "in_progress")
        self.assertEqual(len(result.exercises), 2)

        # Check first exercise (updated)
        self.assertEqual(result.exercises[0].exercise_id, "ex1")
        self.assertEqual(result.exercises[0].reps, 6)
        self.assertEqual(result.exercises[0].weight, 325.0)
        self.assertEqual(result.exercises[0].status, "completed")

        # Check second exercise (new)
        self.assertEqual(result.exercises[1].exercise_id, "ex2")
        self.assertEqual(result.exercises[1].exercise_type, "Bench Press")
        self.assertEqual(result.exercises[1].status, "planned")

    def test_update_workout_nonexistent(self):
        """
        Test updating a workout that doesn't exist
        """
        # Mock repository to return None (workout not found)
        self.workout_repository_mock.get_workout.return_value = None

        # Call the service method
        result = self.workout_service.update_workout(
            "nonexistent", {"status": "completed"}
        )

        # Assert the result is None
        self.assertIsNone(result)

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called_once_with("nonexistent")
        self.workout_repository_mock.update_workout.assert_not_called()

    @patch("src.services.workout_service.dt.datetime")
    def test_start_workout_session_success(self, mock_datetime):
        """
        Test successfully starting a workout timing session
        """
        # Mock current time
        mock_time = "2025-06-24T14:30:00.123456"
        mock_datetime.now.return_value.isoformat.return_value = mock_time

        # Mock existing workout without timing
        existing_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "not_started",
            "start_time": None,
            "finish_time": None,
            "exercises": [],
        }

        # Mock updated workout with start_time
        updated_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": mock_time,
            "finish_time": None,
            "exercises": [],
        }

        # Configure mocks
        self.workout_repository_mock.get_workout.side_effect = [
            existing_workout_data,  # First call in get_workout
            existing_workout_data,  # Second call in update_workout (existing check)
            updated_workout_data,  # Third call in update_workout (return updated)
        ]

        # Call the service method
        result = self.workout_service.start_workout_session("workout123")

        # Assert datetime.now() was called
        mock_datetime.now.assert_called_once()

        # Assert repository update was called with correct data
        self.workout_repository_mock.update_workout.assert_called_once_with(
            "workout123", {"start_time": mock_time, "status": "in_progress"}
        )

        # Assert result is updated workout
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.start_time, mock_time)
        self.assertEqual(result.status, "in_progress")

    def test_start_workout_session_nonexistent_workout(self):
        """
        Test starting a session for a workout that doesn't exist
        """
        # Configure mock to return None (workout not found)
        self.workout_repository_mock.get_workout.return_value = None

        # Call the service method
        result = self.workout_service.start_workout_session("nonexistent")

        # Assert repository was called to check for workout
        self.workout_repository_mock.get_workout.assert_called_once_with("nonexistent")

        # Assert update was not called
        self.workout_repository_mock.update_workout.assert_not_called()

        # Assert result is None
        self.assertIsNone(result)

    def test_start_workout_session_already_started(self):
        """
        Test starting a session for a workout that already has start_time
        """
        # Mock existing workout with start_time already set
        existing_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": "2025-06-24T14:00:00.123456",
            "finish_time": None,
            "exercises": [],
        }

        # Configure mock
        self.workout_repository_mock.get_workout.return_value = existing_workout_data

        # Call the service method
        result = self.workout_service.start_workout_session("workout123")

        # Assert repository was called to get workout
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")

        # Assert update was NOT called (session already started)
        self.workout_repository_mock.update_workout.assert_not_called()

        # Assert result is the existing workout
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.start_time, "2025-06-24T14:00:00.123456")
        self.assertEqual(result.status, "in_progress")

    @patch("src.services.workout_service.dt.datetime")
    def test_finish_workout_session_success(self, mock_datetime):
        """
        Test successfully finishing a workout timing session
        """
        # Mock current time
        mock_time = "2025-06-24T15:45:00.789012"
        mock_datetime.now.return_value.isoformat.return_value = mock_time

        # Mock existing workout with start_time but no finish_time
        existing_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": "2025-06-24T14:30:00.123456",
            "finish_time": None,
            "exercises": [],
        }

        # Mock updated workout with finish_time
        updated_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": "2025-06-24T14:30:00.123456",
            "finish_time": mock_time,
            "exercises": [],
        }

        # Configure mocks
        self.workout_repository_mock.get_workout.side_effect = [
            existing_workout_data,  # First call in get_workout
            existing_workout_data,  # Second call in update_workout (existing check)
            updated_workout_data,  # Third call in update_workout (return updated)
        ]

        # Call the service method
        result = self.workout_service.finish_workout_session("workout123")

        # Assert datetime.now() was called
        mock_datetime.now.assert_called_once()

        # Assert repository update was called with correct data
        self.workout_repository_mock.update_workout.assert_called_once_with(
            "workout123", {"finish_time": mock_time}
        )

        # Assert result is updated workout
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.finish_time, mock_time)
        self.assertEqual(result.start_time, "2025-06-24T14:30:00.123456")

    def test_finish_workout_session_nonexistent_workout(self):
        """
        Test finishing a session for a workout that doesn't exist
        """
        # Configure mock to return None (workout not found)
        self.workout_repository_mock.get_workout.return_value = None

        # Call the service method
        result = self.workout_service.finish_workout_session("nonexistent")

        # Assert repository was called to check for workout
        self.workout_repository_mock.get_workout.assert_called_once_with("nonexistent")

        # Assert update was not called
        self.workout_repository_mock.update_workout.assert_not_called()

        # Assert result is None
        self.assertIsNone(result)

    def test_finish_workout_session_not_started(self):
        """
        Test finishing a session for a workout that was never started
        """
        # Mock existing workout without start_time
        existing_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "not_started",
            "start_time": None,
            "finish_time": None,
            "exercises": [],
        }

        # Configure mock
        self.workout_repository_mock.get_workout.return_value = existing_workout_data

        # Call the service method
        result = self.workout_service.finish_workout_session("workout123")

        # Assert repository was called to get workout
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")

        # Assert update was NOT called (session never started)
        self.workout_repository_mock.update_workout.assert_not_called()

        # Assert result is None (cannot finish unstarted session)
        self.assertIsNone(result)

    def test_finish_workout_session_already_finished(self):
        """
        Test finishing a session for a workout that already has finish_time
        """
        # Mock existing workout with both start_time and finish_time
        existing_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "completed",
            "start_time": "2025-06-24T14:30:00.123456",
            "finish_time": "2025-06-24T15:30:00.654321",
            "exercises": [],
        }

        # Configure mock
        self.workout_repository_mock.get_workout.return_value = existing_workout_data

        # Call the service method
        result = self.workout_service.finish_workout_session("workout123")

        # Assert repository was called to get workout
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")

        # Assert update was NOT called (session already finished)
        self.workout_repository_mock.update_workout.assert_not_called()

        # Assert result is the existing workout
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.start_time, "2025-06-24T14:30:00.123456")
        self.assertEqual(result.finish_time, "2025-06-24T15:30:00.654321")

    @patch("src.services.workout_service.dt.datetime")
    def test_start_finish_workout_session_complete_flow(self, mock_datetime):
        """
        Test complete flow of starting and finishing a workout session
        """
        # Mock times
        start_time = "2025-06-24T14:30:00.123456"
        finish_time = "2025-06-24T15:45:00.789012"
        mock_datetime.now.return_value.isoformat.side_effect = [start_time, finish_time]

        # Mock initial workout
        initial_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "not_started",
            "start_time": None,
            "finish_time": None,
            "exercises": [],
        }

        # Mock workout after start
        started_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": start_time,
            "finish_time": None,
            "exercises": [],
        }

        # Mock workout after finish
        finished_workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": start_time,
            "finish_time": finish_time,
            "exercises": [],
        }

        # Configure mocks for start operation
        self.workout_repository_mock.get_workout.side_effect = [
            initial_workout_data,  # get_workout call in start_workout_session
            initial_workout_data,  # get_workout call in update_workout (existing check)
            started_workout_data,  # get_workout call in update_workout (return updated)
            started_workout_data,  # get_workout call in finish_workout_session
            started_workout_data,  # get_workout call in update_workout (existing check)
            finished_workout_data,  # get_workout call in update_workout (return updated)
        ]

        # Start the session
        start_result = self.workout_service.start_workout_session("workout123")

        # Assert start worked correctly
        self.assertIsInstance(start_result, Workout)
        self.assertEqual(start_result.start_time, start_time)
        self.assertEqual(start_result.status, "in_progress")
        self.assertIsNone(start_result.finish_time)

        # Finish the session
        finish_result = self.workout_service.finish_workout_session("workout123")

        # Assert finish worked correctly
        self.assertIsInstance(finish_result, Workout)
        self.assertEqual(finish_result.start_time, start_time)
        self.assertEqual(finish_result.finish_time, finish_time)

        # Assert both datetime calls were made
        self.assertEqual(mock_datetime.now.call_count, 2)

        # Assert both update calls were made
        self.assertEqual(self.workout_repository_mock.update_workout.call_count, 2)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
