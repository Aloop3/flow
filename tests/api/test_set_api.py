import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

class TestSetAPI(BaseTest):
    """Test suite for Set API handlers"""
    
    def setUp(self):
        """Set up test environment before each test method"""
        # Create service mocks
        self.set_service_patch = patch('src.api.set.set_service')
        self.workout_service_patch = patch('src.api.set.workout_service')
        
        self.set_service_mock = self.set_service_patch.start()
        self.workout_service_mock = self.workout_service_patch.start()
        
        # Import the handlers after patching services
        # Make sure the filename is correct here - it should match your actual implementation
        from src.api.set import get_set, get_sets_for_exercise, create_set, update_set, delete_set
        
        self.get_set = get_set
        self.get_sets_for_exercise = get_sets_for_exercise
        self.create_set = create_set
        self.update_set = update_set
        self.delete_set = delete_set

    def tearDown(self):
        """Clean up after each test"""
        self.set_service_patch.stop()
        self.workout_service_patch.stop()

    def test_get_set(self):
        """Test getting a set by ID"""
        # Configure mock
        mock_set = MagicMock()
        mock_set.to_dict.return_value = {
            "set_id": "set123",
            "completed_exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 5,
            "weight": 225.0
        }
        self.set_service_mock.get_set.return_value = mock_set
        
        # Create test event
        event = {
            "pathParameters": {
                "set_id": "set123"
            }
        }
        
        # Call handler
        response = self.get_set(event, {})
        
        # Parse response body
        body = json.loads(response["body"])
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["set_id"], "set123")
        self.assertEqual(body["reps"], 5)
        self.assertEqual(body["weight"], 225.0)
        self.set_service_mock.get_set.assert_called_once_with("set123")
        
    def test_get_set_not_found(self):
        """Test getting a set that doesn't exist"""
        # Configure mock
        self.set_service_mock.get_set.return_value = None
        
        # Create test event
        event = {
            "pathParameters": {
                "set_id": "nonexistent"
            }
        }
        
        # Call handler
        response = self.get_set(event, {})
        
        # Parse response body
        body = json.loads(response["body"])
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], "Set not found")
        self.set_service_mock.get_set.assert_called_once_with("nonexistent")

    def test_get_sets_for_exercise(self):
        """Test getting all sets for an exercise"""
        # Configure mock
        mock_set1 = MagicMock()
        mock_set1.to_dict.return_value = {
            "set_id": "set1",
            "completed_exercise_id": "exercise123",
            "workout_id": "workout456",
            "set_number": 1,
            "reps": 5,
            "weight": 225.0
        }
        
        mock_set2 = MagicMock()
        mock_set2.to_dict.return_value = {
            "set_id": "set2",
            "completed_exercise_id": "exercise123",
            "workout_id": "workout456",
            "set_number": 2,
            "reps": 5,
            "weight": 235.0
        }
        
        self.set_service_mock.get_sets_for_exercise.return_value = [mock_set1, mock_set2]
        
        # Create test event
        event = {
            "pathParameters": {
                "exercise_id": "exercise123"
            }
        }
        
        # Call handler
        response = self.get_sets_for_exercise(event, {})
        
        # Parse response body
        body = json.loads(response["body"])
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["exercise_id"], "exercise123")
        self.assertEqual(len(body["sets"]), 2)
        self.assertEqual(body["sets"][0]["set_id"], "set1")
        self.assertEqual(body["sets"][1]["set_id"], "set2")
        self.set_service_mock.get_sets_for_exercise.assert_called_once_with("exercise123")

    def test_create_set(self):
        """Test creating a new set"""
        # Configure mock
        mock_set = MagicMock()
        mock_set.to_dict.return_value = {
            "set_id": "new-set",
            "completed_exercise_id": "exercise123",
            "workout_id": "workout456",
            "set_number": 3,
            "reps": 5,
            "weight": 245.0,
            "rpe": 8.5
        }
        self.workout_service_mock.add_set_to_exercise.return_value = mock_set
        
        # Create test event
        event = {
            "pathParameters": {
                "exercise_id": "exercise123"
            },
            "body": json.dumps({
                "workout_id": "workout456",
                "set_number": 3,
                "reps": 5,
                "weight": 245.0,
                "rpe": 8.5
            })
        }
        
        # Call handler
        response = self.create_set(event, {})
        
        # Parse response body
        body = json.loads(response["body"])
        
        # Assert
        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["set_id"], "new-set")
        self.assertEqual(body["reps"], 5)
        self.assertEqual(body["weight"], 245.0)
        self.assertEqual(body["rpe"], 8.5)
        self.workout_service_mock.add_set_to_exercise.assert_called_once()

    def test_update_set(self):
        """Test updating a set"""
        # Configure mock
        mock_set = MagicMock()
        mock_set.to_dict.return_value = {
            "set_id": "set123",
            "completed_exercise_id": "exercise456",
            "workout_id": "workout789",
            "set_number": 1,
            "reps": 6,  # Updated value
            "weight": 235.0,  # Updated value
            "rpe": 9.0
        }
        self.workout_service_mock.update_set.return_value = mock_set
        
        # Create test event
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
        
        # Call handler
        response = self.update_set(event, {})
        
        # Parse response body
        body = json.loads(response["body"])
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["set_id"], "set123")
        self.assertEqual(body["reps"], 6)
        self.assertEqual(body["weight"], 235.0)
        self.assertEqual(body["rpe"], 9.0)
        self.workout_service_mock.update_set.assert_called_once()

    def test_delete_set(self):
        """Test deleting a set"""
        # Configure mock
        self.workout_service_mock.delete_set.return_value = True
        
        # Create test event
        event = {
            "pathParameters": {
                "set_id": "set123"
            }
        }
        
        # Call handler
        response = self.delete_set(event, {})
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        self.workout_service_mock.delete_set.assert_called_once_with("set123")

    def test_delete_set_not_found(self):
        """Test deleting a set that doesn't exist"""
        # Configure mock
        self.workout_service_mock.delete_set.return_value = False
        
        # Create test event
        event = {
            "pathParameters": {
                "set_id": "nonexistent"
            }
        }
        
        # Call handler
        response = self.delete_set(event, {})
        
        # Parse response body
        body = json.loads(response["body"])
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["error"], "Set not found")
        self.workout_service_mock.delete_set.assert_called_once_with("nonexistent")


if __name__ == "__main__": # pragma: no cover
    unittest.main()