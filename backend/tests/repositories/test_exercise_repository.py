import unittest
from decimal import Decimal
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

    def test_get_exercises_by_workout_converts_decimals(self):
        """
        Test that get_exercises_by_workout converts Decimal to float
        """
        # Mock DynamoDB response with Decimal values (simulates real DynamoDB data)
        mock_response = {
            "Items": [
                {
                    "exercise_id": "ex1",
                    "workout_id": "workout1",
                    "sets": Decimal("3"),
                    "reps": Decimal("8"),
                    "weight": Decimal("100.5"),
                    "status": "completed",
                },
                {
                    "exercise_id": "ex2",
                    "workout_id": "workout1",
                    "sets": Decimal("4"),
                    "reps": Decimal("6"),
                    "weight": Decimal("85.0"),
                    "status": "planned",
                },
            ]
        }

        self.table_mock.query.return_value = mock_response

        # Call the method
        exercises = self.repository.get_exercises_by_workout("workout1")

        # Verify decimal conversion happened
        self.assertEqual(len(exercises), 2)

        # Check first exercise - should be floats now
        ex1 = exercises[0]
        self.assertIsInstance(ex1["sets"], float)
        self.assertIsInstance(ex1["reps"], float)
        self.assertIsInstance(ex1["weight"], float)
        self.assertEqual(ex1["sets"], 3.0)
        self.assertEqual(ex1["reps"], 8.0)
        self.assertEqual(ex1["weight"], 100.5)

        # Check second exercise
        ex2 = exercises[1]
        self.assertIsInstance(ex2["sets"], float)
        self.assertIsInstance(ex2["reps"], float)
        self.assertIsInstance(ex2["weight"], float)
        self.assertEqual(ex2["weight"], 85.0)

    def test_get_exercises_by_day_converts_decimals(self):
        """
        Test that get_exercises_by_day converts Decimal to float
        """
        # Mock DynamoDB response with Decimal values
        mock_response = {
            "Items": [
                {
                    "exercise_id": "ex1",
                    "day_id": "day1",
                    "sets": Decimal("5"),
                    "reps": Decimal("5"),
                    "weight": Decimal("135.75"),
                    "status": "completed",
                }
            ]
        }

        self.table_mock.query.return_value = mock_response

        # Call the method
        exercises = self.repository.get_exercises_by_day("day1")

        # Verify decimal conversion happened
        self.assertEqual(len(exercises), 1)
        ex1 = exercises[0]
        self.assertIsInstance(ex1["sets"], float)
        self.assertIsInstance(ex1["reps"], float)
        self.assertIsInstance(ex1["weight"], float)
        self.assertEqual(ex1["weight"], 135.75)

    def test_get_exercises_by_workout_empty_response_handling(self):
        """
        Test that empty responses are handled correctly after decimal conversion fix
        """
        mock_response = {"Items": []}
        self.table_mock.query.return_value = mock_response

        exercises = self.repository.get_exercises_by_workout("workout1")

        self.assertEqual(exercises, [])

    def test_get_exercises_by_workout_mixed_decimal_types(self):
        """
        Test handling of mixed data types including nested Decimal values
        Comprehensive test for UC22 production blocker
        """
        # Mock response with complex nested data including sets_data
        mock_response = {
            "Items": [
                {
                    "exercise_id": "ex1",
                    "workout_id": "workout1",
                    "sets": Decimal("3"),
                    "reps": Decimal("8"),
                    "weight": Decimal("102.27"),
                    "rpe": Decimal("8.5"),
                    "status": "completed",
                    "sets_data": [
                        {
                            "set_number": 1,
                            "reps": Decimal("8"),
                            "weight": Decimal("102.27"),
                            "completed": True,
                        },
                        {
                            "set_number": 2,
                            "reps": Decimal("7"),
                            "weight": Decimal("102.27"),
                            "completed": True,
                        },
                    ],
                }
            ]
        }

        self.table_mock.query.return_value = mock_response

        exercises = self.repository.get_exercises_by_workout("workout1")

        # Verify top-level decimal conversion
        ex1 = exercises[0]
        self.assertIsInstance(ex1["sets"], float)
        self.assertIsInstance(ex1["reps"], float)
        self.assertIsInstance(ex1["weight"], float)
        self.assertIsInstance(ex1["rpe"], float)

        # Verify nested sets_data decimal conversion
        sets_data = ex1["sets_data"]
        self.assertEqual(len(sets_data), 2)

        set1 = sets_data[0]
        self.assertIsInstance(set1["reps"], float)
        self.assertIsInstance(set1["weight"], float)
        self.assertEqual(set1["weight"], 102.27)

        set2 = sets_data[1]
        self.assertIsInstance(set2["reps"], float)
        self.assertIsInstance(set2["weight"], float)
        self.assertEqual(set2["reps"], 7.0)

    def test_get_exercise_includes_planned_sets_data(self):
        """
        Test that get_exercise returns planned_sets_data when present
        """
        # Mock exercise data with planned_sets_data
        exercise_data = {
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
        self.table_mock.get_item.return_value = {"Item": exercise_data}

        # Call the repository method
        result = self.repository.get_exercise("ex123")

        # Assert the table was called correctly
        self.table_mock.get_item.assert_called_once_with(Key={"exercise_id": "ex123"})

        # Assert the result includes planned_sets_data
        self.assertEqual(result, exercise_data)
        self.assertIn("planned_sets_data", result)
        self.assertEqual(
            result["planned_sets_data"], exercise_data["planned_sets_data"]
        )

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

    def test_create_exercise_with_planned_sets_data(self):
        """
        Test creating an exercise with planned_sets_data field
        """
        # Mock exercise data with planned_sets_data
        exercise_data = {
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
            "planned_sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 3, "reps": 5, "weight": 225.0, "completed": False},
            ],
        }

        # Configure mock to return the created exercise
        self.table_mock.put_item.return_value = exercise_data

        # Call the repository method
        result = self.repository.create_exercise(exercise_data)

        # Assert put_item was called once (without checking exact parameters due to Decimal conversion)
        self.table_mock.put_item.assert_called_once()

        # Verify the call included the planned_sets_data field
        call_args = self.table_mock.put_item.call_args[1]
        self.assertIn("Item", call_args)
        item = call_args["Item"]
        self.assertIn("planned_sets_data", item)
        self.assertEqual(len(item["planned_sets_data"]), 3)

        # Verify the planned_sets_data structure (accounting for Decimal conversion)
        planned_set_1 = item["planned_sets_data"][0]
        self.assertEqual(planned_set_1["set_number"], 1)
        self.assertEqual(planned_set_1["reps"], 5)
        self.assertEqual(
            float(planned_set_1["weight"]), 225.0
        )  # Convert Decimal back to float for comparison
        self.assertEqual(planned_set_1["completed"], False)

        # Assert the result is corrects
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
            "set #sets = :sets, #weight = :weight", call_args["UpdateExpression"]
        )

        # Check attribute values are correct
        self.assertEqual(
            call_args["ExpressionAttributeValues"], {":sets": 3, ":weight": 335.0}
        )

        # Check expression attribute names are correct
        self.assertEqual(
            call_args["ExpressionAttributeNames"],
            {"#sets": "sets", "#weight": "weight"},
        )

        # The actual BaseRepository.update method returns the Attributes field from the response
        # So result should be just {"exercise_id": "ex123"}
        self.assertEqual(result, {"exercise_id": "ex123"})

    def test_update_exercise_with_planned_sets_data(self):
        """
        Test updating an exercise with planned_sets_data field
        """
        exercise_id = "ex123"
        update_data = {
            "planned_sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
            ]
        }

        # Mock the update response in DynamoDB format (with Attributes wrapper)
        mock_attributes = {"exercise_id": exercise_id, **update_data}
        self.table_mock.update_item.return_value = {"Attributes": mock_attributes}

        # Call the repository method
        result = self.repository.update_exercise(exercise_id, update_data)

        # Assert update_item was called with correct parameters
        self.table_mock.update_item.assert_called_once()
        call_args = self.table_mock.update_item.call_args[1]

        # Verify the Key parameter
        self.assertEqual(call_args["Key"], {"exercise_id": exercise_id})

        # Verify ReturnValues is set
        self.assertEqual(call_args["ReturnValues"], "ALL_NEW")

        # Verify the UpdateExpression includes planned_sets_data
        self.assertIn("planned_sets_data", call_args["UpdateExpression"])

        # Verify ExpressionAttributeValues includes planned_sets_data (accounting for Decimal conversion)
        self.assertIn(":planned_sets_data", call_args["ExpressionAttributeValues"])
        planned_sets_value = call_args["ExpressionAttributeValues"][
            ":planned_sets_data"
        ]
        self.assertEqual(len(planned_sets_value), 2)

        # Verify ExpressionAttributeNames includes planned_sets_data
        self.assertIn("#planned_sets_data", call_args["ExpressionAttributeNames"])
        self.assertEqual(
            call_args["ExpressionAttributeNames"]["#planned_sets_data"],
            "planned_sets_data",
        )

        # Assert the result is correct (should be the converted attributes)
        self.assertEqual(result, mock_attributes)

    def test_update_exercise_with_multiple_fields_including_planned_sets_data(self):
        """
        Test updating an exercise with multiple fields including planned_sets_data
        """
        exercise_id = "ex123"
        update_data = {
            "status": "in_progress",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 230.0, "completed": True},
            ],
            "planned_sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
            ],
        }

        # Mock the update response in DynamoDB format (with Attributes wrapper)
        mock_attributes = {"exercise_id": exercise_id, **update_data}
        self.table_mock.update_item.return_value = {"Attributes": mock_attributes}

        # Call the repository method
        result = self.repository.update_exercise(exercise_id, update_data)

        # Assert update_item was called
        self.table_mock.update_item.assert_called_once()
        call_args = self.table_mock.update_item.call_args[1]

        # Verify all fields are in the update expression
        update_expression = call_args["UpdateExpression"]
        self.assertIn("status", update_expression)
        self.assertIn("sets_data", update_expression)
        self.assertIn("planned_sets_data", update_expression)

        # Verify all fields are in ExpressionAttributeValues
        expression_values = call_args["ExpressionAttributeValues"]
        self.assertIn(":status", expression_values)
        self.assertIn(":sets_data", expression_values)
        self.assertIn(":planned_sets_data", expression_values)

        # Assert the result is correct (should be the converted attributes)
        self.assertEqual(result, mock_attributes)

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

    @patch("src.repositories.workout_repository.WorkoutRepository")
    def test_get_exercises_with_workout_context_basic(self, mock_workout_repo_class):
        """
        Test getting exercises with workout context - basic scenario
        """
        # Setup mock workout repository
        mock_workout_repo = MagicMock()
        mock_workout_repo_class.return_value = mock_workout_repo

        # Mock workout data
        mock_workouts = [
            {"workout_id": "workout1", "date": "2025-03-01", "status": "completed"},
            {"workout_id": "workout2", "date": "2025-03-02", "status": "in_progress"},
        ]
        mock_workout_repo.get_all_workouts_by_athlete.return_value = mock_workouts

        # Mock exercise data for each workout
        workout1_exercises = [
            {
                "exercise_id": "ex1",
                "workout_id": "workout1",
                "exercise_type": "Squat",
                "sets": 3,
                "reps": 5,
                "weight": Decimal("225.0"),
            }
        ]

        workout2_exercises = [
            {
                "exercise_id": "ex2",
                "workout_id": "workout2",
                "exercise_type": "Bench Press",
                "sets": 3,
                "reps": 8,
                "weight": Decimal("185.0"),
            }
        ]

        # Configure table mock for exercise queries
        self.table_mock.query.side_effect = [
            {"Items": workout1_exercises},
            {"Items": workout2_exercises},
        ]

        # Call the method
        result = self.repository.get_exercises_with_workout_context("athlete123")

        # Verify workout repository was called
        mock_workout_repo.get_all_workouts_by_athlete.assert_called_once_with(
            "athlete123"
        )

        # Verify table queries for exercises
        self.assertEqual(self.table_mock.query.call_count, 2)

        # Verify results have workout context added
        self.assertEqual(len(result), 2)

        # Check first exercise has workout context
        first_exercise = result[0]
        self.assertEqual(first_exercise["exercise_id"], "ex1")
        self.assertEqual(first_exercise["workout_date"], "2025-03-01")
        self.assertEqual(first_exercise["workout_status"], "completed")

        # Check second exercise has workout context
        second_exercise = result[1]
        self.assertEqual(second_exercise["exercise_id"], "ex2")
        self.assertEqual(second_exercise["workout_date"], "2025-03-02")
        self.assertEqual(second_exercise["workout_status"], "in_progress")

    @patch("src.repositories.workout_repository.WorkoutRepository")
    def test_get_exercises_with_workout_context_with_filters(
        self, mock_workout_repo_class
    ):
        """
        Test getting exercises with workout context with exercise_type and date filters
        """
        # Setup mock workout repository
        mock_workout_repo = MagicMock()
        mock_workout_repo_class.return_value = mock_workout_repo

        # Mock workout data (some before start_date, some after)
        mock_workouts = [
            {
                "workout_id": "workout1",
                "date": "2025-02-28",  # Before start_date
                "status": "completed",
            },
            {
                "workout_id": "workout2",
                "date": "2025-03-01",  # On/after start_date
                "status": "completed",
            },
        ]
        mock_workout_repo.get_all_workouts_by_athlete.return_value = mock_workouts

        # Mock exercise data - mixed exercise types
        workout2_exercises = [
            {
                "exercise_id": "ex1",
                "workout_id": "workout2",
                "exercise_type": "Squat",  # Matches filter
                "sets": 3,
                "reps": 5,
                "weight": Decimal("225.0"),
            },
            {
                "exercise_id": "ex2",
                "workout_id": "workout2",
                "exercise_type": "Bench Press",  # Doesn't match filter
                "sets": 3,
                "reps": 8,
                "weight": Decimal("185.0"),
            },
        ]

        # Configure table mock - only one workout should be queried (after date filter)
        self.table_mock.query.return_value = {"Items": workout2_exercises}

        # Call the method with filters
        result = self.repository.get_exercises_with_workout_context(
            athlete_id="athlete123", exercise_type="Squat", start_date="2025-03-01"
        )

        # Verify workout repository was called
        mock_workout_repo.get_all_workouts_by_athlete.assert_called_once_with(
            "athlete123"
        )

        # Verify only one table query (workout1 filtered out by date)
        self.table_mock.query.assert_called_once()

        # Verify results - only Squat exercise should remain after exercise_type filter
        self.assertEqual(len(result), 1)

        exercise = result[0]
        self.assertEqual(exercise["exercise_id"], "ex1")
        self.assertEqual(exercise["exercise_type"], "Squat")
        self.assertEqual(exercise["workout_date"], "2025-03-01")
        self.assertEqual(exercise["workout_status"], "completed")

    @patch("src.repositories.workout_repository.WorkoutRepository")
    def test_get_exercises_with_workout_context_no_workouts(
        self, mock_workout_repo_class
    ):
        """
        Test getting exercises with workout context when athlete has no workouts
        """
        # Setup mock workout repository
        mock_workout_repo = MagicMock()
        mock_workout_repo_class.return_value = mock_workout_repo

        # Mock empty workout data
        mock_workout_repo.get_all_workouts_by_athlete.return_value = []

        # Call the method
        result = self.repository.get_exercises_with_workout_context("athlete123")

        # Verify workout repository was called
        mock_workout_repo.get_all_workouts_by_athlete.assert_called_once_with(
            "athlete123"
        )

        # Verify no table queries for exercises
        self.table_mock.query.assert_not_called()

        # Verify empty result
        self.assertEqual(len(result), 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
