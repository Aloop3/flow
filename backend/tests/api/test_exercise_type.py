import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import exercise_type_api after mocks are set up
with patch("boto3.resource"):
    from src.api import exercise_type_api
    from src.models.exercise_type import ExerciseCategory, ExerciseType


class TestExerciseTypeAPI(BaseTest):
    """
    Test suite for the Exercise Type API module
    """

    def test_get_exercise_types_success(self):
        """
        Test successful retrieval of exercise types with correct structure
        """
        # Call API without mocking (uses real ExerciseType class)
        event = {}
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Check that all expected categories are present
        expected_categories = ["barbell", "dumbbell", "bodyweight", "machine", "cable", "all"]
        for category in expected_categories:
            self.assertIn(category, response_body)

        # Check that categories contain exercises (not empty)
        self.assertGreater(len(response_body["barbell"]), 0)
        self.assertGreater(len(response_body["dumbbell"]), 0)
        self.assertGreater(len(response_body["bodyweight"]), 0)
        self.assertGreater(len(response_body["machine"]), 0)
        self.assertGreater(len(response_body["cable"]), 0)
        self.assertGreater(len(response_body["all"]), 0)

        # Check that "all" contains exercises from all categories
        all_exercises = response_body["all"]
        for category in ["barbell", "dumbbell", "bodyweight", "machine", "cable"]:
            for exercise in response_body[category]:
                self.assertIn(exercise, all_exercises)

        # Verify some known exercises exist
        self.assertIn("Bench Press", response_body["barbell"])
        self.assertIn("Dumbbell Bench Press", response_body["dumbbell"])
        self.assertIn("Push Ups", response_body["bodyweight"])

        # Ensure custom category is not included
        self.assertNotIn("custom", response_body)

    @patch("src.models.exercise_type.ExerciseType.get_categories")
    def test_get_exercise_types_error(self, mock_get_categories):
        """
        Test error handling in get_exercise_types
        """
        # Setup exception
        mock_get_categories.side_effect = Exception("Test exception")

        # Call API
        event = {}
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")
    
    @patch("src.services.user_service.UserService.get_user")
    def test_get_exercise_types_with_custom_exercises(self, mock_get_user):
        """
        Test get_exercise_types with user_id parameter includes custom exercises
        """
        # Setup mock user with custom exercises
        mock_user = MagicMock()
        mock_user.custom_exercises = [
            {"name": "Bulgarian Split Squat", "category": "BODYWEIGHT"},
            {"name": "Band Pull-Aparts", "category": "BODYWEIGHT"},
            {"name": "Custom Barbell Exercise", "category": "BARBELL"}
        ]
        mock_get_user.return_value = mock_user

        # Call API with user_id parameter
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Check that custom exercises are included in appropriate categories
        self.assertIn("Bulgarian Split Squat", response_body["bodyweight"])
        self.assertIn("Band Pull-Aparts", response_body["bodyweight"])
        self.assertIn("Custom Barbell Exercise", response_body["barbell"])
        
        # Check that custom exercises are also in "all" category
        self.assertIn("Bulgarian Split Squat", response_body["all"])
        self.assertIn("Band Pull-Aparts", response_body["all"])
        self.assertIn("Custom Barbell Exercise", response_body["all"])

        # Verify service was called
        mock_get_user.assert_called_once_with("user123")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_exercise_types_user_not_found(self, mock_get_user):
        """
        Test get_exercise_types when user not found (should still return predefined exercises)
        """
        # Setup
        mock_get_user.return_value = None

        # Call API with user_id parameter
        event = {
            "queryStringParameters": {"user_id": "nonexistent"}
        }
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should still contain predefined exercises
        self.assertIn("barbell", response_body)
        self.assertIn("all", response_body)

        # Verify service was called
        mock_get_user.assert_called_once_with("nonexistent")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_exercise_types_user_no_custom_exercises(self, mock_get_user):
        """
        Test get_exercise_types when user has no custom exercises
        """
        # Setup mock user with empty custom exercises
        mock_user = MagicMock()
        mock_user.custom_exercises = []
        mock_get_user.return_value = mock_user

        # Call API with user_id parameter
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should contain predefined exercises only
        self.assertIn("barbell", response_body)
        self.assertIn("all", response_body)

        # Verify service was called
        mock_get_user.assert_called_once_with("user123")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_exercise_types_user_service_exception(self, mock_get_user):
        """
        Test get_exercise_types when user service throws exception (should continue gracefully)
        """
        # Setup
        mock_get_user.side_effect = Exception("Database error")

        # Call API with user_id parameter
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert - should still succeed with predefined exercises only
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should contain predefined exercises
        self.assertIn("barbell", response_body)
        self.assertIn("all", response_body)

        # Verify service was called
        mock_get_user.assert_called_once_with("user123")

    def test_get_exercise_types_no_query_parameters(self):
        """
        Test get_exercise_types without query parameters (should return predefined exercises only)
        """
        # Call API without query parameters
        event = {}
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should contain predefined exercises with correct structure
        self.assertIn("barbell", response_body)
        self.assertIn("dumbbell", response_body) 
        self.assertIn("bodyweight", response_body)
        self.assertIn("machine", response_body)
        self.assertIn("cable", response_body)
        self.assertIn("all", response_body)

        # Should not contain custom category
        self.assertNotIn("custom", response_body)

    def test_get_exercise_types_empty_query_parameters(self):
        """
        Test get_exercise_types with empty query parameters
        """
        # Call API with empty query parameters
        event = {
            "queryStringParameters": {}
        }
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Should contain predefined exercises
        self.assertIn("all", response_body)
        self.assertIn("barbell", response_body)


if __name__ == "__main__":
    unittest.main()
