import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

with patch("boto3.resource"):
    from src.api import exercise_api


class TestExerciseAPI(BaseTest):
    """
    Test suite for the Exercise API module
    """

    def create_test_event_with_auth(self, body_data, path_parameters=None):
        """Helper to create test events with proper Cognito auth structure"""
        event = {
            "body": json.dumps(body_data),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        if path_parameters:
            event["pathParameters"] = path_parameters
        return event

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda x, y, z, w=None: x,
    )
    @patch("src.api.exercise_api.convert_weight_to_kg", return_value=315.0)
    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="lb")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.create_exercise")
    def test_create_exercise_success(
        self,
        mock_create_exercise,
        mock_get_workout,
        mock_convert_kg,
        mock_get_unit,
        mock_convert_display,
        mock_get_pref,
    ):
        """
        Test successful exercise creation
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

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
            "order": 1,
        }
        mock_create_exercise.return_value = mock_exercise

        event = self.create_test_event_with_auth(
            {
                "workout_id": "workout456",
                "exercise_type": "Squat",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 315.0,
                "rpe": 8.5,
                "notes": "Use belt",
                "order": 1,
            }
        )
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

        # Verify weight conversion functions were called
        mock_get_pref.assert_called_once_with("test-user-id")
        mock_convert_kg.assert_called_once()
        mock_convert_display.assert_called_once()

    @patch("src.services.exercise_service.ExerciseService.create_exercise")
    def test_create_exercise_missing_fields(self, mock_create_exercise):
        """
        Test exercise creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "workout_id": "workout456",
                    "exercise_type": "Squat",
                    # Missing sets
                    "reps": 5
                    # Missing weight
                }
            )
        }
        context = {}

        # Call API
        response = exercise_api.create_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_exercise.assert_not_called()

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda x, y, z: x,
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.create_exercise")
    def test_create_exercise_exception(
        self,
        mock_create_exercise,
        mock_get_workout,
        mock_convert_display,
        mock_get_pref,
    ):
        """
        Test exception handling during exercise creation
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_create_exercise.side_effect = Exception("Database connection error")

        event = self.create_test_event_with_auth(
            {
                "workout_id": "workout456",
                "exercise_type": "Squat",
                "exercise_category": "barbell",
                "sets": 5,
                "reps": 5,
                "weight": 315.0,
            }
        )
        context = {}

        # Call API
        response = exercise_api.create_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database connection error")

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda ex_dict, user_pref, ex_type, ex_category=None: ex_dict,
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercises_for_workout")
    def test_get_exercises_for_workout_success(
        self, mock_get_exercises, mock_get_workout, mock_convert_display, mock_get_pref
    ):
        """
        Test successful retrieval of exercises for a workout
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "exercise_type": "Squat",
            "sets": 5,
            "reps": 5,
            "weight": 315.0,
        }
        mock_exercise.exercise_type = "Squat"
        mock_get_exercises.return_value = [mock_exercise]

        event = self.create_test_event_with_auth({}, {"workout_id": "workout456"})
        context = {}

        # Call API
        response = exercise_api.get_exercises_for_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0]["exercise_id"], "ex123")

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercises_for_workout")
    def test_get_exercises_for_workout_exception(
        self, mock_get_exercises, mock_get_workout, mock_get_pref
    ):
        """
        Test exception handling during exercise retrieval
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_get_exercises.side_effect = Exception("Database query failed")

        event = self.create_test_event_with_auth({}, {"workout_id": "workout456"})
        context = {}

        # Call API
        response = exercise_api.get_exercises_for_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database query failed")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_user_weight_preference_success(self, mock_get_user):
        """Test get_user_weight_preference with valid user"""
        # Setup
        mock_user = MagicMock()
        mock_user.weight_unit_preference = "kg"
        mock_get_user.return_value = mock_user

        # Call function
        result = exercise_api.get_user_weight_preference("test-user-id")

        # Assert
        self.assertEqual(result, "kg")
        mock_get_user.assert_called_once_with("test-user-id")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_user_weight_preference_user_not_found(self, mock_get_user):
        """Test get_user_weight_preference when user not found"""
        # Setup
        mock_get_user.return_value = None

        # Call function
        result = exercise_api.get_user_weight_preference("nonexistent-user")

        # Assert
        self.assertEqual(result, "auto")
        mock_get_user.assert_called_once_with("nonexistent-user")

    @patch("src.services.user_service.UserService.get_user")
    def test_get_user_weight_preference_exception(self, mock_get_user):
        """Test get_user_weight_preference with service exception"""
        # Setup
        mock_get_user.side_effect = Exception("Database error")

        # Call function
        result = exercise_api.get_user_weight_preference("test-user-id")

        # Assert
        self.assertEqual(result, "auto")  # Should fallback to "auto"
        mock_get_user.assert_called_once_with("test-user-id")

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.update_exercise")
    def test_update_exercise_success(
        self, mock_update_exercise, mock_get_exercise, mock_get_workout
    ):
        """
        Test successful exercise update
        """

        # Setup ownership mocks
        mock_existing = MagicMock()
        mock_existing.workout_id = "workout456"
        mock_get_exercise.return_value = mock_existing

        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "sets": 3,  # Updated
            "reps": 5,
            "weight": 335.0,  # Updated
            "rpe": 9.0,  # Updated
            "notes": "Use belt and knee sleeves",  # Updated
        }
        mock_update_exercise.return_value = mock_exercise

        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "body": json.dumps(
                {
                    "sets": 3,
                    "weight": 335.0,
                    "rpe": 9.0,
                    "notes": "Use belt and knee sleeves",
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
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
        mock_update_exercise.assert_called_once_with(
            "ex123",
            {
                "sets": 3,
                "weight": 335.0,
                "rpe": 9.0,
                "notes": "Use belt and knee sleeves",
            },
        )

    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_update_exercise_not_found(self, mock_get_exercise):
        """
        Test exercise update when exercise not found
        """

        # Setup
        mock_get_exercise.return_value = None

        event = {
            "pathParameters": {"exercise_id": "nonexistent"},
            "body": json.dumps({"sets": 3}),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.update_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Exercise not found", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.update_exercise")
    def test_update_exercise_exception(
        self, mock_update_exercise, mock_get_exercise, mock_get_workout
    ):
        """
        Test exception handling in update exercise
        """
        # Setup ownership mocks
        mock_existing = MagicMock()
        mock_existing.workout_id = "workout456"
        mock_get_exercise.return_value = mock_existing

        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_update_exercise.side_effect = Exception("Update operation failed")

        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "body": json.dumps({"sets": 3, "weight": 335.0}),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.update_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Update operation failed")
        mock_update_exercise.assert_called_once()

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.delete_exercise")
    def test_delete_exercise_success(
        self, mock_delete_exercise, mock_get_exercise, mock_get_workout
    ):
        """
        Test successful exercise deletion
        """

        # Setup ownership mocks
        mock_existing = MagicMock()
        mock_existing.workout_id = "workout456"
        mock_get_exercise.return_value = mock_existing

        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_delete_exercise.return_value = True

        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_exercise.assert_called_once_with("ex123")

    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_delete_exercise_not_found(self, mock_get_exercise):
        """
        Test exercise deletion when exercise not found
        """

        # Setup
        mock_get_exercise.return_value = None

        event = {
            "pathParameters": {"exercise_id": "nonexistent"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Exercise not found", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.delete_exercise")
    def test_delete_exercise_exception(
        self, mock_delete_exercise, mock_get_exercise, mock_get_workout
    ):
        """
        Test exception handling in delete exercise
        """
        # Setup ownership mocks
        mock_existing = MagicMock()
        mock_existing.workout_id = "workout456"
        mock_get_exercise.return_value = mock_existing

        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_delete_exercise.side_effect = Exception("Delete operation failed")

        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Delete operation failed")
        mock_delete_exercise.assert_called_once_with("ex123")

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.reorder_exercises")
    def test_reorder_exercises_success(self, mock_reorder_exercises, mock_get_workout):
        """
        Test successful exercise reordering
        """

        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise1 = MagicMock()
        mock_exercise1.to_dict.return_value = {
            "exercise_id": "ex1",
            "order": 2,  # Reordered from 1 to 2
        }
        mock_exercise2 = MagicMock()
        mock_exercise2.to_dict.return_value = {
            "exercise_id": "ex2",
            "order": 1,  # Reordered from 2 to 1
        }
        mock_reorder_exercises.return_value = [
            mock_exercise2,
            mock_exercise1,
        ]  # New order

        event = {
            "body": json.dumps(
                {
                    "workout_id": "workout456",
                    "exercise_order": ["ex2", "ex1"],  # New order
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
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

    @patch("src.services.exercise_service.ExerciseService.reorder_exercises")
    def test_reorder_exercises_missing_fields(self, mock_reorder_exercises):
        """
        Test exercise reordering with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    # Missing workout_id
                    "exercise_order": ["ex2", "ex1"]
                }
            )
        }
        context = {}

        # Call API
        response = exercise_api.reorder_exercises(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_reorder_exercises.assert_not_called()

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.reorder_exercises")
    def test_reorder_exercises_exception(
        self, mock_reorder_exercises, mock_get_workout
    ):
        """
        Test exception handling in reorder exercises
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_reorder_exercises.side_effect = Exception("Reorder operation failed")

        event = {
            "body": json.dumps(
                {"workout_id": "workout456", "exercise_order": ["ex2", "ex1"]}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.reorder_exercises(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Reorder operation failed")
        mock_reorder_exercises.assert_called_once_with("workout456", ["ex2", "ex1"])

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="kg")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda ex_dict, user_pref, ex_type, ex_category=None: ex_dict,
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_reorder_sets_success(
        self,
        mock_service_class,
        mock_get_workout,
        mock_convert_weights,
        mock_get_preference,
    ):
        # Arrange
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        body_data = {"set_order": [3, 1, 2]}
        path_parameters = {"exercise_id": "test-exercise-id"}
        event = self.create_test_event_with_auth(body_data, path_parameters)

        # Mock service instance
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        # Create complete Exercise object for get_exercise return
        from src.models.exercise import Exercise

        exercise = Exercise(
            exercise_id="test-exercise-id",
            workout_id="test-workout",
            exercise_type="Bench Press",
            sets=3,
            reps=10,
            weight=100,
            rpe=8,
            status="planned",
            notes="",
            order=1,
            sets_data=[
                {"set_number": 1, "reps": 10, "weight": 100},
                {"set_number": 2, "reps": 8, "weight": 105},
                {"set_number": 3, "reps": 6, "weight": 110},
            ],
        )

        # Mock service methods directly
        mock_service.get_exercise.return_value = exercise
        mock_service.reorder_sets.return_value = exercise  # Simplified for test

        # Act & Assert
        response = exercise_api.reorder_sets(event, {})
        self.assertEqual(response["statusCode"], 200)

    def test_reorder_sets_invalid_json(self):
        """
        Test reorder_sets with invalid JSON body.

        Given: Event with malformed JSON body
        When: POST /exercises/{exercise_id}/reorder-sets
        Then: Should return 400 error with JSON decode message
        """
        # Arrange
        event = {
            "pathParameters": {"exercise_id": "test-exercise-id"},
            "body": "invalid json {{",
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Act
        response = exercise_api.reorder_sets(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])

    def test_reorder_sets_missing_set_order(self):
        """
        Test reorder_sets with missing set_order in body.

        Given: Valid JSON body without set_order field
        When: POST /exercises/{exercise_id}/reorder-sets
        Then: Should return 400 error for missing set_order
        """
        # Arrange
        body_data = {"other_field": "value"}  # Missing set_order
        path_parameters = {"exercise_id": "test-exercise-id"}
        event = self.create_test_event_with_auth(body_data, path_parameters)
        context = {}

        # Act
        response = exercise_api.reorder_sets(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing set_order array", response_body["error"])

    @patch("src.api.exercise_api.ExerciseService")
    def test_reorder_sets_exercise_not_found(self, mock_service_class):
        """
        Test reorder_sets when exercise doesn't exist.

        Given: Non-existent exercise ID
        When: POST /exercises/{exercise_id}/reorder-sets
        Then: Should return 404 error
        """
        # Arrange
        body_data = {"set_order": [1, 2, 3]}
        path_parameters = {"exercise_id": "nonexistent-exercise"}
        event = self.create_test_event_with_auth(body_data, path_parameters)

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_exercise.return_value = None  # Exercise not found

        context = {}

        # Act
        response = exercise_api.reorder_sets(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Exercise not found", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_reorder_sets_value_error(self, mock_service_class, mock_get_workout):
        """
        Test reorder_sets when service raises ValueError.

        Given: Invalid set_order causing ValueError in service
        When: POST /exercises/{exercise_id}/reorder-sets
        Then: Should return 400 error with ValueError message
        """
        # Arrange
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        body_data = {"set_order": [1, 2, 4]}  # Invalid set number
        path_parameters = {"exercise_id": "test-exercise-id"}
        event = self.create_test_event_with_auth(body_data, path_parameters)

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        mock_exercise = MagicMock()
        mock_service.get_exercise.return_value = mock_exercise
        mock_service.reorder_sets.side_effect = ValueError("Invalid set numbers")

        context = {}

        # Act
        response = exercise_api.reorder_sets(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid parameters: Invalid set numbers", response_body["error"])

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda ex_dict, user_pref, ex_type, ex_category=None: ex_dict,
    )
    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="kg")
    @patch("src.api.exercise_api.convert_weight_to_kg", return_value=140.0)
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.track_set")
    def test_track_set_success(
        self,
        mock_track_set,
        mock_get_exercise,
        mock_get_workout,
        mock_convert_kg,
        mock_get_unit,
        mock_convert_display,
        mock_get_pref,
    ):
        """
        Test successful set tracking
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_get_exercise.return_value = mock_exercise

        mock_updated_exercise = MagicMock()
        mock_updated_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "exercise_type": "Squat",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 140.0, "completed": True}
            ],
        }
        mock_updated_exercise.exercise_type = "Squat"
        mock_track_set.return_value = mock_updated_exercise

        event = self.create_test_event_with_auth(
            {
                "reps": 5,
                "weight": 315.0,
                "rpe": 8,
                "completed": True,
            },
            {"exercise_id": "ex123", "set_number": "1"},
        )
        context = {}

        # Call API
        response = exercise_api.track_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["exercise_id"], "ex123")

        # Verify service was called with converted weight
        mock_track_set.assert_called_once_with(
            exercise_id="ex123",
            set_number=1,
            reps=5,
            weight=140.0,  # Converted weight
            rpe=8,
            completed=True,
            notes=None,
        )

    @patch("src.services.exercise_service.ExerciseService")
    def test_track_set_missing_fields(self, mock_service):
        # Setup mock service
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance

        # Create mock event missing required fields
        event = {
            "pathParameters": {"exercise_id": "test123", "set_number": "1"},
            "body": json.dumps(
                {
                    # Missing reps
                    "weight": 225.0,
                    "completed": True,
                }
            ),
        }

        # Call API function
        response = exercise_api.track_set(event, {})

        # Verify error response
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertIn("error", body)

        # Verify service not called
        mock_service_instance.track_set.assert_not_called()

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_track_set_exercise_not_found(self, mock_get_exercise, mock_get_pref):
        """
        Test tracking set when exercise is not found
        """
        # Setup
        mock_get_exercise.return_value = None

        event = self.create_test_event_with_auth(
            {"reps": 5, "weight": 315.0}, {"exercise_id": "ex123", "set_number": "1"}
        )
        context = {}

        # Call API
        response = exercise_api.track_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Exercise not found")

    def test_track_set_invalid_set_number(self):
        """Test track_set with invalid set number parameter"""
        # Setup
        event = self.create_test_event_with_auth(
            {"reps": 5, "weight": 315.0},
            {"exercise_id": "ex123", "set_number": "invalid"},
        )
        context = {}

        # Call API
        response = exercise_api.track_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid parameters", response_body["error"])

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=Exception("Conversion error"),
    )
    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="kg")
    @patch("src.api.exercise_api.convert_weight_to_kg", return_value=140.0)
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.track_set")
    def test_track_set_exception(
        self,
        mock_track_set,
        mock_get_exercise,
        mock_get_workout,
        mock_convert_kg,
        mock_get_unit,
        mock_convert_display,
        mock_get_pref,
    ):
        """Test track_set with exception during processing"""
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_get_exercise.return_value = mock_exercise

        mock_updated_exercise = MagicMock()
        mock_updated_exercise.to_dict.return_value = {"exercise_id": "ex123"}
        mock_updated_exercise.exercise_type = "Squat"
        mock_track_set.return_value = mock_updated_exercise

        event = self.create_test_event_with_auth(
            {"reps": 5, "weight": 315.0}, {"exercise_id": "ex123", "set_number": "1"}
        )
        context = {}

        # Call API
        response = exercise_api.track_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertIn("Server error", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_delete_exercise_set_success(self, MockExerciseService, mock_get_workout):
        """
        Test successful exercise set deletion
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "test-exercise-1",
            "workout_id": "test-workout-1",
            "sets_data": [
                {"set_number": 1, "reps": 10, "weight": 100.0, "completed": True}
            ],
        }
        mock_service_instance = MockExerciseService.return_value
        mock_service_instance.get_exercise.return_value = mock_exercise
        mock_service_instance.delete_set.return_value = mock_exercise

        event = {
            "pathParameters": {"exercise_id": "test-exercise-1", "set_number": "1"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_service_instance.delete_set.assert_called_once_with("test-exercise-1", 1)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["exercise_id"], "test-exercise-1")

    @patch("src.api.exercise_api.ExerciseService")
    def test_delete_exercise_set_exercise_not_found(self, MockExerciseService):
        """
        Test exercise set deletion when the exercise is not found
        """

        # Setup
        mock_service_instance = MockExerciseService.return_value
        mock_service_instance.get_exercise.return_value = None

        event = {
            "pathParameters": {"exercise_id": "test-exercise-1", "set_number": "1"}
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Exercise not found", response_body["error"])
        mock_service_instance.delete_set.assert_not_called()

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_delete_exercise_set_not_found(self, MockExerciseService, mock_get_workout):
        """
        Test exercise set deletion when the set is not found
        """

        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "test-exercise-1",
            "workout_id": "test-workout-1",
            "sets_data": [
                {"set_number": 1, "reps": 10, "weight": 100.0, "completed": True}
            ],
        }
        mock_service_instance = MockExerciseService.return_value
        mock_service_instance.get_exercise.return_value = mock_exercise
        mock_service_instance.delete_set.return_value = None

        event = {
            "pathParameters": {"exercise_id": "test-exercise-1", "set_number": "999"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Set not found or already deleted", response_body["error"])

    def test_delete_exercise_set_invalid_set_number(self):
        """
        Test exercise set deletion when an invalid set number is provided
        """

        # Setup
        event = {
            "pathParameters": {
                "exercise_id": "test-exercise-1",
                "set_number": "not-a-number",
            }
        }
        context = {}

        # Call API
        response = exercise_api.delete_exercise_set(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid parameters", response_body["error"])

    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="kg")
    @patch("src.api.exercise_api.convert_weight_from_kg", return_value=315.0)
    def test_convert_exercise_weights_for_display_with_weight(
        self, mock_convert_from_kg, mock_get_unit
    ):
        """Test convert_exercise_weights_for_display with exercise weight"""
        # Setup
        exercise_dict = {
            "exercise_id": "ex123",
            "exercise_type": "Squat",
            "weight": 143.0,  # kg storage
            "sets_data": [
                {"set_number": 1, "weight": 140.0, "reps": 5},
                {"set_number": 2, "weight": 145.0, "reps": 5},
            ],
        }
        user_preference = "auto"
        exercise_type = "Squat"

        # Call function
        result = exercise_api.convert_exercise_weights_for_display(
            exercise_dict, user_preference, exercise_type
        )

        # Assert
        self.assertEqual(mock_get_unit.call_count, 1)
        call_args = mock_get_unit.call_args
        self.assertEqual(
            call_args[0][0], "Squat"
        )  # First positional arg: exercise_type
        self.assertEqual(
            call_args[0][1], "auto"
        )  # Second positional arg: user_preference
        self.assertEqual(
            call_args[0][2], None
        )  # Third positional arg: exercise_category

    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="lb")
    @patch("src.api.exercise_api.convert_weight_from_kg", return_value=225.0)
    def test_convert_exercise_weights_for_display_no_weight(
        self, mock_convert_from_kg, mock_get_unit
    ):
        """Test convert_exercise_weights_for_display with no weight data"""
        # Setup
        exercise_dict = {
            "exercise_id": "ex123",
            "exercise_type": "Dumbbell Curl",
            "weight": None,  # No weight
            "sets_data": None,  # No sets data
        }
        user_preference = "lb"
        exercise_type = "Dumbbell Curl"

        # Call function
        result = exercise_api.convert_exercise_weights_for_display(
            exercise_dict, user_preference, exercise_type
        )

        # Assert
        self.assertEqual(result["display_unit"], "lb")
        mock_get_unit.assert_called_once_with("Dumbbell Curl", "lb", None)
        self.assertEqual(mock_get_unit.call_count, 1)
        call_args = mock_get_unit.call_args
        self.assertEqual(
            call_args[0][0], "Dumbbell Curl"
        )  # First positional arg: exercise_type
        self.assertEqual(
            call_args[0][1], "lb"
        )  # Second positional arg: user_preference
        self.assertEqual(
            call_args[0][2], None
        )  # Third positional arg: exercise_category

    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="lb")
    @patch("src.api.exercise_api.convert_weight_from_kg", return_value=225.0)
    def test_convert_exercise_weights_for_display_with_planned_sets_data(
        self, mock_convert_from_kg, mock_get_unit
    ):
        """Test convert_exercise_weights_for_display includes planned_sets_data conversion"""
        # Setup
        exercise_dict = {
            "exercise_id": "ex123",
            "exercise_type": "Squat",
            "weight": 102.0,  # kg storage
            "sets_data": [
                {"set_number": 1, "weight": 104.0, "reps": 5, "completed": True},
                {"set_number": 2, "weight": 106.0, "reps": 4, "completed": True},
            ],
            "planned_sets_data": [
                {"set_number": 1, "weight": 102.0, "reps": 5, "completed": False},
                {"set_number": 2, "weight": 102.0, "reps": 5, "completed": False},
            ],
        }
        user_preference = "auto"
        exercise_type = "Squat"

        # Call function
        result = exercise_api.convert_exercise_weights_for_display(
            exercise_dict, user_preference, exercise_type
        )

        # Assert the function was called for each weight field
        # Expected calls: template weight + 2 sets_data weights + 2 planned_sets_data weights = 5 calls
        self.assertEqual(mock_convert_from_kg.call_count, 5)

        # Verify planned_sets_data is included in result
        self.assertIn("planned_sets_data", result)
        self.assertEqual(len(result["planned_sets_data"]), 2)

        # Verify display_unit is set
        self.assertEqual(result["display_unit"], "lb")

        # Verify get_unit was called correctly
        mock_get_unit.assert_called_once_with("Squat", "auto", None)

    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="kg")
    @patch("src.api.exercise_api.convert_weight_from_kg", return_value=100.0)
    def test_convert_exercise_weights_for_display_planned_sets_data_only(
        self, mock_convert_from_kg, mock_get_unit
    ):
        """Test convert_exercise_weights_for_display with only planned_sets_data"""
        # Setup
        exercise_dict = {
            "exercise_id": "ex123",
            "exercise_type": "Bench Press",
            "weight": 100.0,  # kg storage
            "sets_data": None,  # No actual sets yet
            "planned_sets_data": [
                {"set_number": 1, "weight": 100.0, "reps": 8, "completed": False},
                {"set_number": 2, "weight": 100.0, "reps": 8, "completed": False},
                {"set_number": 3, "weight": 100.0, "reps": 8, "completed": False},
            ],
        }
        user_preference = "kg"
        exercise_type = "Bench Press"

        # Call function
        result = exercise_api.convert_exercise_weights_for_display(
            exercise_dict, user_preference, exercise_type
        )

        # Assert the function was called for template weight + 3 planned_sets_data weights = 4 calls
        self.assertEqual(mock_convert_from_kg.call_count, 4)

        # Verify planned_sets_data is included and properly structured
        self.assertIn("planned_sets_data", result)
        self.assertEqual(len(result["planned_sets_data"]), 3)

        # Verify sets_data handling (should remain None)
        self.assertIsNone(result.get("sets_data"))

        # Verify display_unit is set
        self.assertEqual(result["display_unit"], "kg")

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda x, y, z, w=None: x,
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercises_for_workout")
    def test_get_exercises_for_workout_includes_planned_sets_data(
        self, mock_get_exercises, mock_get_workout, mock_convert_display, mock_get_pref
    ):
        """Test that get_exercises_for_workout API returns planned_sets_data"""
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        # Setup mock exercises with planned_sets_data
        mock_exercise = MagicMock()
        mock_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "exercise_category": "barbell",
            "sets": 3,
            "reps": 5,
            "weight": 225.0,
            "sets_data": [
                {"set_number": 1, "weight": 230.0, "reps": 5, "completed": True},
            ],
            "planned_sets_data": [
                {"set_number": 1, "weight": 225.0, "reps": 5, "completed": False},
            ],
        }
        mock_get_exercises.return_value = [mock_exercise]

        # Create test event
        event = {
            "pathParameters": {"workout_id": "workout456"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.get_exercises_for_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 1)

        # Verify planned_sets_data is included in response
        exercise_response = response_body[0]
        self.assertIn("planned_sets_data", exercise_response)
        self.assertEqual(len(exercise_response["planned_sets_data"]), 1)
        self.assertEqual(exercise_response["planned_sets_data"][0]["weight"], 225.0)

        # Verify service was called correctly
        mock_get_exercises.assert_called_once_with("workout456")

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch(
        "src.api.exercise_api.convert_exercise_weights_for_display",
        side_effect=lambda ex_dict, user_pref, ex_type, ex_category=None: ex_dict,
    )
    @patch("src.api.exercise_api.get_exercise_default_unit", return_value="kg")
    @patch("src.api.exercise_api.convert_weight_to_kg", return_value=140.0)
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.workout_service.WorkoutService.complete_exercise")
    def test_complete_exercise_success(
        self,
        mock_complete_exercise,
        mock_get_exercise,
        mock_get_workout,
        mock_convert_kg,
        mock_get_unit,
        mock_convert_display,
        mock_get_pref,
    ):
        """Test successful exercise completion with weight conversion"""
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "test-user-id"
        mock_get_workout.return_value = mock_workout

        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_get_exercise.return_value = mock_exercise

        mock_completed_exercise = MagicMock()
        mock_completed_exercise.to_dict.return_value = {
            "exercise_id": "ex123",
            "exercise_type": "Squat",
            "status": "completed",
            "sets": 3,
            "reps": 5,
            "weight": 140.0,
            "rpe": 8.0,
        }
        mock_completed_exercise.exercise_type = "Squat"
        mock_complete_exercise.return_value = mock_completed_exercise

        event = self.create_test_event_with_auth(
            {
                "sets": 3,
                "reps": 5,
                "weight": 315.0,  # Display weight
                "rpe": 8.0,
                "notes": "Felt strong",
            },
            {"exercise_id": "ex123"},
        )
        context = {}

        # Call API
        response = exercise_api.complete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        mock_get_pref.assert_called_once_with("test-user-id")
        mock_get_exercise.assert_called_once_with("ex123")
        mock_convert_kg.assert_called_once_with(315.0, "kg")
        mock_complete_exercise.assert_called_once_with(
            exercise_id="ex123",
            sets=3,
            reps=5,
            weight=140.0,  # Converted weight
            rpe=8.0,
            notes="Felt strong",
        )

    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_complete_exercise_not_found(self, mock_get_exercise, mock_get_pref):
        """Test complete_exercise when exercise not found"""
        # Setup
        mock_get_exercise.return_value = None

        event = self.create_test_event_with_auth(
            {"sets": 3, "reps": 5, "weight": 315.0}, {"exercise_id": "nonexistent"}
        )
        context = {}

        # Call API
        response = exercise_api.complete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Exercise not found")

    def test_complete_exercise_missing_fields(self):
        """Test complete_exercise with missing required fields"""
        # Setup
        event = self.create_test_event_with_auth(
            {
                "sets": 3,
                "reps": 5
                # Missing weight
            },
            {"exercise_id": "ex123"},
        )
        context = {}

        # Call API
        response = exercise_api.complete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])

    def test_complete_exercise_invalid_json(self):
        """Test complete_exercise with invalid JSON"""
        # Setup
        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "body": "invalid json",
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = exercise_api.complete_exercise(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid JSON", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_create_exercise_workout_not_found(self, mock_get_workout):
        """Test create_exercise when workout doesn't exist"""
        mock_get_workout.return_value = None
        event = self.create_test_event_with_auth(
            {
                "workout_id": "nonexistent",
                "exercise_type": "Squat",
                "sets": 5,
                "reps": 5,
            }
        )
        response = exercise_api.create_exercise(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_get_exercises_workout_not_found(self, mock_get_workout):
        """Test get_exercises_for_workout when workout doesn't exist"""
        mock_get_workout.return_value = None
        event = self.create_test_event_with_auth({}, {"workout_id": "nonexistent"})
        response = exercise_api.get_exercises_for_workout(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_update_exercise_workout_not_found(
        self, mock_get_exercise, mock_get_workout
    ):
        """Test update_exercise when workout doesn't exist"""
        mock_existing = MagicMock()
        mock_existing.workout_id = "nonexistent"
        mock_get_exercise.return_value = mock_existing
        mock_get_workout.return_value = None

        event = self.create_test_event_with_auth({"sets": 3}, {"exercise_id": "ex123"})
        response = exercise_api.update_exercise(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_complete_exercise_workout_not_found(
        self, mock_get_exercise, mock_get_pref, mock_get_workout
    ):
        """Test complete_exercise when workout doesn't exist"""
        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_get_exercise.return_value = mock_exercise
        mock_get_workout.return_value = None

        event = self.create_test_event_with_auth(
            {"sets": 3, "reps": 5, "weight": 315.0}, {"exercise_id": "ex123"}
        )
        response = exercise_api.complete_exercise(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    def test_delete_exercise_workout_not_found(
        self, mock_get_exercise, mock_get_workout
    ):
        """Test delete_exercise when workout doesn't exist"""
        mock_existing = MagicMock()
        mock_existing.workout_id = "nonexistent"
        mock_get_exercise.return_value = mock_existing
        mock_get_workout.return_value = None

        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        response = exercise_api.delete_exercise(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_reorder_exercises_workout_not_found(self, mock_get_workout):
        """Test reorder_exercises when workout doesn't exist"""
        mock_get_workout.return_value = None
        event = {
            "body": json.dumps(
                {"workout_id": "nonexistent", "exercise_order": ["ex1"]}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        response = exercise_api.reorder_exercises(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_reorder_sets_workout_not_found(self, mock_service_class, mock_get_workout):
        """Test reorder_sets when workout doesn't exist"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_exercise.return_value = MagicMock()
        mock_get_workout.return_value = None

        event = self.create_test_event_with_auth(
            {"set_order": [1, 2]}, {"exercise_id": "ex123"}
        )
        response = exercise_api.reorder_sets(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.api.exercise_api.ExerciseService")
    def test_track_set_workout_not_found(
        self, mock_service_class, mock_get_pref, mock_get_workout
    ):
        """Test track_set when workout doesn't exist"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_service.get_exercise.return_value = mock_exercise
        mock_get_workout.return_value = None

        event = self.create_test_event_with_auth(
            {"reps": 5, "weight": 315.0}, {"exercise_id": "ex123", "set_number": "1"}
        )
        response = exercise_api.track_set(event, {})
        self.assertEqual(response["statusCode"], 404)

    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_delete_exercise_set_workout_not_found(
        self, mock_service_class, mock_get_workout
    ):
        """Test delete_exercise_set when workout doesn't exist"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.get_exercise.return_value = MagicMock()
        mock_get_workout.return_value = None

        event = {
            "pathParameters": {"exercise_id": "ex123", "set_number": "1"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        response = exercise_api.delete_exercise_set(event, {})
        self.assertEqual(response["statusCode"], 404)

    # ---- IDOR Tests

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.create_exercise")
    def test_create_exercise_unauthorized(
        self, mock_create, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot create exercise in another athlete's workout"""
        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = self.create_test_event_with_auth(
            {"workout_id": "workout456", "exercise_type": "Squat", "sets": 5, "reps": 5}
        )
        response = exercise_api.create_exercise(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_create.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_get_exercises_for_workout_unauthorized(
        self, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot get exercises from another athlete's workout"""
        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = self.create_test_event_with_auth({}, {"workout_id": "workout456"})
        response = exercise_api.get_exercises_for_workout(event, {})
        self.assertEqual(response["statusCode"], 403)

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.update_exercise")
    def test_update_exercise_unauthorized(
        self, mock_update, mock_get_exercise, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot update another athlete's exercise"""
        mock_existing = MagicMock()
        mock_existing.workout_id = "workout456"
        mock_get_exercise.return_value = mock_existing

        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = self.create_test_event_with_auth({"sets": 3}, {"exercise_id": "ex123"})
        response = exercise_api.update_exercise(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_update.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.workout_service.WorkoutService.complete_exercise")
    def test_complete_exercise_unauthorized(
        self,
        mock_complete,
        mock_get_exercise,
        mock_get_pref,
        mock_get_workout,
        mock_get_relationship,
    ):
        """Test that user cannot complete another athlete's exercise"""
        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_get_exercise.return_value = mock_exercise

        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = self.create_test_event_with_auth(
            {"sets": 3, "reps": 5, "weight": 315.0}, {"exercise_id": "ex123"}
        )
        response = exercise_api.complete_exercise(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_complete.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.get_exercise")
    @patch("src.services.exercise_service.ExerciseService.delete_exercise")
    def test_delete_exercise_unauthorized(
        self, mock_delete, mock_get_exercise, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot delete another athlete's exercise"""
        mock_existing = MagicMock()
        mock_existing.workout_id = "workout456"
        mock_get_exercise.return_value = mock_existing

        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"exercise_id": "ex123"},
            "requestContext": {"authorizer": {"claims": {"sub": "attacker-user"}}},
        }
        response = exercise_api.delete_exercise(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_delete.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.services.exercise_service.ExerciseService.reorder_exercises")
    def test_reorder_exercises_unauthorized(
        self, mock_reorder, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot reorder exercises in another athlete's workout"""
        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = {
            "body": json.dumps(
                {"workout_id": "workout456", "exercise_order": ["ex2", "ex1"]}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "attacker-user"}}},
        }
        response = exercise_api.reorder_exercises(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_reorder.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_reorder_sets_unauthorized(
        self, mock_service_class, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot reorder sets in another athlete's exercise"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        mock_exercise = MagicMock()
        mock_service.get_exercise.return_value = mock_exercise

        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = self.create_test_event_with_auth(
            {"set_order": [1, 2, 3]}, {"exercise_id": "ex123"}
        )
        response = exercise_api.reorder_sets(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_service.reorder_sets.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.get_user_weight_preference", return_value="auto")
    @patch("src.api.exercise_api.ExerciseService")
    def test_track_set_unauthorized(
        self, mock_service_class, mock_get_pref, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot track set in another athlete's exercise"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        mock_exercise = MagicMock()
        mock_exercise.exercise_type = "Squat"
        mock_service.get_exercise.return_value = mock_exercise

        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = self.create_test_event_with_auth(
            {"reps": 5, "weight": 315.0}, {"exercise_id": "ex123", "set_number": "1"}
        )
        response = exercise_api.track_set(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_service.track_set.assert_not_called()

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    @patch("src.api.exercise_api.ExerciseService")
    def test_delete_exercise_set_unauthorized(
        self, mock_service_class, mock_get_workout, mock_get_relationship
    ):
        """Test that user cannot delete set in another athlete's exercise"""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service

        mock_exercise = MagicMock()
        mock_service.get_exercise.return_value = mock_exercise

        mock_workout = MagicMock()
        mock_workout.athlete_id = "other-athlete"
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"exercise_id": "ex123", "set_number": "1"},
            "requestContext": {"authorizer": {"claims": {"sub": "attacker-user"}}},
        }
        response = exercise_api.delete_exercise_set(event, {})
        self.assertEqual(response["statusCode"], 403)
        mock_service.delete_set.assert_not_called()


if __name__ == "__main__":
    unittest.main()
