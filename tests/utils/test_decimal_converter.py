import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from src.utils.decimal_converter import convert_floats_to_decimals
from src.repositories.base_repository import BaseRepository

class TestDecimalConverter(unittest.TestCase):
    """
    Test suite for the decimal conversion utility
    """

    def test_convert_simple_float(self):
        """
        Test converting a simple float value
        """

        result = convert_floats_to_decimals(308.65)
        self.assertIsInstance(result, Decimal)
        self.assertEqual(str(result), "308.65")

    def test_convert_exercise_data(self):
        """
        Test converting exercise data with float values
        """

        exercise_data = {
            "exercise_id": "ex123",
            "day_id": "day456",
            "exercise_type": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 319.67,
            "rpe": 8.5,
            "notes": "Beltless",
            "order": 1
        }

        result = convert_floats_to_decimals(exercise_data)

        # Verify that float values were converted to Decimal
        self.assertIsInstance(result["weight"], Decimal)
        self.assertEqual(str(result["weight"]), "319.67")
        self.assertIsInstance(result["rpe"], Decimal)
        self.assertEqual(str(result["rpe"]), "8.5")

        # Verify that non-float values remain unchanged
        self.assertEqual(result["exercise_id"], "ex123")
        self.assertEqual(result["day_id"], "day456")
        self.assertEqual(result["exercise_type"], "Squat")
        self.assertEqual(result["sets"], 3)
        self.assertEqual(result["reps"], 5)
        self.assertEqual(result["notes"], "Beltless")
    
    def test_convert_workout_with_exercises(self):
        """
        Test converting a completed workout with multiple exercises
        """

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
                    "exercise_id": "ex1",
                    "actual_sets": 5,
                    "actual_reps": 5,
                    "actual_weight": 319.67,
                    "actual_rpe": 6.5
                },
                {
                    "completed_id": "comp2",
                    "exercise_id": "ex2",
                    "actual_sets": 3,
                    "actual_reps": 8,
                    "actual_weight": 297.62,
                    "actual_rpe": 7.5
                }
            ]
        }

        result = convert_floats_to_decimals(workout_data)

        # Verify that the nested exercise float values were converted
        self.assertIsInstance(result["exercises"][0]["actual_weight"], Decimal)
        self.assertEqual(str(result["exercises"][0]["actual_weight"]), "319.67")
        self.assertIsInstance(result["exercises"][0]["actual_rpe"], Decimal)
        self.assertEqual(str(result["exercises"][0]["actual_rpe"]), "6.5")

        self.assertIsInstance(result["exercises"][1]["actual_weight"], Decimal)
        self.assertEqual(str(result["exercises"][1]["actual_weight"]), "297.62")
        self.assertIsInstance(result["exercises"][1]["actual_rpe"], Decimal)
        self.assertEqual(str(result["exercises"][1]["actual_rpe"]), "7.5")

class TestBaseRepository(unittest.TestCase):
    """
    Test suite for BaseRepository with decimal conversion
    """

    def setUp(self):
        """
        Set up test environment
        """

        # Create a mcok for DynamoDB table
        self.mock_table = MagicMock()

        # Create a patcher for boto3.resource
        self.resource_patcher = patch('boto3.resource')
        self.mock_resource = self.resource_patcher.start()

        # Configure boto3.resource to returna mock DynamoDB with the mock table
        self.mock_dynamodb = MagicMock()
        self.mock_resource.return_value = self.mock_dynamodb
        self.mock_dynamodb.Table.return_value = self.mock_table

        # Create a BaseRepository instance
        self.repo = BaseRepository("test-ddb-table")

    def tearDown(self):
        """
        Tear down test environment
        """

        # Stop the patcher
        self.resource_patcher.stop()
    
    def test_create_exercise_with_float_values(self):
        """
        Test that create method converts exercise float values to Decimal
        """

        exercise_data = {
            "exercise_id": "ex123",
            "day_id": "day456",
            "exercise_type": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": 286.6,
            "rpe": 6.0,
            "notes": "Beltless for one set",
            "order": 1
        }

        # Call the create method
        self.repo.create(exercise_data)

        # Verify put_item was called once
        self.mock_table.put_item.assert_called_once()

        # Get the item that was passed to put_item
        args, kwargs = self.mock_table.put_item.call_args
        dynamo_item = kwargs["Item"]

        # Verify float values were converted to Decimal
        self.assertIsInstance(dynamo_item["weight"], Decimal)
        self.assertEqual(str(dynamo_item["weight"]), "286.6")
        self.assertIsInstance(dynamo_item["rpe"], Decimal)
        self.assertEqual(str(dynamo_item["rpe"]), "6.0")
    
    def test_update_exercise_weights(self):
        """
        Test that update method converts weight/RPE values to Decimal
        """

        # Test data for updating an exercise
        key = {"exercise_id": "ex123"}
        update_expression = "set weight = :weight, rpe = :rpe"
        expression_values = {
            ":weight": 308.65,
            ":rpe": 7.5
        }

        # Call the update method
        self.repo.update(key, update_expression, expression_values)

        # Get the args passed to update_item - call_args returns a tuple of (args, kwargs)
        args, kwargs = self.mock_table.update_item.call_args

        # ExpressionAttributeValues is passed as a kwarg
        dynamo_expression_values = kwargs["ExpressionAttributeValues"]

        # Verify float values were converted to Decimal
        self.assertIsInstance(dynamo_expression_values[":weight"], Decimal)
        self.assertEqual(str(dynamo_expression_values[":weight"]), "308.65")
        self.assertIsInstance(dynamo_expression_values[":rpe"], Decimal)
        self.assertEqual(str(dynamo_expression_values[":rpe"]), "7.5")


if __name__ == "__main__": # pragma: no cover
    unittest.main()