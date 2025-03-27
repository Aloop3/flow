import unittest
from src.models.completed_exercise import CompletedExercise
from src.models.set import Set

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
            notes="Feeling sluggish"
        )

        self.assertEqual(exercise.completed_id, "comp123")
        self.assertEqual(exercise.workout_id, "workout456")
        self.assertEqual(exercise.exercise_id, "ex789")
        self.assertEqual(exercise.notes, "Feeling sluggish")
        self.assertEqual(exercise.sets, [])

    def test_add_set(self):
        """
        Test adding an Set to the CompletedExercise
        """ 

        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )

        set_obj = Set(
            set_id="set123",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=1,
            reps=5,
            weight=220.46,
            completed=False
        )

        exercise.add_set(set_obj)

        self.assertEqual(len(exercise.sets), 1)
        self.assertEqual(exercise.sets[0].set_id, "set123")
    
    def test_update_set(self):
        """
        Test updating a Set in a completed exercise
        """

        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )

        set_obj = Set(
            set_id="set123",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=1,
            reps=5,
            weight=220.46,
            completed=False
        )

        exercise.add_set(set_obj)

        # Update the set with new weight
        updated_set = exercise.update_set(
            set_id="set123",
            completed=False,
            reps=5,
            weight=286.6,
            rpe=6.5
        )

        self.assertTrue(updated_set)
        self.assertFalse(exercise.sets[0].completed)
        self.assertEqual(exercise.sets[0].reps, 5)
        self.assertEqual(exercise.sets[0].weight, 286.6)
        self.assertEqual(exercise.sets[0].rpe, 6.5)

    def test_update_nonexistent_set(self):
        """
        Test updating a set that does not exist
        """

        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )
        
        result = exercise.update_set("nonexistent set", completed=True)
        
        self.assertFalse(result)
    
    def test_to_dict(self):
        """
        Test to_dict method
        """

        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789",
            notes="Test notes"
        )
        
        # Add a set
        set_obj = Set(
            set_id="set123",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=1,
            reps=5,
            weight=225.0,
            completed=True
        )
        
        exercise.add_set(set_obj)

        # Convert to dict
        exercise_dict = exercise.to_dict()

        self.assertEqual(exercise_dict["completed_id"], "comp123")
        self.assertEqual(exercise_dict["workout_id"], "workout456")
        self.assertEqual(exercise_dict["exercise_id"], "ex789")
        self.assertEqual(exercise_dict["notes"], "Test notes")
        self.assertEqual(len(exercise_dict["sets"]), 1)


if __name__ == "__main__": # pragma: no cover
    unittest.main()