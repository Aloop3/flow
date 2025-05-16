import unittest
from unittest.mock import MagicMock, patch
from src.repositories.workout_repository import WorkoutRepository


class TestWorkoutRepository(unittest.TestCase):
    """
    Test suite for the WorkoutRepository class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        self.mock_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

        # Patch boto3 resource
        with patch("boto3.resource", return_value=self.mock_dynamodb):
            self.workout_repository = WorkoutRepository()

    def test_get_workout(self):
        """
        Test retrieving a workout
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
                    "exercise_id": "exercise1",
                    "exercise_type": "Squat",
                    "sets": 3,
                    "reps": 5,
                    "weight": 315.0,
                    "status": "completed",
                },
                {
                    "exercise_id": "exercise2",
                    "exercise_type": "Bench Press",
                    "sets": 3,
                    "reps": 5,
                    "weight": 225.0,
                    "status": "completed",
                },
            ],
        }

        # Configure mocks
        self.mock_table.get_item.return_value = {"Item": mock_workout}

        # Call the method
        result = self.workout_repository.get_workout("workout123")

        # Assert get_item was called with correct args
        self.mock_table.get_item.assert_called_once_with(
            Key={"workout_id": "workout123"}
        )

        # Assert the result contains the workout data
        self.assertEqual(result["workout_id"], "workout123")
        self.assertEqual(result["athlete_id"], "athlete456")
        self.assertEqual(len(result["exercises"]), 2)

    def test_get_workout_not_found(self):
        """
        Test retrieving a workout that doesn't exist
        """
        # Configure mock to return None (no item found)
        self.mock_table.get_item.return_value = {}

        # Call the method
        result = self.workout_repository.get_workout("nonexistent")

        # Assert get_item was called
        self.mock_table.get_item.assert_called_once()

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
                    {
                        "exercise_id": "ex1",
                        "exercise_type": "Squat",
                        "status": "completed",
                    }
                ],
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete123",
                "date": "2025-03-03",
                "exercises": [
                    {
                        "exercise_id": "ex2",
                        "exercise_type": "Bench Press",
                        "status": "completed",
                    }
                ],
            },
        ]

        # Configure mocks
        self.mock_table.query.return_value = {"Items": mock_workouts}

        # Call the method
        result = self.workout_repository.get_workouts_by_athlete("athlete123")

        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once_with(
            IndexName="athlete-index",
            KeyConditionExpression=unittest.mock.ANY,
            Limit=unittest.mock.ANY,
        )

        # Assert correct number of workouts returned
        self.assertEqual(len(result), 2)

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
                {
                    "exercise_id": "exercise1",
                    "exercise_type": "Squat",
                    "status": "completed",
                }
            ],
        }

        # Configure mocks
        self.mock_table.query.return_value = {"Items": [mock_workout]}

        # Call the method
        result = self.workout_repository.get_workout_by_day("athlete456", "day789")

        # Assert query was called with correct filter
        self.mock_table.query.assert_called_once()

        # Assert the result contains the workout data
        self.assertEqual(result["workout_id"], "workout123")
        self.assertEqual(result["athlete_id"], "athlete456")

    def test_get_workout_by_day_not_found(self):
        """
        Test retrieving a workout by day when it doesn't exist
        """
        # Configure mock to return empty list
        self.mock_table.query.return_value = {"Items": []}

        # Call the method
        result = self.workout_repository.get_workout_by_day(
            "athlete456", "nonexistent-day"
        )

        # Assert query was called
        self.mock_table.query.assert_called_once()

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
                    {
                        "exercise_id": "ex1",
                        "exercise_type": "Squat",
                        "status": "completed",
                    }
                ],
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete123",
                "date": "2025-03-03",
                "status": "completed",
                "exercises": [
                    {
                        "exercise_id": "ex2",
                        "exercise_type": "Bench Press",
                        "status": "completed",
                    }
                ],
            },
        ]

        # Configure mocks
        self.mock_table.query.return_value = {"Items": mock_workouts}

        # Call the method
        result = self.workout_repository.get_completed_workouts_since(
            "athlete123", "2025-03-01"
        )

        # Assert query was called with correct parameters
        self.mock_table.query.assert_called_once()

        # Assert correct number of workouts returned
        self.assertEqual(len(result), 2)

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
                    {
                        "exercise_id": "ex1",
                        "exercise_type": "Squat",
                        "status": "completed",
                    },
                    {
                        "exercise_id": "ex2",
                        "exercise_type": "Bench Press",
                        "status": "completed",
                    },
                ],
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete123",
                "date": "2025-03-03",
                "status": "completed",
                "exercises": [
                    {
                        "exercise_id": "ex3",
                        "exercise_type": "Squat",
                        "status": "completed",
                    },
                    {
                        "exercise_id": "ex4",
                        "exercise_type": "Deadlift",
                        "status": "completed",
                    },
                ],
            },
        ]

        # Configure mock to return workouts
        with patch.object(
            self.workout_repository,
            "get_workouts_by_athlete",
            return_value=mock_workouts,
        ):
            # Call the method
            result = self.workout_repository.get_exercises_by_type(
                "athlete123", "Squat"
            )

            # Assert get_workouts_by_athlete was called
            self.workout_repository.get_workouts_by_athlete.assert_called_once_with(
                "athlete123"
            )

            # Assert the result contains only Squat exercises
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["exercise_type"], "Squat")
            self.assertEqual(result[1]["exercise_type"], "Squat")

    def test_create_workout(self):
        """
        Test creating a workout
        """
        # Test data with exercises and sets
        workout_data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "not_started",
            "exercises": [
                {
                    "exercise_id": "exercise1",
                    "exercise_type": "Squat",
                    "sets": 3,
                    "reps": 5,
                    "weight": 315.0,
                    "status": "planned",
                },
                {
                    "exercise_id": "exercise2",
                    "exercise_type": "Bench Press",
                    "sets": 3,
                    "reps": 5,
                    "weight": 225.0,
                    "status": "planned",
                },
            ],
        }

        # Call the method
        self.workout_repository.create_workout(workout_data)

        # Assert that put_item was called on the workout table
        self.mock_table.put_item.assert_called_once()

    def test_update_workout(self):
        """
        Test updating a workout
        """
        # Test data for update
        workout_id = "workout123"
        update_data = {
            "date": "2025-03-16",
            "notes": "Updated workout notes",
            "exercises": [
                {
                    "exercise_id": "exercise1",
                    "exercise_type": "Squat",
                    "sets": 3,
                    "reps": 5,
                    "weight": 315.0,
                    "status": "completed",
                }
            ],
        }

        # Call the method
        self.workout_repository.update_workout(workout_id, update_data)

        # Assert update was called on the workout itself
        self.mock_table.update_item.assert_called_once()

    def test_delete_workout_with_sets(self):
        """
        Test deleting a workout and its sets
        """
        # Mock response data
        mock_response = {
            "Attributes": {"workout_id": "workout123", "athlete_id": "athlete456"}
        }

        # Configure mock
        self.mock_table.delete_item.return_value = mock_response

        # Call the method
        result = self.workout_repository.delete_workout("workout123")

        # Assert delete_item was called on the workout
        self.mock_table.delete_item.assert_called_once_with(
            Key={"workout_id": "workout123"}, ReturnValues="ALL_OLD"
        )

        # Assert the result matches our mock response
        self.assertEqual(result, mock_response.get("Attributes"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
