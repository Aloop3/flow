import unittest
from unittest.mock import MagicMock, patch
from src.models.workout import Workout
from src.models.completed_exercise import CompletedExercise
from src.models.set import Set
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
        self.set_service_mock = MagicMock()

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
            "src.services.workout_service.SetService",
            return_value=self.set_service_mock,
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
        # Mock data for a workout with exercises and sets
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
                    "notes": "Felt strong",
                    "sets": [
                        {
                            "set_id": "set1",
                            "completed_exercise_id": "comp1",
                            "workout_id": "workout123",
                            "set_number": 1,
                            "reps": 5,
                            "weight": 225.0,
                            "rpe": 8.0,
                            "notes": "Good form",
                            "completed": True,
                        }
                    ],
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
        self.assertIsInstance(result.exercises[0], CompletedExercise)
        self.assertEqual(result.exercises[0].completed_id, "comp1")
        self.assertEqual(result.exercises[0].exercise_id, "ex1")

        # Check that sets were correctly loaded
        self.assertEqual(len(result.exercises[0].sets), 1)
        self.assertIsInstance(result.exercises[0].sets[0], Set)
        self.assertEqual(result.exercises[0].sets[0].set_id, "set1")
        self.assertEqual(result.exercises[0].sets[0].reps, 5)
        self.assertEqual(result.exercises[0].sets[0].weight, 225.0)

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

    def test_log_workout_new(self):
        """
        Test logging a new workout with sets
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Prepare completed exercises data with sets
        completed_exercises = [
            {
                "exercise_id": "ex123",
                "notes": "Felt good",
                "sets": [
                    {"set_number": 1, "reps": 5, "weight": 225.0, "rpe": 8.0},
                    {"set_number": 2, "reps": 5, "weight": 225.0, "rpe": 8.5},
                ],
            },
            {
                "exercise_id": "ex456",
                "notes": "Hard work",
                "sets": [{"set_number": 1, "reps": 10, "weight": 135.0, "rpe": 7.0}],
            },
        ]

        # Call the service method
        result = self.workout_service.log_workout(
            athlete_id="athlete123",
            day_id="day456",
            date="2025-03-15",
            completed_exercises=completed_exercises,
            notes="Good workout",
            status="completed",
        )

        # Check UUIDs were generated for all elements (don't check exact values)
        self.assertEqual(
            self.uuid_mock.call_count, 6
        )  # 1 workout + 2 exercises + 3 sets

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete123", "day456"
        )
        self.workout_repository_mock.create_workout.assert_called_once()

        # Check the workout data passed to create_workout
        workout_dict = self.workout_repository_mock.create_workout.call_args[0][0]
        self.assertEqual(workout_dict["workout_id"], "workout-uuid")
        self.assertEqual(workout_dict["athlete_id"], "athlete123")
        self.assertEqual(workout_dict["day_id"], "day456")
        self.assertEqual(workout_dict["date"], "2025-03-15")
        self.assertEqual(workout_dict["notes"], "Good workout")
        self.assertEqual(workout_dict["status"], "completed")

        # Check the exercises in the workout
        self.assertEqual(len(workout_dict["exercises"]), 2)
        self.assertEqual(workout_dict["exercises"][0]["completed_id"], "exercise1-uuid")
        self.assertEqual(workout_dict["exercises"][0]["workout_id"], "workout-uuid")
        self.assertEqual(workout_dict["exercises"][0]["exercise_id"], "ex123")

        # Check sets were created - but don't check specific UUIDs
        self.assertEqual(len(workout_dict["exercises"][0]["sets"]), 2)
        for set_data in workout_dict["exercises"][0]["sets"]:
            self.assertIn("set_id", set_data)
            self.assertIn("completed_exercise_id", set_data)
            self.assertEqual(set_data["workout_id"], "workout-uuid")
            self.assertIn("set_number", set_data)
            self.assertIn("reps", set_data)
            self.assertIn("weight", set_data)

        self.assertEqual(len(workout_dict["exercises"][1]["sets"]), 1)
        for set_data in workout_dict["exercises"][1]["sets"]:
            self.assertIn("set_id", set_data)
            self.assertIn("completed_exercise_id", set_data)
            self.assertEqual(set_data["workout_id"], "workout-uuid")
            self.assertIn("set_number", set_data)
            self.assertIn("reps", set_data)
            self.assertIn("weight", set_data)

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
                    "notes": "Initial effort",
                    "sets": [
                        {
                            "set_id": "old-set",
                            "completed_exercise_id": "old-exercise",
                            "workout_id": "existing-workout",
                            "set_number": 1,
                            "reps": 5,
                            "weight": 205.0,
                            "rpe": 9.0,
                        }
                    ],
                }
            ],
        }

        # Configure mock to return the existing workout
        self.workout_repository_mock.get_workout_by_day.return_value = existing_workout

        # New completed exercise data with sets
        updated_exercises = [
            {
                "exercise_id": "ex123",
                "notes": "Improved effort",
                "sets": [
                    {"set_number": 1, "reps": 5, "weight": 225.0, "rpe": 8.0},
                    {"set_number": 2, "reps": 5, "weight": 225.0, "rpe": 8.5},
                ],
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

            # Add a completed exercise with sets to the workout
            completed_exercise = CompletedExercise(
                completed_id="updated-exercise",
                workout_id="existing-workout",
                exercise_id="ex123",
                notes="Improved effort",
            )

            # Add sets to the exercise
            exercise_set1 = Set(
                set_id="new-set1",
                completed_exercise_id="updated-exercise",
                workout_id="existing-workout",
                set_number=1,
                reps=5,
                weight=225.0,
                rpe=8.0,
            )

            exercise_set2 = Set(
                set_id="new-set2",
                completed_exercise_id="updated-exercise",
                workout_id="existing-workout",
                set_number=2,
                reps=5,
                weight=225.0,
                rpe=8.5,
            )

            completed_exercise.add_set(exercise_set1)
            completed_exercise.add_set(exercise_set2)
            updated_workout.add_exercise(completed_exercise)

            mock_update_workout.return_value = updated_workout

            # Call the service method
            result = self.workout_service.log_workout(
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                completed_exercises=updated_exercises,
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

            # Check that exercises and sets were correctly updated
            self.assertEqual(len(result.exercises), 1)
            self.assertEqual(result.exercises[0].notes, "Improved effort")
            self.assertEqual(len(result.exercises[0].sets), 2)

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

    def test_add_set_to_exercise(self):
        """
        Test adding a set to an exercise in a workout
        """
        # Mock workout data with an exercise
        workout_data = {
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
                    "notes": "Bench press",
                    "sets": [
                        {
                            "set_id": "set1",
                            "completed_exercise_id": "comp1",
                            "workout_id": "workout123",
                            "set_number": 1,
                            "reps": 5,
                            "weight": 225.0,
                            "rpe": 8.0,
                        }
                    ],
                }
            ],
        }

        # Configure mocks
        self.workout_repository_mock.get_workout.return_value = workout_data

        # Mock the set service
        self.set_service_mock.create_set.return_value = Set(
            set_id="set2",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=2,
            reps=5,
            weight=235.0,
            rpe=9.0,
        )

        # Set data to add
        set_data = {"set_number": 2, "reps": 5, "weight": 235.0, "rpe": 9.0}

        # Call the service method
        result = self.workout_service.add_set_to_exercise(
            "workout123", "comp1", set_data
        )

        # Assert repository and service methods were called correctly
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")
        self.set_service_mock.create_set.assert_called_once()
        self.workout_repository_mock.update_workout.assert_called_once()

        # Assert the returned object is the new set
        self.assertIsInstance(result, Set)
        self.assertEqual(result.set_id, "set2")
        self.assertEqual(result.set_number, 2)
        self.assertEqual(result.reps, 5)
        self.assertEqual(result.weight, 235.0)
        self.assertEqual(result.rpe, 9.0)

    def test_update_set(self):
        """
        Test updating a set in a workout
        """
        # Mock set data
        updated_set = Set(
            set_id="set1",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=1,
            reps=6,
            weight=235.0,
            rpe=9.0,
        )

        # Configure mock
        self.set_service_mock.update_set.return_value = updated_set

        # Set data to update
        update_data = {"reps": 6, "weight": 235.0, "rpe": 9.0}

        # Call the service method
        result = self.workout_service.update_set("set1", update_data)

        # Assert service methods were called correctly
        self.set_service_mock.update_set.assert_called_once_with("set1", update_data)

        # Assert the returned object is the updated set
        self.assertIsInstance(result, Set)
        self.assertEqual(result.set_id, "set1")
        self.assertEqual(result.reps, 6)
        self.assertEqual(result.weight, 235.0)
        self.assertEqual(result.rpe, 9.0)

    def test_delete_set(self):
        """
        Test deleting a set from a workout
        """
        # Mock set data
        set_data = Set(
            set_id="set1",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=225.0,
            rpe=8.0,
        )

        # Mock workout data
        workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "completed",
        }

        # Configure mocks
        self.set_service_mock.get_set.return_value = set_data
        self.set_service_mock.delete_set.return_value = True
        self.workout_repository_mock.get_workout.return_value = workout_data

        # Call the service method
        result = self.workout_service.delete_set("set1")

        # Assert service methods were called correctly
        self.set_service_mock.get_set.assert_called_once_with("set1")
        self.set_service_mock.delete_set.assert_called_once_with("set1")
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")
        self.workout_repository_mock.update_workout.assert_called_once()

        # Assert the result is True (successful deletion)
        self.assertTrue(result)

    def test_get_workout_sets(self):
        """
        Test getting all sets for a workout, organized by exercise
        """
        # Mock workout data with exercises and sets
        workout_data = {
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
                    "notes": "Bench press",
                    "sets": [
                        {
                            "set_id": "set1",
                            "completed_exercise_id": "comp1",
                            "workout_id": "workout123",
                            "set_number": 1,
                            "reps": 5,
                            "weight": 225.0,
                            "rpe": 8.0,
                        },
                        {
                            "set_id": "set2",
                            "completed_exercise_id": "comp1",
                            "workout_id": "workout123",
                            "set_number": 2,
                            "reps": 5,
                            "weight": 235.0,
                            "rpe": 8.5,
                        },
                    ],
                },
                {
                    "completed_id": "comp2",
                    "workout_id": "workout123",
                    "exercise_id": "ex2",
                    "notes": "Squat",
                    "sets": [
                        {
                            "set_id": "set3",
                            "completed_exercise_id": "comp2",
                            "workout_id": "workout123",
                            "set_number": 1,
                            "reps": 5,
                            "weight": 315.0,
                            "rpe": 9.0,
                        }
                    ],
                },
            ],
        }

        # Configure mock
        self.workout_repository_mock.get_workout.return_value = workout_data

        # Call the service method
        result = self.workout_service.get_workout_sets("workout123")

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")

        # Assert the result is a dictionary mapping exercise IDs to sets
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertIn("comp1", result)
        self.assertIn("comp2", result)
        self.assertEqual(len(result["comp1"]), 2)
        self.assertEqual(len(result["comp2"]), 1)

    def test_get_exercise_sets(self):
        """
        Test getting all sets for a specific exercise
        """
        # Mock set data
        sets_data = [
            Set(
                set_id="set1",
                completed_exercise_id="comp1",
                workout_id="workout123",
                set_number=1,
                reps=5,
                weight=225.0,
                rpe=8.0,
            ),
            Set(
                set_id="set2",
                completed_exercise_id="comp1",
                workout_id="workout123",
                set_number=2,
                reps=5,
                weight=235.0,
                rpe=8.5,
            ),
        ]

        # Configure mock
        self.set_service_mock.get_sets_for_exercise.return_value = sets_data

        # Call the service method
        result = self.workout_service.get_exercise_sets("comp1")

        # Assert service methods were called correctly
        self.set_service_mock.get_sets_for_exercise.assert_called_once_with("comp1")

        # Assert the result is a list of sets
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Set)
        self.assertEqual(result[0].set_id, "set1")
        self.assertEqual(result[1].set_id, "set2")

    def test_log_workout_with_minimal_data(self):
        """
        Test logging a workout with minimal required data
        """
        # Configure mock to return None (no existing workout)
        self.workout_repository_mock.get_workout_by_day.return_value = None

        # Prepare minimal completed exercises data with minimal set data
        completed_exercises = [
            {
                "exercise_id": "ex123",
                "sets": [
                    {
                        "set_number": 1,
                        "reps": 5,
                        "weight": 225.0
                        # No RPE or notes
                    }
                ],
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
        self.workout_repository_mock.get_workout_by_day.assert_called_once_with(
            "athlete123", "day456"
        )
        self.workout_repository_mock.create_workout.assert_called_once()

        # Check the workout data uses default values where missing
        workout_dict = self.workout_repository_mock.create_workout.call_args[0][0]
        self.assertEqual(workout_dict["status"], "completed")  # Default status
        self.assertIsNone(workout_dict["notes"])  # Default None for notes

        # Check the exercise has None for optional fields
        exercise_dict = workout_dict["exercises"][0]
        self.assertIsNone(exercise_dict.get("notes"))

        # Check the set has None for optional fields
        set_dict = exercise_dict["sets"][0]
        self.assertIsNone(set_dict.get("rpe"))
        self.assertIsNone(set_dict.get("notes"))

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
                "sets": [{"set_number": 1, "reps": 5, "weight": 225.0}],
            }
        ]

        # Call the service method with invalid status
        with self.assertRaises(ValueError):
            self.workout_service.log_workout(
                athlete_id="athlete123",
                day_id="day456",
                date="2025-03-15",
                completed_exercises=completed_exercises,
                status="invalid_status",  # Not one of: completed, partial, skipped
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

    def test_update_workout_with_exercises_and_sets(self):
        """
        Test updating a workout with exercises and sets (both existing and new)
        """
        # Mock the existing workout with exercises and sets
        existing_workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            status="partial",
        )

        # Add an existing exercise with sets
        existing_exercise = CompletedExercise(
            completed_id="existing-exercise",
            workout_id="workout123",
            exercise_id="ex1",
            notes="Initial notes",
        )

        # Add a set to the existing exercise
        existing_set = Set(
            set_id="existing-set",
            completed_exercise_id="existing-exercise",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=315.0,
        )

        existing_exercise.add_set(existing_set)
        existing_workout.add_exercise(existing_exercise)

        # Mock get_workout to return the existing workout first
        self.workout_repository_mock.get_workout.side_effect = [
            # First call when checking if workout exists
            {
                "workout_id": "workout123",
                "athlete_id": "athlete456",
                "day_id": "day789",
                "date": "2025-03-15",
                "status": "partial",
                "exercises": [
                    {
                        "completed_id": "existing-exercise",
                        "workout_id": "workout123",
                        "exercise_id": "ex1",
                        "notes": "Initial notes",
                        "sets": [
                            {
                                "set_id": "existing-set",
                                "completed_exercise_id": "existing-exercise",
                                "workout_id": "workout123",
                                "set_number": 1,
                                "reps": 5,
                                "weight": 315.0,
                            }
                        ],
                    }
                ],
            },
            # Second call after update
            {
                "workout_id": "workout123",
                "athlete_id": "athlete456",
                "day_id": "day789",
                "date": "2025-03-15",
                "status": "completed",
                "exercises": [
                    {
                        "completed_id": "existing-exercise",
                        "workout_id": "workout123",
                        "exercise_id": "ex1",
                        "notes": "Updated notes",
                        "sets": [
                            {
                                "set_id": "existing-set",
                                "completed_exercise_id": "existing-exercise",
                                "workout_id": "workout123",
                                "set_number": 1,
                                "reps": 6,
                                "weight": 325.0,
                            },
                            {
                                "set_id": "new-set",
                                "completed_exercise_id": "existing-exercise",
                                "workout_id": "workout123",
                                "set_number": 2,
                                "reps": 5,
                                "weight": 325.0,
                            },
                        ],
                    },
                    {
                        "completed_id": "new-exercise",
                        "workout_id": "workout123",
                        "exercise_id": "ex2",
                        "notes": "New exercise",
                        "sets": [
                            {
                                "set_id": "new-exercise-set",
                                "completed_exercise_id": "new-exercise",
                                "workout_id": "workout123",
                                "set_number": 1,
                                "reps": 8,
                                "weight": 225.0,
                            }
                        ],
                    },
                ],
            },
        ]

        # Mock the set service
        self.set_service_mock.get_sets_for_exercise.return_value = [existing_set]

        # Update data to send
        update_data = {
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "existing-exercise",
                    "exercise_id": "ex1",
                    "notes": "Updated notes",
                    "sets": [
                        {
                            "set_id": "existing-set",
                            "set_number": 1,
                            "reps": 6,
                            "weight": 325.0,  # Updated weight
                        },
                        {"set_number": 2, "reps": 5, "weight": 325.0},  # New set
                    ],
                },
                {
                    "exercise_id": "ex2",
                    "notes": "New exercise",
                    "sets": [{"set_number": 1, "reps": 8, "weight": 225.0}],
                },
            ],
        }

        # Call the service method
        result = self.workout_service.update_workout("workout123", update_data)

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called()
        self.workout_repository_mock.update_workout.assert_called()

        # Assert set service methods were called for updating existing sets
        self.set_service_mock.update_set.assert_called_with(
            "existing-set",
            {"set_id": "existing-set", "set_number": 1, "reps": 6, "weight": 325.0},
        )

        # Assert set service methods were called for creating new sets
        self.set_service_mock.create_set.assert_called()

        # Assert the result is a Workout with updated data
        self.assertIsInstance(result, Workout)
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.exercises), 2)

        # UUID should have been called for new IDs
        self.assertTrue(self.uuid_mock.called)

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

    def test_add_set_to_exercise_workout_not_found(self):
        """
        Test adding a set to an exercise when the workout doesn't exist
        """
        # Mock repository to return None (workout not found)
        self.workout_repository_mock.get_workout.return_value = None

        # Call the service method
        result = self.workout_service.add_set_to_exercise(
            "nonexistent", "exercise1", {"reps": 5, "weight": 225.0}
        )

        # Assert the result is None
        self.assertIsNone(result)

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called_once_with("nonexistent")
        self.set_service_mock.create_set.assert_not_called()

    def test_add_set_to_exercise_exercise_not_found(self):
        """
        Test adding a set to an exercise that doesn't exist in the workout
        """
        # Mock workout data without the target exercise
        workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "exercises": [
                {
                    "completed_id": "exercise1",
                    "workout_id": "workout123",
                    "exercise_id": "ex1",
                }
            ],
        }

        # Mock repository to return workout without the target exercise
        self.workout_repository_mock.get_workout.return_value = workout_data

        # Call the service method
        result = self.workout_service.add_set_to_exercise(
            "workout123", "nonexistent-exercise", {"reps": 5, "weight": 225.0}
        )

        # Assert the result is None
        self.assertIsNone(result)

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called_once_with("workout123")
        self.set_service_mock.create_set.assert_not_called()

    def test_delete_set_not_found(self):
        """
        Test deleting a set that doesn't exist
        """
        # Mock set service to return None (set not found)
        self.set_service_mock.get_set.return_value = None

        # Call the service method
        result = self.workout_service.delete_set("nonexistent")

        # Assert the result is False
        self.assertFalse(result)

        # Assert service methods were called correctly
        self.set_service_mock.get_set.assert_called_once_with("nonexistent")
        self.set_service_mock.delete_set.assert_not_called()
        self.workout_repository_mock.get_workout.assert_not_called()
        self.workout_repository_mock.update_workout.assert_not_called()

    def test_delete_set_fails(self):
        """
        Test when set service delete operation fails
        """
        # Mock set data
        set_data = Set(
            set_id="set1",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=225.0,
        )

        # Mock set service to return set but fail on delete
        self.set_service_mock.get_set.return_value = set_data
        self.set_service_mock.delete_set.return_value = False

        # Call the service method
        result = self.workout_service.delete_set("set1")

        # Assert the result is False
        self.assertFalse(result)

        # Assert service methods were called correctly
        self.set_service_mock.get_set.assert_called_once_with("set1")
        self.set_service_mock.delete_set.assert_called_once_with("set1")
        self.workout_repository_mock.get_workout.assert_not_called()
        self.workout_repository_mock.update_workout.assert_not_called()

    def test_get_workout_sets_no_workout(self):
        """
        Test getting sets for a workout that doesn't exist
        """
        # Mock repository to return None (workout not found)
        self.workout_repository_mock.get_workout.return_value = None

        # Call the service method
        result = self.workout_service.get_workout_sets("nonexistent")

        # Assert the result is an empty dictionary
        self.assertEqual(result, {})

        # Assert repository methods were called correctly
        self.workout_repository_mock.get_workout.assert_called_once_with("nonexistent")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
