import unittest
from unittest.mock import MagicMock
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

    def test_get_exercise_default_unit_big_three_exact_only(self):
        """Test default units for EXACT Big 3 exercises only"""
        # Core Big 3 - should be kg
        self.assertEqual(get_exercise_default_unit("Squat", "auto"), "kg")
        self.assertEqual(get_exercise_default_unit("Bench Press", "auto"), "kg")
        self.assertEqual(get_exercise_default_unit("Deadlift", "auto"), "kg")
        self.assertEqual(
            get_exercise_default_unit("squat", "auto"), "kg"
        )  # Case insensitive
        self.assertEqual(get_exercise_default_unit("bench press", "auto"), "kg")
        self.assertEqual(get_exercise_default_unit("deadlift", "auto"), "kg")

    def test_get_exercise_default_unit_squat_variations_are_lb(self):
        """Test that squat variations default to lb (not kg)"""
        squat_variations = [
            "Low Bar Squat",
            "High Bar Squat",
            "Front Squat",
            "Bulgarian Split Squat",
            "Goblet Squat",
            "Contralateral Split Squat",
            "Box Squat",
            "Pause Squat",
        ]

        for exercise in squat_variations:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(
                    result, "lb", f"{exercise} should default to lb (not kg)"
                )

    def test_get_exercise_default_unit_bench_variations_are_lb(self):
        """Test that bench variations default to lb (not kg)"""
        bench_variations = [
            "Close Grip Bench Press",
            "Incline Bench Press",
            "Decline Bench Press",
            "Floor Press",
            "Spoto Press",
        ]

        for exercise in bench_variations:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(
                    result, "lb", f"{exercise} should default to lb (not kg)"
                )

    def test_get_exercise_default_unit_deadlift_variations_are_lb(self):
        """Test that deadlift variations default to lb (not kg)"""
        deadlift_variations = [
            "Romanian Deadlift",
            "Sumo Deadlift",
            "Stiff Leg Deadlift",
            "Rack Pull",
            "Deficit Deadlift",
        ]

        for exercise in deadlift_variations:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(
                    result, "lb", f"{exercise} should default to lb (not kg)"
                )

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

    def test_dumbbell_bench_press_classification_fix(self):
        """Test that dumbbell bench press correctly defaults to lb (equipment priority)"""
        result = get_exercise_default_unit("Dumbbell Bench Press", "auto")
        self.assertEqual(result, "lb", "Dumbbell bench press should default to lb")

        result = get_exercise_default_unit("dumbbell bench press", "auto")
        self.assertEqual(
            result, "lb", "Case insensitive dumbbell bench press should default to lb"
        )

    def test_machine_bench_press_classification_fix(self):
        """Test that machine bench press correctly defaults to lb (equipment priority)"""
        result = get_exercise_default_unit("Machine Bench Press", "auto")
        self.assertEqual(result, "lb", "Machine bench press should default to lb")

    def test_barbell_bench_press_remains_kg(self):
        """Test that EXACT barbell bench press (no equipment modifier) remains kg"""
        result = get_exercise_default_unit("Bench Press", "auto")
        self.assertEqual(result, "kg", "Exact 'Bench Press' should default to kg")

        result = get_exercise_default_unit("bench press", "auto")
        self.assertEqual(
            result, "kg", "Case insensitive exact 'bench press' should default to kg"
        )

    def test_equipment_priority_over_movement_type(self):
        """Test that equipment type takes priority over movement type in classification"""
        # Dumbbell exercises with SBD movement names should still be lb
        dumbbell_exercises = [
            "Dumbbell Squat",  # Has "squat" but should be lb due to "dumbbell"
            "Dumbbell Deadlift",  # Has "deadlift" but should be lb due to "dumbbell"
            "Dumbbell Bench Press",  # Has "bench press" but should be lb due to "dumbbell"
        ]

        for exercise in dumbbell_exercises:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(
                    result,
                    "lb",
                    f"{exercise} should default to lb due to equipment priority",
                )

    def test_machine_equipment_priority(self):
        """Test that machine exercises default to lb regardless of movement"""
        machine_exercises = [
            "Machine Row",
            "Machine Shoulder Press",
            "Leg Press Machine",
            "Machine Squat",  # Has "squat" but should be lb due to "machine"
        ]

        for exercise in machine_exercises:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(result, "lb", f"{exercise} should default to lb")

    def test_cable_equipment_priority(self):
        """Test that cable exercises default to lb"""
        cable_exercises = ["Cable Row", "Cable Lateral Raise", "Cable Tricep Extension"]

        for exercise in cable_exercises:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(result, "lb", f"{exercise} should default to lb")

    def test_barbell_sbd_movements_exact_match_only(self):
        """Test that ONLY exact Big 3 movements get kg defaults"""
        # Only these exact matches should be kg
        exact_big_three = ["Squat", "Deadlift", "Bench Press"]

        for exercise in exact_big_three:
            with self.subTest(exercise=exercise):
                result = get_exercise_default_unit(exercise, "auto")
                self.assertEqual(
                    result, "kg", f"Exact '{exercise}' should default to kg"
                )

    def test_custom_exercise_category_priority(self):
        """Test that custom exercise categories work correctly"""
        # Custom dumbbell exercise should be lb
        result = get_exercise_default_unit("Custom Curl", "auto", "dumbbell")
        self.assertEqual(result, "lb", "Custom dumbbell exercise should be lb")

        # Custom machine exercise should be lb
        result = get_exercise_default_unit("Custom Press", "auto", "machine")
        self.assertEqual(result, "lb", "Custom machine exercise should be lb")

        # Custom cable exercise should be lb
        result = get_exercise_default_unit("Custom Row", "auto", "cable")
        self.assertEqual(result, "lb", "Custom cable exercise should be lb")

    def test_big_three_beats_category(self):
        """Test that Big 3 exact matches override category"""
        # Even if someone sets category="barbell", Big 3 should still be kg
        result = get_exercise_default_unit("Squat", "auto", "barbell")
        self.assertEqual(result, "kg", "Big 3 should override category")

        result = get_exercise_default_unit("Bench Press", "auto", "barbell")
        self.assertEqual(result, "kg", "Big 3 should override category")

        result = get_exercise_default_unit("Deadlift", "auto", "barbell")
        self.assertEqual(result, "kg", "Big 3 should override category")

    def test_contralateral_split_squat_with_dumbbell_category(self):
        """Test the specific case mentioned - split squat with dumbbell category"""
        result = get_exercise_default_unit(
            "Contralateral Split Squat", "auto", "dumbbell"
        )
        self.assertEqual(
            result,
            "lb",
            "Contralateral Split Squat with dumbbell category should be lb",
        )

    def test_exercise_type_object_with_name_attribute(self):
        """Test that function handles ExerciseType objects with .name attribute"""
        mock_exercise_type = MagicMock()
        mock_exercise_type.name = "Dumbbell Bench Press"

        result = get_exercise_default_unit(mock_exercise_type, "auto")
        self.assertEqual(result, "lb", "Should handle ExerciseType objects correctly")

        # Test with exact Big 3 variant
        mock_exercise_type.name = "Bench Press"
        result = get_exercise_default_unit(mock_exercise_type, "auto")
        self.assertEqual(
            result,
            "kg",
            "Should handle ExerciseType objects correctly for exact Big 3 movements",
        )

    def test_user_preference_overrides_equipment_classification(self):
        """Test that user preference overrides equipment-based classification"""
        # Force kg preference on dumbbell exercise
        result = get_exercise_default_unit("Dumbbell Bench Press", "kg")
        self.assertEqual(
            result, "kg", "kg preference should override equipment classification"
        )

        # Force lb preference on Big 3 exercise
        result = get_exercise_default_unit("Bench Press", "lb")
        self.assertEqual(
            result, "lb", "lb preference should override Big 3 classification"
        )


if __name__ == "__main__":
    unittest.main()
