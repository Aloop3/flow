import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import exercise after the mocks are set up in BaseTest
with patch('boto3.resource'):
    from src.api import exercise_api

class TestExerciseAPI(BaseTest):
    """
    Test suite for the Exercise API module
    """

    @patch('src.services.exercise_service.ExerciseService.create_exercise')
    def test_create_exercise_success(self, mock_create_exercise):
        """
        Test successful exercise creation
        """
        
        # Setup
        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "exercise_category": "barbell",
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
            "rpe": 8.5,
            "notes": "Use belt",
            "order": 1
        }
        mock_create_exercise.return_value = mock_exercise
        
        event = {
            "body": json.dumps({
                "workout_id": "workout456",
                "exercise_type": "Squat",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 315.0,
                "rpe": 8.5,
                "notes": "Use belt",
                "order": 1
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.create_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["exercise_id"], "ex123")
        self.assertEqual(response_body["workout_id"], "workout456")
        self.assertEqual(response_body["exercise_type"], "Squat")
        self.assertEqual(response_body["sets"], 5)
        mock_create_exercise.assert_called_once_with(
            workout_id="workout456",
            exercise_type="Squat",
            exercise_category="barbell",
            sets=5,
            reps=5,
            weight=315.0,
            rpe=8.5,
            notes="Use belt",
            order=1
        )
    
    @patch('src.services.exercise_service.ExerciseService.create_exercise')
    def test_create_exercise_missing_fields(self, mock_create_exercise):
        """
        Test exercise creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps({
                "workout_id": "workout456",
                "exercise_type": "Squat",
                # Missing sets
                "reps": 5
                # Missing weight
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.create_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_exercise.assert_not_called()
    
    @patch('src.services.exercise_service.ExerciseService.create_exercise')
    def test_create_exercise_exception(self, mock_create_exercise):
        """
        Test exception handling in exercise creation
        """
        # Setup - simulate an exception
        mock_create_exercise.side_effect = Exception("Database connection error")
        
        event = {
            "body": json.dumps({
                "workout_id": "workout456",
                "exercise_type": "Squat",
                "sets": 5,
                "reps": 5,
                "weight": 315.0
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.create_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database connection error")
        mock_create_exercise.assert_called_once()
    
    @patch('src.services.exercise_service.ExerciseService.get_exercises_for_workout')
    def test_get_exercises_for_workout_success(self, mock_get_exercises):
        """
        Test successful retrieval of exercises for a workout
        """

        # Setup
        mock_exercise1 = MagicMock()
        mock_exercise1.to_dict.return_value = {
            "exercise_id": "ex1",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
            "order": 1
        }
        mock_exercise2 = MagicMock()
        mock_exercise2.to_dict.return_value = {
            "exercise_id": "ex2",
            "workout_id": "workout456",
            "exercise_type": "Bench Press",
            "sets": 5,
            "reps": 5,
            "weight": 225.0,
            "order": 2
        }
        mock_get_exercises.return_value = [mock_exercise1, mock_exercise2]
        
        event = {
            "pathParameters": {
                "workout_id": "workout456"
            }
        }
        context = {}
        
        # Call API
        response = exercise_api.get_exercises_for_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["exercise_id"], "ex1")
        self.assertEqual(response_body[0]["exercise_type"], "Squat")
        self.assertEqual(response_body[1]["exercise_id"], "ex2")
        self.assertEqual(response_body[1]["exercise_type"], "Bench Press")
        mock_get_exercises.assert_called_once_with("workout456")
    
    @patch('src.services.exercise_service.ExerciseService.get_exercises_for_workout')
    def test_get_exercises_for_workout_exception(self, mock_get_exercises):
        """
        Test exception handling in get exercises for workout
        """
        # Setup - simulate an exception
        mock_get_exercises.side_effect = Exception("Database query failed")
        
        event = {
            "pathParameters": {
                "workout_id": "workout456"
            }
        }
        context = {}
        
        # Call API
        response = exercise_api.get_exercises_for_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database query failed")
        mock_get_exercises.assert_called_once_with("workout456")

    @patch('src.services.exercise_service.ExerciseService.update_exercise')
    def test_update_exercise_success(self, mock_update_exercise):
        """
        Test successful exercise update
        """

        # Setup
        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 3,  # Updated
            "reps": 5,
            "weight": 335.0,  # Updated
            "rpe": 9.0,  # Updated
            "notes": "Use belt and knee sleeves"  # Updated
        }
        mock_update_exercise.return_value = mock_exercise
        
        event = {
            "pathParameters": {
                "exercise_id": "ex123"
            },
            "body": json.dumps({
                "sets": 3,
                "weight": 335.0,
                "rpe": 9.0,
                "notes": "Use belt and knee sleeves"
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.update_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["exercise_id"], "ex123")
        self.assertEqual(response_body["sets"], 3)
        self.assertEqual(response_body["weight"], 335.0)
        self.assertEqual(response_body["rpe"], 9.0)
        self.assertEqual(response_body["notes"], "Use belt and knee sleeves")
        mock_update_exercise.assert_called_once_with("ex123", {
            "sets": 3,
            "weight": 335.0,
            "rpe": 9.0,
            "notes": "Use belt and knee sleeves"
        })
    
    @patch('src.services.exercise_service.ExerciseService.update_exercise')
    def test_update_exercise_not_found(self, mock_update_exercise):
        """
        Test exercise update when exercise not found
        """

        # Setup
        mock_update_exercise.return_value = None
        
        event = {
            "pathParameters": {
                "exercise_id": "nonexistent"
            },
            "body": json.dumps({
                "sets": 3
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.update_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Exercise not found", response_body["error"])
    
    @patch('src.services.exercise_service.ExerciseService.update_exercise')
    def test_update_exercise_exception(self, mock_update_exercise):
        """
        Test exception handling in update exercise
        """
        # Setup - simulate an exception
        mock_update_exercise.side_effect = Exception("Update operation failed")
        
        event = {
            "pathParameters": {
                "exercise_id": "ex123"
            },
            "body": json.dumps({
                "sets": 3,
                "weight": 335.0
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.update_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Update operation failed")
        mock_update_exercise.assert_called_once()

    @patch('src.services.exercise_service.ExerciseService.delete_exercise')
    def test_delete_exercise_success(self, mock_delete_exercise):
        """
        Test successful exercise deletion
        """

        # Setup
        mock_delete_exercise.return_value = True
        
        event = {
            "pathParameters": {
                "exercise_id": "ex123"
            }
        }
        context = {}
        
        # Call API
        response = exercise_api.delete_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_exercise.assert_called_once_with("ex123")
    
    @patch('src.services.exercise_service.ExerciseService.delete_exercise')
    def test_delete_exercise_not_found(self, mock_delete_exercise):
        """
        Test exercise deletion when exercise not found
        """

        # Setup
        mock_delete_exercise.return_value = False
        
        event = {
            "pathParameters": {
                "exercise_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = exercise_api.delete_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Exercise not found", response_body["error"])
    
    @patch('src.services.exercise_service.ExerciseService.delete_exercise')
    def test_delete_exercise_exception(self, mock_delete_exercise):
        """
        Test exception handling in delete exercise
        """
        # Setup - simulate an exception
        mock_delete_exercise.side_effect = Exception("Delete operation failed")
        
        event = {
            "pathParameters": {
                "exercise_id": "ex123"
            }
        }
        context = {}
        
        # Call API
        response = exercise_api.delete_exercise(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Delete operation failed")
        mock_delete_exercise.assert_called_once_with("ex123")
    
    @patch('src.services.exercise_service.ExerciseService.reorder_exercises')
    def test_reorder_exercises_success(self, mock_reorder_exercises):
        """
        Test successful exercise reordering
        """

        # Setup
        mock_exercise1 = MagicMock()
        mock_exercise1.to_dict.return_value = {
            "exercise_id": "ex1",
            "order": 2  # Reordered from 1 to 2
        }
        mock_exercise2 = MagicMock()
        mock_exercise2.to_dict.return_value = {
            "exercise_id": "ex2",
            "order": 1  # Reordered from 2 to 1
        }
        mock_reorder_exercises.return_value = [mock_exercise2, mock_exercise1]  # New order
        
        event = {
            "body": json.dumps({
                "workout_id": "workout456",
                "exercise_order": ["ex2", "ex1"]  # New order
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.reorder_exercises(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["exercise_id"], "ex2")
        self.assertEqual(response_body[0]["order"], 1)
        self.assertEqual(response_body[1]["exercise_id"], "ex1")
        self.assertEqual(response_body[1]["order"], 2)
        mock_reorder_exercises.assert_called_once_with("workout456", ["ex2", "ex1"])
    
    @patch('src.services.exercise_service.ExerciseService.reorder_exercises')
    def test_reorder_exercises_missing_fields(self, mock_reorder_exercises):
        """
        Test exercise reordering with missing required fields
        """
        
        # Setup
        event = {
            "body": json.dumps({
                # Missing workout_id
                "exercise_order": ["ex2", "ex1"]
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.reorder_exercises(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_reorder_exercises.assert_not_called()
    
    @patch('src.services.exercise_service.ExerciseService.reorder_exercises')
    def test_reorder_exercises_exception(self, mock_reorder_exercises):
        """
        Test exception handling in reorder exercises
        """
        # Setup - simulate an exception
        mock_reorder_exercises.side_effect = Exception("Reorder operation failed")
        
        event = {
            "body": json.dumps({
                "workout_id": "workout456",
                "exercise_order": ["ex2", "ex1"]
            })
        }
        context = {}
        
        # Call API
        response = exercise_api.reorder_exercises(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Reorder operation failed")
        mock_reorder_exercises.assert_called_once_with("workout456", ["ex2", "ex1"])

if __name__ == "__main__":
    unittest.main()