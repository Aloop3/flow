import unittest
from src.models.completed_exercise import CompletedExercise

class TestCompletedExerciseModel(unittest.TestCase):
    """
    Test suit for the CompletedExercise model
    """

    def test_completed_exercise_initialization(self):
        """
        Test CompletedExercise model initialization with required attributes and optional attributes
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789",
            actual_sets=3,
            actual_reps=4,
            actual_rpe=6,
            actual_weight=308.0,
            notes="Feeling sluggish"
        )

        self.assertEqual(exercise.completed_id, "comp123")
        self.assertEqual(exercise.workout_id, "workout456")
        self.assertEqual(exercise.exercise_id, "ex789")
        self.assertEqual(exercise.actual_sets, 3)
        self.assertEqual(exercise.actual_reps, 4)
        self.assertEqual(exercise.actual_rpe, 6)
        self.assertEqual(exercise.actual_weight, 308.0)
        self.assertEqual(exercise.notes, "Feeling sluggish")
    
    def test_completed_exercise_initialization_without_optional(self):
        """
        Test CompletedExercise model initialization without optional attributes
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789",
            actual_sets=3,
            actual_reps=5,
            actual_weight=330.0
        )

        self.assertEqual(exercise.completed_id, "comp123")
        self.assertEqual(exercise.workout_id, "workout456")
        self.assertEqual(exercise.exercise_id, "ex789")
        self.assertEqual(exercise.actual_sets, 3)
        self.assertEqual(exercise.actual_reps, 5)
        self.assertEqual(exercise.actual_weight, 330.0)
        self.assertIsNone(exercise.actual_rpe)
        self.assertIsNone(exercise.notes)
    
    def test_completed_exercise_to_dict(self):
        """
        Test CompletedExercise model to_dict method
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789",
            actual_sets=3,
            actual_reps=4,
            actual_rpe=6,
            actual_weight=308.0,
            notes="Feeling sluggish"
        )

        exercise_dict = exercise.to_dict()

        self.assertEqual(exercise_dict["completed_id"], "comp123")
        self.assertEqual(exercise_dict["workout_id"], "workout456")
        self.assertEqual(exercise_dict["exercise_id"], "ex789")
        self.assertEqual(exercise_dict["actual_sets"], 3)
        self.assertEqual(exercise_dict["actual_reps"], 4)
        self.assertEqual(exercise_dict["actual_rpe"], 6)
        self.assertEqual(exercise_dict["actual_weight"], 308.0)
        self.assertEqual(exercise_dict["notes"], "Feeling sluggish")
    
    def test_missing_required_fields(self):
        """
        Test that missing required fields raise ValueError
        """
        with self.assertRaises(ValueError):
            CompletedExercise("", "workout456", "ex789", 3, 4, 308.0)  # completed_id empty
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "", "ex789", 3, 4, 308.0)  # workout_id empty
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "workout456", "", 3, 4, 308.0)  # exercise_id empty

    def test_invalid_sets_reps_weight(self):
        """
        Test that negative or zero values for sets, reps, weight raise ValueError
        """
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "workout456", "ex789", 0, 4, 308.0)  # actual_sets <= 0
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "workout456", "ex789", 3, 0, 308.0)  # actual_reps <= 0
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "workout456", "ex789", 3, 4, 0.0)  # actual_weight <= 0

    def test_invalid_actual_rpe(self):
        """
        Test that actual_rpe outside the valid range (0-10) raises ValueError
        """
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "workout456", "ex789", 3, 4, 308.0, actual_rpe=-1)  # Negative RPE
        with self.assertRaises(ValueError):
            CompletedExercise("comp123", "workout456", "ex789", 3, 4, 308.0, actual_rpe=11)  # RPE > 10

if __name__ == "__main__": # pragma: no cover
    unittest.main()