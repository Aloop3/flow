import json
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch('boto3.resource'):
    from src.api import block

class TestBlockAPI(BaseTest):
    """
    Test suite for the Block API module
    """

    @patch('src.services.block_service.BlockService.create_block')
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
            "coach_id": "coach789"
        }
        mock_create_block.return_value = mock_block
        
        event = {
            "body": json.dumps({
                "athlete_id": "athlete456",
                "title": "Test Block",
                "description": "Test Description",
                "start_date": "2025-03-01",
                "end_date": "2025-04-01",
                "status": "draft",
                "coach_id": "coach789"
            })
        }
        context = {}
        
        # Call API
        response = block.create_block(event, context)
        
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
            coach_id="coach789"
        )
    
    @patch('src.services.block_service.BlockService.create_block')
    def test_create_block_missing_fields(self, mock_create_block):
        """
        Test block creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps({
                "athlete_id": "athlete456",
                # Missing title
                "description": "Test Description",
                "start_date": "2025-03-01",
                "end_date": "2025-04-01"
            })
        }
        context = {}
        
        # Call API
        response = block.create_block(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_block.assert_not_called()
    
    @patch('src.services.block_service.BlockService.get_block')
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
            "coach_id": "coach789"
        }
        mock_get_block.return_value = mock_block
        
        event = {
            "pathParameters": {
                "block_id": "block123"
            }
        }
        context = {}
        
        # Call API
        response = block.get_block(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["block_id"], "block123")
        self.assertEqual(response_body["title"], "Test Block")
        mock_get_block.assert_called_once_with("block123")
    
    @patch('src.services.block_service.BlockService.get_block')
    def test_get_block_not_found(self, mock_get_block):
        """
        Test block retrieval when block not found
        """

        # Setup
        mock_get_block.return_value = None
        
        event = {
            "pathParameters": {
                "block_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = block.get_block(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block not found", response_body["error"])
    
    @patch('src.services.block_service.BlockService.get_blocks_for_athlete')
    def test_get_blocks_by_athlete(self, mock_get_blocks):
        """
        Test retrieving blocks by athlete
        """

        # Setup
        mock_block1 = MagicMock()
        mock_block1.to_dict.return_value = {
            "block_id": "block1",
            "athlete_id": "athlete456",
            "title": "Block 1"
        }
        mock_block2 = MagicMock()
        mock_block2.to_dict.return_value = {
            "block_id": "block2",
            "athlete_id": "athlete456",
            "title": "Block 2"
        }
        mock_get_blocks.return_value = [mock_block1, mock_block2]
        
        event = {
            "pathParameters": {
                "athlete_id": "athlete456"
            }
        }
        context = {}
        
        # Call API
        response = block.get_blocks_by_athlete(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["block_id"], "block1")
        self.assertEqual(response_body[1]["block_id"], "block2")
        mock_get_blocks.assert_called_once_with("athlete456")
    
    @patch('src.services.block_service.BlockService.update_block')
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
            "status": "active"
        }
        mock_update_block.return_value = mock_block
        
        event = {
            "pathParameters": {
                "block_id": "block123"
            },
            "body": json.dumps({
                "title": "Updated Block",
                "description": "Updated Description",
                "status": "active"
            })
        }
        context = {}
        
        # Call API
        response = block.update_block(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["title"], "Updated Block")
        self.assertEqual(response_body["status"], "active")
        mock_update_block.assert_called_once()
    
    @patch('src.services.block_service.BlockService.delete_block')
    def test_delete_block_success(self, mock_delete_block):
        """
        Test successful block deletion
        """
        
        # Setup
        mock_delete_block.return_value = True
        
        event = {
            "pathParameters": {
                "block_id": "block123"
            }
        }
        context = {}
        
        # Call API
        response = block.delete_block(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_block.assert_called_once_with("block123")
    
    @patch('src.services.block_service.BlockService.delete_block')
    def test_delete_block_not_found(self, mock_delete_block):
        """
        Test block deletion when block not found
        """
        
        # Setup
        mock_delete_block.return_value = False
        
        event = {
            "pathParameters": {
                "block_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = block.delete_block(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Block not found", response_body["error"])

if __name__ == "__main__":
    unittest.main()