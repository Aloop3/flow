import unittest
from src.models.workout import Workout
from src.models.completed_exercise import CompletedExercise

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
            status="completed"
        )

        self.assertEqual(workout.workout_id, "workout123")
        self.assertEqual(workout.athlete_id, "athlete456")
        self.assertEqual(workout.day_id, "day789")
        self.assertEqual(workout.date, "2025-03-12")
        self.assertEqual(workout.notes, "Solid session")
        self.assertEqual(workout.status, "completed")
        self.assertEqual(workout.exercises, []) # Empty list by default

    def test_workout_initialization_without_optional_attributes(self):
        """
        Test Workout model initialization without optional attributes
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12"
        )

        self.assertEqual(workout.workout_id, "workout123")
        self.assertEqual(workout.athlete_id, "athlete456")
        self.assertEqual(workout.day_id, "day789")
        self.assertEqual(workout.date, "2025-03-12")
        self.assertIsNone(workout.notes)
        self.assertEqual(workout.status, "completed") # Default value
        self.assertEqual(workout.exercises, []) # Empty list by default
    
    def test_workout_with_exercises(self):
        """
        Test Workout with completed exercises
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            status="completed"
        )

        # Add completed exercises
        exercise1 = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1",
            actual_sets=3,
            actual_reps=5,
            actual_weight=225.0
        )
        
        exercise2 = CompletedExercise(
            completed_id="comp2",
            workout_id="workout123",
            exercise_id="ex2",
            actual_sets=2,
            actual_reps=8,
            actual_weight=165.0
        )

        workout.exercises.append(exercise1)
        workout.exercises.append(exercise2)


        self.assertEqual(len(workout.exercises), 2)
        self.assertEqual(workout.exercises[0].completed_id, "comp1")
        self.assertEqual(workout.exercises[1].completed_id, "comp2")
    
    def test_workout_with_partial_status(self):
        """
        Test Workout with partial status
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            status="partial"
        )
    
    def test_workout_with_skipped_status(self):
        """
        Test Workout with skipped status
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15",
            status="skipped",
            notes="Feeling sick"
        )

        self.assertEqual(workout.status, "skipped")
        self.assertEqual(workout.notes, "Feeling sick")
    
    def test_workout_to_dict(self):
        """
        Test Workout model to_dict method
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12",
            notes="Solid session",
            status="completed"
        )

        # Add a completed exercise
        exercise = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1",
            actual_sets=3,
            actual_reps=5,
            actual_weight=225.0
        )
        
        workout.exercises.append(exercise)

        workout_dict = workout.to_dict()

        self.assertEqual(workout_dict['workout_id'], "workout123")
        self.assertEqual(workout_dict['athlete_id'], "athlete456")
        self.assertEqual(workout_dict['day_id'], "day789")
        self.assertEqual(workout_dict['date'], "2025-03-12")
        self.assertEqual(workout_dict['notes'], "Solid session")
        self.assertEqual(workout_dict['status'], "completed")

        # Check exercises
        self.assertEqual(len(workout_dict['exercises']), 1)
        self.assertEqual(workout_dict['exercises'][0]['completed_id'], "comp1")
        self.assertEqual(workout_dict['exercises'][0]['workout_id'], "workout123")
        self.assertEqual(workout_dict['exercises'][0]['exercise_id'], "ex1")


if __name__ == "__main__": # pragma: no cover
    unittest.main()