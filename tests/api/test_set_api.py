import json
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import set_api after the mocks are set up in BaseTest
with patch('boto3.resource'):
    from src.api import set_api as set_module

class TestSetAPI(BaseTest):
    """Test suite for the Set API module"""

    @patch('src.api.set_api.set_service')
    def test_get_set_success(self, mock_set_service):
        """Test successful set retrieval"""
        # Setup
        mock_set = MagicMock()
        mock_set.to_dict.return_value = {
            "set_id": "set123",
            "exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 5,
            "weight": 225.0,
            "rpe": 8.5,
            "notes": "Good set"
        }
        mock_set_service.get_set.return_value = mock_set
        
        event = {
            "pathParameters": {
                "set_id": "set123"
            }
        }
        context = {}
        
        # Call API
        response = set_module.get_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["set_id"], "set123")
        self.assertEqual(response_body["exercise_id"], "exercise456")
        self.assertEqual(response_body["reps"], 5)
        mock_set_service.get_set.assert_called_once_with("set123")
    
    @patch('src.api.set_api.set_service')
    def test_get_set_not_found(self, mock_set_service):
        """Test set retrieval when set not found"""
        # Setup
        mock_set_service.get_set.return_value = None
        
        event = {
            "pathParameters": {
                "set_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = set_module.get_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Set not found", response_body["error"])
        mock_set_service.get_set.assert_called_once_with("nonexistent")
    
    @patch('src.api.set_api.set_service')
    def test_get_set_exception(self, mock_set_service):
        """Test set retrieval with an exception"""
        # Setup
        mock_set_service.get_set.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "set_id": "set123"
            }
        }
        context = {}
        
        # Call API
        response = set_module.get_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])
    
    @patch('src.api.set_api.set_service')
    def test_get_sets_for_exercise_success(self, mock_set_service):
        """Test successful retrieval of sets for an exercise"""
        # Setup
        mock_set1 = MagicMock()
        mock_set1.to_dict.return_value = {
            "set_id": "set1",
            "exercise_id": "exercise123",
            "set_number": 1,
            "reps": 5,
            "weight": 225.0
        }
        mock_set2 = MagicMock()
        mock_set2.to_dict.return_value = {
            "set_id": "set2",
            "exercise_id": "exercise123",
            "set_number": 2,
            "reps": 5,
            "weight": 235.0
        }
        mock_set_service.get_sets_for_exercise.return_value = [mock_set1, mock_set2]
        
        event = {
            "pathParameters": {
                "exercise_id": "exercise123"
            }
        }
        context = {}
        
        # Call API
        response = set_module.get_sets_for_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["exercise_id"], "exercise123")
        self.assertEqual(len(response_body["sets"]), 2)
        self.assertEqual(response_body["sets"][0]["set_id"], "set1")
        self.assertEqual(response_body["sets"][1]["set_id"], "set2")
        mock_set_service.get_sets_for_exercise.assert_called_once_with("exercise123")
    
    @patch('src.api.set_api.set_service')
    def test_get_sets_for_exercise_exception(self, mock_set_service):
        """Test retrieval of sets for an exercise with an exception"""
        # Setup
        mock_set_service.get_sets_for_exercise.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "exercise_id": "exercise123"
            }
        }
        context = {}
        
        # Call API
        response = set_module.get_sets_for_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_create_set_success(self, mock_workout_service):
        """Test successful set creation"""
        # Setup
        mock_set = MagicMock()
        mock_set.to_dict.return_value = {
            "set_id": "newset123",
            "exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 3,
            "reps": 5,
            "weight": 245.0,
            "rpe": 8.5,
            "notes": "Good set",
            "completed": True
        }
        mock_workout_service.add_set_to_exercise.return_value = mock_set
        
        event = {
            "pathParameters": {
                "exercise_id": "exercise456"
            },
            "body": json.dumps({
                "workout_id": "workout789",
                "set_number": 3,
                "reps": 5,
                "weight": 245.0,
                "rpe": 8.5,
                "notes": "Good set",
                "completed": True
            })
        }
        context = {}
        
        # Call API
        response = set_module.create_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["set_id"], "newset123")
        self.assertEqual(response_body["exercise_id"], "exercise456")
        self.assertEqual(response_body["reps"], 5)
        mock_workout_service.add_set_to_exercise.assert_called_once()
    
    @patch('src.api.set_api.workout_service')
    def test_create_set_missing_fields(self, mock_workout_service):
        """Test set creation with missing required fields"""
        # Setup
        event = {
            "pathParameters": {
                "exercise_id": "exercise456"
            },
            "body": json.dumps({
                "workout_id": "workout789",
                # Missing reps
                "weight": 245.0
            })
        }
        context = {}
        
        # Call API
        response = set_module.create_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required field", response_body["error"])
        mock_workout_service.add_set_to_exercise.assert_not_called()
    
    @patch('src.api.set_api.workout_service')
    def test_create_set_failed(self, mock_workout_service):
        """Test set creation when it fails"""
        # Setup
        mock_workout_service.add_set_to_exercise.return_value = None
        
        event = {
            "pathParameters": {
                "exercise_id": "exercise456"
            },
            "body": json.dumps({
                "workout_id": "workout789",
                "reps": 5,
                "weight": 245.0
            })
        }
        context = {}
        
        # Call API
        response = set_module.create_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Failed to create set", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_create_set_value_error(self, mock_workout_service):
        """Test set creation with a ValueError"""
        # Setup
        mock_workout_service.add_set_to_exercise.side_effect = ValueError("Invalid data")
        
        event = {
            "pathParameters": {
                "exercise_id": "exercise456"
            },
            "body": json.dumps({
                "workout_id": "workout789",
                "reps": 5,
                "weight": 245.0
            })
        }
        context = {}
        
        # Call API
        response = set_module.create_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid data", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_create_set_exception(self, mock_workout_service):
        """Test set creation with an exception"""
        # Setup
        mock_workout_service.add_set_to_exercise.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "exercise_id": "exercise456"
            },
            "body": json.dumps({
                "workout_id": "workout789",
                "reps": 5,
                "weight": 245.0
            })
        }
        context = {}
        
        # Call API
        response = set_module.create_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_update_set_success(self, mock_workout_service):
        """Test successful set update"""
        # Setup
        mock_set = MagicMock()
        mock_set.to_dict.return_value = {
            "set_id": "set123",
            "exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 6,  # Updated
            "weight": 235.0,  # Updated
            "rpe": 9.0  # Updated
        }
        mock_workout_service.update_set.return_value = mock_set
        
        event = {
            "pathParameters": {
                "set_id": "set123"
            },
            "body": json.dumps({
                "reps": 6,
                "weight": 235.0,
                "rpe": 9.0
            })
        }
        context = {}
        
        # Call API
        response = set_module.update_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["set_id"], "set123")
        self.assertEqual(response_body["reps"], 6)
        self.assertEqual(response_body["weight"], 235.0)
        self.assertEqual(response_body["rpe"], 9.0)
        mock_workout_service.update_set.assert_called_once()
    
    @patch('src.api.set_api.workout_service')
    def test_update_set_not_found(self, mock_workout_service):
        """Test set update when set not found"""
        # Setup
        mock_workout_service.update_set.return_value = None
        
        event = {
            "pathParameters": {
                "set_id": "nonexistent"
            },
            "body": json.dumps({
                "reps": 6
            })
        }
        context = {}
        
        # Call API
        response = set_module.update_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Set not found", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_update_set_exception(self, mock_workout_service):
        """Test set update with an exception"""
        # Setup
        mock_workout_service.update_set.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "set_id": "set123"
            },
            "body": json.dumps({
                "reps": 6
            })
        }
        context = {}
        
        # Call API
        response = set_module.update_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_delete_set_success(self, mock_workout_service):
        """Test successful set deletion"""
        # Setup
        mock_workout_service.delete_set.return_value = True
        
        event = {
            "pathParameters": {
                "set_id": "set123"
            }
        }
        context = {}
        
        # Call API
        response = set_module.delete_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_workout_service.delete_set.assert_called_once_with("set123")
    
    @patch('src.api.set_api.workout_service')
    def test_delete_set_not_found(self, mock_workout_service):
        """Test set deletion when set not found"""
        # Setup
        mock_workout_service.delete_set.return_value = False
        
        event = {
            "pathParameters": {
                "set_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = set_module.delete_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Set not found", response_body["error"])
    
    @patch('src.api.set_api.workout_service')
    def test_delete_set_exception(self, mock_workout_service):
        """Test set deletion with an exception"""
        # Setup
        mock_workout_service.delete_set.side_effect = Exception("Test exception")
        
        event = {
            "pathParameters": {
                "set_id": "set123"
            }
        }
        context = {}
        
        # Call API
        response = set_module.delete_set(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Test exception", response_body["error"])

if __name__ == "__main__": # pragma: no cover
    unittest.main()