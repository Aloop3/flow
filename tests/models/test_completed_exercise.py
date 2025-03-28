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

    def test_completed_exercise_initialization_without_notes(self):
        """
        Test CompletedExercise model initialization without the optional notes parameter
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )

        self.assertEqual(exercise.completed_id, "comp123")
        self.assertEqual(exercise.workout_id, "workout456")
        self.assertEqual(exercise.exercise_id, "ex789")
        self.assertIsNone(exercise.notes)
        self.assertEqual(exercise.sets, [])

    def test_initialization_with_empty_completed_id(self):
        """
        Test that empty completed_id raises ValueError
        """
        with self.assertRaises(ValueError) as context:
            CompletedExercise(
                completed_id="",
                workout_id="workout456",
                exercise_id="ex789"
            )
        self.assertIn("completed_id cannot be empty", str(context.exception))

    def test_initialization_with_empty_workout_id(self):
        """
        Test that empty workout_id raises ValueError
        """
        with self.assertRaises(ValueError) as context:
            CompletedExercise(
                completed_id="comp123",
                workout_id="",
                exercise_id="ex789"
            )
        self.assertIn("workout_id cannot be empty", str(context.exception))

    def test_initialization_with_empty_exercise_id(self):
        """
        Test that empty exercise_id raises ValueError
        """
        with self.assertRaises(ValueError) as context:
            CompletedExercise(
                completed_id="comp123",
                workout_id="workout456",
                exercise_id=""
            )
        self.assertIn("exercise_id cannot be empty", str(context.exception))

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
    
    def test_add_sets_maintains_order(self):
        """
        Test that sets are ordered by set_number when added
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )

        # Create sets with out-of-order set_numbers
        set2 = Set(
            set_id="set2",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=2,
            reps=5,
            weight=220.46,
        )

        set1 = Set(
            set_id="set1",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=1,
            reps=5,
            weight=225.0,
        )

        # Add sets in reverse order
        exercise.add_set(set2)
        exercise.add_set(set1)

        # Verify they're ordered by set_number
        self.assertEqual(len(exercise.sets), 2)
        self.assertEqual(exercise.sets[0].set_id, "set1") # First is set1 (set_number=1)
        self.assertEqual(exercise.sets[1].set_id, "set2") # Second is set2 (set_number=2)

    def test_get_set(self):
        """
        Test retrieving a set by ID
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
        )

        exercise.add_set(set_obj)

        # Test getting an existing set
        found_set = exercise.get_set("set123")
        self.assertIsNotNone(found_set)
        self.assertEqual(found_set.set_id, "set123")

        # Test getting a non-existent set
        not_found_set = exercise.get_set("nonexistent")
        self.assertIsNone(not_found_set)
    
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
    
    def test_update_set_with_nonexistent_attribute(self):
        """
        Test updating a set with a non-existent attribute
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
        )

        exercise.add_set(set_obj)

        # Update with a non-existent attribute
        result = exercise.update_set("set123", nonexistent_attr="value", reps=8)
        
        # The update should succeed because the set exists
        self.assertTrue(result)
        
        # The reps should be updated
        self.assertEqual(exercise.sets[0].reps, 8)
        
        # The nonexistent attribute should not be added
        self.assertFalse(hasattr(exercise.sets[0], "nonexistent_attr"))
    
    def test_remove_set(self):
        """
        Test removing a set from the exercise
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )

        # Add two sets
        set1 = Set(
            set_id="set1",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=1,
            reps=5,
            weight=225.0
        )
        
        set2 = Set(
            set_id="set2",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=2,
            reps=5,
            weight=225.0
        )

        exercise.add_set(set1)
        exercise.add_set(set2)
        
        # Verify initial state
        self.assertEqual(len(exercise.sets), 2)
        
        # Remove the first set
        result = exercise.remove_set("set1")
        self.assertTrue(result)
        self.assertEqual(len(exercise.sets), 1)
        self.assertEqual(exercise.sets[0].set_id, "set2")
        
        # Try to remove a non-existent set
        result = exercise.remove_set("nonexistent")
        self.assertFalse(result)
        self.assertEqual(len(exercise.sets), 1)
    
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
        self.assertEqual(exercise_dict["sets"][0]["set_id"], "set123")
    
    def test_calculate_volume(self):
        """
        Test calculating volume for an exercise with sets
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )

        # Add two sets with known weights and reps
        set1 = Set(
            set_id="set1",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=1,
            reps=5,
            weight=225.0
        )
        
        set2 = Set(
            set_id="set2",
            completed_exercise_id=exercise.completed_id,
            workout_id=exercise.workout_id,
            set_number=2,
            reps=5,
            weight=225.0
        )

        exercise.add_set(set1)
        exercise.add_set(set2)
        
        # Calculate volume
        volume = exercise.calculate_volume()
        
        # Expected: (5 * 225.0) + (5 * 225.0) = 2250.0
        self.assertEqual(volume, 2250.0)
    
    def test_calculate_volume_no_sets(self):
        """
        Test calculating volume for an exercise with no sets
        """
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout456",
            exercise_id="ex789"
        )
        
        # Calculate volume with no sets
        volume = exercise.calculate_volume()
        
        # Expected: 0.0
        self.assertEqual(volume, 0.0)

if __name__ == "__main__": # pragma: no cover
    unittest.main()