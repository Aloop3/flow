import unittest
from src.utils.weight_defaults import get_default_unit


class TestWeightDefaults(unittest.TestCase):
    """
    Test suite for the weight defaults utility functions
    """

    def test_get_default_unit_powerlifting_squat(self):
        """
        Test that squat exercises default to kg
        """
        result = get_default_unit("Squat", "lb")
        self.assertEqual(result, "kg")

    def test_get_default_unit_powerlifting_bench_press(self):
        """
        Test that bench press exercises default to kg
        """
        result = get_default_unit("Bench Press", "lb")
        self.assertEqual(result, "kg")

    def test_get_default_unit_powerlifting_deadlift(self):
        """
        Test that deadlift exercises default to kg
        """
        result = get_default_unit("Deadlift", "lb")
        self.assertEqual(result, "kg")

    def test_get_default_unit_powerlifting_case_insensitive(self):
        """
        Test that powerlifting exercise detection is case insensitive
        """
        result = get_default_unit("SQUAT", "lb")
        self.assertEqual(result, "kg")

        result = get_default_unit("bench press", "lb")
        self.assertEqual(result, "kg")

    def test_get_default_unit_powerlifting_partial_match(self):
        """
        Test that powerlifting exercise detection works with partial matches
        """
        result = get_default_unit("Low Bar Squat", "lb")
        self.assertEqual(result, "kg")

        result = get_default_unit("Romanian Deadlift", "lb")
        self.assertEqual(result, "kg")

    def test_get_default_unit_non_powerlifting_user_preference_kg(self):
        """
        Test that non-powerlifting exercises use user preference (kg)
        """
        result = get_default_unit("Bicep Curl", "kg")
        self.assertEqual(result, "kg")

    def test_get_default_unit_non_powerlifting_user_preference_lb(self):
        """
        Test that non-powerlifting exercises use user preference (lb)
        """
        result = get_default_unit("Bicep Curl", "lb")
        self.assertEqual(result, "lb")

    def test_get_default_unit_non_powerlifting_various_exercises(self):
        """
        Test various non-powerlifting exercises use user preference
        """
        exercises = [
            "Dumbbell Press",
            "Pull Ups",
            "Lat Pulldown",
            "Leg Extension",
            "Tricep Pushdown",
        ]

        for exercise in exercises:
            with self.subTest(exercise=exercise):
                result = get_default_unit(exercise, "kg")
                self.assertEqual(result, "kg")

                result = get_default_unit(exercise, "lb")
                self.assertEqual(result, "lb")

    def test_get_default_unit_empty_exercise_name(self):
        """
        Test that empty exercise name uses user preference
        """
        result = get_default_unit("", "kg")
        self.assertEqual(result, "kg")

        result = get_default_unit("", "lb")
        self.assertEqual(result, "lb")


if __name__ == "__main__":
    unittest.main()
