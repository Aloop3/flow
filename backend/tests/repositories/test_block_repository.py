import unittest
from unittest.mock import MagicMock, patch
from boto3.dynamodb.conditions import Key
from src.repositories.block_repository import BlockRepository
from src.config.block_config import BlockConfig


class TestBlockRepository(unittest.TestCase):
    """
    Test suite for the BlockRepository class
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
            self.block_repository = BlockRepository()

    def test_init(self):
        """
        Test BlockRepository initialization
        """
        # Create a new mock to avoid interference from setUp
        new_dynamodb_mock = MagicMock()

        # Save original value to restore later
        original_table_name = BlockConfig.TABLE_NAME

        try:
            # Update the table name for this test only
            with patch.object(BlockConfig, "TABLE_NAME", "test-blocks-table"):
                with patch("boto3.resource", return_value=new_dynamodb_mock):
                    repository = BlockRepository()
                    new_dynamodb_mock.Table.assert_called_once_with("test-blocks-table")
        finally:
            # Ensure we restore the original value even if the test fails
            BlockConfig.TABLE_NAME = original_table_name

    def test_get_block(self):
        """
        Test retrieving a block by block_id
        """
        # Mock data for a block
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Test Block",
            "description": "Test Description",
            "start_date": "2025-03-01",
            "end_date": "2025-04-01",
            "status": "active",
            "coach_id": "coach789",
        }

        # Configure get_by_id mock using patch
        with patch.object(
            self.block_repository, "get_by_id", return_value=mock_block
        ) as mock_get_by_id:
            # Call the method
            result = self.block_repository.get_block("block123")

            # Assert get_by_id was called with correct parameters
            mock_get_by_id.assert_called_once_with("block_id", "block123")

            # Assert the result is the mock block
            self.assertEqual(result, mock_block)

    def test_get_blocks_by_athlete(self):
        """
        Test retrieving blocks by athlete_id
        """
        # Mock data for blocks
        mock_blocks = [
            {
                "block_id": "block1",
                "athlete_id": "athlete123",
                "title": "Block 1",
                "status": "active",
            },
            {
                "block_id": "block2",
                "athlete_id": "athlete123",
                "title": "Block 2",
                "status": "draft",
            },
        ]

        # Configure table.query to return our mock blocks
        self.table_mock.query.return_value = {"Items": mock_blocks}

        # Call the method
        result = self.block_repository.get_blocks_by_athlete("athlete123")

        # Assert query was called with correct parameters
        self.table_mock.query.assert_called_once_with(
            IndexName=BlockConfig.ATHLETE_INDEX,
            KeyConditionExpression=Key("athlete_id").eq("athlete123"),
            Limit=BlockConfig.MAX_ITEMS,
        )

        # Assert the result is the list of mock blocks
        self.assertEqual(result, mock_blocks)

    def test_get_blocks_by_athlete_empty(self):
        """
        Test retrieving blocks for an athlete with no blocks
        """
        # Configure table.query to return no items
        self.table_mock.query.return_value = {"Items": []}

        # Call the method
        result = self.block_repository.get_blocks_by_athlete("athlete_no_blocks")

        # Assert query was called with correct parameters
        self.table_mock.query.assert_called_once_with(
            IndexName=BlockConfig.ATHLETE_INDEX,
            KeyConditionExpression=Key("athlete_id").eq("athlete_no_blocks"),
            Limit=BlockConfig.MAX_ITEMS,
        )

        # Assert the result is an empty list
        self.assertEqual(result, [])

    def test_get_blocks_by_coach(self):
        """
        Test retrieving blocks by coach_id
        """
        # Mock data for blocks
        mock_blocks = [
            {
                "block_id": "block1",
                "athlete_id": "athlete123",
                "coach_id": "coach456",
                "title": "Block 1",
                "status": "active",
            },
            {
                "block_id": "block2",
                "athlete_id": "athlete789",
                "coach_id": "coach456",
                "title": "Block 2",
                "status": "draft",
            },
        ]

        # Configure table.query to return our mock blocks
        self.table_mock.query.return_value = {"Items": mock_blocks}

        # Call the method
        result = self.block_repository.get_blocks_by_coach("coach456")

        # Assert query was called with correct parameters
        self.table_mock.query.assert_called_once_with(
            IndexName=BlockConfig.COACH_INDEX,
            KeyConditionExpression=Key("coach_id").eq("coach456"),
            Limit=BlockConfig.MAX_ITEMS,
        )

        # Assert the result is the list of mock blocks
        self.assertEqual(result, mock_blocks)

    def test_get_blocks_by_coach_empty(self):
        """
        Test retrieving blocks for a coach with no blocks
        """
        # Configure table.query to return no items
        self.table_mock.query.return_value = {"Items": []}

        # Call the method
        result = self.block_repository.get_blocks_by_coach("coach_no_blocks")

        # Assert query was called with correct parameters
        self.table_mock.query.assert_called_once_with(
            IndexName=BlockConfig.COACH_INDEX,
            KeyConditionExpression=Key("coach_id").eq("coach_no_blocks"),
            Limit=BlockConfig.MAX_ITEMS,
        )

        # Assert the result is an empty list
        self.assertEqual(result, [])

    def test_create_block(self):
        """
        Test creating a new block
        """
        # Mock data for a block
        mock_block = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Test Block",
            "description": "Test Description",
            "start_date": "2025-03-01",
            "end_date": "2025-04-01",
            "status": "draft",
            "coach_id": "coach789",
        }

        # Mock the create method from the parent class
        with patch.object(
            self.block_repository, "create", return_value=mock_block
        ) as mock_create:
            # Call the method
            result = self.block_repository.create_block(mock_block)

            # Assert create was called with correct parameter
            mock_create.assert_called_once_with(mock_block)

            # Assert the result is the mock block
            self.assertEqual(result, mock_block)

    def test_update_block(self):
        """
        Test updating a block
        """
        # Mock data for update
        block_id = "block123"
        update_data = {
            "title": "Updated Block",
            "description": "Updated Description",
            "status": "active",
        }

        # Mock the update method from the parent class
        expected_update_expression = (
            "set title = :title, description = :description, status = :status"
        )
        expected_expression_values = {
            ":title": "Updated Block",
            ":description": "Updated Description",
            ":status": "active",
        }

        with patch.object(
            self.block_repository, "update", return_value={"title": "Updated Block"}
        ) as mock_update:
            # Call the method
            result = self.block_repository.update_block(block_id, update_data)

            # Assert update was called with correct parameters
            mock_update.assert_called_once()
            call_args = mock_update.call_args[0]

            # Check the key
            self.assertEqual(call_args[0], {"block_id": block_id})

            # Check that the UpdateExpression contains all expected parts
            for field in update_data.keys():
                self.assertIn(f"{field} = :{field}", call_args[1])

            # Check the ExpressionAttributeValues
            for key, value in expected_expression_values.items():
                self.assertEqual(call_args[2][key], value)

            # Assert the result is the value returned from the mocked update method
            self.assertEqual(result, {"title": "Updated Block"})

    def test_delete_block(self):
        """
        Test deleting a block
        """
        # Mock data
        block_id = "block123"
        mock_response = {"Attributes": {"block_id": block_id}}

        # Mock the delete method from the parent class
        with patch.object(
            self.block_repository, "delete", return_value=mock_response["Attributes"]
        ) as mock_delete:
            # Call the method
            result = self.block_repository.delete_block(block_id)

            # Assert delete was called with correct parameter
            mock_delete.assert_called_once_with({"block_id": block_id})

            # Assert the result is what was returned from the mocked delete method
            self.assertEqual(result, mock_response["Attributes"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
