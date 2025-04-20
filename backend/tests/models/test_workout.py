import unittest
from src.models.workout import Workout
from src.models.exercise import Exercise


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

        # Volume should be 3 sets * 5 reps * 225 weight = 3375
        self.assertEqual(workout_dict["total_volume"], 3375.0)

        # Check exercises
        self.assertEqual(len(workout_dict["exercises"]), 1)
        self.assertEqual(workout_dict["exercises"][0]["exercise_id"], "ex1")
        self.assertEqual(workout_dict["exercises"][0]["exercise_type"], "Bench Press")
        self.assertEqual(workout_dict["exercises"][0]["notes"], "Felt strong")
        self.assertEqual(workout_dict["exercises"][0]["status"], "completed")
        self.assertEqual(workout_dict["exercises"][0]["rpe"], 8.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
