import unittest
from src.utils.weight_utils import (
    lb_to_kg,
    kg_to_lb,
    convert_weight_to_kg,
    convert_weight_from_kg,
    get_exercise_default_unit,
)


class TestWeightUtils(unittest.TestCase):
    """
    Test suite for weight conversion utilities
    """

    def test_lb_to_kg_conversion(self):
        """Test pounds to kilograms conversion"""
        self.assertEqual(lb_to_kg(100), 45.36)
        self.assertEqual(lb_to_kg(220), 99.79)
        self.assertEqual(lb_to_kg(0), 0)

    def test_kg_to_lb_conversion(self):
        """Test kilograms to pounds conversion"""
        self.assertEqual(kg_to_lb(100), 220.46)
        self.assertEqual(kg_to_lb(45.36), 100.0)
        self.assertEqual(kg_to_lb(0), 0)

    def test_convert_weight_to_kg(self):
        """Test conversion from any unit to kg"""
        self.assertEqual(convert_weight_to_kg(100, "lb"), 45.36)
        self.assertEqual(convert_weight_to_kg(100, "kg"), 100)

        with self.assertRaises(ValueError):
            convert_weight_to_kg(100, "invalid")

    def test_convert_weight_from_kg(self):
        """Test conversion from kg to any unit"""
        self.assertEqual(convert_weight_from_kg(45.36, "lb"), 100.0)
        self.assertEqual(convert_weight_from_kg(100, "kg"), 100)

        with self.assertRaises(ValueError):
            convert_weight_from_kg(100, "invalid")

    def test_get_exercise_default_unit_big_three(self):
        """Test default units for big 3 exercises"""
        self.assertEqual(get_exercise_default_unit("Squat", "auto"), "kg")
        self.assertEqual(get_exercise_default_unit("Bench Press", "auto"), "kg")
        self.assertEqual(get_exercise_default_unit("Deadlift", "auto"), "kg")
        self.assertEqual(get_exercise_default_unit("Low Bar Squat", "auto"), "kg")

    def test_get_exercise_default_unit_accessories(self):
        """Test default units for accessory exercises"""
        self.assertEqual(get_exercise_default_unit("Dumbbell Curl", "auto"), "lb")
        self.assertEqual(get_exercise_default_unit("Lat Pulldown", "auto"), "lb")
        self.assertEqual(get_exercise_default_unit("Machine Press", "auto"), "lb")

    def test_get_exercise_default_unit_user_override(self):
        """Test user preference overrides"""
        self.assertEqual(get_exercise_default_unit("Squat", "lb"), "lb")
        self.assertEqual(get_exercise_default_unit("Dumbbell Curl", "kg"), "kg")
        self.assertEqual(get_exercise_default_unit("Bench Press", "lb"), "lb")


if __name__ == "__main__":
    unittest.main()
