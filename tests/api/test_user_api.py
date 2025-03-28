import json
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.api import user_api

class TestUserAPI(BaseTest):
    """Test suite for the User API module"""

    @patch('src.services.user_service.UserService.create_user')
    def test_create_user_success(self, mock_create_user):
        """
        Test successful user creation
        """
        
        # Setup
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "user_id": "test-uuid",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete"
        }
        mock_create_user.return_value = mock_user
        
        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "name": "Test User",
                "role": "athlete"
            })
        }
        context = {}
        
        # Call API
        response = user_api.create_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["user_id"], "test-uuid")
        self.assertEqual(response_body["email"], "test@example.com")
        mock_create_user.assert_called_once_with(
            email="test@example.com",
            name="Test User",
            role="athlete"
        )
    
    @patch('src.services.user_service.UserService.create_user')
    def test_create_user_missing_fields(self, mock_create_user):
        """
        Test user creation with missing fields
        """
        
        # Setup
        event = {
            "body": json.dumps({
                "email": "test@example.com",
                # Missing name
                "role": "athlete"
            })
        }
        context = {}
        
        # Call API
        response = user_api.create_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_user.assert_not_called()
    
    @patch('src.services.user_service.UserService.create_user')
    def test_create_user_invalid_role(self, mock_create_user):
        """
        Test user creation with invalid role
        """
        
        # Setup
        event = {
            "body": json.dumps({
                "email": "test@example.com",
                "name": "Test User",
                "role": "invalid_role"  # Invalid role
            })
        }
        context = {}
        
        # Call API
        response = user_api.create_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid role", response_body["error"])
        mock_create_user.assert_not_called()
    
    @patch('src.services.user_service.UserService.get_user')
    def test_get_user_success(self, mock_get_user):
        """
        Test successful user retrieval
        """
        
        # Setup
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "user_id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "athlete"
        }
        mock_get_user.return_value = mock_user
        
        event = {
            "pathParameters": {
                "user_id": "user123"
            }
        }
        context = {}
        
        # Call API
        response = user_api.get_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["user_id"], "user123")
        mock_get_user.assert_called_once_with("user123")
    
    @patch('src.services.user_service.UserService.get_user')
    def test_get_user_not_found(self, mock_get_user):
        """
        Test user retrieval when user not found
        """
        
        # Setup
        mock_get_user.return_value = None
        
        event = {
            "pathParameters": {
                "user_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = user_api.get_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("User not found", response_body["error"])
    
    @patch('src.services.user_service.UserService.update_user')
    def test_update_user_success(self, mock_update_user):
        """
        Test successful user update
        """
        
        # Setup
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {
            "user_id": "user123",
            "email": "updated@example.com",
            "name": "Updated User",
            "role": "coach"
        }
        mock_update_user.return_value = mock_user
        
        event = {
            "pathParameters": {
                "user_id": "user123"
            },
            "body": json.dumps({
                "email": "updated@example.com",
                "name": "Updated User",
                "role": "coach"
            })
        }
        context = {}
        
        # Call API
        response = user_api.update_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["email"], "updated@example.com")
        mock_update_user.assert_called_once()
    
    @patch('src.services.user_service.UserService.update_user')
    def test_update_user_not_found(self, mock_update_user):
        """
        Test user update when user not found
        """
        
        # Setup
        mock_update_user.return_value = None
        
        event = {
            "pathParameters": {
                "user_id": "nonexistent"
            },
            "body": json.dumps({
                "name": "Updated User"
            })
        }
        context = {}
        
        # Call API
        response = user_api.update_user(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("User not found", response_body["error"])

if __name__ == "__main__": # pragma: no cover
    unittest.main()