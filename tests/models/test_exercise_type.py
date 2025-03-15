import unittest
from src.models.exercise_type import ExerciseType, ExerciseCategory

class TestExerciseType(unittest.TestCase):
    """
    Test suit for the ExerciseType model
    """
    def test_predefined_exercise(self):
        """
        Test creation of a predefined exercise
        """
        # Barbell exercise
        squat = ExerciseType("Squat")
        self.assertEqual(squat.name, "Squat")
        self.assertEqual(squat.category, ExerciseCategory.BARBELL)
        self.assertTrue(squat.is_predefined)

        # Dumbbell exercise
        db_press = ExerciseType("Dumbbell Bench Press")
        self.assertEqual(db_press.name, "Dumbbell Bench Press")
        self.assertEqual(db_press.category, ExerciseCategory.DUMBBELL)
        self.assertTrue(db_press.is_predefined)

        # Cable exercise
        lat_pulldown = ExerciseType("Lat Pulldown")
        self.assertEqual(lat_pulldown.name, "Lat Pulldown")
        self.assertEqual(lat_pulldown.category, ExerciseCategory.CABLE)
        self.assertTrue(lat_pulldown.is_predefined)

    def test_custom_exercise_with_category(self):
        """
        Test creation of a custom exercise with specified category
        """
        custom = ExerciseType("Zercher Squat", ExerciseCategory.BARBELL)
        self.assertEqual(custom.name, "Zercher Squat")
        self.assertEqual(custom.category, ExerciseCategory.BARBELL)
        self.assertFalse(custom.is_predefined)

    def test_custom_exercise_without_category(self):
        """
        Test creation of a custom exercise without specified category (defaults to CUSTOM)
        """
        custom = ExerciseType("Unique Exercise")
        self.assertEqual(custom.name, "Unique Exercise")
        self.assertEqual(custom.category, ExerciseCategory.CUSTOM)
        self.assertFalse(custom.is_predefined)
    
    def test_whitespace_handling(self):
        """
        Test that whitespace is handled correctly in exercise names
        """
        deadlift = ExerciseType("   Deadlift   ")
        self.assertEqual(deadlift.name, "Deadlift")
        self.assertEqual(deadlift.category, ExerciseCategory.BARBELL)
        self.assertTrue(deadlift.is_predefined)
    
    def test_get_all_predefined(self):
        """
        Test retrieving all predefined exercises
        """
        all_exercises = ExerciseType.get_all_predefined()
        self.assertTrue(isinstance(all_exercises, list))
        self.assertIn("Bench Press", all_exercises)
        self.assertIn("Pull Ups", all_exercises)
        self.assertIn("Machine Low Row", all_exercises)
    
    def test_get_by_category(self):
        """
        Test retrieving exercises by category
        """
        barbell_exercises = ExerciseType.get_by_category(ExerciseCategory.BARBELL)
        self.assertTrue(isinstance(barbell_exercises, list))
        self.assertIn("Squat", barbell_exercises)
        self.assertIn("Bench Press", barbell_exercises)
        self.assertNotIn("Pull Ups", barbell_exercises) # Not a barbell exercise

        bodyweight_exercises = ExerciseType.get_by_category(ExerciseCategory.BODYWEIGHT)
        self.assertIn("Pull Ups", bodyweight_exercises)
        self.assertNotIn("Squat", bodyweight_exercises) # Not a bodyweight exercise

    def test_is_valid_predefined(self):
        """
        Test checking if an exercise name is a valid predefined exercise
        """
        self.assertTrue(ExerciseType.is_valid_predefined("Squat"))
        self.assertTrue(ExerciseType.is_valid_predefined("Deadlift"))
        self.assertFalse(ExerciseType.is_valid_predefined("Not an exercise"))
        self.assertTrue(ExerciseType.is_valid_predefined("   Squat   ")) # Whitespace is handled
    
    def test_get_categories(self):
        """
        Test retrieving all exercise categories
        """
        categories = ExerciseType.get_categories()
        self.assertEqual(len(categories), 6) # BARBELL, DUMBBELL, BODYWEIGHT, MACHINE, CABLE, CUSTOM
        self.assertIn(ExerciseCategory.BARBELL, categories)
        self.assertIn(ExerciseCategory.CUSTOM, categories)
        self.assertNotIn("Calisthenics", categories)
    
    def test_string_representation(self):
        """
        Test string representation of ExerciseType
        """
        squat = ExerciseType("Squat")
        self.assertEqual(str(squat), "Squat")
    
    def test_equality(self):
        """
        Test equality comparison between ExerciseType objects
        """
        squat1 = ExerciseType("Squat")
        squat2 = ExerciseType("Squat")
        bench = ExerciseType("Bench Press")

        self.assertEqual(squat1, squat2)
        self.assertNotEqual(squat1, bench)

        # Custom exercise with same name should be equal
        custom_squat = ExerciseType("Squat", ExerciseCategory.CUSTOM)
        self.assertEqual(squat1, custom_squat)

        # Not equal to other types
        self.assertNotEqual(squat1, "Squat")

if __name__ == "__main__": # pragma: no cover
    unittest.main()