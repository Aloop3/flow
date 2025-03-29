import unittest
from unittest.mock import MagicMock, patch
from boto3.dynamodb.conditions import Key
from src.repositories.day_repository import DayRepository


class TestDayRepository(unittest.TestCase):
    """
    Test suite for the DayRepository class
    """

    def setUp(self):
        """
        Set up test environment before each test method
        """
        # Create patcher for table
        self.table_mock = MagicMock()
        self.dynamodb_mock = MagicMock()
        self.dynamodb_mock.Table.return_value = self.table_mock

        # Create repository with mocked DynamoDB resource
        with patch("boto3.resource", return_value=self.dynamodb_mock):
            self.day_repository = DayRepository()

    def test_init(self):
        """
        Test DayRepository initialization
        """
        # Create a new mock to avoid interference from setUp
        new_dynamodb_mock = MagicMock()

        # Test that DayRepository initializes with the correct table name
        with patch("os.environ.get", return_value="test-days-table"):
            with patch("boto3.resource", return_value=new_dynamodb_mock):
                repository = DayRepository()
                new_dynamodb_mock.Table.assert_called_once_with("test-days-table")

    def test_get_day(self):
        """
        Test retrieving a day by day_id
        """
        # Mock data for a day
        mock_day = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
        }

        # Configure table.get_item to return our mock day
        self.table_mock.get_item.return_value = {"Item": mock_day}

        # Call the method
        result = self.day_repository.get_day("day123")

        # Assert the get_item was called with correct parameters
        self.table_mock.get_item.assert_called_once_with(Key={"day_id": "day123"})

        # Assert the result is the mock day
        self.assertEqual(result, mock_day)

    def test_get_day_not_found(self):
        """
        Test retrieving a non-existent day
        """
        # Configure table.get_item to return no item
        self.table_mock.get_item.return_value = {}

        # Call the method
        result = self.day_repository.get_day("nonexistent")

        # Assert the get_item was called with correct parameters
        self.table_mock.get_item.assert_called_once_with(Key={"day_id": "nonexistent"})

        # Assert the result is None
        self.assertIsNone(result)

    def test_get_days_by_week(self):
        """
        Test retrieving all days for a week
        """
        # Mock data for days
        mock_days = [
            {
                "day_id": "day1",
                "week_id": "week123",
                "day_number": 1,
                "date": "2025-03-15",
            },
            {
                "day_id": "day2",
                "week_id": "week123",
                "day_number": 2,
                "date": "2025-03-16",
            },
        ]

        # Configure table.query to return our mock days
        self.table_mock.query.return_value = {"Items": mock_days}

        # Call the method
        result = self.day_repository.get_days_by_week("week123")

        # Assert the query was called with correct parameters
        self.table_mock.query.assert_called_once_with(
            IndexName="week-index", KeyConditionExpression=Key("week_id").eq("week123")
        )

        # Assert the result is the list of mock days
        self.assertEqual(result, mock_days)

    def test_get_days_by_week_empty(self):
        """
        Test retrieving days for a week with no days
        """
        # Configure table.query to return no items
        self.table_mock.query.return_value = {"Items": []}

        # Call the method
        result = self.day_repository.get_days_by_week("emptyweek")

        # Assert the query was called with correct parameters
        self.table_mock.query.assert_called_once_with(
            IndexName="week-index",
            KeyConditionExpression=Key("week_id").eq("emptyweek"),
        )

        # Assert the result is an empty list
        self.assertEqual(result, [])

    def test_create_day(self):
        """
        Test creating a new day
        """
        # Mock data for a day
        mock_day = {
            "day_id": "day123",
            "week_id": "week456",
            "day_number": 1,
            "date": "2025-03-15",
        }

        # Call the method
        result = self.day_repository.create_day(mock_day)

        # Assert the put_item was called with correct parameters
        self.table_mock.put_item.assert_called_once_with(Item=mock_day)

        # Assert the result is the mock day
        self.assertEqual(result, mock_day)

    def test_update_day(self):
        """
        Test updating an existing day
        """
        # Mock data for update
        update_data = {"date": "2025-03-20", "notes": "Updated notes"}

        # Mock response from DynamoDB
        mock_response = {
            "Attributes": {
                "day_id": "day123",
                "week_id": "week456",
                "day_number": 1,
                "date": "2025-03-20",
                "notes": "Updated notes",
            }
        }

        # Configure table.update_item to return our mock response
        self.table_mock.update_item.return_value = mock_response

        # Call the method
        result = self.day_repository.update_day("day123", update_data)

        # Assert the update_item was called with correct parameters
        expected_update_expression = "set date = :date, notes = :notes"
        expected_expression_values = {":date": "2025-03-20", ":notes": "Updated notes"}

        self.table_mock.update_item.assert_called_once()
        call_args = self.table_mock.update_item.call_args[1]

        # Check the key
        self.assertEqual(call_args["Key"], {"day_id": "day123"})

        # Check the UpdateExpression (accounting for different order of items)
        self.assertIn("date = :date", call_args["UpdateExpression"])
        self.assertIn("notes = :notes", call_args["UpdateExpression"])

        # Check the ExpressionAttributeValues
        self.assertEqual(
            call_args["ExpressionAttributeValues"], expected_expression_values
        )

        # Assert the result is the returned Attributes
        self.assertEqual(result, mock_response["Attributes"])

    def test_delete_day(self):
        """
        Test deleting a day
        """
        # Mock response from DynamoDB
        mock_response = {
            "Attributes": {
                "day_id": "day123",
                "week_id": "week456",
                "day_number": 1,
                "date": "2025-03-15",
            }
        }

        # Configure table.delete_item to return our mock response
        self.table_mock.delete_item.return_value = mock_response

        # Call the method
        result = self.day_repository.delete_day("day123")

        # Assert the delete_item was called with correct parameters
        self.table_mock.delete_item.assert_called_once_with(
            Key={"day_id": "day123"}, ReturnValues="ALL_OLD"
        )

        # Assert the result is the returned Attributes
        self.assertEqual(result, mock_response["Attributes"])

    def test_delete_day_by_week(self):
        """
        Test deleting all days for a week
        """
        # Mock data for days
        mock_days = [
            {
                "day_id": "day1",
                "week_id": "week123",
                "day_number": 1,
                "date": "2025-03-15",
            },
            {
                "day_id": "day2",
                "week_id": "week123",
                "day_number": 2,
                "date": "2025-03-16",
            },
        ]

        # Configure repository's get_days_by_week to return our mock days
        with patch.object(
            self.day_repository, "get_days_by_week", return_value=mock_days
        ):
            # Create a mock for the batch writer
            batch_writer_mock = MagicMock()
            self.table_mock.batch_writer.return_value.__enter__.return_value = (
                batch_writer_mock
            )

            # Call the method
            result = self.day_repository.delete_day_by_week("week123")

            # Assert get_days_by_week was called
            self.day_repository.get_days_by_week.assert_called_once_with("week123")

            # Assert batch_writer was called
            self.table_mock.batch_writer.assert_called_once()

            # Assert delete_item was called twice (once for each day)
            self.assertEqual(batch_writer_mock.delete_item.call_count, 2)
            batch_writer_mock.delete_item.assert_any_call(Key={"day_id": "day1"})
            batch_writer_mock.delete_item.assert_any_call(Key={"day_id": "day2"})

            # Assert the result is the number of days deleted
            self.assertEqual(result, 2)

    def test_delete_day_by_week_empty(self):
        """
        Test deleting days for a week with no days
        """
        # Configure repository's get_days_by_week to return an empty list
        with patch.object(self.day_repository, "get_days_by_week", return_value=[]):
            # Create a mock for the batch writer
            batch_writer_mock = MagicMock()
            self.table_mock.batch_writer.return_value.__enter__.return_value = (
                batch_writer_mock
            )

            # Call the method
            result = self.day_repository.delete_day_by_week("emptyweek")

            # Assert get_days_by_week was called
            self.day_repository.get_days_by_week.assert_called_once_with("emptyweek")

            # Assert batch_writer was called
            self.table_mock.batch_writer.assert_called_once()

            # Assert delete_item was not called
            batch_writer_mock.delete_item.assert_not_called()

            # Assert the result is 0 (no days deleted)
            self.assertEqual(result, 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
