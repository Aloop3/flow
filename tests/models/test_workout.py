import unittest
from src.models.workout import Workout
from src.models.completed_exercise import CompletedExercise
from src.models.set import Set

class TestWorkoutModel(unittest.TestCase):
    """
    Test suite for Workout model
    """

    def test_workout_initialization(self):
        """
        Test Workout model initialization with all attributes
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12",
            notes="Solid session",
            status="completed"
        )

        self.assertEqual(workout.workout_id, "workout123")
        self.assertEqual(workout.athlete_id, "athlete456")
        self.assertEqual(workout.day_id, "day789")
        self.assertEqual(workout.date, "2025-03-12")
        self.assertEqual(workout.notes, "Solid session")
        self.assertEqual(workout.status, "completed")
        self.assertEqual(workout.exercises, []) # Empty list by default

    def test_workout_initialization_without_optional_attributes(self):
        """
        Test Workout model initialization without optional attributes
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12"
        )

        self.assertEqual(workout.workout_id, "workout123")
        self.assertEqual(workout.athlete_id, "athlete456")
        self.assertEqual(workout.day_id, "day789")
        self.assertEqual(workout.date, "2025-03-12")
        self.assertIsNone(workout.notes)
        self.assertEqual(workout.status, "partial") # partial
        self.assertEqual(workout.exercises, []) # Empty list by default
    
    def test_add_exercise(self):
        """
        Test adding a completed exercise to a workout
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15"
        )

        # Create a completed exercise
        exercise = CompletedExercise(
            completed_id="comp123",
            workout_id="workout123",
            exercise_id="ex789"
        )

        # Add the exercise to the workout
        workout.add_exercise(exercise)

        # Assert the exercise was added
        self.assertEqual(len(workout.exercises), 1)
        self.assertEqual(workout.exercises[0].completed_id, "comp123")
    
    def test_get_exercise(self):
        """
        Test getting an exercise by ID
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15"
        )

        # Create exercises with different IDs
        exercise1 = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1"
        )

        exercise2 = CompletedExercise(
            completed_id="comp2",
            workout_id="workout123",
            exercise_id="ex2"
        )

        workout.add_exercise(exercise1)
        workout.add_exercise(exercise2)

        # Get an exercise by ID
        result = workout.get_exercise("ex1")

        # Assert we got the right exercise
        self.assertIsNotNone(result)
        self.assertEqual(result.exercise_id, "ex1")

        # Test getting a non-existent exercise
        self.assertIsNone(workout.get_exercise("nonexistent"))
    
    def test_remove_exercise(self):
        """
        Test removing an exercise by ID
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15"
        )

        # Create exercises with different IDs
        exercise1 = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1"
        )

        exercise2 = CompletedExercise(
            completed_id="comp2",
            workout_id="workout123",
            exercise_id="ex2"
        )

        workout.add_exercise(exercise1)
        workout.add_exercise(exercise2)

        # Remove an exercise
        result = workout.remove_exercise("ex1")

        # Assert the exercise was removed
        self.assertTrue(result)
        self.assertEqual(len(workout.exercises), 1)
        self.assertEqual(workout.exercises[0].exercise_id, "ex2")

        # Test removing a non-existent exercise
        self.assertFalse(workout.remove_exercise("nonexistent"))
    
    def test_status_calculation(self):
        """
        Test workout status calculation based on exercise completion
        """
        
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15"
        )

        # With no explicit status, default should be 'partial'
        self.assertEqual(workout.status, "partial")

        # Create and add exercises doesn't change status
        exercise1 = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1"
        )

        # Add a completed exercise
        set1 = Set(
            set_id="set1",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=225.0,
            completed=True
        )
        exercise1.add_set(set1)
        workout.add_exercise(exercise1)

        # Still 'partial' since status not explicitly set
        self.assertEqual(workout.status, "partial")

        # Explicitly set to completed
        workout.status = "completed"
        self.assertEqual(workout.status, "completed")

        # Add another exercise doesn't change explicit status
        exercise2 = CompletedExercise(
            completed_id="comp2",
            workout_id="workout123",
            exercise_id="ex2"
        )
        
        set2 = Set(
            set_id="set2",
            completed_exercise_id="comp2",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=135.0,
            completed=False
        )
        
        exercise2.add_set(set2)
        workout.add_exercise(exercise2)

        # Status remains what it was explicitly set to
        self.assertEqual(workout.status, "completed")
    
    def test_status_override(self):
        """
        Test explicitly setting workout status
        """
        
        workout = Workout(
        workout_id="workout123",
        athlete_id="athlete456",
        day_id="day789",
        date="2025-03-15"
        )
        
        # Create fully completed exercise
        exercise = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1"
        )
        
        set1 = Set(
            set_id="set1",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=225.0,
            completed=True
        )
        exercise.add_set(set1)
        workout.add_exercise(exercise)
        
        # Status should be partial by default (changed from completed)
        self.assertEqual(workout.status, "partial")
        
        # Explicitly set to completed
        workout.status = "completed"
        self.assertEqual(workout.status, "completed")
        
        # Explicitly set to skipped
        workout.status = "skipped"
        self.assertEqual(workout.status, "skipped")
        
        # Test invalid status
        with self.assertRaises(ValueError):
            workout.status = "invalid_status"
    
    def test_calculate_volume(self):
        """
        Test calculating workout volume
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-15"
        )
        
        # Create exercises with sets
        bench_exercise = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="bench"
        )
        
        # 3 sets of bench, 5 reps at 225 = 3375 total volume
        for i in range(1, 4):
            bench_set = Set(
                set_id=f"set{i}",
                completed_exercise_id="comp1",
                workout_id="workout123",
                set_number=i,
                reps=5,
                weight=225.0,
                completed=True
            )
            bench_exercise.add_set(bench_set)
        
        # Squat exercise with some incomplete sets
        squat_exercise = CompletedExercise(
            completed_id="comp2",
            workout_id="workout123",
            exercise_id="squat"
        )
        
        # 2 completed sets + 1 incomplete set of squats
        squat_set1 = Set(
            set_id="squat1",
            completed_exercise_id="comp2",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=315.0,
            completed=True
        )
        
        squat_set2 = Set(
            set_id="squat2",
            completed_exercise_id="comp2",
            workout_id="workout123",
            set_number=2,
            reps=5,
            weight=315.0,
            completed=True
        )
        
        squat_set3 = Set(
            set_id="squat3",
            completed_exercise_id="comp2",
            workout_id="workout123",
            set_number=3,
            reps=5,
            weight=315.0, 
            completed=False  # Not completed, should not count in volume
        )
        
        squat_exercise.add_set(squat_set1)
        squat_exercise.add_set(squat_set2)
        squat_exercise.add_set(squat_set3)
        
        workout.add_exercise(bench_exercise)
        workout.add_exercise(squat_exercise)
        
        # Expected volume: bench (5*225*3) + squat (5*315*2) = 3375 + 3150 = 6525
        self.assertEqual(workout.calculate_volume(), 6525.0)
    
    def test_to_dict(self):
        """
        Test Workout model to_dict method
        """
        workout = Workout(
            workout_id="workout123",
            athlete_id="athlete456",
            day_id="day789",
            date="2025-03-12",
            notes="Solid session"
        )

        # Add a completed exercise with sets
        exercise = CompletedExercise(
            completed_id="comp1",
            workout_id="workout123",
            exercise_id="ex1",
            notes="Felt strong"
        )
        
        # Add a set to the exercise
        exercise_set = Set(
            set_id="set1",
            completed_exercise_id="comp1",
            workout_id="workout123",
            set_number=1,
            reps=5,
            weight=225.0,
            completed=True,
            rpe=8.0
        )
        
        exercise.add_set(exercise_set)
        workout.add_exercise(exercise)

        workout_dict = workout.to_dict()

        self.assertEqual(workout_dict['workout_id'], "workout123")
        self.assertEqual(workout_dict['athlete_id'], "athlete456")
        self.assertEqual(workout_dict['day_id'], "day789")
        self.assertEqual(workout_dict['date'], "2025-03-12")
        self.assertEqual(workout_dict['notes'], "Solid session")
        self.assertEqual(workout_dict['status'], "partial")
        self.assertEqual(workout_dict['total_volume'], 1125.0)  # 5 * 225 = 1125

        # Check exercises
        self.assertEqual(len(workout_dict['exercises']), 1)
        self.assertEqual(workout_dict['exercises'][0]['completed_id'], "comp1")
        self.assertEqual(workout_dict['exercises'][0]['notes'], "Felt strong")
        
        # Check sets in the exercise
        self.assertEqual(len(workout_dict['exercises'][0]['sets']), 1)
        self.assertEqual(workout_dict['exercises'][0]['sets'][0]['set_id'], "set1")
        self.assertEqual(workout_dict['exercises'][0]['sets'][0]['reps'], 5)
        self.assertEqual(workout_dict['exercises'][0]['sets'][0]['weight'], 225.0)
        self.assertEqual(workout_dict['exercises'][0]['sets'][0]['rpe'], 8.0)


if __name__ == "__main__": # pragma: no cover
    unittest.main()