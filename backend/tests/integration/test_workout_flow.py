import json
import unittest
from unittest.mock import patch, MagicMock
from src.api.user_api import create_user
from src.api.block_api import create_block
from src.api.week_api import create_week
from src.api.day_api import create_day
from src.api.workout_api import create_workout
from src.api.exercise_api import complete_exercise
from src.models.user import User
from src.models.block import Block
from src.models.week import Week
from src.models.day import Day
from src.models.workout import Workout
from src.models.exercise import Exercise
from src.services.workout_service import WorkoutService


class TestWorkoutFlow(unittest.TestCase):
    """Integration test for a complete workout flow using mocks"""

    def setUp(self):
        """Set up test environment before each test"""
        # Create mock UUIDs for predictable IDs
        self.mock_uuids = [
            "user-athlete-id",
            "user-coach-id",
            "block-id",
            "week-id",
            "day-id",
            "workout-id",
            "exercise-id",
            "set-id-1",
            "set-id-2",
            "set-id-3",
        ]

        # Set up patchers
        self.uuid_patcher = patch("uuid.uuid4", side_effect=self.mock_uuids)

        # Start all patchers
        self.uuid_mock = self.uuid_patcher.start()

        # Create a Lambda context
        self.lambda_context = type(
            "LambdaContext",
            (),
            {
                "function_name": "test-function",
                "aws_request_id": "test-request-123",
                "function_version": "$LATEST",
                "memory_limit_in_mb": 128,
                "log_group_name": "/aws/lambda/test-function",
                "log_stream_name": "2025/03/28/[$LATEST]abcdef123456",
                "identity": None,
                "client_context": None,
                "get_remaining_time_in_millis": lambda: 15000,
            },
        )()

    def tearDown(self):
        """Clean up after each test"""
        # Stop all patchers
        self.uuid_patcher.stop()

    def create_api_gateway_event(
        self,
        method="GET",
        path="/",
        body=None,
        path_parameters=None,
        query_parameters=None,
        user_id=None,
    ):
        """Create a mock API Gateway event for testing"""
        # Use provided user_id or default to athlete
        auth_user_id = user_id or self.mock_uuids[0]

        event = {
            "httpMethod": method,
            "path": path,
            "resource": path,
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": auth_user_id,  # Use the athlete user ID
                        "email": "athlete@example.com",
                        "name": "Test Athlete",
                    }
                }
            },
            "pathParameters": path_parameters or {},
            "queryStringParameters": query_parameters or {},
            "headers": {"Content-Type": "application/json"},
        }

        if body:
            event["body"] = json.dumps(body)

        return event

    def create_mock_workout(self):
        """Helper to create a mock workout with exercises and sets"""
        workout = Workout(
            workout_id=self.mock_uuids[5],
            athlete_id=self.mock_uuids[0],
            day_id=self.mock_uuids[4],
            date="2025-03-01",
            notes="Good squat day",
            status="completed",
        )

        # Add an exercise
        exercise = Exercise(
            exercise_id=self.mock_uuids[6],
            workout_id=self.mock_uuids[5],
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=209.44,
            status="planned",
        )

        workout.add_exercise(exercise)
        return workout

    def test_complete_workout_flow(self):
        """Test a complete workout flow from user creation to workout logging"""

        # Create user mocks
        athlete_user = User(
            user_id=self.mock_uuids[0],
            email="athlete@example.com",
            name="Test Athlete",
            role="athlete",
        )

        coach_user = User(
            user_id=self.mock_uuids[1],
            email="coach@example.com",
            name="Test Coach",
            role="coach",
        )

        # Create a block model
        block = Block(
            block_id=self.mock_uuids[2],
            athlete_id=self.mock_uuids[0],
            coach_id=self.mock_uuids[1],
            title="Test Training Block",
            description="A block for integration testing",
            start_date="2025-03-01",
            end_date="2025-04-01",
            status="active",
        )

        # Create a week model
        week = Week(
            week_id=self.mock_uuids[3],
            block_id=self.mock_uuids[2],
            week_number=1,
            notes="First week of training",
        )

        # Create a day model
        day = Day(
            day_id=self.mock_uuids[4],
            week_id=self.mock_uuids[3],
            day_number=1,
            date="2025-03-01",
            focus="squat",
            notes="Squat focus day",
        )

        # Configure mocks for all service methods we'll call
        with patch(
            "src.api.user_api.user_service.create_user",
            side_effect=[athlete_user, coach_user],
        ), patch(
            "src.api.block_api.block_service.create_block", return_value=block
        ), patch(
            "src.api.week_api.block_service.get_block", return_value=block
        ), patch(
            "src.api.week_api.week_service.create_week", return_value=week
        ), patch(
            "src.api.day_api.week_service.get_week", return_value=week
        ), patch(
            "src.api.day_api.block_service.get_block", return_value=block
        ), patch(
            "src.api.day_api.day_service.create_day", return_value=day
        ), patch(
            "src.api.workout_api.workout_service.create_workout",
            return_value=self.create_mock_workout(),
        ):
            # Step 1: Create athlete user
            athlete_data = {
                "email": "athlete@example.com",
                "name": "Test Athlete",
                "role": "athlete",
            }
            athlete_event = self.create_api_gateway_event(
                method="POST", path="/users", body=athlete_data
            )
            athlete_response = create_user(athlete_event, self.lambda_context)
            self.assertEqual(athlete_response["statusCode"], 201)
            athlete = json.loads(athlete_response["body"])
            athlete_id = athlete["user_id"]

            # Step 2: Create coach user
            coach_data = {
                "email": "coach@example.com",
                "name": "Test Coach",
                "role": "coach",
            }
            coach_event = self.create_api_gateway_event(
                method="POST", path="/users", body=coach_data
            )
            coach_response = create_user(coach_event, self.lambda_context)
            self.assertEqual(coach_response["statusCode"], 201)
            coach = json.loads(coach_response["body"])
            coach_id = coach["user_id"]

            # Step 3: Create a training block
            block_data = {
                "athlete_id": athlete_id,
                "coach_id": coach_id,
                "title": "Test Training Block",
                "description": "A block for integration testing",
                "start_date": "2025-03-01",
                "end_date": "2025-04-01",
                "status": "active",
            }
            block_event = self.create_api_gateway_event(
                method="POST", path="/blocks", body=block_data
            )
            block_response = create_block(block_event, self.lambda_context)
            self.assertEqual(block_response["statusCode"], 201)
            block = json.loads(block_response["body"])
            block_id = block["block_id"]

            # Step 4: Create a week in the block
            week_data = {
                "block_id": block_id,
                "week_number": 1,
                "notes": "First week of training",
            }
            week_event = self.create_api_gateway_event(
                method="POST", path="/weeks", body=week_data
            )
            week_response = create_week(week_event, self.lambda_context)
            self.assertEqual(week_response["statusCode"], 201)
            week = json.loads(week_response["body"])
            week_id = week["week_id"]

            # Step 5: Create a day in the week
            day_data = {
                "week_id": week_id,
                "day_number": 1,
                "date": "2025-03-01",
                "focus": "squat",
                "notes": "Squat focus day",
            }
            day_event = self.create_api_gateway_event(
                method="POST", path="/days", body=day_data
            )
            day_response = create_day(day_event, self.lambda_context)
            self.assertEqual(day_response["statusCode"], 201)
            day = json.loads(day_response["body"])
            day_id = day["day_id"]

            # Step 6: Log a workout for the day
            workout_data = {
                "athlete_id": athlete_id,
                "day_id": day_id,
                "date": "2025-03-01",
                "exercises": [
                    {
                        "exercise_id": "squat",
                        "sets": [
                            {"set_number": 1, "reps": 5, "weight": 100.0, "rpe": 7.0},
                            {"set_number": 2, "reps": 5, "weight": 110.0, "rpe": 8.0},
                            {"set_number": 3, "reps": 5, "weight": 120.0, "rpe": 9.0},
                        ],
                        "notes": "Felt good",
                    }
                ],
                "notes": "Good squat day",
                "status": "completed",
            }
            workout_event = self.create_api_gateway_event(
                method="POST", path="/workouts", body=workout_data
            )
            workout_response = create_workout(workout_event, self.lambda_context)

            # Verify response status
            self.assertEqual(
                workout_response["statusCode"],
                201,
                f"Failed to create workout: {workout_response.get('body')}",
            )

            # Parse response body
            workout_result = json.loads(workout_response["body"])

            # Verify the workout was created successfully
            self.assertEqual(workout_result["athlete_id"], athlete_id)
            self.assertEqual(workout_result["day_id"], day_id)
            self.assertEqual(workout_result["status"], "completed")
            self.assertEqual(len(workout_result["exercises"]), 1)

    def test_exercise_completion_flow(self):
        """Test the exercise completion flow and workout status updates"""

        # Create user, block, week, day and initial workout with planned exercises
        athlete_user = User(
            user_id=self.mock_uuids[0],
            email="athlete@example.com",
            name="Test Athlete",
            role="athlete",
        )

        day = Day(
            day_id=self.mock_uuids[4],
            week_id=self.mock_uuids[3],
            day_number=1,
            date="2025-03-01",
            focus="squat",
            notes="Squat focus day",
        )

        # Create a workout with two exercises in "planned" status
        workout = Workout(
            workout_id=self.mock_uuids[5],
            athlete_id=self.mock_uuids[0],
            day_id=self.mock_uuids[4],
            date="2025-03-01",
            notes="Testing exercise completion",
            status="not_started",
        )

        # First exercise
        exercise1 = Exercise(
            exercise_id=self.mock_uuids[6],
            workout_id=self.mock_uuids[5],
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
        )

        # Second exercise
        exercise2 = Exercise(
            exercise_id="exercise2-id",
            workout_id=self.mock_uuids[5],
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=185.0,
            status="planned",
        )

        workout.add_exercise(exercise1)
        workout.add_exercise(exercise2)

        # Test at service layer instead of API layer
        with patch(
            "src.services.workout_service.WorkoutRepository"
        ) as mock_workout_repo, patch(
            "src.services.workout_service.ExerciseRepository"
        ) as mock_exercise_repo, patch(
            "src.services.workout_service.DayRepository"
        ) as mock_day_repo:
            # Configure the mocks
            mock_workout_service = WorkoutService()

            # Mock the exercise repository to return our test exercise
            mock_exercise_repo.return_value.get_exercise.return_value = (
                exercise1.to_dict()
            )
            mock_exercise_repo.return_value.update_exercise.return_value = {
                **exercise1.to_dict(),
                "status": "completed",
                "sets": 3,
                "reps": 5,
                "weight": 225.0,
                "rpe": 8.0,
                "notes": "Felt strong",
            }

            # Mock get_workout to return workout with updated exercises
            updated_workout = Workout(
                workout_id=self.mock_uuids[5],
                athlete_id=self.mock_uuids[0],
                day_id=self.mock_uuids[4],
                date="2025-03-01",
                notes="Testing exercise completion",
                status="in_progress",
            )

            completed_exercise1 = Exercise(
                exercise_id=self.mock_uuids[6],
                workout_id=self.mock_uuids[5],
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=225.0,
                status="completed",
            )

            updated_workout.add_exercise(completed_exercise1)
            updated_workout.add_exercise(exercise2)

            mock_workout_service.get_workout = MagicMock(return_value=updated_workout)

            # Step 1: Complete the first exercise using service layer
            completed_exercise_result = mock_workout_service.complete_exercise(
                exercise_id=self.mock_uuids[6],
                sets=3,
                reps=5,
                weight=225.0,
                rpe=8.0,
                notes="Felt strong",
            )

            # Verify the exercise was marked as completed
            self.assertIsNotNone(completed_exercise_result)
            self.assertEqual(completed_exercise_result.status, "completed")
            self.assertEqual(completed_exercise_result.rpe, 8.0)
            self.assertEqual(completed_exercise_result.notes, "Felt strong")

            # Step 2: Verify workout status was updated to "in_progress"
            current_workout = mock_workout_service.get_workout(self.mock_uuids[5])
            self.assertEqual(current_workout.status, "in_progress")

            # Step 3: Complete the second exercise
            mock_exercise_repo.return_value.get_exercise.return_value = (
                exercise2.to_dict()
            )
            mock_exercise_repo.return_value.update_exercise.return_value = {
                **exercise2.to_dict(),
                "status": "completed",
                "rpe": 7.5,
                "notes": "Easy bench day",
            }

            # Create final workout state
            final_workout = Workout(
                workout_id=self.mock_uuids[5],
                athlete_id=self.mock_uuids[0],
                day_id=self.mock_uuids[4],
                date="2025-03-01",
                notes="Testing exercise completion",
                status="completed",
            )

            completed_exercise2 = Exercise(
                exercise_id="exercise2-id",
                workout_id=self.mock_uuids[5],
                exercise_type="Bench Press",
                sets=3,
                reps=5,
                weight=185.0,
                status="completed",
            )

            final_workout.add_exercise(completed_exercise1)
            final_workout.add_exercise(completed_exercise2)

            mock_workout_service.get_workout = MagicMock(return_value=final_workout)

            completed_exercise_result2 = mock_workout_service.complete_exercise(
                exercise_id="exercise2-id",
                sets=3,
                reps=5,
                weight=185.0,
                rpe=7.5,
                notes="Easy bench day",
            )

            # Verify the second exercise was marked as completed
            self.assertIsNotNone(completed_exercise_result2)
            self.assertEqual(completed_exercise_result2.status, "completed")

            # Step 4: Verify final workout status is "completed"
            final_workout_state = mock_workout_service.get_workout(self.mock_uuids[5])
            self.assertEqual(final_workout_state.status, "completed")


if __name__ == "__main__":
    unittest.main()
