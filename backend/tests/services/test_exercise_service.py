import unittest
from unittest.mock import MagicMock, patch
from src.models.exercise import Exercise
from src.services.exercise_service import ExerciseService


class TestExerciseService(unittest.TestCase):
    """
    Test suite for the ExerciseService
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.exercise_repository_mock = MagicMock()

        # Create patcher for uuid4 to return predictable IDs
        self.uuid_patcher = patch("uuid.uuid4", return_value="test-uuid")
        self.uuid_mock = self.uuid_patcher.start()

        # Initialize service with mocked repository
        with patch(
            "src.services.exercise_service.ExerciseRepository",
            return_value=self.exercise_repository_mock,
        ):
            self.exercise_service = ExerciseService()

    def tearDown(self):
        """
        Clean up after each test method
        """
        self.uuid_patcher.stop()

    def test_get_exercise(self):
        """
        Test retrieving an exercise by ID
        """
        # Mock data that would be returned from the repository
        mock_exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "exercise_category": "barbell",
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
            "rpe": 8.5,
            "notes": "Use belt",
            "order": 1,
            "status": "planned",
        }

        # Configure mock to return our test data
        self.exercise_repository_mock.get_exercise.return_value = mock_exercise_data

        # Call the service method
        result = self.exercise_service.get_exercise("ex123")

        # Assert repository was called with correct ID
        self.exercise_repository_mock.get_exercise.assert_called_once_with("ex123")

        # Assert the result is an Exercise instance with correct data
        self.assertIsInstance(result, Exercise)
        self.assertEqual(result.exercise_id, "ex123")
        self.assertEqual(result.workout_id, "workout456")
        self.assertEqual(result.exercise_type.name, "Squat")
        self.assertEqual(result.exercise_category.value, "barbell")
        self.assertEqual(result.sets, 5)
        self.assertEqual(result.reps, 5)
        self.assertEqual(result.weight, 315.0)
        self.assertEqual(result.rpe, 8.5)
        self.assertEqual(result.notes, "Use belt")
        self.assertEqual(result.order, 1)
        self.assertEqual(result.status, "planned")

    def test_get_exercise_not_found(self):
        """
        Test retrieving a non-existent exercise returns None
        """
        # Configure mock to return None (exercise not found)
        self.exercise_repository_mock.get_exercise.return_value = None

        # Call the service method
        result = self.exercise_service.get_exercise("nonexistent")

        # Assert repository was called with correct ID
        self.exercise_repository_mock.get_exercise.assert_called_once_with(
            "nonexistent"
        )

        # Assert the result is None
        self.assertIsNone(result)

    def test_get_exercises_by_workout(self):
        """
        Test retrieving all exercises for a workout
        """
        # Mock data that would be returned from the repository
        mock_exercises_data = [
            {
                "exercise_id": "ex1",
                "workout_id": "workout123",
                "exercise_type": "Squat",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 315.0,
                "order": 1,
            },
            {
                "exercise_id": "ex2",
                "workout_id": "workout123",
                "exercise_type": "Bench Press",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 225.0,
                "order": 2,
            },
        ]

        # Configure mock to return our test data
        self.exercise_repository_mock.get_exercises_by_workout.return_value = (
            mock_exercises_data
        )

        # Call the service method
        result = self.exercise_service.get_exercises_for_workout("workout123")

        # Assert repository was called with correct workout ID
        self.exercise_repository_mock.get_exercises_by_workout.assert_called_once_with(
            "workout123"
        )

        # Assert the result is a list of Exercise instances with correct data
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Exercise)
        self.assertEqual(result[0].exercise_id, "ex1")
        self.assertEqual(result[0].exercise_type.name, "Squat")
        self.assertEqual(result[1].exercise_id, "ex2")
        self.assertEqual(result[1].exercise_type.name, "Bench Press")

    def test_create_exercise(self):
        """
        Test creating a new exercise
        """
        # Call the service method
        result = self.exercise_service.create_exercise(
            workout_id="workout123",
            exercise_type="Squat",
            sets=5,
            reps=5,
            weight=315.0,
            rpe=8.5,
            notes="Use belt",
            order=1,
        )

        # Assert the UUID function was called
        self.uuid_mock.assert_called()

        # Assert repository create method was called
        self.exercise_repository_mock.create_exercise.assert_called_once()

        # Assert the returned object is an Exercise with correct data
        self.assertIsInstance(result, Exercise)
        self.assertEqual(result.exercise_id, "test-uuid")
        self.assertEqual(result.workout_id, "workout123")
        self.assertEqual(result.exercise_type.name, "Squat")
        self.assertEqual(result.sets, 5)
        self.assertEqual(result.reps, 5)
        self.assertEqual(result.weight, 315.0)
        self.assertEqual(result.rpe, 8.5)
        self.assertEqual(result.notes, "Use belt")
        self.assertEqual(result.order, 1)

    def test_create_exercise_without_order(self):
        """
        Test creating an exercise without specifying order (should auto-assign)
        """
        # Mock existing exercises
        existing_exercises = [{"order": 1}, {"order": 2}]

        # Configure mock to return the existing exercises
        self.exercise_repository_mock.get_exercises_by_workout.return_value = (
            existing_exercises
        )

        # Call the service method without order
        result = self.exercise_service.create_exercise(
            workout_id="workout123",
            exercise_type="Deadlift",
            sets=3,
            reps=5,
            weight=405.0,
        )

        # Assert repository was called to get existing exercises
        self.exercise_repository_mock.get_exercises_by_workout.assert_called_once_with(
            "workout123"
        )

        # Assert the exercise was created with the next order number (3)
        self.assertEqual(result.order, 3)

        # Assert the create method was called with the correct data
        self.exercise_repository_mock.create_exercise.assert_called_once()

    def test_update_exercise(self):
        """
        Test updating an exercise
        """
        # Mock data for the updated exercise
        updated_exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "exercise_category": "barbell",
            "sets": 3,  # Updated from 5 to 3
            "reps": 5,
            "weight": 335.0,  # Updated weight
            "rpe": 9.0,  # Updated RPE
            "notes": "Use belt and knee sleeves",  # Updated notes
            "order": 1,
        }

        # Configure mocks
        self.exercise_repository_mock.update_exercise.return_value = {
            "Attributes": {"sets": 3, "weight": 335.0}
        }
        self.exercise_repository_mock.get_exercise.return_value = updated_exercise_data

        # Data to update
        update_data = {
            "sets": 3,
            "weight": 335.0,
            "rpe": 9.0,
            "notes": "Use belt and knee sleeves",
        }

        # Call the service method
        result = self.exercise_service.update_exercise("ex123", update_data)

        # Assert repository methods were called correctly
        self.exercise_repository_mock.update_exercise.assert_called_once_with(
            "ex123", update_data
        )
        self.exercise_repository_mock.get_exercise.assert_called_once_with("ex123")

        # Assert the returned object has the updated values
        self.assertIsInstance(result, Exercise)
        self.assertEqual(result.sets, 3)
        self.assertEqual(result.weight, 335.0)
        self.assertEqual(result.rpe, 9.0)
        self.assertEqual(result.notes, "Use belt and knee sleeves")

        # Assert the other values remain unchanged
        self.assertEqual(result.exercise_id, "ex123")
        self.assertEqual(result.workout_id, "workout456")
        self.assertEqual(result.exercise_type.name, "Squat")

    def test_delete_exercise(self):
        """Test deleting an exercise"""
        # Configure mock to return a successful response
        self.exercise_repository_mock.delete_exercise.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        # Call the service method
        result = self.exercise_service.delete_exercise("ex123")

        # Assert repository was called with correct ID
        self.exercise_repository_mock.delete_exercise.assert_called_once_with("ex123")

        # Assert the result is True (successful deletion)
        self.assertTrue(result)

    def test_reorder_exercises(self):
        """Test reordering exercises for a workout"""
        # New order for exercises
        exercise_order = ["ex3", "ex1", "ex2"]

        # Mock data for the exercises
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "workout_id": "workout123",
                "exercise_type": "Squat",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 315.0,
                "order": 1,
            },
            {
                "exercise_id": "ex2",
                "workout_id": "workout123",
                "exercise_type": "Bench Press",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 225.0,
                "order": 2,
            },
            {
                "exercise_id": "ex3",
                "workout_id": "workout123",
                "exercise_type": "Deadlift",
                "exercise_category": "barbell",
                "sets": 3,
                "reps": 5,
                "weight": 405.0,
                "order": 3,
            },
        ]

        # Configure mock to return exercises for get_exercises_for_workout
        # We need to return this twice: once for initially loading, once after reordering
        self.exercise_repository_mock.get_exercises_by_workout.return_value = (
            mock_exercises
        )

        # Mock the update_exercise method to avoid having to set up complex return behavior
        with patch.object(
            self.exercise_service, "update_exercise"
        ) as mock_update_exercise:
            # Call the service method
            self.exercise_service.reorder_exercises("workout123", exercise_order)

            # Assert update_exercise was called for each exercise with the correct order
            # First call: update ex3 to order 1
            mock_update_exercise.assert_any_call("ex3", {"order": 1})
            # Second call: update ex1 to order 2
            mock_update_exercise.assert_any_call("ex1", {"order": 2})
            # Third call: update ex2 to order 3
            mock_update_exercise.assert_any_call("ex2", {"order": 3})

            # Assert update_exercise was called the correct number of times
            self.assertEqual(mock_update_exercise.call_count, 3)

    def test_reorder_exercises_with_invalid_ids(self):
        """Test reordering with some invalid exercise IDs"""
        # New order with one invalid ID
        exercise_order = ["ex1", "invalid-id", "ex2"]

        # Mock data for the exercises
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "workout_id": "workout123",
                "exercise_type": "Squat",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 315.0,
                "order": 1,
            },
            {
                "exercise_id": "ex2",
                "workout_id": "workout123",
                "exercise_type": "Bench Press",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 225.0,
                "order": 2,
            },
        ]

        # Configure mock for get_exercises_for_workout
        self.exercise_repository_mock.get_exercises_by_workout.return_value = (
            mock_exercises
        )

        # Mock the update_exercise method
        with patch.object(
            self.exercise_service, "update_exercise"
        ) as mock_update_exercise:
            # Call the service method
            self.exercise_service.reorder_exercises("workout123", exercise_order)

            # Assert update_exercise was called for valid IDs with the correct order
            mock_update_exercise.assert_any_call("ex1", {"order": 1})
            mock_update_exercise.assert_any_call("ex2", {"order": 3})

            # Assert update_exercise was called only for valid IDs (2 times, not 3)
            self.assertEqual(mock_update_exercise.call_count, 2)

    def test_reorder_sets_success_simple_reorder(self):
        """
        Test successful reordering of sets in simple case.

        Given: Exercise with 3 sets in order [1, 2, 3]
        When: Reordering to [3, 1, 2]
        Then: Set numbers should be renumbered to [1, 2, 3] respectively
        """
        # Arrange
        exercise_id = "test-exercise-id"
        original_sets_data = [
            {"set_number": 1, "reps": 10, "weight": 100, "completed": True},
            {"set_number": 2, "reps": 8, "weight": 105, "completed": True},
            {"set_number": 3, "reps": 6, "weight": 110, "completed": False},
        ]

        exercise_dict = {
            "exercise_id": exercise_id,
            "workout_id": "test-workout",
            "exercise_type": "Bench Press",
            "sets": 3,
            "reps": 10,
            "weight": 100,
            "sets_data": original_sets_data,
            "status": "planned",
        }

        # Mock repository responses
        self.exercise_repository_mock.get_exercise.return_value = exercise_dict

        updated_exercise_dict = exercise_dict.copy()
        updated_exercise_dict["sets_data"] = [
            {
                "set_number": 1,
                "reps": 6,
                "weight": 110,
                "completed": False,
            },  # Was set 3
            {
                "set_number": 2,
                "reps": 10,
                "weight": 100,
                "completed": True,
            },  # Was set 1
            {"set_number": 3, "reps": 8, "weight": 105, "completed": True},  # Was set 2
        ]

        # Mock update_exercise to return updated exercise
        with patch.object(self.exercise_service, "update_exercise") as mock_update:
            from src.models.exercise import Exercise

            updated_exercise = Exercise.from_dict(updated_exercise_dict)
            mock_update.return_value = updated_exercise

            new_order = [3, 1, 2]  # Reorder: set 3 first, then set 1, then set 2

            # Act
            result = self.exercise_service.reorder_sets(exercise_id, new_order)

            # Assert
            self.assertIsNotNone(result)
            self.assertEqual(len(result.sets_data), 3)

            # Verify the sets are reordered correctly
            self.assertEqual(
                result.sets_data[0]["reps"], 6
            )  # Original set 3 → position 1
            self.assertEqual(
                result.sets_data[1]["reps"], 10
            )  # Original set 1 → position 2
            self.assertEqual(
                result.sets_data[2]["reps"], 8
            )  # Original set 2 → position 3

            # Verify set_numbers are sequential
            self.assertEqual(result.sets_data[0]["set_number"], 1)
            self.assertEqual(result.sets_data[1]["set_number"], 2)
            self.assertEqual(result.sets_data[2]["set_number"], 3)

            # Verify update_exercise was called with correct data
            mock_update.assert_called_once()

    def test_reorder_sets_exercise_not_found(self):
        """
        Test reorder_sets when exercise doesn't exist.

        Given: Non-existent exercise ID
        When: Attempting to reorder sets
        Then: Should return None
        """
        # Arrange
        exercise_id = "nonexistent-exercise"
        self.exercise_repository_mock.get_exercise.return_value = None
        new_order = [1, 2, 3]

        # Act
        result = self.exercise_service.reorder_sets(exercise_id, new_order)

        # Assert
        self.assertIsNone(result)

    def test_reorder_sets_no_sets_data(self):
        """
        Test reorder_sets when exercise has no sets_data.

        Given: Exercise without any tracked sets
        When: Attempting to reorder sets
        Then: Should return None
        """
        # Arrange
        exercise_id = "test-exercise-id"
        exercise_dict = {
            "exercise_id": exercise_id,
            "workout_id": "test-workout",
            "exercise_type": "Bench Press",
            "sets": 3,
            "reps": 10,
            "weight": 100,
            "sets_data": None,  # No sets tracked yet
        }

        self.exercise_repository_mock.get_exercise.return_value = exercise_dict
        new_order = [1, 2, 3]

        # Act
        result = self.exercise_service.reorder_sets(exercise_id, new_order)

        # Assert
        self.assertIsNone(result)

    def test_reorder_sets_invalid_order_missing_set(self):
        """
        Test reorder_sets with invalid new_order (missing set numbers).

        Given: Exercise with sets [1, 2, 3]
        When: new_order is [1, 2] (missing set 3)
        Then: Should raise ValueError
        """
        # Arrange
        exercise_id = "test-exercise-id"
        original_sets_data = [
            {"set_number": 1, "reps": 10, "weight": 100},
            {"set_number": 2, "reps": 8, "weight": 105},
            {"set_number": 3, "reps": 6, "weight": 110},
        ]

        exercise_dict = {
            "exercise_id": exercise_id,
            "workout_id": "test-workout",
            "exercise_type": "Bench Press",
            "sets": 3,
            "reps": 10,
            "weight": 100,
            "sets_data": original_sets_data,
        }

        self.exercise_repository_mock.get_exercise.return_value = exercise_dict

        invalid_order = [1, 2]  # Missing set 3

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.exercise_service.reorder_sets(exercise_id, invalid_order)

        self.assertIn(
            "new_order must contain all existing set numbers", str(context.exception)
        )

    def test_reorder_sets_single_set_no_change(self):
        """
        Test reorder_sets with single set (edge case).

        Given: Exercise with only 1 set
        When: Reordering with [1]
        Then: Should succeed with no changes
        """
        # Arrange
        exercise_id = "test-exercise-id"
        original_sets_data = [
            {"set_number": 1, "reps": 10, "weight": 100, "completed": True}
        ]

        exercise_dict = {
            "exercise_id": exercise_id,
            "workout_id": "test-workout",
            "exercise_type": "Bench Press",
            "sets": 1,
            "reps": 10,
            "weight": 100,
            "sets_data": original_sets_data,
            "status": "planned",
        }

        self.exercise_repository_mock.get_exercise.return_value = exercise_dict

        # Mock update_exercise to return same exercise
        with patch.object(self.exercise_service, "update_exercise") as mock_update:
            from src.models.exercise import Exercise

            exercise = Exercise.from_dict(exercise_dict)
            mock_update.return_value = exercise

            new_order = [1]

            # Act
            result = self.exercise_service.reorder_sets(exercise_id, new_order)

            # Assert
            self.assertIsNotNone(result)
            self.assertEqual(len(result.sets_data), 1)
            self.assertEqual(result.sets_data[0]["set_number"], 1)
            self.assertEqual(result.sets_data[0]["reps"], 10)

    def test_get_exercises_for_workout_empty(self):
        """Test retrieving exercises for a workout that has no exercises"""
        # Configure mock to return an empty list
        self.exercise_repository_mock.get_exercises_by_workout.return_value = []

        # Call the service method
        result = self.exercise_service.get_exercises_for_workout("empty-workout")

        # Assert repository was called with correct workout ID
        self.exercise_repository_mock.get_exercises_by_workout.assert_called_once_with(
            "empty-workout"
        )

        # Assert the result is an empty list
        self.assertEqual(result, [])

    def test_delete_exercises_by_workout(self):
        """
        Test deleting all exercises associated with a workout
        """
        # Mock data for exercises
        mock_exercises = [
            {
                "exercise_id": "ex1",
                "workout_id": "workout123",
                "exercise_type": "Squat",
            },
            {
                "exercise_id": "ex2",
                "workout_id": "workout123",
                "exercise_type": "Bench Press",
            },
            {
                "exercise_id": "ex3",
                "workout_id": "workout123",
                "exercise_type": "Deadlift",
            },
        ]

        # Mock the batch writer
        mock_batch_writer = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_context_manager.__exit__ = MagicMock(return_value=None)

        # Configure mocks
        self.exercise_repository_mock.get_exercises_by_workout.return_value = (
            mock_exercises
        )
        self.exercise_repository_mock.table.batch_writer.return_value = (
            mock_context_manager
        )

        # Call the service method
        result = self.exercise_service.delete_exercises_by_workout("workout123")

        # Assert repository was called to get exercises
        self.exercise_repository_mock.get_exercises_by_workout.assert_called_once_with(
            "workout123"
        )

        # Assert batch writer was used
        self.exercise_repository_mock.table.batch_writer.assert_called_once()

        # Assert delete_item was called for each exercise
        self.assertEqual(mock_batch_writer.delete_item.call_count, 3)
        mock_batch_writer.delete_item.assert_any_call(Key={"exercise_id": "ex1"})
        mock_batch_writer.delete_item.assert_any_call(Key={"exercise_id": "ex2"})
        mock_batch_writer.delete_item.assert_any_call(Key={"exercise_id": "ex3"})

        # Assert the result is the number of exercises deleted
        self.assertEqual(result, 3)

    def test_delete_exercises_by_workout_empty(self):
        """
        Test deleting exercises for a workout that has no exercises
        """
        # Configure mock to return empty list
        self.exercise_repository_mock.get_exercises_by_workout.return_value = []

        # Mock the batch writer
        mock_batch_writer = MagicMock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__ = MagicMock(return_value=mock_batch_writer)
        mock_context_manager.__exit__ = MagicMock(return_value=None)
        self.exercise_repository_mock.table.batch_writer.return_value = (
            mock_context_manager
        )

        # Call the service method
        result = self.exercise_service.delete_exercises_by_workout("empty-workout")

        # Assert repository was called
        self.exercise_repository_mock.get_exercises_by_workout.assert_called_once_with(
            "empty-workout"
        )

        # Assert batch writer was used
        self.exercise_repository_mock.table.batch_writer.assert_called_once()

        # Assert delete_item was not called (no exercises to delete)
        mock_batch_writer.delete_item.assert_not_called()

        # Assert the result is 0 (no exercises deleted)
        self.assertEqual(result, 0)

    def test_capture_planned_snapshot_success(self):
        """
        Test capturing planned snapshot when sets_data exists and planned_sets_data is None
        """
        # Mock exercise with sets_data but no planned_sets_data
        mock_exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 225.0,
            "status": "planned",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 3, "reps": 5, "weight": 225.0, "completed": False},
            ],
            "planned_sets_data": None,
        }

        # Mock updated exercise after snapshot
        mock_updated_exercise_data = mock_exercise_data.copy()
        mock_updated_exercise_data["planned_sets_data"] = [
            {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
            {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
            {"set_number": 3, "reps": 5, "weight": 225.0, "completed": False},
        ]

        # Configure mocks
        self.exercise_repository_mock.get_exercise.side_effect = [
            mock_exercise_data,  # First call in capture_planned_snapshot
            mock_updated_exercise_data,  # Second call at end of method
        ]

        # Call the service method
        result = self.exercise_service.capture_planned_snapshot("ex123")

        # Assert repository methods were called
        self.assertEqual(self.exercise_repository_mock.get_exercise.call_count, 2)
        self.exercise_repository_mock.update_exercise.assert_called_once()

        # Verify update_exercise was called with planned_sets_data
        update_call_args = self.exercise_repository_mock.update_exercise.call_args
        self.assertEqual(update_call_args[0][0], "ex123")  # exercise_id
        self.assertIn("planned_sets_data", update_call_args[0][1])  # update_data

        # Assert the result is an Exercise instance
        self.assertIsInstance(result, Exercise)
        self.assertIsNotNone(result.planned_sets_data)

    def test_capture_planned_snapshot_already_captured(self):
        """
        Test that capture_planned_snapshot does nothing when planned_sets_data already exists
        """
        # Mock exercise with both sets_data and planned_sets_data
        mock_exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 225.0,
            "status": "planned",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 230.0, "completed": True},
            ],
            "planned_sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
            ],
        }

        # Configure mock
        self.exercise_repository_mock.get_exercise.return_value = mock_exercise_data

        # Call the service method
        result = self.exercise_service.capture_planned_snapshot("ex123")

        # Assert repository get was called but update was NOT called
        self.exercise_repository_mock.get_exercise.assert_called_once_with("ex123")
        self.exercise_repository_mock.update_exercise.assert_not_called()

        # Assert the result is the same exercise
        self.assertIsInstance(result, Exercise)
        self.assertIsNotNone(result.planned_sets_data)

    def test_capture_planned_snapshot_exercise_not_found(self):
        """
        Test that capture_planned_snapshot returns None when exercise doesn't exist
        """
        # Configure mock to return None (exercise not found)
        self.exercise_repository_mock.get_exercise.return_value = None

        # Call the service method
        result = self.exercise_service.capture_planned_snapshot("nonexistent")

        # Assert repository was called but update was not
        self.exercise_repository_mock.get_exercise.assert_called_once_with(
            "nonexistent"
        )
        self.exercise_repository_mock.update_exercise.assert_not_called()

        # Assert the result is None
        self.assertIsNone(result)

    def test_track_set_captures_planned_snapshot(self):
        """
        Test that track_set captures planned snapshot on first set tracking
        """
        # Mock exercise without planned_sets_data
        mock_exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 225.0,
            "status": "planned",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 3, "reps": 5, "weight": 225.0, "completed": False},
            ],
            "planned_sets_data": None,
        }

        # Use return_value instead of side_effect to avoid StopIteration
        self.exercise_repository_mock.get_exercise.return_value = mock_exercise_data

        # Call track_set
        result = self.exercise_service.track_set(
            exercise_id="ex123", set_number=1, reps=5, weight=230.0, completed=True
        )

        # Assert that update_exercise was called (at least once for planned snapshot)
        self.assertTrue(self.exercise_repository_mock.update_exercise.called)

        # Check if any update call included planned_sets_data
        update_calls = self.exercise_repository_mock.update_exercise.call_args_list
        planned_snapshot_captured = any(
            "planned_sets_data" in call[0][1] for call in update_calls
        )
        self.assertTrue(
            planned_snapshot_captured, "Planned snapshot should have been captured"
        )

        # Assert result is an Exercise
        self.assertIsInstance(result, Exercise)

    @patch("src.repositories.exercise_repository.ExerciseRepository")
    def test_track_set(self, mock_repo):
        # Setup
        service = ExerciseService()
        service.exercise_repository = mock_repo

        # Mock existing exercise
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            sets_data=[],
            status="planned",
        )

        # Setup repository behavior
        exercise_dict = exercise.to_dict()
        exercise_dict.pop("is_predefined", None)
        mock_repo.get_exercise.return_value = exercise_dict
        mock_repo.update_exercise.return_value = {
            **exercise.to_dict(),
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": True}
            ],
            "status": "in_progress",
        }

        # Call service method
        result = service.track_set(
            exercise_id="test123", set_number=1, reps=5, weight=225.0, completed=True
        )

        # Verify repository was called correctly
        mock_repo.update_exercise.assert_called_once()
        call_args = mock_repo.update_exercise.call_args[0]
        self.assertEqual(call_args[0], "test123")  # exercise_id

        # Check that sets_data was included in update
        update_data = call_args[1]
        self.assertIn("sets_data", update_data)
        self.assertEqual(len(update_data["sets_data"]), 1)

        # Verify result
        self.assertIsNotNone(result)

    @patch("src.repositories.exercise_repository.ExerciseRepository")
    def test_track_set_updates_status(self, mock_repo):
        # Setup
        service = ExerciseService()
        service.exercise_repository = mock_repo

        # Mock existing exercise with "planned" status
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
            sets_data=[],
        )

        # Setup repository behavior
        exercise_dict = exercise.to_dict()
        exercise_dict.pop("is_predefined", None)
        mock_repo.get_exercise.return_value = exercise_dict
        updated_exercise_dict = {
            **exercise.to_dict(),
            "status": "in_progress",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": True}
            ],
        }
        mock_repo.update_exercise.return_value = updated_exercise_dict

        # Call service method
        result = service.track_set(
            exercise_id="test123", set_number=1, reps=5, weight=225.0, completed=True
        )

        # Verify status was updated
        update_data = mock_repo.update_exercise.call_args[0][1]
        self.assertIn("status", update_data)
        self.assertEqual(update_data["status"], "in_progress")

        # Verify result
        self.assertIsNotNone(result)

    @patch("src.repositories.exercise_repository.ExerciseRepository")
    def test_track_set_nonexistent_exercise(self, mock_repo):
        # Setup
        service = ExerciseService()
        service.exercise_repository = mock_repo

        # Setup repository behavior for nonexistent exercise
        mock_repo.get_exercise.return_value = None

        # Call service method
        result = service.track_set(
            exercise_id="nonexistent", set_number=1, reps=5, weight=225.0
        )

        # Verify result is None
        self.assertIsNone(result)

        # Verify update was not called
        mock_repo.update_exercise.assert_not_called()

    @patch("src.repositories.exercise_repository.ExerciseRepository")
    def test_track_set_with_rpe_and_notes(self, mock_repo):
        """Test for adding RPE and notes to the set data"""
        # Setup
        service = ExerciseService()
        service.exercise_repository = mock_repo

        # Mock existing exercise
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            sets_data=[],
        )

        # Setup repository behavior
        exercise_dict = exercise.to_dict()
        exercise_dict.pop("is_predefined", None)
        mock_repo.get_exercise.return_value = exercise_dict
        mock_repo.update_exercise.return_value = {
            **exercise.to_dict(),
            "sets_data": [
                {
                    "set_number": 1,
                    "reps": 5,
                    "weight": 225.0,
                    "completed": True,
                    "rpe": 8,
                    "notes": "Felt good",
                }
            ],
        }

        # Call service method with RPE and notes
        result = service.track_set(
            exercise_id="test123",
            set_number=1,
            reps=5,
            weight=225.0,
            rpe=8,  # Adding RPE
            notes="Felt good",  # Adding notes
            completed=True,
        )

        # Verify repository was called with correct data
        mock_repo.update_exercise.assert_called_once()
        call_args = mock_repo.update_exercise.call_args[0]
        update_data = call_args[1]

        # Verify sets_data includes RPE and notes
        self.assertIn("sets_data", update_data)
        set_data = update_data["sets_data"][0]
        self.assertEqual(set_data["rpe"], 8)
        self.assertEqual(set_data["notes"], "Felt good")

    @patch("src.repositories.exercise_repository.ExerciseRepository")
    def test_track_set_already_in_progress(self, mock_repo):
        """Test for Exercise already in progress"""
        # Setup
        service = ExerciseService()
        service.exercise_repository = mock_repo

        # Mock existing exercise with "in_progress" status
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            status="in_progress",
            sets_data=[
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": True}
            ],
        )

        # Setup repository behavior
        exercise_dict = exercise.to_dict()
        exercise_dict.pop("is_predefined", None)
        mock_repo.get_exercise.return_value = exercise_dict
        mock_repo.update_exercise.return_value = {
            **exercise.to_dict(),
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": True},
                {"set_number": 2, "reps": 5, "weight": 230.0, "completed": True},
            ],
        }

        # Call service method
        result = service.track_set(
            exercise_id="test123", set_number=2, reps=5, weight=230.0, completed=True
        )

        # Verify update doesn't include status change
        update_data = mock_repo.update_exercise.call_args[0][1]
        self.assertIn("sets_data", update_data)
        self.assertNotIn(
            "status", update_data
        )  # Status not updated when already in progress

    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.update_exercise")
    def test_delete_set_success(self, mock_update_exercise, mock_get_exercise):
        """
        Test successful set deletion
        """
        # Setup mock exercise with proper structure
        mock_exercise = MagicMock()
        mock_exercise.sets_data = [
            {"set_number": 1, "reps": 10, "weight": 100.0, "completed": True}
        ]
        mock_get_exercise.return_value = mock_exercise

        # Setup updated exercise with no sets
        updated_exercise = {
            "exercise_id": "test-exercise-1",
            "workout_id": "test-workout-1",
            "sets_data": [],
        }
        mock_update_exercise.return_value = updated_exercise

        # Call service method
        result = self.exercise_service.delete_set("test-exercise-1", 1)

        # Assert update_exercise was called with correct parameters
        mock_update_exercise.assert_called_once()
        call_args = mock_update_exercise.call_args[0]
        self.assertEqual(call_args[0], "test-exercise-1")
        self.assertIn("sets_data", call_args[1])
        self.assertEqual(len(call_args[1]["sets_data"]), 0)

        # Assert result is the updated exercise
        self.assertEqual(result, updated_exercise)

    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.update_exercise")
    def test_delete_set_all_completed(self, mock_update_exercise, mock_get_exercise):
        """
        Test deleting a set when all sets are marked as completed
        """
        # Setup mock exercise with all sets completed
        mock_exercise = MagicMock()
        mock_exercise.sets_data = [
            {"set_number": 1, "reps": 10, "weight": 100.0, "completed": True},
            {"set_number": 2, "reps": 8, "weight": 90.0, "completed": True},
        ]
        mock_get_exercise.return_value = mock_exercise

        # Setup updated exercise with one set remaining
        updated_exercise = {
            "exercise_id": "test-exercise-1",
            "workout_id": "test-workout-1",
            "sets_data": [
                {"set_number": 1, "reps": 10, "weight": 100.0, "completed": True}
            ],
        }
        mock_update_exercise.return_value = updated_exercise

        # Call service method
        result = self.exercise_service.delete_set("test-exercise-1", 2)

        # Assert update_exercise was called with correct parameters
        mock_update_exercise.assert_called_once()
        call_args = mock_update_exercise.call_args[0]
        self.assertEqual(call_args[0], "test-exercise-1")

        # Fix: Verify remaining sets
        self.assertIn("sets_data", call_args[1])
        self.assertEqual(len(call_args[1]["sets_data"]), 1)
        self.assertEqual(call_args[1]["sets_data"][0]["set_number"], 1)

        # Assert result is the updated exercise
        self.assertEqual(result, updated_exercise)

    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_delete_set_exercise_not_found(self, mock_get_exercise):
        """
        Test exercise set deletion when the exercise is not found
        """
        # Setup mock to return None for exercise
        mock_get_exercise.return_value = None

        # Define event and context
        event = {
            "pathParameters": {"exercise_id": "test-exercise-1", "set_number": "1"}
        }
        context = {}

        # Call service method
        result = self.exercise_service.delete_set("test-exercise-1", 1)

        # Assert the result is None, as exercise was not found
        self.assertEqual(result, None)

    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.update_exercise")
    def test_delete_set_not_found(self, mock_update_exercise, mock_get_exercise):
        """
        Test deleting a set when the set is not found
        """
        # Setup mock exercise with empty sets data
        mock_exercise = MagicMock()
        mock_exercise.sets_data = []
        mock_get_exercise.return_value = mock_exercise

        # Define event and context
        event = {
            "pathParameters": {"exercise_id": "test-exercise-1", "set_number": "999"}
        }
        context = {}

        # Call service method
        result = self.exercise_service.delete_set("test-exercise-1", 999)

        # Assert the result is None, as the set was not found
        self.assertEqual(result, None)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
