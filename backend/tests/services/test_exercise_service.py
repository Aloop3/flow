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
            "is_predefined": True,
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
            "rpe": 8.5,
            "notes": "Use belt",
            "order": 1,
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
                "is_predefined": True,
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
                "is_predefined": True,
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
            "is_predefined": True,
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
                "is_predefined": True,
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
                "is_predefined": True,
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
                "is_predefined": True,
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
                "is_predefined": True,
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
                "is_predefined": True,
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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
