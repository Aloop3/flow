import json
import unittest
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest
from src.models.day import Day
from src.models.week import Week
from src.models.block import Block
from src.models.workout import Workout
from src.models.relationship import Relationship


# Import workout after the mocks are set up in BaseTest
def mock_with_middleware(middlewares):
    """Mock decorator that returns the original function unchanged"""
    def decorator(func):
        return func  # Return function without middleware
    return decorator

with patch("src.middleware.middleware.with_middleware", side_effect=mock_with_middleware):
    with patch("boto3.resource"):
        from src.api import workout_api



class TestWorkoutAPI(BaseTest):
    """
    Test suite for the Workout API module
    """

    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_workout_success(self, mock_create_workout):
        """
        Test successful workout creation
        """

        # Setup
        mock_workout = MagicMock()
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Good session",
            "status": "not_started",
            "exercises": [
                {
                    "exercise_id": "ex1",
                    "sets": 5,
                    "reps": 5,
                    "weight": 315.0,
                    "rpe": 8.5,
                }
            ],
        }
        mock_create_workout.return_value = mock_workout

        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                    "notes": "Good session",
                    "status": "not_started",
                    "exercises": [
                        {
                            "exercise_id": "ex1",
                            "sets": 5,
                            "reps": 5,
                            "weight": 315.0,
                            "rpe": 8.5,
                        }
                    ],
                }
            ),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.create_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["athlete_id"], "athlete456")
        self.assertEqual(response_body["day_id"], "day789")
        self.assertEqual(len(response_body["exercises"]), 1)
        self.assertEqual(response_body["exercises"][0]["sets"], 5)
        self.assertEqual(response_body["status"], "not_started")
        mock_create_workout.assert_called_once_with(
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            exercises=[
                {
                    "exercise_id": "ex1",
                    "sets": 5,
                    "reps": 5,
                    "weight": 315.0,
                    "rpe": 8.5,
                }
            ],
            notes="Good session",
            status="not_started",
        )

    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_workout_missing_fields(self, mock_create_workout):
        """
        Test workout creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    # Missing day_id
                    "date": "2025-03-15",
                    "exercises": [],
                }
            ),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.create_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_create_workout.assert_not_called()

    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_workout_with_validation_error(self, mock_create_workout):
        """
        Test workout creation with service-level validation error
        """

        # Setup - service throws a ValueError for validation failure
        mock_create_workout.side_effect = ValueError("Invalid status value")

        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                    "status": "invalid_status",  # Invalid status that will cause ValueError
                    "exercises": [
                        {
                            "exercise_id": "ex1",
                            "sets": 5,
                            "reps": 5,
                            "weight": 315.0,
                        }
                    ],
                }
            ),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.create_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid status value", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_workout_invalid_json(self, mock_create_workout):
        """
        Test workout creation with invalid JSON
        """
        event = {
            "body": "invalid json",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.create_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Expecting value", response_body["error"])
        mock_create_workout.assert_not_called()

    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_workout_general_exception(self, mock_create_workout):
        """
        Test workout creation when a general exception occurs
        """
        # Setup - simulate a DynamoDB error
        mock_create_workout.side_effect = Exception("DynamoDB error occurred")

        event = {
            "body": json.dumps(
                {
                    "athlete_id": "athlete456",
                    "day_id": "day789",
                    "date": "2025-03-15",
                    "exercises": [],
                }
            ),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.create_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "DynamoDB error occurred")
        mock_create_workout.assert_called_once()

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_get_workout_success(self, mock_get_workout):
        """
        Test successful workout retrieval
        """

        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "completed",
            "exercises": [
                {
                    "exercise_id": "ex1",
                    "sets": 5,
                    "reps": 5,
                    "weight": 315.0,
                }
            ],
        }
        mock_get_workout.return_value = mock_workout

        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.get_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["athlete_id"], "athlete456")
        self.assertEqual(len(response_body["exercises"]), 1)
        self.assertEqual(mock_get_workout.call_count, 2)
        mock_get_workout.assert_called_with("workout123")

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_get_workout_not_found(self, mock_get_workout):
        """
        Test workout retrieval when workout not found
        """

        # Setup
        mock_get_workout.return_value = None

        event = {
            "pathParameters": {"workout_id": "nonexistent"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.get_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Workout not found", response_body["error"])

    @patch(
        "src.repositories.workout_repository.WorkoutRepository.get_workouts_by_athlete"
    )
    def test_get_workouts_by_athlete(self, mock_get_workouts):
        """
        Test retrieving workouts by athlete
        """

        # Setup
        mock_workouts = [
            {
                "workout_id": "workout1",
                "athlete_id": "athlete456",
                "day_id": "day1",
                "date": "2025-03-15",
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete456",
                "day_id": "day2",
                "date": "2025-03-16",
            },
        ]
        mock_get_workouts.return_value = mock_workouts

        # Override the boto3 resource for this specific test
        with patch("boto3.resource", return_value=self.mock_dynamodb):
            event = {
                "pathParameters": {"athlete_id": "athlete456"},
                "requestContext": {
                    "authorizer": {
                        "claims": {
                            "sub": "athlete456"
                        }
                    }
                }
            }
            context = {}

            # Call API
            response = workout_api.get_workouts_by_athlete(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 200)
            response_body = json.loads(response["body"])
            self.assertEqual(len(response_body), 2)
            self.assertEqual(response_body[0]["workout_id"], "workout1")
            self.assertEqual(response_body[1]["workout_id"], "workout2")
            mock_get_workouts.assert_called_once_with("athlete456")

    @patch(
        "src.repositories.workout_repository.WorkoutRepository.get_workouts_by_athlete"
    )
    def test_get_workouts_by_athlete_exception(self, mock_get_workouts):
        """
        Test exception handling in get_workouts_by_athlete
        """
        # Setup
        mock_get_workouts.side_effect = Exception("Test exception")

        # Override the boto3 resource for this specific test
        with patch("boto3.resource", return_value=self.mock_dynamodb):
            event = {
                "pathParameters": {"athlete_id": "athlete456"},
                "requestContext": {
                    "authorizer": {
                        "claims": {
                            "sub": "athlete456"
                        }
                    }
                }
            }
            context = {}

            # Call API
            response = workout_api.get_workouts_by_athlete(event, context)

            # Assert
            self.assertEqual(response["statusCode"], 500)
            response_body = json.loads(response["body"])
            self.assertEqual(response_body["error"], "Test exception")

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_get_workout_exception(self, mock_get_workout):
        """
        Test exception handling in get_workout
        """
        # Setup
        mock_get_workout.side_effect = Exception("Test exception")

        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.get_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Test exception")

    @patch("src.api.workout_api.convert_exercise_weights_for_display")
    @patch("src.api.workout_api.get_user_weight_preference")
    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    def test_get_workout_by_day_success(
        self, mock_get_workout, mock_get_preference, mock_convert_weights
    ):
        """
        Test successful workout retrieval by day with weight conversion
        """
        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"  # Required for middleware validation
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "exercises": [
                {
                    "exercise_id": "ex1",
                    "exercise_type": "Bench Press",
                    "weight": 100.0,
                    "sets": 3,
                    "reps": 10,
                }
            ],
        }
        mock_get_workout.return_value = mock_workout

        # Mock user preference
        mock_get_preference.return_value = "auto"

        # Mock weight conversion (returns exercise unchanged for simplicity)
        mock_convert_weights.side_effect = lambda exercise, pref, ex_type, ex_cat: {
            **exercise,
            "display_unit": "kg",
        }

        # Add required requestContext structure
        event = {
            "pathParameters": {"athlete_id": "athlete456", "day_id": "day789"},
            "requestContext": {"authorizer": {"claims": {"sub": "test-user-id"}}},
        }
        context = {}

        # Call API
        response = workout_api.get_workout_by_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")

        # Verify new functions were called
        mock_get_preference.assert_called_once_with("test-user-id")
        self.assertTrue(mock_convert_weights.called)
        mock_get_workout.assert_called_once_with("athlete456", "day789")

    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    def test_get_workout_by_day_not_found(self, mock_get_workout):
        """
        Test workout by day not found returns 404 with proper error message
        """
        # Setup
        mock_get_workout.return_value = None

        event = {
            "pathParameters": {"athlete_id": "athlete456", "day_id": "day789"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Execute
        response = workout_api.get_workout_by_day(event, context)

        # Verify
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Workout not found")

        # Verify service was called with correct parameters
        mock_get_workout.assert_called_once_with("athlete456", "day789")

    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    def test_get_workout_by_day_exception(self, mock_get_workout):
        """Test exception handling when getting workout by day"""
        # Setup
        mock_get_workout.side_effect = Exception("Service error")

        event = {
            "pathParameters": {"athlete_id": "athlete456", "day_id": "day789"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.get_workout_by_day(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Service error")
        mock_get_workout.assert_called_once_with("athlete456", "day789")

    @patch("src.services.workout_service.WorkoutService.update_workout")
    def test_update_workout_success(self, mock_update_workout):
        """
        Test successful workout update
        """

        # Setup
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"  # Required for middleware validation
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Updated notes",
            "status": "in_progress",  # Updated status
            "exercises": [
                {
                    "exercise_id": "ex1",
                    "sets": 4,  # Updated sets
                    "reps": 5,
                    "weight": 315.0,
                }
            ],
        }
        mock_update_workout.return_value = mock_workout

        event = {
            "pathParameters": {"workout_id": "workout123"},
            "body": json.dumps(
                {
                    "notes": "Updated notes",
                    "status": "in_progress",
                    "exercises": [
                        {
                            "exercise_id": "ex1",
                            "sets": 4,
                            "reps": 5,
                            "weight": 315.0,
                        }
                    ],
                }
            ),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.update_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["notes"], "Updated notes")
        self.assertEqual(response_body["status"], "in_progress")
        self.assertEqual(response_body["exercises"][0]["sets"], 4)
        mock_update_workout.assert_called_once()

    @patch("src.services.workout_service.WorkoutService.update_workout")
    def test_update_workout_not_found(self, mock_update_workout):
        """
        Test workout update when workout not found
        """

        # Setup
        mock_update_workout.return_value = None

        event = {
            "pathParameters": {"workout_id": "nonexistent"},
            "body": json.dumps({"notes": "Updated notes"}),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.update_workout(event, context)

        # Assert
        # Middleware returns 400 when workout not found during authorization
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Workout not found", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.update_workout")
    def test_update_workout_exception(self, mock_update_workout):
        """Test exception handling when updating a workout"""
        # Setup
        mock_update_workout.side_effect = Exception("Update error")

        event = {
            "pathParameters": {"workout_id": "workout123"},
            "body": json.dumps({"notes": "Updated notes"}),
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.update_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Update error")
        mock_update_workout.assert_called_once()

    @patch("src.services.workout_service.WorkoutService.delete_workout")
    def test_delete_workout_success(self, mock_delete_workout):
        """
        Test successful workout deletion
        """

        # Setup
        mock_delete_workout.return_value = True

        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.delete_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_workout.assert_called_once_with("workout123")

    @patch("src.services.workout_service.WorkoutService.delete_workout")
    def test_delete_workout_not_found(self, mock_delete_workout):
        """
        Test workout deletion when workout not found
        """

        # Setup
        mock_delete_workout.return_value = False

        event = {
            "pathParameters": {"workout_id": "nonexistent"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.delete_workout(event, context)

        # Assert
        # Middleware returns 400 when workout not found during authorization
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Workout not found", response_body["error"])

    @patch("src.services.workout_service.WorkoutService.delete_workout")
    def test_delete_workout_exception(self, mock_delete_workout):
        """Test exception handling when deleting a workout"""
        # Setup
        mock_delete_workout.side_effect = Exception("Delete error")

        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "athlete456"
                    }
                }
            }
        }
        context = {}

        # Call API
        response = workout_api.delete_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Delete error")
        mock_delete_workout.assert_called_once_with("workout123")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_day_workout_success(
        self,
        mock_create_workout,
        mock_get_day,
        mock_get_week,
        mock_get_block,
        mock_get_relationship,
    ):
        """
        Test successful creation of a workout for a specific day
        """
        # Setup mock day
        mock_day = Day(
            day_id="day789",
            week_id="week123",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="",
        )
        mock_get_day.return_value = mock_day

        # Setup mock week
        mock_week = Week(
            week_id="week123", block_id="block456", week_number=1, notes=""
        )
        mock_get_week.return_value = mock_week

        # Setup mock block
        mock_block = Block(
            block_id="block456",
            athlete_id="athlete456",
            coach_id=None,
            title="Test Block",
            description="Test",
            start_date="2025-03-01",
            end_date="2025-03-31",
            status="active",
        )
        mock_get_block.return_value = mock_block

        # No need to mock relationship since user is the athlete
        mock_get_relationship.return_value = None

        mock_workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            status="not_started",
            notes="",
        )
        mock_workout.exercises = []
        mock_create_workout.return_value = mock_workout

        # Prepare test event
        event = {
            "pathParameters": {"day_id": "day789"},
            "body": json.dumps(
                {
                    "exercises": [
                        {
                            "exerciseType": "Bench Press",
                            "sets": 3,
                            "reps": 10,
                            "weight": 225.0,
                            "notes": "",
                        }
                    ]
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.create_day_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["athlete_id"], "athlete456")

    @patch("src.services.day_service.DayService.get_day")
    def test_create_day_workout_day_not_found(self, mock_get_day):
        """
        Test workout creation when the day doesn't exist
        """
        # Setup - day not found
        mock_get_day.return_value = None

        event = {
            "pathParameters": {"day_id": "nonexistent"},
            "body": json.dumps(
                {
                    "exercises": [
                        {
                            "exerciseType": "Bench Press",
                            "sets": 3,
                            "reps": 10,
                            "weight": 225.0,
                        }
                    ]
                }
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.create_day_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Day not found")
        mock_get_day.assert_called_once_with("nonexistent")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    def test_create_day_workout_no_exercises(
        self, mock_get_day, mock_get_week, mock_get_block, mock_get_relationship
    ):
        """
        Test workout creation with no exercises
        """
        # Setup mock day
        mock_day = Day(
            day_id="day789",
            week_id="week123",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="",
        )
        mock_get_day.return_value = mock_day

        # Setup mock week
        mock_week = Week(
            week_id="week123", block_id="block456", week_number=1, notes=""
        )
        mock_get_week.return_value = mock_week

        # Setup mock block
        mock_block = Block(
            block_id="block456",
            athlete_id="athlete456",
            coach_id=None,
            title="Test Block",
            description="Test",
            start_date="2025-03-01",
            end_date="2025-03-31",
            status="active",
        )
        mock_get_block.return_value = mock_block

        # No need to mock relationship since user is the athlete
        mock_get_relationship.return_value = None

        event = {
            "pathParameters": {"day_id": "day789"},
            "body": json.dumps({"exercises": []}),  # Empty exercises array
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.create_day_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("No exercises provided", response["body"])

    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_copy_workout_success(
        self, mock_create_workout, mock_get_day, mock_get_workout
    ):
        """
        Test successful workout copying from one day to another
        """
        # Setup mocks
        # Source workout with exercises
        mock_source_workout = MagicMock()
        mock_source_workout.exercises = [
            MagicMock(
                exercise_id="ex1",
                exercise_type="Bench Press",
                sets=3,
                reps=10,
                weight=225.0,
                notes="Test notes",
            ),
            MagicMock(
                exercise_id="ex2",
                exercise_type="Squat",
                sets=4,
                reps=8,
                weight=315.0,
                notes="",
            ),
        ]
        mock_get_workout.side_effect = [
            mock_source_workout,
            None,
        ]  # First return source workout, then None for target

        # Mock day
        mock_day = MagicMock()
        mock_day.date = "2025-03-20"
        mock_get_day.return_value = mock_day

        # Mock new workout
        mock_new_workout = MagicMock()
        mock_new_workout.to_dict.return_value = {
            "workout_id": "new-workout-123",
            "athlete_id": "athlete456",
            "day_id": "target-day-789",
            "date": "2025-03-20",
            "status": "not_started",
        }
        mock_create_workout.return_value = mock_new_workout

        # Prepare test event
        event = {
            "body": json.dumps(
                {"source_day_id": "source-day-123", "target_day_id": "target-day-789"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.copy_workout(event, context)

        # Assert response
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "new-workout-123")
        self.assertEqual(response_body["day_id"], "target-day-789")

        # Verify service calls
        mock_get_workout.assert_any_call("athlete456", "source-day-123")
        mock_get_workout.assert_any_call("athlete456", "target-day-789")
        mock_get_day.assert_called_once_with("target-day-789")

        # Verify that create_workout was called with transformed exercises
        mock_create_workout.assert_called_once()
        call_args = mock_create_workout.call_args[1]
        self.assertEqual(call_args["athlete_id"], "athlete456")
        self.assertEqual(call_args["day_id"], "target-day-789")
        self.assertEqual(call_args["date"], "2025-03-20")
        self.assertEqual(call_args["status"], "not_started")

        # Check that we properly transformed the exercises
        exercises = call_args["exercises"]
        self.assertEqual(len(exercises), 2)
        self.assertEqual(exercises[0]["exercise_id"], "ex1")
        self.assertEqual(exercises[0]["exercise_type"], "Bench Press")
        self.assertEqual(exercises[1]["exercise_id"], "ex2")
        self.assertEqual(exercises[1]["sets"], 4)

    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    def test_copy_workout_source_not_found(self, mock_get_workout):
        """
        Test copying when source workout doesn't exist
        """
        # Setup - source workout not found
        mock_get_workout.return_value = None

        event = {
            "body": json.dumps(
                {"source_day_id": "source-day-123", "target_day_id": "target-day-789"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.copy_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Source workout not found")
        mock_get_workout.assert_called_once_with("athlete456", "source-day-123")

    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    @patch("src.services.day_service.DayService.get_day")
    def test_copy_workout_target_not_found(self, mock_get_day, mock_get_workout):
        """
        Test copying when target day doesn't exist
        """
        # Setup - source workout exists but target day doesn't
        mock_source_workout = MagicMock()
        mock_get_workout.return_value = mock_source_workout
        mock_get_day.return_value = None

        event = {
            "body": json.dumps(
                {"source_day_id": "source-day-123", "target_day_id": "target-day-789"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.copy_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Target day not found")
        mock_get_workout.assert_called_once_with("athlete456", "source-day-123")
        mock_get_day.assert_called_once_with("target-day-789")

    @patch("src.services.workout_service.WorkoutService.get_workout_by_day")
    @patch("src.services.day_service.DayService.get_day")
    def test_copy_workout_target_has_workout(self, mock_get_day, mock_get_workout):
        """
        Test copying when target day already has a workout
        """
        # Setup - both source and target workouts exist
        mock_source_workout = MagicMock()
        mock_target_workout = MagicMock()
        mock_get_workout.side_effect = [mock_source_workout, mock_target_workout]
        mock_get_day.return_value = MagicMock()

        event = {
            "body": json.dumps(
                {"source_day_id": "source-day-123", "target_day_id": "target-day-789"}
            ),
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.copy_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 409)
        response_body = json.loads(response["body"])
        self.assertIn("Target day already has a workout", response_body["error"])

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.block_service.BlockService.get_block")
    @patch("src.services.week_service.WeekService.get_week")
    @patch("src.services.day_service.DayService.get_day")
    @patch("src.services.workout_service.WorkoutService.create_workout")
    def test_create_day_workout_as_coach(
        self,
        mock_create_workout,
        mock_get_day,
        mock_get_week,
        mock_get_block,
        mock_get_relationship,
    ):
        """
        Test coach creating a workout for their athlete
        """
        # Setup mock day
        mock_day = Day(
            day_id="day789",
            week_id="week123",
            day_number=1,
            date="2025-03-15",
            focus="squat",
            notes="",
        )
        mock_get_day.return_value = mock_day

        # Setup mock week
        mock_week = Week(
            week_id="week123", block_id="block456", week_number=1, notes=""
        )
        mock_get_week.return_value = mock_week

        # Setup mock block (owned by athlete, created by coach)
        mock_block = Block(
            block_id="block456",
            athlete_id="athlete456",
            coach_id="coach789",
            title="Test Block",
            description="Test",
            start_date="2025-03-01",
            end_date="2025-03-31",
            status="active",
        )
        mock_get_block.return_value = mock_block

        # Mock active relationship between coach and athlete
        mock_relationship = Relationship(
            relationship_id="rel123",
            coach_id="coach789",
            athlete_id="athlete456",
            status="active",
            created_at="2025-01-01",
        )
        mock_get_relationship.return_value = mock_relationship

        mock_workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",  # Should be athlete, not coach
            day_id="day789",
            date="2025-03-15",
            status="not_started",
            notes="",
        )
        mock_workout.exercises = []
        mock_create_workout.return_value = mock_workout

        # Prepare test event from coach
        event = {
            "pathParameters": {"day_id": "day789"},
            "body": json.dumps(
                {
                    "exercises": [
                        {
                            "exerciseType": "Bench Press",
                            "sets": 3,
                            "reps": 10,
                            "weight": 225.0,
                            "notes": "",
                        }
                    ]
                }
            ),
            "requestContext": {
                "authorizer": {"claims": {"sub": "coach789"}}
            },  # Coach is creating
        }
        context = {}

        # Call API
        response = workout_api.create_day_workout(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["athlete_id"], "athlete456"
        )  # Should be athlete, not coach

        # Verify create_workout was called with athlete_id, not coach_id
        mock_create_workout.assert_called_once()
        call_args = mock_create_workout.call_args[1]
        self.assertEqual(call_args["athlete_id"], "athlete456")

    @patch("src.services.workout_service.WorkoutService.start_workout_session")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_start_workout_session_success(self, mock_get_workout, mock_start_session):
        """
        Test successful workout timing session start
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": "2025-06-24T14:30:00.123456",
            "finish_time": None,
            "exercises": [],
        }

        # Setup mocks
        mock_get_workout.return_value = mock_workout
        mock_start_session.return_value = mock_workout

        # Setup event - athlete starting their own workout
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.start_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["status"], "in_progress")
        self.assertEqual(response_body["start_time"], "2025-06-24T14:30:00.123456")
        self.assertIsNone(response_body["finish_time"])

        # Verify service calls (middleware calls get_workout for auth, then API calls it)
        self.assertEqual(mock_get_workout.call_count, 2)
        mock_get_workout.assert_called_with("workout123")
        mock_start_session.assert_called_once_with("workout123")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.start_workout_session")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_start_workout_session_coach_success(
        self, mock_get_workout, mock_start_session, mock_get_relationship
    ):
        """
        Test successful workout timing session start by coach
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": "2025-06-24T14:30:00.123456",
            "finish_time": None,
            "exercises": [],
        }

        # Setup mock relationship
        mock_relationship = MagicMock()
        mock_relationship.status = "active"

        # Setup mocks
        mock_get_workout.return_value = mock_workout
        mock_start_session.return_value = mock_workout
        mock_get_relationship.return_value = mock_relationship

        # Setup event - coach starting athlete's workout
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {
                "authorizer": {
                    "claims": {"sub": "coach789"}  # Different from athlete_id
                }
            },
        }
        context = {}

        # Call API
        response = workout_api.start_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["status"], "in_progress")

        # Verify service calls (middleware calls get_workout for auth, then API calls it)
        self.assertEqual(mock_get_workout.call_count, 2)
        mock_get_workout.assert_called_with("workout123")
        mock_get_relationship.assert_called_once_with(
            coach_id="coach789", athlete_id="athlete456"
        )
        mock_start_session.assert_called_once_with("workout123")

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_start_workout_session_workout_not_found(self, mock_get_workout):
        """
        Test starting workout session for non-existent workout
        """
        # Setup mock to return None
        mock_get_workout.return_value = None

        # Setup event
        event = {
            "pathParameters": {"workout_id": "nonexistent"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.start_workout_session(event, context)

        # Assert
        # Middleware returns 400 when workout not found during authorization
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Workout not found")

        # Verify service call (middleware calls get_workout for auth check)
        mock_get_workout.assert_called_once_with("nonexistent")

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_start_workout_session_unauthorized(
        self, mock_get_workout, mock_get_relationship
    ):
        """
        Test starting workout session without permission
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"

        # Setup mocks - no active relationship
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        # Setup event - unauthorized user
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "unauthorized789"}}},
        }
        context = {}

        # Call API
        response = workout_api.start_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["error"], "Unauthorized to start timing for this workout"
        )

        # Verify service calls (middleware calls get_workout for auth check)
        mock_get_workout.assert_called_once_with("workout123")
        mock_get_relationship.assert_called_once_with(
            coach_id="unauthorized789", athlete_id="athlete456"
        )

    @patch("src.services.workout_service.WorkoutService.start_workout_session")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_start_workout_session_service_failure(
        self, mock_get_workout, mock_start_session
    ):
        """
        Test starting workout session when service fails
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"

        # Setup mocks - service returns None (failure)
        mock_get_workout.return_value = mock_workout
        mock_start_session.return_value = None

        # Setup event
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.start_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Failed to start workout session")

    @patch("src.services.workout_service.WorkoutService.finish_workout_session")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_finish_workout_session_success(
        self, mock_get_workout, mock_finish_session
    ):
        """
        Test successful workout timing session finish
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "in_progress",
            "start_time": "2025-06-24T14:30:00.123456",
            "finish_time": "2025-06-24T15:45:00.789012",
            "exercises": [],
        }

        # Setup mocks
        mock_get_workout.return_value = mock_workout
        mock_finish_session.return_value = mock_workout

        # Setup event
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.finish_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["start_time"], "2025-06-24T14:30:00.123456")
        self.assertEqual(response_body["finish_time"], "2025-06-24T15:45:00.789012")

        # Verify service calls (middleware calls get_workout for auth, then API calls it)
        self.assertEqual(mock_get_workout.call_count, 2)
        mock_get_workout.assert_called_with("workout123")
        mock_finish_session.assert_called_once_with("workout123")

    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_finish_workout_session_workout_not_found(self, mock_get_workout):
        """
        Test finishing workout session for non-existent workout
        """
        # Setup mock to return None
        mock_get_workout.return_value = None

        # Setup event
        event = {
            "pathParameters": {"workout_id": "nonexistent"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.finish_workout_session(event, context)

        # Assert
        # Middleware returns 400 when workout not found during authorization
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Workout not found")

    @patch("src.services.workout_service.WorkoutService.finish_workout_session")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_finish_workout_session_not_started(
        self, mock_get_workout, mock_finish_session
    ):
        """
        Test finishing workout session that was never started
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"

        # Setup mocks - service returns None (cannot finish)
        mock_get_workout.return_value = mock_workout
        mock_finish_session.return_value = None

        # Setup event
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.finish_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["error"],
            "Cannot finish workout session - session not started or already finished",
        )

    @patch(
        "src.services.relationship_service.RelationshipService.get_active_relationship"
    )
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_finish_workout_session_unauthorized(
        self, mock_get_workout, mock_get_relationship
    ):
        """
        Test finishing workout session without permission
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"

        # Setup mocks - no active relationship
        mock_get_workout.return_value = mock_workout
        mock_get_relationship.return_value = None

        # Setup event - unauthorized user
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "unauthorized789"}}},
        }
        context = {}

        # Call API
        response = workout_api.finish_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertEqual(
            response_body["error"], "Unauthorized to finish timing for this workout"
        )

    @patch("src.services.workout_service.WorkoutService.start_workout_session")
    @patch("src.services.workout_service.WorkoutService.get_workout")
    def test_start_workout_session_general_exception(
        self, mock_get_workout, mock_start_session
    ):
        """
        Test starting workout session when general exception occurs
        """
        # Setup mock workout
        mock_workout = MagicMock()
        mock_workout.athlete_id = "athlete456"

        # Setup mocks - service throws exception
        mock_get_workout.return_value = mock_workout
        mock_start_session.side_effect = Exception("Database connection error")

        # Setup event
        event = {
            "pathParameters": {"workout_id": "workout123"},
            "requestContext": {"authorizer": {"claims": {"sub": "athlete456"}}},
        }
        context = {}

        # Call API
        response = workout_api.start_workout_session(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["error"], "Database connection error")


if __name__ == "__main__":
    unittest.main()
