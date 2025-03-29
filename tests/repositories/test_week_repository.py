import unittest
from unittest.mock import MagicMock, patch
from src.repositories.week_repository import WeekRepository
from boto3.dynamodb.conditions import Key


class TestWeekRepository(unittest.TestCase):
    """
    Test suite for the WeekRepository class
    """

    def setUp(self):
        """
        Set up test environment before each test
        """
        self.mock_table = MagicMock()
        self.mock_dynamodb = MagicMock()
        self.mock_dynamodb.Table.return_value = self.mock_table

        # Patch boto3.resource to return our mock
        self.patcher = patch("boto3.resource")
        self.mock_boto3 = self.patcher.start()
        self.mock_boto3.return_value = self.mock_dynamodb

        # Initialize repository with mocked resources
        self.repository = WeekRepository()

    def tearDown(self):
        """
        Clean up after each test
        """
        self.patcher.stop()

    def test_get_week(self):
        """
        Test retrieving a week by ID
        """
        # Setup mock return value
        mock_week = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Test week",
        }
        self.mock_table.get_item.return_value = {"Item": mock_week}

        # Call the method
        result = self.repository.get_week("week123")

        # Assert
        self.mock_table.get_item.assert_called_once_with(Key={"week_id": "week123"})
        self.assertEqual(result, mock_week)

    def test_get_week_not_found(self):
        """
        Test retrieving a non-existent week
        """
        # Setup mock return value for not found case
        self.mock_table.get_item.return_value = {}

        # Call the method
        result = self.repository.get_week("nonexistent")

        # Assert
        self.mock_table.get_item.assert_called_once_with(Key={"week_id": "nonexistent"})
        self.assertIsNone(result)

    def test_get_weeks_by_block(self):
        """
        Test retrieving weeks by block ID
        """
        # Setup mock return value
        mock_weeks = [
            {"week_id": "week1", "block_id": "block123", "week_number": 1},
            {"week_id": "week2", "block_id": "block123", "week_number": 2},
        ]
        self.mock_table.query.return_value = {"Items": mock_weeks}

        # Call the method
        result = self.repository.get_weeks_by_block("block123")

        # Assert
        self.mock_table.query.assert_called_once()

        # Check index name and KeyConditionExpression
        call_args = self.mock_table.query.call_args[1]
        self.assertEqual(call_args["IndexName"], "block-index")
        self.assertIn("KeyConditionExpression", call_args)

        # Verify the result
        self.assertEqual(result, mock_weeks)

    def test_get_weeks_by_block_empty(self):
        """
        Test retrieving weeks for a block with no weeks
        """
        # Setup mock return value
        self.mock_table.query.return_value = {"Items": []}

        # Call the method
        result = self.repository.get_weeks_by_block("empty-block")

        # Assert
        self.mock_table.query.assert_called_once()
        self.assertEqual(result, [])

    def test_create_week(self):
        """
        Test creating a new week
        """
        # Data to create
        week_data = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Test week",
        }

        # Call the method
        result = self.repository.create_week(week_data)

        # Assert
        self.mock_table.put_item.assert_called_once_with(Item=week_data)
        self.assertEqual(result, week_data)

    def test_update_week(self):
        """
        Test updating a week
        """
        # Setup mock return value
        mock_updated_week = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
            "notes": "Updated notes",  # Updated
        }
        # BaseRepository.update returns the Attributes directly
        self.mock_table.update_item.return_value = {"Attributes": mock_updated_week}

        # Update data
        update_data = {"notes": "Updated notes"}

        # Call the method
        result = self.repository.update_week("week123", update_data)

        # Assert
        self.mock_table.update_item.assert_called_once()

        # Check call arguments
        call_args = self.mock_table.update_item.call_args[1]
        self.assertEqual(call_args["Key"], {"week_id": "week123"})
        self.assertEqual(call_args["UpdateExpression"], "set notes = :notes")
        self.assertEqual(
            call_args["ExpressionAttributeValues"], {":notes": "Updated notes"}
        )

        # Check result - should match mock_updated_week directly
        self.assertEqual(result, mock_updated_week)

    def test_update_week_multiple_attributes(self):
        """
        Test updating multiple attributes of a week
        """
        # Setup mock return value
        mock_updated_week = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 2,  # Updated
            "notes": "Updated notes",  # Updated
        }
        # BaseRepository.update returns the Attributes directly
        self.mock_table.update_item.return_value = {"Attributes": mock_updated_week}

        # Update data
        update_data = {"week_number": 2, "notes": "Updated notes"}

        # Call the method
        result = self.repository.update_week("week123", update_data)

        # Assert
        self.mock_table.update_item.assert_called_once()

        # Check call arguments - exact expression depends on dictionary order
        call_args = self.mock_table.update_item.call_args[1]
        self.assertEqual(call_args["Key"], {"week_id": "week123"})

        # Check that the update expression starts with "set " and contains both attributes
        self.assertTrue(call_args["UpdateExpression"].startswith("set "))
        self.assertIn("week_number = :week_number", call_args["UpdateExpression"])
        self.assertIn("notes = :notes", call_args["UpdateExpression"])

        # Check that expression values contains both attributes
        self.assertEqual(len(call_args["ExpressionAttributeValues"]), 2)
        self.assertEqual(call_args["ExpressionAttributeValues"][":week_number"], 2)
        self.assertEqual(
            call_args["ExpressionAttributeValues"][":notes"], "Updated notes"
        )

        # Check result - should match mock_updated_week directly
        self.assertEqual(result, mock_updated_week)

    def test_delete_week(self):
        """
        Test deleting a week
        """
        # Setup mock return value
        mock_deleted_week = {
            "week_id": "week123",
            "block_id": "block456",
            "week_number": 1,
        }
        # BaseRepository.delete returns the Attributes directly
        self.mock_table.delete_item.return_value = {"Attributes": mock_deleted_week}

        # Call the method
        result = self.repository.delete_week("week123")

        # Assert
        self.mock_table.delete_item.assert_called_once_with(
            Key={"week_id": "week123"}, ReturnValues="ALL_OLD"
        )
        # Check result - should match mock_deleted_week directly
        self.assertEqual(result, mock_deleted_week)

    def test_delete_weeks_by_block(self):
        """
        Test deleting all weeks associated with a block
        """
        # Setup mock return values
        mock_weeks = [
            {"week_id": "week1", "block_id": "block123"},
            {"week_id": "week2", "block_id": "block123"},
            {"week_id": "week3", "block_id": "block123"},
        ]
        self.mock_table.query.return_value = {"Items": mock_weeks}

        # Mock batch writer
        mock_batch = MagicMock()
        self.mock_table.batch_writer.return_value.__enter__.return_value = mock_batch

        # Call the method
        result = self.repository.delete_weeks_by_block("block123")

        # Assert
        # Verify query was called with correct parameters
        self.mock_table.query.assert_called_once()

        # Verify batch writer was used to delete each week
        self.assertEqual(mock_batch.delete_item.call_count, 3)
        mock_batch.delete_item.assert_any_call(Key={"week_id": "week1"})
        mock_batch.delete_item.assert_any_call(Key={"week_id": "week2"})
        mock_batch.delete_item.assert_any_call(Key={"week_id": "week3"})

        # Verify result is the count of deleted weeks
        self.assertEqual(result, 3)

    def test_delete_weeks_by_block_empty(self):
        """
        Test deleting weeks for a block with no weeks
        """
        # Setup mock to return empty list
        self.mock_table.query.return_value = {"Items": []}

        # Mock batch writer
        mock_batch = MagicMock()
        self.mock_table.batch_writer.return_value.__enter__.return_value = mock_batch

        # Call the method
        result = self.repository.delete_weeks_by_block("empty-block")

        # Assert
        self.mock_table.query.assert_called_once()

        # Verify batch writer was not used to delete any weeks
        mock_batch.delete_item.assert_not_called()

        # Verify result is 0 (no weeks deleted)
        self.assertEqual(result, 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
