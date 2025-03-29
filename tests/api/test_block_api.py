import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.api import block_api


class TestBlockAPI(BaseTest):
    """
    Test suite for the Block API module
    """

    @patch("src.services.block_service.BlockService.create_block")
    def test_create_block_success(self, mock_create_block):
        """
        Test successful block creation
        """

        # Setup
        mock_block = MagicMock()
        mock_block.to_dict.return_value = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Test Block",
            "description": "Test Description",
            "start_date": "2025-03-01",
            "end_date": "2025-04-01",
            "status": "draft",
            "coach_id": "coach789",
        }
        mock_create_block.return_value = mock_block

        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    "title": "Test Block",
                    "description": "Test Description",
                    "start_date": "2025-03-01",
                    "end_date": "2025-04-01",
                    "status": "draft",
                    "coach_id": "coach789",
                }
            )
        }
        context = {}

        # Call API
        response = block_api.create_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["block_id"], "block123")
        self.assertEqual(response_body["title"], "Test Block")
        mock_create_block.assert_called_once_with(
            athlete_id="athlete456",
            title="Test Block",
            description="Test Description",
            start_date="2025-03-01",
            end_date="2025-04-01",
            status="draft",
            coach_id="coach789",
        )

    @patch("src.services.block_service.BlockService.create_block")
    def test_create_block_with_json_decode_error(self, mock_create_block):
        """
        Test handling of invalid JSON in request body
        """
        # Setup
        event = {"body": "{invalid-json"}  # Invalid JSON format
        context = {}

        # Call API
        response = block_api.create_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON in request body", response_body["error"])
        mock_create_block.assert_not_called()

    @patch("src.services.block_service.BlockService.create_block")
    def test_create_block_missing_fields(self, mock_create_block):
        """
        Test block creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    # Missing title
                    "description": "Test Description",
                    "start_date": "2025-03-01",
                    "end_date": "2025-04-01",
                }
            )
        }
        context = {}

        # Call API
        response = block_api.create_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_block.assert_not_called()

    @patch("src.services.block_service.BlockService.create_block")
    def test_create_block_with_service_exception(self, mock_create_block):
        """Test handling of an exception from the block service during creation"""
        # Setup - create a valid event but make the service throw an exception
        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    "title": "Test Block",
                    "description": "Test Description",
                    "start_date": "2025-03-01",
                    "end_date": "2025-04-01",
                }
            )
        }
        context = {}

        # Make the service method throw an exception
        mock_create_block.side_effect = Exception("Service failure")

        # Call API
        response = block_api.create_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Service failure", response_body["error"])
        mock_create_block.assert_called_once()

    @patch("src.services.block_service.BlockService.get_block")
    def test_get_block_success(self, mock_get_block):
        """
        Test successful block retrieval
        """

        # Setup
        mock_block = MagicMock()
        mock_block.to_dict.return_value = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Test Block",
            "description": "Test Description",
            "start_date": "2025-03-01",
            "end_date": "2025-04-01",
            "status": "active",
            "coach_id": "coach789",
        }
        mock_get_block.return_value = mock_block

        event = {"pathParameters": {"block_id": "block123"}}
        context = {}

        # Call API
        response = block_api.get_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["block_id"], "block123")
        self.assertEqual(response_body["title"], "Test Block")
        mock_get_block.assert_called_once_with("block123")

    @patch("src.services.block_service.BlockService.get_block")
    def test_get_block_not_found(self, mock_get_block):
        """
        Test block retrieval when block not found
        """

        # Setup
        mock_get_block.return_value = None

        event = {"pathParameters": {"block_id": "nonexistent"}}
        context = {}

        # Call API
        response = block_api.get_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block not found", response_body["error"])

    @patch("src.services.block_service.BlockService.get_blocks_for_athlete")
    def test_get_blocks_by_athlete(self, mock_get_blocks):
        """
        Test retrieving blocks by athlete
        """

        # Setup
        mock_block1 = MagicMock()
        mock_block1.to_dict.return_value = {
            "block_id": "block1",
            "athlete_id": "athlete456",
            "title": "Block 1",
        }
        mock_block2 = MagicMock()
        mock_block2.to_dict.return_value = {
            "block_id": "block2",
            "athlete_id": "athlete456",
            "title": "Block 2",
        }
        mock_get_blocks.return_value = [mock_block1, mock_block2]

        event = {"pathParameters": {"athlete_id": "athlete456"}}
        context = {}

        # Call API
        response = block_api.get_blocks_by_athlete(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["block_id"], "block1")
        self.assertEqual(response_body[1]["block_id"], "block2")
        mock_get_blocks.assert_called_once_with("athlete456")

    @patch("src.services.block_service.BlockService.get_block")
    def test_get_block_missing_path_parameter(self, mock_get_block):
        """Test handling of missing block_id parameter"""
        # Setup - event with no pathParameters
        event = {}
        context = {}

        # Call API
        response = block_api.get_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing block_id parameter", response_body["error"])
        mock_get_block.assert_not_called()

    @patch("src.services.block_service.BlockService.get_block")
    def test_get_block_with_empty_path_parameters(self, mock_get_block):
        """Test when pathParameters exists but block_id is missing"""
        # Setup
        event = {"pathParameters": {}}  # Empty dict but the key exists
        context = {}

        # Call API
        response = block_api.get_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing block_id parameter", response_body["error"])
        mock_get_block.assert_not_called()

    @patch("src.services.block_service.BlockService.get_blocks_for_athlete")
    def test_get_blocks_by_athlete_with_empty_path_parameters(self, mock_get_blocks):
        """Test when pathParameters exists but athlete_id is missing"""
        # Setup
        event = {"pathParameters": {}}  # Empty dict but the key exists
        context = {}

        # Call API
        response = block_api.get_blocks_by_athlete(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing athlete_id parameter", response_body["error"])
        mock_get_blocks.assert_not_called()

    @patch("src.services.block_service.BlockService.get_blocks_for_athlete")
    def test_get_blocks_with_exception(self, mock_get_blocks):
        """Test handling of exceptions during blocks retrieval"""
        # Setup
        mock_get_blocks.side_effect = Exception("Test exception")

        event = {"pathParameters": {"athlete_id": "athlete456"}}
        context = {}

        # Call API
        response = block_api.get_blocks_by_athlete(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])

    @patch("src.services.block_service.BlockService.get_block")
    def test_get_block_with_general_exception(self, mock_get_block):
        """Test handling of a general exception in get_block"""
        # Setup
        mock_get_block.side_effect = Exception("Unexpected error")

        event = {"pathParameters": {"block_id": "block123"}}
        context = {}

        # Call API
        response = block_api.get_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Unexpected error", response_body["error"])

    @patch("src.services.block_service.BlockService.update_block")
    def test_update_block_with_exception(self, mock_update_block):
        """Test handling of exceptions during block update"""
        # Setup
        mock_update_block.side_effect = Exception("Test exception")

        event = {
            "pathParameters": {"block_id": "block123"},
            "body": json.dumps({"title": "Updated Block"}),
        }
        context = {}

        # Call API
        response = block_api.update_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])

    @patch("src.services.block_service.BlockService.update_block")
    def test_update_block_with_empty_path_parameters(self, mock_update_block):
        """Test when pathParameters exists but block_id is missing"""
        # Setup
        event = {
            "pathParameters": {},  # Empty dict but the key exists
            "body": json.dumps({"title": "Updated Title"}),
        }
        context = {}

        # Call API
        response = block_api.update_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing block_id parameter", response_body["error"])
        mock_update_block.assert_not_called()

    @patch("src.services.block_service.BlockService.update_block")
    def test_update_block_with_json_decode_error(self, mock_update_block):
        """Test handling of invalid JSON in request body during update"""
        # Setup
        event = {
            "pathParameters": {"block_id": "block123"},
            "body": "{invalid-json",  # Invalid JSON format
        }
        context = {}

        # Call API
        response = block_api.update_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON in request body", response_body["error"])
        mock_update_block.assert_not_called()

    @patch("src.services.block_service.BlockService.update_block")
    def test_update_block_success(self, mock_update_block):
        """
        Test successful block update
        """

        # Setup
        mock_block = MagicMock()
        mock_block.to_dict.return_value = {
            "block_id": "block123",
            "athlete_id": "athlete456",
            "title": "Updated Block",
            "description": "Updated Description",
            "start_date": "2025-03-01",
            "end_date": "2025-04-01",
            "status": "active",
        }
        mock_update_block.return_value = mock_block

        event = {
            "pathParameters": {"block_id": "block123"},
            "body": json.dumps(
                {
                    "title": "Updated Block",
                    "description": "Updated Description",
                    "status": "active",
                }
            ),
        }
        context = {}

        # Call API
        response = block_api.update_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["title"], "Updated Block")
        self.assertEqual(response_body["status"], "active")
        mock_update_block.assert_called_once()

    @patch("src.services.block_service.BlockService.update_block")
    def test_update_block_without_body(self, mock_update_block):
        """Test update_block with missing body attribute"""
        # Setup
        event = {
            "pathParameters": {"block_id": "block123"}
            # Intentionally missing the "body" attribute
        }
        context = {}

        # Call API
        response = block_api.update_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("error", response_body)

    @patch("src.services.block_service.BlockService.update_block")
    def test_update_block_not_found(self, mock_update_block):
        """Test handling of block not found during update"""
        # Setup
        event = {
            "pathParameters": {"block_id": "nonexistent"},
            "body": json.dumps({"title": "Updated Block"}),
        }
        context = {}

        # Configure the mock to return None, indicating block not found
        mock_update_block.return_value = None

        # Call API
        response = block_api.update_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block not found", response_body["error"])

        # Verify the mock was called with the expected parameters
        mock_update_block.assert_called_once_with(
            "nonexistent", {"title": "Updated Block"}
        )

    @patch("src.services.block_service.BlockService.delete_block")
    def test_delete_block_success(self, mock_delete_block):
        """
        Test successful block deletion
        """

        # Setup
        mock_delete_block.return_value = True

        event = {"pathParameters": {"block_id": "block123"}}
        context = {}

        # Call API
        response = block_api.delete_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_block.assert_called_once_with("block123")

    @patch("src.services.block_service.BlockService.delete_block")
    def test_delete_block_not_found(self, mock_delete_block):
        """
        Test block deletion when block not found
        """

        # Setup
        mock_delete_block.return_value = False

        event = {"pathParameters": {"block_id": "nonexistent"}}
        context = {}

        # Call API
        response = block_api.delete_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block not found", response_body["error"])

    @patch("src.services.block_service.BlockService.delete_block")
    def test_delete_block_with_empty_path_parameters(self, mock_delete_block):
        """Test when pathParameters exists but block_id is missing for deletion"""
        # Setup
        event = {"pathParameters": {}}  # Empty dict but the key exists
        context = {}

        # Call API
        response = block_api.delete_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing block_id parameter", response_body["error"])
        mock_delete_block.assert_not_called()

    @patch("src.services.block_service.BlockService.delete_block")
    def test_delete_block_with_general_exception(self, mock_delete_block):
        """Test handling of a general exception in delete_block"""
        # Setup
        mock_delete_block.side_effect = Exception("Database connection error")

        event = {"pathParameters": {"block_id": "block123"}}
        context = {}

        # Call API
        response = block_api.delete_block(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Database connection error", response_body["error"])


if __name__ == "__main__":
    unittest.main()
