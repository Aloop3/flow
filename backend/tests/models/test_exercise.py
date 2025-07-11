import unittest
from src.models.exercise import Exercise
from src.models.exercise_type import ExerciseType, ExerciseCategory


class TestExerciseModel(unittest.TestCase):
    """
    Test suite for the Exercise Model
    """

    def test_exercise_initialization_with_string_type(self):
        """
        Test Exercise model initialization with exercise_type as string
        """
        exercise = Exercise(
            exercise_id="ex123",
            workout_id="workout456",
            exercise_type="Squat",  # Predefined exercise as string
            sets=3,
            reps=5,
            weight=315.0,
            rpe=8.5,
            notes="Focus on bracing into belt",
            order=1,
        )

        self.assertEqual(exercise.exercise_id, "ex123")
        self.assertEqual(exercise.workout_id, "workout456")
        self.assertIsInstance(exercise.exercise_type, ExerciseType)
        self.assertEqual(exercise.exercise_type.name, "Squat")
        self.assertEqual(exercise.exercise_type.category, ExerciseCategory.BARBELL)
        self.assertTrue(exercise.exercise_type.is_predefined)
        self.assertEqual(exercise.sets, 3)
        self.assertEqual(exercise.reps, 5)
        self.assertEqual(exercise.weight, 315.0)
        self.assertEqual(exercise.rpe, 8.5)
        self.assertEqual(exercise.notes, "Focus on bracing into belt")
        self.assertEqual(exercise.order, 1)

    def test_exercise_initialization_with_exercise_type(self):
        """
        Test Exercise model initialization with ExerciseType object
        """
        ex_type = ExerciseType("Dumbbell Bench Press")

        exercise = Exercise(
            exercise_id="ex123",
            workout_id="workout456",
            exercise_type=ex_type,  # ExerciseType object
            sets=4,
            reps=10,
            weight=70.0,
            rpe=7.5,
            notes="Focus on elbow path",
            order=2,
        )

        self.assertEqual(exercise.exercise_type.name, "Dumbbell Bench Press")
        self.assertEqual(exercise.exercise_category, ExerciseCategory.DUMBBELL)
        self.assertTrue(exercise.exercise_type.is_predefined, False)

    def test_exercise_initialization_with_custom_exercise(self):
        """
        Test Exercise model initialization with custom exrcise
        """
        exercise = Exercise(
            exercise_id="ex123",
            workout_id="workout456",
            exercise_type="Single Arm Cable Pull",  # Custom exercise
            sets=3,
            reps=12,
            weight=50.0,
        )

        self.assertEqual(exercise.exercise_type.name, "Single Arm Cable Pull")
        self.assertEqual(exercise.exercise_category, ExerciseCategory.CUSTOM)
        self.assertFalse(exercise.is_predefined)

    def test_to_dict(self):
        """
        Test Exercise model to_dict method for serialization
        """
        exercise = Exercise(
            exercise_id="ex123",
            workout_id="workout456",
            exercise_type="Squat",
            sets=5,
            reps=5,
            weight=315.0,
            rpe=8.5,
            notes="Focus on bracing into belt",
            order=1,
        )

        exercise_dict = exercise.to_dict()

        self.assertEqual(exercise_dict["exercise_id"], "ex123")
        self.assertEqual(exercise_dict["workout_id"], "workout456")
        self.assertEqual(exercise_dict["exercise_type"], "Squat")
        self.assertEqual(exercise_dict["exercise_category"], "barbell")
        self.assertTrue(exercise_dict["is_predefined"])
        self.assertEqual(exercise_dict["sets"], 5)
        self.assertEqual(exercise_dict["reps"], 5)
        self.assertEqual(exercise_dict["weight"], 315.0)
        self.assertEqual(exercise_dict["rpe"], 8.5)
        self.assertEqual(exercise_dict["notes"], "Focus on bracing into belt")
        self.assertEqual(exercise_dict["order"], 1)

    def test_from_dict(self):
        """
        Test creating Exercise from dictionary using from_dict
        """
        data = {
            "exercise_id": "ex123",
            "workout_id": "workout456",
            "exercise_type": "Squat",
            "exercise_category": "barbell",
            "is_predefined": True,
            "sets": 3,
            "reps": 5,
            "weight": 315.0,
            "rpe": 8.5,
            "notes": "Focus on bracing into belt",
            "order": 1,
            "status": "completed",
        }

        exercise = Exercise.from_dict(data)

        self.assertEqual(exercise.exercise_id, "ex123")
        self.assertEqual(exercise.exercise_type.name, "Squat")
        self.assertEqual(exercise.exercise_category, ExerciseCategory.BARBELL)
        self.assertTrue(exercise.exercise_type.is_predefined)
        self.assertEqual(exercise.weight, 315.0)

    def test_from_dict_custom_exercise(self):
        """
        Test creating custom Exercise from dictionary using from_dict
        """
        data = {
            "exercise_id": "ex456",
            "workout_id": "workout789",
            "exercise_type": "Custom Exercise",
            "exercise_category": "custom",
            "is_predefined": False,
            "sets": 3,
            "reps": 12,
            "weight": 100.0,
            "status": "planned",
        }

        exercise = Exercise.from_dict(data)

        self.assertEqual(exercise.exercise_id, "ex456")
        self.assertEqual(exercise.exercise_type.name, "Custom Exercise")
        self.assertFalse(exercise.exercise_type.is_predefined)

    def test_exercise_category_assignment(self):
        """
        Test that exercise_category is assigned correctly
        """
        exercise = Exercise(
            exercise_id="ex123",
            workout_id="workout456",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            exercise_category="barbell",
        )

        custom_exercise = Exercise(
            exercise_id="ex124",
            workout_id="workout457",
            exercise_type="Custom movement",
            sets=3,
            reps=5,
            weight=200.0,
            exercise_category="random_category",
        )

        no_category_exercise = Exercise(
            exercise_id="ex130",
            workout_id="workout463",
            exercise_type="Zercher squat",
            sets=3,
            reps=5,
            weight=405.0,
            exercise_category=None,
        )

        self.assertEqual(exercise.exercise_category, ExerciseCategory.BARBELL)
        self.assertEqual(custom_exercise.exercise_category, ExerciseCategory.CUSTOM)
        self.assertEqual(
            no_category_exercise.exercise_category, ExerciseCategory.CUSTOM
        )

    def test_empty_exercise_id(self):
        """
        Test Exercise with empty exercise_id
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="",  # Empty ID should raise ValueError
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=315.0,
            )

    def test_empty_workout_id(self):
        """
        Test Exercise with empty workout_id
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="",  # Empty ID should raise ValueError
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=315.0,
            )

    def test_invalid_exercise_type(self):
        """
        Test Exercise with invalid exercise_type parameter type
        """
        with self.assertRaises(TypeError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type=231,  # Not a string or ExerciseType
                sets=3,
                reps=5,
                weight=315.0,
            )

    def test_negative_sets(self):
        """
        Test Exercise with negative sets value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=-3,  # Negative sets should raise ValueError
                reps=5,
                weight=315.0,
            )

    def test_zero_sets(self):
        """
        Test Exercise with zero sets value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=0,  # Zero sets should raise ValueError
                reps=5,
                weight=315.0,
            )

    def test_negative_reps(self):
        """
        Test Exercise with negative reps value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=-5,  # Negative reps should raise ValueError
                weight=315.0,
            )

    def test_zero_reps(self):
        """
        Test Exercise with zero reps value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=0,  # Zero reps should raise ValueError
                weight=315.0,
            )

    def test_negative_weight(self):
        """
        Test Exercise with negative weight value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=-315.0,  # Negative weight should raise ValueError
            )

    def test_missing_weight(self):
        """
        Test Exercise with missing weight value
        """
        with self.assertRaises(TypeError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=5
                # weight is missing but required
            )

    def test_invalid_rpe_range(self):
        """
        Test Exercise with RPE value outside of valid range
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=315.0,
                rpe=12.0,  # RPE > 10 should raise ValueError
            )

    def test_negative_order(self):
        """
        Test Exercise with negative order value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                workout_id="workout456",
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=315.0,
                rpe=8.5,
                notes="Focus on bracing into belt",
                order=-1,  # Invalid negative order
            )

    def test_add_set_data(self):
        # Create exercise with empty sets_data
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
        )

        # Add set data
        set_data = {"set_number": 1, "reps": 5, "weight": 225.0, "completed": True}
        exercise.add_set_data(set_data)

        # Verify set was added
        self.assertEqual(len(exercise.sets_data), 1)
        self.assertEqual(exercise.sets_data[0]["set_number"], 1)

        # Update existing set
        updated_set = {
            "set_number": 1,
            "reps": 5,
            "weight": 230.0,  # Weight increased
            "completed": True,
        }
        exercise.add_set_data(updated_set)

        # Verify set was updated (not added as new)
        self.assertEqual(len(exercise.sets_data), 1)
        self.assertEqual(exercise.sets_data[0]["weight"], 230.0)

        # Add another set with different number
        second_set = {"set_number": 2, "reps": 5, "weight": 225.0, "completed": True}
        exercise.add_set_data(second_set)

        # Verify sets are properly sorted by set_number
        self.assertEqual(len(exercise.sets_data), 2)
        self.assertEqual(exercise.sets_data[0]["set_number"], 1)
        self.assertEqual(exercise.sets_data[1]["set_number"], 2)

    def test_get_set_data(self):
        # Create exercise with sets
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            sets_data=[
                {"set_number": 1, "reps": 5, "weight": 225.0},
                {"set_number": 2, "reps": 5, "weight": 230.0},
            ],
        )

        # Get existing set
        set_data = exercise.get_set_data(2)
        self.assertIsNotNone(set_data)
        self.assertEqual(set_data["weight"], 230.0)

        # Get non-existent set
        set_data = exercise.get_set_data(3)
        self.assertIsNone(set_data)

    def test_to_dict_includes_sets_data(self):
        # Create exercise with sets
        sets_data = [
            {"set_number": 1, "reps": 5, "weight": 225.0},
            {"set_number": 2, "reps": 5, "weight": 230.0},
        ]
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            sets_data=sets_data,
        )

        # Convert to dict
        exercise_dict = exercise.to_dict()

        # Verify sets_data is included
        self.assertIn("sets_data", exercise_dict)
        self.assertEqual(len(exercise_dict["sets_data"]), 2)
        self.assertEqual(exercise_dict["sets_data"], sets_data)

    def test_to_dict_with_planned_sets_data(self):
        """Test that to_dict includes planned_sets_data when present"""
        # Create exercise with both sets_data and planned_sets_data
        sets_data = [
            {"set_number": 1, "reps": 5, "weight": 230.0, "completed": True},
            {"set_number": 2, "reps": 4, "weight": 230.0, "completed": True},
        ]
        planned_sets_data = [
            {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
            {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
        ]
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=2,
            reps=5,
            weight=225.0,
            sets_data=sets_data,
            planned_sets_data=planned_sets_data,
        )

        # Convert to dict
        exercise_dict = exercise.to_dict()

        # Verify both sets_data and planned_sets_data are included
        self.assertIn("sets_data", exercise_dict)
        self.assertIn("planned_sets_data", exercise_dict)
        self.assertEqual(exercise_dict["sets_data"], sets_data)
        self.assertEqual(exercise_dict["planned_sets_data"], planned_sets_data)

    def test_from_dict_with_planned_sets_data(self):
        """Test creating Exercise from dict with planned_sets_data"""
        exercise_data = {
            "exercise_id": "test123",
            "workout_id": "workout123",
            "exercise_type": "Squat",
            "sets": 2,
            "reps": 5,
            "weight": 225.0,
            "status": "planned",
            "sets_data": [
                {"set_number": 1, "reps": 5, "weight": 230.0, "completed": True},
                {"set_number": 2, "reps": 4, "weight": 230.0, "completed": True},
            ],
            "planned_sets_data": [
                {"set_number": 1, "reps": 5, "weight": 225.0, "completed": False},
                {"set_number": 2, "reps": 5, "weight": 225.0, "completed": False},
            ],
        }

        exercise = Exercise.from_dict(exercise_data)

        # Verify planned_sets_data is properly set
        self.assertIsNotNone(exercise.planned_sets_data)
        self.assertEqual(len(exercise.planned_sets_data), 2)
        self.assertEqual(exercise.planned_sets_data[0]["reps"], 5)
        self.assertEqual(exercise.planned_sets_data[0]["weight"], 225.0)
        self.assertEqual(exercise.planned_sets_data[1]["reps"], 5)
        self.assertEqual(exercise.planned_sets_data[1]["weight"], 225.0)

    def test_planned_sets_data_defaults_to_none(self):
        """Test that planned_sets_data defaults to None when not provided"""
        exercise = Exercise(
            exercise_id="test123",
            workout_id="workout123",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=225.0,
            status="planned",
        )

        self.assertIsNone(exercise.planned_sets_data)

        # Test from_dict without planned_sets_data
        exercise_data = {
            "exercise_id": "test456",
            "workout_id": "workout456",
            "exercise_type": "Bench Press",
            "sets": 3,
            "reps": 8,
            "weight": 185.0,
            "status": "planned",
        }

        exercise_from_dict = Exercise.from_dict(exercise_data)
        self.assertIsNone(exercise_from_dict.planned_sets_data)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
