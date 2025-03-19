import json
from unittest.mock import patch, MagicMock
from tests.base_test import BaseTest

# Import workout after the mocks are set up in BaseTest
with patch('boto3.resource'):
    from src.api import workout

class TestWorkoutAPI(BaseTest):
    """
    Test suite for the Workout API module
    """

    @patch('src.services.workout_service.WorkoutService.log_workout')
    def test_create_workout_success(self, mock_log_workout):
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
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "comp1",
                    "exercise_id": "ex1",
                    "actual_sets": 5,
                    "actual_reps": 5,
                    "actual_weight": 315.0,
                    "actual_rpe": 8.5
                }
            ]
        }
        mock_log_workout.return_value = mock_workout
        
        event = {
            "body": json.dumps({
                "athlete_id": "athlete456",
                "day_id": "day789",
                "date": "2025-03-15",
                "notes": "Good session",
                "status": "completed",
                "exercises": [
                    {
                        "exercise_id": "ex1",
                        "actual_sets": 5,
                        "actual_reps": 5,
                        "actual_weight": 315.0,
                        "actual_rpe": 8.5
                    }
                ]
            })
        }
        context = {}
        
        # Call API
        response = workout.create_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 201)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["athlete_id"], "athlete456")
        self.assertEqual(response_body["day_id"], "day789")
        self.assertEqual(len(response_body["exercises"]), 1)
        self.assertEqual(response_body["exercises"][0]["actual_sets"], 5)
        self.assertEqual(response_body["status"], "completed")
        mock_log_workout.assert_called_once_with(
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            completed_exercises=[
                {
                    "exercise_id": "ex1",
                    "actual_sets": 5,
                    "actual_reps": 5,
                    "actual_weight": 315.0,
                    "actual_rpe": 8.5
                }
            ],
            notes="Good session",
            status="completed"
        )
    
    @patch('src.services.workout_service.WorkoutService.log_workout')
    def test_create_workout_missing_fields(self, mock_log_workout):
        """
        Test workout creation with missing required fields
        """

        # Setup
        event = {
            "body": json.dumps({
                "athlete_id": "athlete456",
                # Missing day_id
                "date": "2025-03-15",
                "exercises": []
            })
        }
        context = {}
        
        # Call API
        response = workout.create_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Missing required fields", response_body["error"])
        mock_log_workout.assert_not_called()
    
    @patch('src.services.workout_service.WorkoutService.log_workout')
    def test_create_workout_with_validation_error(self, mock_log_workout):
        """
        Test workout creation with service-level validation error
        """
        
        # Setup - service throws a ValueError for validation failure
        mock_log_workout.side_effect = ValueError("Invalid status value")
        
        event = {
            "body": json.dumps({
                "athlete_id": "athlete456",
                "day_id": "day789",
                "date": "2025-03-15",
                "status": "invalid_status",  # Invalid status that will cause ValueError
                "exercises": [
                    {
                        "exercise_id": "ex1",
                        "actual_sets": 5,
                        "actual_reps": 5,
                        "actual_weight": 315.0
                    }
                ]
            })
        }
        context = {}
        
        # Call API
        response = workout.create_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertIn("Invalid status value", response_body["error"])
    
    @patch('src.services.workout_service.WorkoutService.get_workout')
    def test_get_workout_success(self, mock_get_workout):
        """
        Test successful workout retrieval
        """
        
        # Setup
        mock_workout = MagicMock()
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "status": "completed",
            "exercises": [
                {
                    "completed_id": "comp1",
                    "exercise_id": "ex1",
                    "actual_sets": 5,
                    "actual_reps": 5,
                    "actual_weight": 315.0
                }
            ]
        }
        mock_get_workout.return_value = mock_workout
        
        event = {
            "pathParameters": {
                "workout_id": "workout123"
            }
        }
        context = {}
        
        # Call API
        response = workout.get_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["athlete_id"], "athlete456")
        self.assertEqual(len(response_body["exercises"]), 1)
        mock_get_workout.assert_called_once_with("workout123")
    
    @patch('src.services.workout_service.WorkoutService.get_workout')
    def test_get_workout_not_found(self, mock_get_workout):
        """
        Test workout retrieval when workout not found
        """

        # Setup
        mock_get_workout.return_value = None
        
        event = {
            "pathParameters": {
                "workout_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = workout.get_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Workout not found", response_body["error"])
    
    @patch('src.repositories.workout_repository.WorkoutRepository.get_workouts_by_athlete')
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
                "date": "2025-03-15"
            },
            {
                "workout_id": "workout2",
                "athlete_id": "athlete456",
                "day_id": "day2",
                "date": "2025-03-16"
            }
        ]
        mock_get_workouts.return_value = mock_workouts
        
        event = {
            "pathParameters": {
                "athlete_id": "athlete456"
            }
        }
        context = {}
        
        # Call API
        response = workout.get_workouts_by_athlete(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0]["workout_id"], "workout1")
        self.assertEqual(response_body[1]["workout_id"], "workout2")
        mock_get_workouts.assert_called_once_with("athlete456")
    
    @patch('src.services.workout_service.WorkoutService.update_workout')
    def test_update_workout_success(self, mock_update_workout):
        """
        Test successful workout update
        """

        # Setup
        mock_workout = MagicMock()
        mock_workout.to_dict.return_value = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-03-15",
            "notes": "Updated notes",
            "status": "partial",  # Updated status
            "exercises": [
                {
                    "completed_id": "comp1",
                    "exercise_id": "ex1",
                    "actual_sets": 4,  # Updated sets
                    "actual_reps": 5,
                    "actual_weight": 315.0
                }
            ]
        }
        mock_update_workout.return_value = mock_workout
        
        event = {
            "pathParameters": {
                "workout_id": "workout123"
            },
            "body": json.dumps({
                "notes": "Updated notes",
                "status": "partial",
                "exercises": [
                    {
                        "completed_id": "comp1",
                        "exercise_id": "ex1",
                        "actual_sets": 4,
                        "actual_reps": 5,
                        "actual_weight": 315.0
                    }
                ]
            })
        }
        context = {}
        
        # Call API
        response = workout.update_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["workout_id"], "workout123")
        self.assertEqual(response_body["notes"], "Updated notes")
        self.assertEqual(response_body["status"], "partial")
        self.assertEqual(response_body["exercises"][0]["actual_sets"], 4)
        mock_update_workout.assert_called_once()
    
    @patch('src.services.workout_service.WorkoutService.update_workout')
    def test_update_workout_not_found(self, mock_update_workout):
        """
        Test workout update when workout not found
        """

        # Setup
        mock_update_workout.return_value = None
        
        event = {
            "pathParameters": {
                "workout_id": "nonexistent"
            },
            "body": json.dumps({
                "notes": "Updated notes"
            })
        }
        context = {}
        
        # Call API
        response = workout.update_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Workout not found", response_body["error"])
    
    @patch('src.services.workout_service.WorkoutService.delete_workout')
    def test_delete_workout_success(self, mock_delete_workout):
        """
        Test successful workout deletion
        """

        # Setup
        mock_delete_workout.return_value = True
        
        event = {
            "pathParameters": {
                "workout_id": "workout123"
            }
        }
        context = {}
        
        # Call API
        response = workout.delete_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 204)
        mock_delete_workout.assert_called_once_with("workout123")
    
    @patch('src.services.workout_service.WorkoutService.delete_workout')
    def test_delete_workout_not_found(self, mock_delete_workout):
        """
        Test workout deletion when workout not found
        """
        
        # Setup
        mock_delete_workout.return_value = False
        
        event = {
            "pathParameters": {
                "workout_id": "nonexistent"
            }
        }
        context = {}
        
        # Call API
        response = workout.delete_workout(event, context)
        
        # Assert
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertIn("Workout not found", response_body["error"])

if __name__ == "__main__":
    unittest.main()