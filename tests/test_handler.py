import unittest
from unittest.mock import patch, MagicMock
import json
import os

os.environ["USERS_TABLE"] = "test-users-table"
os.environ["BLOCKS_TABLE"] = "test-blocks-table"
os.environ["WEEKS_TABLE"] = "test-weeks-table"
os.environ["DAYS_TABLE"] = "test-days-table"
os.environ["EXERCISES_TABLE"] = "test-exercises-table"
os.environ["WORKOUTS_TABLE"] = "test-workouts-table"
os.environ["COMPLETED_EXERCISES_TABLE"] = "test-completed-exercises-table"
os.environ["RELATIONSHIPS_TABLE"] = "test-relationships-table"

with patch("boto3.resource"):
    import handler

class TestHandler(unittest.TestCase):
    """
    Test suite for the main Lambda handler
    """

    @patch("handler.ROUTE_CONFIG", new_callable=dict)
    def test_route_to_create_user(self, mock_route_config):
        """Test that POST /users routes to the create_user function"""
        # Setup
        mock_create_user = MagicMock(return_value={"statusCode": 201})
        mock_route_config["POST /users"] = mock_create_user
        event = {
            "httpMethod": "POST",
            "resource": "/users",
            "path": "/users",
            "body": json.dumps({"email": "test@example.com", "name": "Test User", "role": "athlete"})
        }
        context = {}
        
        # Call handler
        result = handler.lambda_handler(event, context)
        
        # Assert
        mock_create_user.assert_called_once_with(event, context)
        self.assertEqual(result, {"statusCode": 201})
    
    @patch("handler.ROUTE_CONFIG", new_callable=dict)
    def test_route_to_get_block(self, mock_route_config):
        """
        Test that GET /blocks/{block_id} routes to the get_block function
        """
        # Setup
        mock_get_block = MagicMock(return_value={"statusCode": 200})
        mock_route_config["GET /blocks/{block_id}"] = mock_get_block
        event = {
            "httpMethod": "GET",
            "resource": "/blocks/{block_id}",
            "path": "/blocks/123",
            "pathParameters": {"block_id": "123"}
        }
        context = {}
        
        # Call handler
        result = handler.lambda_handler(event, context)
        
        # Assert
        mock_get_block.assert_called_once_with(event, context)
        self.assertEqual(result, {"statusCode": 200})
    
    @patch("handler.ROUTE_CONFIG", new_callable=dict)
    def test_route_not_found(self, mock_route_config):
        """
        Test that a non-existent route returns 404
        """
        # Setup
        mock_get_block = MagicMock(return_value={"statusCode": 200})
        mock_route_config["GET /blocks/{block_id}"] = mock_get_block
    
        event = {
            "httpMethod": "GET",
            "resource": "/non-existent",
            "path": "/non-existent"
        }
        context = {}
        
        # Call handler
        result = handler.lambda_handler(event, context)
        
        # Assert
        self.assertEqual(result["statusCode"], 404)
        self.assertIn("Not Found", result["body"])
    
    @patch('handler.find_handler')
    def test_handler_exception(self, mock_find_handler):
        """
        Test that exceptions in handlers are caught and return 500
        """
        # Setup
        mock_handler = MagicMock()
        mock_handler.side_effect = Exception("Test exception")
        mock_find_handler.return_value = mock_handler
        
        event = {
            "httpMethod": "GET",
            "resource": "/users/123",
            "path": "/users/123",
            "pathParameters": {"user_id": "123"}
        }
        context = {}
        
        # Call handler
        result = handler.lambda_handler(event, context)
        
        # Assert
        self.assertEqual(result["statusCode"], 500)
        self.assertIn("Internal server error", result["body"])

if __name__ == "__main__": # pragma: no cover
    unittest.main()