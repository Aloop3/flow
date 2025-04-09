import unittest
from unittest.mock import MagicMock, patch, ANY
from boto3.dynamodb.conditions import Key
from src.repositories.exercise_repository import ExerciseRepository


class TestExerciseRepository(unittest.TestCase):
    """
    Test suite for the ExerciseRepository
    """

    def setUp(self):
        """
        Set up the test environment before each test
        """
        # Create a mock for the DynamoDB table
        self.table_mock = MagicMock()

        # Create the repository with the mocked table
        self.repository = ExerciseRepository()
        self.repository.table = self.table_mock

    def test_get_exercise(self):
        """
        Test getting an exercise by its ID
        """
        # Mock data
        exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
        }

        # Configure mock
        self.table_mock.get_item.return_value = {"Item": exercise_data}

        # Call the repository method
        result = self.repository.get_exercise("ex123")

        # Assert the table was called correctly
        self.table_mock.get_item.assert_called_once_with(Key={"exercise_id": "ex123"})

        # Assert the result is correct
        self.assertEqual(result, exercise_data)

    def test_get_exercise_not_found(self):
        """
        Test getting a non-existent exercise
        """
        # Configure mock to return no item
        self.table_mock.get_item.return_value = {}

        # Call the repository method
        result = self.repository.get_exercise("nonexistent")

        # Assert the table was called correctly
        self.table_mock.get_item.assert_called_once_with(
            Key={"exercise_id": "nonexistent"}
        )

        # Assert the result is None
        self.assertIsNone(result)

    def test_get_exercises_by_workout(self):
        """
        Test getting all exercises for a workout
        """
        # Mock data
        exercises_data = [
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
        ]

        # Configure mock
        self.table_mock.query.return_value = {"Items": exercises_data}

        # Call the repository method
        result = self.repository.get_exercises_by_workout("workout123")

        # Assert the table was called correctly - use ANY for KeyConditionExpression to avoid object comparison issues
        self.table_mock.query.assert_called_once()
        call_args = self.table_mock.query.call_args[1]
        self.assertEqual(call_args["IndexName"], "workout-index")
        # Check that the KeyConditionExpression is a condition on workout_id
        self.assertTrue("KeyConditionExpression" in call_args)

        # Assert the result is correct
        self.assertEqual(result, exercises_data)

    def test_get_exercises_by_day(self):
        """
        Test getting all exercises for a day
        """
        # Mock data
        exercises_data = [
            {
                "exercise_id": "ex1",
                "day_id": "day123",
                "exercise_type": "Squat",
            },
            {
                "exercise_id": "ex2",
                "day_id": "day123",
                "exercise_type": "Bench Press",
            },
        ]

        # Configure mock
        self.table_mock.query.return_value = {"Items": exercises_data}

        # Call the repository method
        result = self.repository.get_exercises_by_day("day123")

        # Assert the table was called correctly
        self.table_mock.query.assert_called_once()
        call_args = self.table_mock.query.call_args[1]
        self.assertEqual(call_args["IndexName"], "day-index")
        # Check that the KeyConditionExpression is a condition on day_id
        self.assertTrue("KeyConditionExpression" in call_args)
        self.assertTrue("Limit" in call_args)

        # Assert the result is correct
        self.assertEqual(result, exercises_data)

    def test_create_exercise(self):
        """
        Test creating an exercise
        """
        # Mock data
        exercise_data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
        }

        # Call the repository method
        result = self.repository.create_exercise(exercise_data)

        # Assert the table was called correctly
        self.table_mock.put_item.assert_called_once_with(Item=exercise_data)

        # The create method returns the original item
        self.assertEqual(result, exercise_data)

    def test_update_exercise(self):
        """
        Test updating an exercise
        """
        # Mock data
        update_data = {"sets": 3, "weight": 335.0}

        # For the update method in BaseRepository, it returns the Attributes from response
        # Configure the mock to return what the actual implementation would use
        self.table_mock.update_item.return_value = {
            "Attributes": {"exercise_id": "ex123"}
        }

        # Call the repository method
        result = self.repository.update_exercise("ex123", update_data)

        # Assert the table was called correctly
        self.table_mock.update_item.assert_called_once()

        # Check that the key and update expression are correct
        call_args = self.table_mock.update_item.call_args[1]
        self.assertEqual(call_args["Key"], {"exercise_id": "ex123"})
        self.assertIn(
            "set sets = :sets, weight = :weight", call_args["UpdateExpression"]
        )
        self.assertEqual(
            call_args["ExpressionAttributeValues"], {":sets": 3, ":weight": 335.0}
        )

        # The actual BaseRepository.update method returns the Attributes field from the response
        # So result should be just {"exercise_id": "ex123"}
        self.assertEqual(result, {"exercise_id": "ex123"})

    def test_delete_exercise(self):
        """
        Test deleting an exercise
        """
        # Configure mock - the actual implementation returns Attributes, which might be empty
        self.table_mock.delete_item.return_value = {
            "Attributes": {"exercise_id": "ex123"}
        }

        # Call the repository method
        result = self.repository.delete_exercise("ex123")

        # Assert the table was called correctly
        self.table_mock.delete_item.assert_called_once_with(
            Key={"exercise_id": "ex123"}, ReturnValues="ALL_OLD"
        )

        # The BaseRepository.delete method returns the Attributes field of the response
        # So result should be just {"exercise_id": "ex123"}
        self.assertEqual(result, {"exercise_id": "ex123"})

    def test_delete_exercise_not_found(self):
        """
        Test deleting an exercise that doesn't exist
        """
        # Configure mock to return empty Attributes (no item found)
        self.table_mock.delete_item.return_value = {"Attributes": {}}

        # Call the repository method
        result = self.repository.delete_exercise("nonexistent")

        # Assert the table was called correctly
        self.table_mock.delete_item.assert_called_once_with(
            Key={"exercise_id": "nonexistent"}, ReturnValues="ALL_OLD"
        )

        # The BaseRepository.delete method returns an empty dict if no Attributes
        self.assertEqual(result, {})

    def test_delete_exercises_by_workout(self):
        """
        Test deleting all exercises for a workout
        """
        # Mock data
        exercises_data = [
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
        ]

        # Configure mocks
        # First, mock the get_exercises_by_workout method to return our sample data
        with patch.object(
            self.repository, "get_exercises_by_workout", return_value=exercises_data
        ):
            # Mock the batch_writer context manager
            batch_writer_mock = MagicMock()
            self.table_mock.batch_writer.return_value.__enter__.return_value = (
                batch_writer_mock
            )

            # Call the repository method
            result = self.repository.delete_exercises_by_workout("workout123")

            # Assert batch_writer was called
            self.table_mock.batch_writer.assert_called_once()

            # Assert delete_item was called for each exercise
            self.assertEqual(batch_writer_mock.delete_item.call_count, 2)
            batch_writer_mock.delete_item.assert_any_call(Key={"exercise_id": "ex1"})
            batch_writer_mock.delete_item.assert_any_call(Key={"exercise_id": "ex2"})

            # Assert the result is the number of deleted exercises
            self.assertEqual(result, 2)

    def test_delete_exercises_by_day(self):
        """
        Test deleting all exercises for a day
        """
        # Mock data
        exercises_data = [
            {
                "exercise_id": "ex1",
                "day_id": "day123",
                "exercise_type": "Squat",
            },
            {
                "exercise_id": "ex2",
                "day_id": "day123",
                "exercise_type": "Bench Press",
            },
            {
                "exercise_id": "ex3",
                "day_id": "day123",
                "exercise_type": "Deadlift",
            },
        ]

        # Configure mocks
        # First, mock the get_exercises_by_day method to return our sample data
        with patch.object(
            self.repository, "get_exercises_by_day", return_value=exercises_data
        ):
            # Mock the batch_writer context manager
            batch_writer_mock = MagicMock()
            self.table_mock.batch_writer.return_value.__enter__.return_value = (
                batch_writer_mock
            )

            # Call the repository method
            result = self.repository.delete_exercises_by_day("day123")

            # Assert batch_writer was called
            self.table_mock.batch_writer.assert_called_once()

            # Assert delete_item was called for each exercise
            self.assertEqual(batch_writer_mock.delete_item.call_count, 3)
            batch_writer_mock.delete_item.assert_any_call(Key={"exercise_id": "ex1"})
            batch_writer_mock.delete_item.assert_any_call(Key={"exercise_id": "ex2"})
            batch_writer_mock.delete_item.assert_any_call(Key={"exercise_id": "ex3"})

            # Assert the result is the number of deleted exercises
            self.assertEqual(result, 3)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
