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
                day_id="day456",
                exercise_type="Squat",  # Predefined exercise as string
                sets=3,
                reps=5,
                weight=315.0,
                rpe=8.5,
                notes="Focus on bracing into belt",
                order=1
        )

        self.assertEqual(exercise.exercise_id, "ex123")
        self.assertEqual(exercise.day_id, "day456")
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
            day_id="day456",
            exercise_type=ex_type,  # ExerciseType object
            sets=4,
            reps=10,
            weight=70.0,
            rpe=7.5,
            notes="Focus on elbow path",
            order=2
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
            day_id="day456",
            exercise_type="Single Arm Cable Pull", # Custom exercise
            sets=3,
            reps=12,
            weight=50.0
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
            day_id="day456",
            exercise_type="Squat",
            sets=5,
            reps=5,
            weight=315.0,
            rpe=8.5,
            notes="Focus on bracing into belt",
            order=1
        )
        
        exercise_dict = exercise.to_dict()
        
        self.assertEqual(exercise_dict["exercise_id"], "ex123")
        self.assertEqual(exercise_dict["day_id"], "day456")
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
            "day_id": "day456",
            "exercise_type": "Squat",
            "exercise_category": "barbell",
            "is_predefined": True,
            "sets": 3,
            "reps": 5,
            "weight": 315.0,
            "rpe": 8.5,
            "notes": "Focus on bracing into belt",
            "order": 1
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
            "day_id": "day789",
            "exercise_type": "Custom Exercise",
            "exercise_category": "custom",
            "is_predefined": False,
            "sets": 3,
            "reps": 12,
            "weight": 100.0
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
            day_id="day456",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            exercise_category="barbell"
        )

        custom_exercise = Exercise(
            exercise_id="ex124",
            day_id="day457",
            exercise_type="Custom movement",
            sets=3,
            reps=5,
            weight=200.0,
            exercise_category="random_category"
        )

        no_category_exercise = Exercise(
             exercise_id="ex130",
            day_id="day463",
            exercise_type="Hex bar deadlift",
            sets=3,
            reps=5,
            weight=405.0,
            exercise_category=None
        )

        self.assertEqual(exercise.exercise_category, ExerciseCategory.BARBELL)
        self.assertEqual(custom_exercise.exercise_category, ExerciseCategory.CUSTOM)
        self.assertEqual(no_category_exercise.exercise_category, ExerciseCategory.CUSTOM)

    def test_empty_exercise_id(self):
        """
        Test Exercise with empty exercise_id
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="",  # Empty ID should raise ValueError
                day_id="day456",
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=315.0
            )
    
    def test_empty_day_id(self):
        """
        Test Exercise with empty day_id
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123",
                day_id="", # Empty ID should raise ValueError
                exercise_type="Squat",
                sets=3,
                reps=5,
                weight=315.0
            )
    
    def test_invalid_exercise_type(self):
        """
        Test Exercise with invalid exercise_type parameter type
        """
        with self.assertRaises(TypeError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type=231, # Not a string or ExerciseType
                sets=3,
                reps=5,
                weight=315.0
            )
    
    def test_negative_sets(self):
        """
        Test Exercise with negative sets value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type="Squat",
                sets=-3, # Negative sets should raise ValueError
                reps=5,
                weight=315.0
            )
    
    def test_zero_sets(self):
        """
        Test Exercise with zero sets value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type="Squat",
                sets=0, # Zero sets should raise ValueError
                reps=5,
                weight=315.0
            )
    
    def test_negative_reps(self):
        """
        Test Exercise with negative reps value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type="Squat",
                sets=3, 
                reps=-5, # Negative reps should raise ValueError
                weight=315.0
            )
    
    def test_zero_reps(self):
        """
        Test Exercise with zero reps value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type="Squat",
                sets=3, 
                reps=0, # Zero reps should raise ValueError
                weight=315.0
            )
    
    def test_negative_weight(self):
        """
        Test Exercise with negative weight value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type="Squat",
                sets=3, 
                reps=5, 
                weight=-315.0 # Negative weight should raise ValueError
            )
    
    def test_zero_weight(self):
        """
        Test Exercise with zero weight value
        """
        with self.assertRaises(ValueError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
                exercise_type="Squat",
                sets=3, 
                reps=5, 
                weight=0.0 # Zero weight should raise ValueError
            )
    
    def test_missing_weight(self):
        """
        Test Exercise with missing weight value
        """
        with self.assertRaises(TypeError):
            Exercise(
                exercise_id="ex123", 
                day_id="day456",
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
                day_id="day456",
                exercise_type="Squat",
                sets=3, 
                reps=5, 
                weight=315.0,
                rpe=12.0  # RPE > 10 should raise ValueError
            )
    
    def test_negative_order(self):
        """
        Test Exercise with negative order value
        """
        with self.assertRaises(ValueError):
            Exercise(
            exercise_id="ex123",
            day_id="day456",
            exercise_type="Squat",
            sets=3,
            reps=5,
            weight=315.0,
            rpe=8.5,
            notes="Focus on bracing into belt",
            order=-1  # Invalid negative order
        )

if __name__ == "__main__": # pragma: no cover
    unittest.main()