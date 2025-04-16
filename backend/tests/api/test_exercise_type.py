import json
import unittest
from unittest.mock import patch
from tests.base_test import BaseTest

# Import exercise_type_api after mocks are set up
with patch("boto3.resource"):
    from src.api import exercise_type_api
    from src.models.exercise_type import ExerciseCategory, ExerciseType


class TestExerciseTypeAPI(BaseTest):
    """
    Test suite for the Exercise Type API module
    """

    @patch("src.models.exercise_type.ExerciseType.get_categories")
    @patch("src.models.exercise_type.ExerciseType.get_by_category")
    @patch("src.models.exercise_type.ExerciseType.get_all_predefined")
    def test_get_exercise_types_success(
        self, mock_get_all, mock_get_by_category, mock_get_categories
    ):
        """
        Test successful retrieval of exercise types with correct structure
        """
        # Setup mocks
        mock_categories = [
            ExerciseCategory.BARBELL,
            ExerciseCategory.DUMBBELL,
            ExerciseCategory.BODYWEIGHT,
        ]
        mock_get_categories.return_value = mock_categories

        # Mock category-specific exercises
        mock_barbell_exercises = ["Bench Press", "Squat", "Deadlift"]
        mock_dumbbell_exercises = ["Dumbbell Curl", "Dumbbell Press"]
        mock_bodyweight_exercises = ["Push Up", "Pull Up"]

        # Setup the mock to return different values based on category
        def get_by_category_side_effect(category):
            if category == ExerciseCategory.BARBELL:
                return mock_barbell_exercises
            elif category == ExerciseCategory.DUMBBELL:
                return mock_dumbbell_exercises
            elif category == ExerciseCategory.BODYWEIGHT:
                return mock_bodyweight_exercises
            return []

        mock_get_by_category.side_effect = get_by_category_side_effect

        # Setup all exercises
        all_exercises = (
            mock_barbell_exercises + mock_dumbbell_exercises + mock_bodyweight_exercises
        )
        mock_get_all.return_value = all_exercises

        # Call API
        event = {}
        context = {}
        response = exercise_type_api.get_exercise_types(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])

        # Check that all categories are present
        self.assertIn("barbell", response_body)
        self.assertIn("dumbbell", response_body)
        self.assertIn("bodyweight", response_body)
        self.assertIn("all", response_body)

        # Check that exercises are correctly categorized
        self.assertEqual(response_body["barbell"], mock_barbell_exercises)
        self.assertEqual(response_body["dumbbell"], mock_dumbbell_exercises)
        self.assertEqual(response_body["bodyweight"], mock_bodyweight_exercises)
        self.assertEqual(response_body["all"], all_exercises)

        # Verify method calls
        mock_get_categories.assert_called_once()
        self.assertEqual(mock_get_by_category.call_count, len(mock_categories))
        mock_get_all.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()
