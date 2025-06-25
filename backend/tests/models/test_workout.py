import unittest
from decimal import Decimal
from unittest.mock import patch
from src.models.workout import Workout
from src.models.exercise import Exercise
import datetime as dt


class TestWorkoutModel(unittest.TestCase):
    """
    Test suite for Workout model
    """

    def test_workout_initialization(self):
        """
        Test Workout model initialization with all attributes
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12",
            notes="Solid session",
            status="completed",
        )

        self.assertEqual(workout.workout_id, "workout123")
        self.assertEqual(workout.athlete_id, "athlete456")
        self.assertEqual(workout.day_id, "day789")
        self.assertEqual(workout.date, "2025-03-12")
        self.assertEqual(workout.notes, "Solid session")
        self.assertEqual(workout.status, "completed")
        self.assertEqual(workout.exercises, [])  # Empty list by default

    def test_workout_initialization_without_optional_attributes(self):
        """
        Test Workout model initialization without optional attributes
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12",
        )

        self.assertEqual(workout.workout_id, "workout123")
        self.assertEqual(workout.athlete_id, "athlete456")
        self.assertEqual(workout.day_id, "day789")
        self.assertEqual(workout.date, "2025-03-12")
        self.assertIsNone(workout.notes)
        self.assertEqual(workout.status, "not_started")
        self.assertEqual(workout.exercises, [])  # Empty list by default

    def test_workout_initialization_with_timing_fields(self):
        """
        Test Workout model initialization with timing fields
        """
        start_time = "2025-06-24T14:30:00"
        finish_time = "2025-06-24T15:45:00"

        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time=start_time,
            finish_time=finish_time,
        )

        self.assertEqual(workout.start_time, start_time)
        self.assertEqual(workout.finish_time, finish_time)

    def test_workout_initialization_without_timing_fields(self):
        """
        Test Workout model initialization without timing fields defaults to None
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
        )

        self.assertIsNone(workout.start_time)
        self.assertIsNone(workout.finish_time)

    def test_add_exercise(self):
        """
        Test adding an exercise to a workout
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Create an Exercise object
        exercise = Exercise(
            workout_id="workout123",
            exercise_id="ex456",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=209.44,
            status="planned",
        )

        # Add the exercise to the workout
        workout.add_exercise(exercise)

        # Assert the exercise was added
        self.assertEqual(len(workout.exercises), 1)
        self.assertEqual(workout.exercises[0].exercise_id, "ex456")
        self.assertEqual(workout.exercises[0].exercise_type, "Bench Press")

    def test_get_exercise(self):
        """
        Test getting an exercise by ID
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Create exercises with different IDs
        exercise1 = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
        )

        exercise2 = Exercise(
            exercise_id="ex2",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            status="planned",
        )

        workout.add_exercise(exercise1)
        workout.add_exercise(exercise2)

        # Get an exercise by ID
        result = workout.get_exercise("ex1")

        # Assert we got the right exercise
        self.assertIsNotNone(result)
        self.assertEqual(result.exercise_id, "ex1")
        self.assertEqual(result.exercise_type, "Bench Press")

        # Test getting a non-existent exercise
        self.assertIsNone(workout.get_exercise("nonexistent"))

    def test_remove_exercise(self):
        """
        Test removing an exercise by ID
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Create exercises with different IDs
        exercise1 = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
        )

        exercise2 = Exercise(
            exercise_id="ex2",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            status="planned",
        )

        workout.add_exercise(exercise1)
        workout.add_exercise(exercise2)

        # Remove an exercise
        result = workout.remove_exercise("ex1")

        # Assert the exercise was removed
        self.assertTrue(result)
        self.assertEqual(len(workout.exercises), 1)
        self.assertEqual(workout.exercises[0].exercise_id, "ex2")

        # Test removing a non-existent exercise
        self.assertFalse(workout.remove_exercise("nonexistent"))

    def test_status_calculation(self):
        """
        Test workout status calculation based on exercise status
        """

        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # With no exercises, status should be not_started
        self.assertEqual(workout.status, "not_started")

        # Add a planned exercise
        exercise1 = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
        )
        workout.add_exercise(exercise1)

        # With only planned exercises, status should be not_started
        self.assertEqual(workout.status, "not_started")

        # Add a completed exercise
        exercise2 = Exercise(
            exercise_id="ex2",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            status="planned",
        )
        workout.add_exercise(exercise2)

        # Call the complete_exercise method to mark the exercise as completed
        workout.complete_exercise(
            exercise_id="ex2",
            sets=3,
            reps=5,
            weight=315.0,
        )

        # With some completed exercises, status should be 'in_progress'
        self.assertEqual(workout.status, "in_progress")

        # Update first exercise to completed
        workout.complete_exercise(
            exercise_id="ex1",
            sets=3,
            reps=5,
            weight=225.0,
        )

        # With all exercises completed, status should be 'completed'
        self.assertEqual(workout.status, "completed")

        # Explicitly set to skipped overrides calculated status
        workout.status = "skipped"
        self.assertEqual(workout.status, "skipped")

    def test_status_override(self):
        """
        Test explicitly setting workout status
        """

        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Create an exercise
        exercise = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
        )
        workout.add_exercise(exercise)

        # Status should be not_started by default
        self.assertEqual(workout.status, "not_started")

        # Explicitly set to completed
        workout.status = "completed"
        self.assertEqual(workout.status, "completed")

        # Explicitly set to skipped
        workout.status = "skipped"
        self.assertEqual(workout.status, "skipped")

        # Test invalid status
        with self.assertRaises(ValueError):
            workout.status = "invalid_status"

    def test_calculate_volume(self):
        """
        Test calculating workout volume
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Create completed exercises
        bench_exercise = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=225.0,
            status="completed",
        )

        # Squat exercise
        squat_exercise = Exercise(
            exercise_id="ex2",
            workout_id="workout123",
            exercise_type="Squat",
            sets=2,  # Only 2 sets done
            reps=5,
            weight=315.0,
            status="completed",
        )

        # Deadlift exercise that's still planned (shouldn't count in volume)
        deadlift_exercise = Exercise(
            exercise_id="ex3",
            workout_id="workout123",
            exercise_type="Deadlift",
            sets=1,
            reps=5,
            weight=405.0,
            status="planned",
        )

        workout.add_exercise(bench_exercise)
        workout.add_exercise(squat_exercise)
        workout.add_exercise(deadlift_exercise)

        # Expected volume: bench (5*225*3) + squat (5*315*2) = 3375 + 3150 = 6525
        # Deadlift doesn't count because it's not completed
        self.assertEqual(workout.calculate_volume(), 6525.0)

    def test_duration_minutes_calculation_valid_times(self):
        """
        Test duration calculation with valid start and finish times
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time="2025-06-24T14:30:00",
            finish_time="2025-06-24T15:45:00",  # 75 minutes later
        )

        self.assertEqual(workout.duration_minutes, 75)

    def test_duration_minutes_calculation_same_time(self):
        """
        Test duration calculation when start and finish times are the same
        """
        same_time = "2025-06-24T14:30:00"
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time=same_time,
            finish_time=same_time,
        )

        self.assertEqual(workout.duration_minutes, 0)

    def test_duration_minutes_with_timezone_suffix(self):
        """
        Test duration calculation with timezone Z suffix
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time="2025-06-24T14:30:00Z",
            finish_time="2025-06-24T16:00:00Z",  # 90 minutes later
        )

        self.assertEqual(workout.duration_minutes, 90)

    def test_duration_minutes_with_timezone_offset(self):
        """
        Test duration calculation with timezone offset
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time="2025-06-24T14:30:00-05:00",
            finish_time="2025-06-24T15:00:00-05:00",  # 30 minutes later
        )

        self.assertEqual(workout.duration_minutes, 30)

    def test_duration_minutes_returns_none_when_no_start_time(self):
        """
        Test duration returns None when start_time is missing
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            finish_time="2025-06-24T15:45:00",
        )

        self.assertIsNone(workout.duration_minutes)

    def test_duration_minutes_returns_none_when_no_finish_time(self):
        """
        Test duration returns None when finish_time is missing
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time="2025-06-24T14:30:00",
        )

        self.assertIsNone(workout.duration_minutes)

    def test_duration_minutes_handles_invalid_timestamp_format(self):
        """
        Test duration returns None for invalid timestamp formats
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time="invalid-timestamp",
            finish_time="2025-06-24T15:45:00",
        )

        self.assertIsNone(workout.duration_minutes)

    def test_duration_minutes_handles_none_values(self):
        """
        Test duration handles None values gracefully
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
        )

        # Explicitly set to None
        workout.start_time = None
        workout.finish_time = None

        self.assertIsNone(workout.duration_minutes)

    def test_duration_minutes_cross_day_calculation(self):
        """
        Test duration calculation across day boundaries
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time="2025-06-24T23:30:00",
            finish_time="2025-06-25T01:00:00",  # 90 minutes later, next day
        )

        self.assertEqual(workout.duration_minutes, 90)

    def test_to_dict(self):
        """
        Test Workout model to_dict method
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12",
            notes="Solid session",
        )

        # Add an exercise
        exercise = Exercise(
            exercise_id="ex1",
            workout_id="workout123",
            exercise_type="Bench Press",
            sets=3,
            reps=5,
            weight=225.0,
            status="completed",
            notes="Felt strong",
            rpe=8.0,
        )

        workout.add_exercise(exercise)

        workout_dict = workout.to_dict()

        self.assertEqual(workout_dict["workout_id"], "workout123")
        self.assertEqual(workout_dict["athlete_id"], "athlete456")
        self.assertEqual(workout_dict["day_id"], "day789")
        self.assertEqual(workout_dict["date"], "2025-03-12")
        self.assertEqual(workout_dict["notes"], "Solid session")

        # Check exercises
        self.assertEqual(len(workout_dict["exercises"]), 1)
        self.assertEqual(workout_dict["exercises"][0]["exercise_id"], "ex1")
        self.assertEqual(workout_dict["exercises"][0]["exercise_type"], "Bench Press")
        self.assertEqual(workout_dict["exercises"][0]["notes"], "Felt strong")
        self.assertEqual(workout_dict["exercises"][0]["status"], "completed")
        self.assertEqual(workout_dict["exercises"][0]["rpe"], 8.0)

    def test_to_dict_includes_timing_fields(self):
        """
        Test to_dict method includes timing fields
        """
        start_time = "2025-06-24T14:30:00"
        finish_time = "2025-06-24T15:45:00"

        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
            start_time=start_time,
            finish_time=finish_time,
        )

        workout_dict = workout.to_dict()

        self.assertEqual(workout_dict["start_time"], start_time)
        self.assertEqual(workout_dict["finish_time"], finish_time)

    def test_to_dict_with_none_timing_fields(self):
        """
        Test to_dict method with None timing fields
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-06-24",
        )

        workout_dict = workout.to_dict()

        self.assertIsNone(workout_dict["start_time"])
        self.assertIsNone(workout_dict["finish_time"])

    def test_volume_calculation_with_decimal_types(self):
        """
        Test volume calculation when DynamoDB returns Decimal types
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Create exercise with Decimal types (simulating DynamoDB data)
        exercise = Exercise(
            exercise_id="test-exercise",
            workout_id="workout123",
            exercise_type="squat",
            sets=Decimal("3"),  # DynamoDB Decimal
            reps=Decimal("8"),  # DynamoDB Decimal
            weight=Decimal("100.5"),  # DynamoDB Decimal
            status="completed",
        )

        workout.add_exercise(exercise)

        # This should NOT raise "unsupported operand type(s) for *: 'decimal.Decimal' and 'float'"
        volume = workout.calculate_volume()

        # Expected: 3 * 8 * 100.5 = 2412.0
        self.assertEqual(volume, 2412.0)
        self.assertIsInstance(volume, float)

    def test_volume_calculation_with_mixed_types(self):
        """
        Test volume calculation with mixed Decimal/int/float types
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        exercise = Exercise(
            exercise_id="test-exercise",
            workout_id="workout123",
            exercise_type="bench_press",
            sets=3,  # int
            reps=Decimal("10"),  # Decimal
            weight=85.5,  # float
            status="completed",
        )

        workout.add_exercise(exercise)
        volume = workout.calculate_volume()

        # Expected: 3 * 10 * 85.5 = 2565.0
        self.assertEqual(volume, 2565.0)

    def test_volume_calculation_with_decimal_precision(self):
        """
        Test volume calculation with decimal precision values
        Tests the defensive float() conversion for precise Decimal values
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Exercise with precise decimal weights (common in powerlifting)
        precise_exercise = Exercise(
            exercise_id="precise-exercise",
            workout_id="workout123",
            exercise_type="bench_press",
            sets=Decimal("4"),
            reps=Decimal("6"),
            weight=Decimal("102.27"),  # 225.5 lbs converted to kg
            status="completed",
        )

        workout.add_exercise(precise_exercise)
        volume = workout.calculate_volume()

        # Expected: 4 * 6 * 102.27 = 2454.48
        self.assertEqual(volume, 2454.48)

    def test_volume_calculation_multiple_decimal_exercises(self):
        """
        Test volume calculation with multiple exercises having Decimal types
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
        )

        # Completed exercise with Decimals
        completed_exercise = Exercise(
            exercise_id="completed-exercise",
            workout_id="workout123",
            exercise_type="squat",
            sets=Decimal("3"),
            reps=Decimal("8"),
            weight=Decimal("100.0"),
            status="completed",
        )

        # Planned exercise with Decimals (should be ignored)
        planned_exercise = Exercise(
            exercise_id="planned-exercise",
            workout_id="workout123",
            exercise_type="bench_press",
            sets=Decimal("3"),
            reps=Decimal("10"),
            weight=Decimal("80.0"),
            status="planned",
        )

        # Another completed exercise with mixed types
        mixed_exercise = Exercise(
            exercise_id="mixed-exercise",
            workout_id="workout123",
            exercise_type="deadlift",
            sets=2,  # int
            reps=Decimal("5"),  # Decimal
            weight=120.5,  # float
            status="completed",
        )

        workout.add_exercise(completed_exercise)
        workout.add_exercise(planned_exercise)
        workout.add_exercise(mixed_exercise)

        volume = workout.calculate_volume()

        # Expected: completed (3*8*100.0) + mixed (2*5*120.5) = 2400.0 + 1205.0 = 3605.0
        # Planned exercise ignored
        self.assertEqual(volume, 3605.0)

    def test_from_dict_with_timing_fields(self):
        """
        Test from_dict method creates workout with timing fields
        """
        data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "start_time": "2025-06-24T14:30:00",
            "finish_time": "2025-06-24T15:45:00",
            "status": "completed",
        }

        workout = Workout.from_dict(data)

        self.assertEqual(workout.start_time, "2025-06-24T14:30:00")
        self.assertEqual(workout.finish_time, "2025-06-24T15:45:00")

    def test_from_dict_without_timing_fields(self):
        """
        Test from_dict method handles missing timing fields gracefully
        """
        data = {
            "workout_id": "workout123",
            "athlete_id": "athlete456",
            "day_id": "day789",
            "date": "2025-06-24",
            "status": "not_started",
        }

        workout = Workout.from_dict(data)

        self.assertIsNone(workout.start_time)
        self.assertIsNone(workout.finish_time)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
