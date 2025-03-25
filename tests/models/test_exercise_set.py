import unittest
from src.models.exercise_set import ExerciseSet

class TestExerciseSetModel(unittest.TestCase):
    """
    Test suite for the ExerciseSet model
    """

    def test_exercise_set_initialization(self):
        """
        Test ExerciseSet model initialization with all attributes
        """

        set_obj = ExerciseSet(
            set_id="set123",
            completed_id="comp456",
            set_number=1,
            reps=5,
            weight=220.46,
            rpe=7.5,
            notes="Technique feels solid",
            completed=True
        )

        self.assertEqual(set_obj.set_id, "set123")
        self.assertEqual(set_obj.completed_id, "comp456")
        self.assertEqual(set_obj.set_number, 1)
        self.assertEqual(set_obj.reps, 5)
        self.assertEqual(set_obj.weight, 220.46)
        self.assertEqual(set_obj.rpe, 7.5)
        self.assertEqual(set_obj.notes, "Technique feels solid")
        self.assertTrue(set_obj.completed)
    
    def test_to_dict(self):
        """
        Test to_dict method
        """

        set_obj = ExerciseSet(
            set_id="set123",
            completed_id="comp456",
            set_number=1,
            reps=5,
            weight=220.46,
            rpe=7.5,
            notes="Technique feels solid",
            completed=True
        )

        set_dict = set_obj.to_dict()

        self.assertEqual(set_dict["set_id"], "set123")
        self.assertEqual(set_dict["completed_id"], "comp456")
        self.assertEqual(set_dict["set_number"], 1)
        self.assertEqual(set_dict["reps"], 5)
        self.assertEqual(set_dict["weight"], 220.46)
        self.assertEqual(set_dict["rpe"], 7.5)
        self.assertEqual(set_dict["notes"], "Technique feels solid")
        self.assertTrue(set_dict["completed"])
    
    def test_validation(self):
        """
        Test validation rules
        """

        # Empty set_id
        with self.assertRaises(ValueError):
            ExerciseSet("", "comp456", 1, 5, 220.46)
        
        # Empty completed_id
        with self.assertRaises(ValueError):
            ExerciseSet("set123", "", 1, 5, 220.46)
        
        # Invalid set_number
        with self.assertRaises(ValueError):
            ExerciseSet("set123", "comp456", -1, 5, 220.46)
        
        # Invalid reps
        with self.assertRaises(ValueError):
            ExerciseSet("set123", "comp456", 1, -1, 220.46)
        
        # Invalid weight
        with self.assertRaises(ValueError):
            ExerciseSet("set123", "comp456", 1, 5, -220.46)
        
        # Invalid RPE
        with self.assertRaises(ValueError):
            ExerciseSet("set123", "comp456", 1, 5, 220.46, rpe=-11)


if __name__ == "__main__": # pragma: no cover
    unittest.main()