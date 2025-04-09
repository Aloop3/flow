import unittest
from src.models.set import Set


class TestSetModel(unittest.TestCase):
    """
    Test suite for the Set model
    """

    def test_exercise_set_initialization(self):
        """
        Test Set model initialization with all attributes
        """
        set_obj = Set(
            set_id="set123",
            completed_exercise_id="comp456",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=220.46,
            rpe=7.5,
            notes="Technique feels solid",
            completed=True,
        )

        self.assertEqual(set_obj.set_id, "set123")
        self.assertEqual(set_obj.completed_exercise_id, "comp456")
        self.assertEqual(set_obj.workout_id, "workout123")
        self.assertEqual(set_obj.set_number, 1)
        self.assertEqual(set_obj.reps, 5)
        self.assertEqual(set_obj.weight, 220.46)
        self.assertEqual(set_obj.rpe, 7.5)
        self.assertEqual(set_obj.notes, "Technique feels solid")
        self.assertEqual(set_obj.completed, True)

    def test_exercise_set_initialization_without_optional(self):
        """
        Test Set model initialization without optional attributes
        """
        set_obj = Set(
            set_id="set123",
            completed_exercise_id="comp456",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=220.46,
        )

        self.assertEqual(set_obj.set_id, "set123")
        self.assertEqual(set_obj.completed_exercise_id, "comp456")
        self.assertEqual(set_obj.workout_id, "workout123")
        self.assertEqual(set_obj.set_number, 1)
        self.assertEqual(set_obj.reps, 5)
        self.assertEqual(set_obj.weight, 220.46)
        self.assertIsNone(set_obj.rpe)
        self.assertIsNone(set_obj.notes)
        self.assertIsNone(set_obj.completed)

    def test_to_dict(self):
        """
        Test to_dict method
        """
        set_obj = Set(
            set_id="set123",
            completed_exercise_id="comp456",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=220.46,
            rpe=7.5,
            notes="Technique feels solid",
            completed=True,
        )

        set_dict = set_obj.to_dict()

        self.assertEqual(set_dict["set_id"], "set123")
        self.assertEqual(set_dict["completed_exercise_id"], "comp456")
        self.assertEqual(set_dict["workout_id"], "workout123")
        self.assertEqual(set_dict["set_number"], 1)
        self.assertEqual(set_dict["reps"], 5)
        self.assertEqual(set_dict["weight"], 220.46)
        self.assertEqual(set_dict["rpe"], 7.5)
        self.assertEqual(set_dict["notes"], "Technique feels solid")
        self.assertEqual(set_dict["completed"], True)

    def test_invalid_set_id(self):
        """
        Test that empty set_id raises ValueError
        """
        with self.assertRaises(ValueError):
            Set(
                set_id="",  # Invalid empty ID
                completed_exercise_id="comp456",
                workout_id="workout789",
                set_number=1,
                reps=8,
                weight=315.0,
            )

    def test_invalid_completed_exercise_id(self):
        """
        Test that empty completed_exercise_id raises ValueError
        """
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="",  # Invalid empty ID
                workout_id="workout789",
                set_number=1,
                reps=8,
                weight=315.0,
            )

    def test_invalid_workout_id(self):
        """
        Test that empty workout_id raises ValueError
        """
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="comp456",
                workout_id="",  # Invalid empty ID
                set_number=1,
                reps=8,
                weight=315.0,
            )

    def test_invalid_set_number(self):
        """
        Test that non-positive set_number raises ValueError
        """
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="comp456",
                workout_id="workout789",
                set_number=0,  # Invalid non-positive number
                reps=8,
                weight=315.0,
            )

    def test_invalid_reps(self):
        """
        Test that non-positive reps raises ValueError
        """
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="comp456",
                workout_id="workout789",
                set_number=1,
                reps=0,  # Invalid non-positive number
                weight=315.0,
            )

    def test_invalid_weight(self):
        """
        Test that non-positive weight raises ValueError
        """
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="comp456",
                workout_id="workout789",
                set_number=1,
                reps=8,
                weight=0.0,  # Invalid non-positive number
            )

    def test_invalid_rpe(self):
        """
        Test that rpe outside valid range raises ValueError
        """
        # RPE too low
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="comp456",
                workout_id="workout789",
                set_number=1,
                reps=8,
                weight=315.0,
                rpe=-1,  # Invalid negative RPE
            )

        # RPE too high
        with self.assertRaises(ValueError):
            Set(
                set_id="set123",
                completed_exercise_id="comp456",
                workout_id="workout789",
                set_number=1,
                reps=8,
                weight=315.0,
                rpe=11,  # Invalid RPE > 10
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
