import uuid
import datetime as dt
from typing import Dict, List, Any, Optional
from src.repositories.workout_repository import WorkoutRepository
from src.repositories.day_repository import DayRepository
from src.repositories.exercise_repository import ExerciseRepository
from src.models.workout import Workout
from src.models.completed_exercise import CompletedExercise

class WorkoutService:
    def __init__(self):
        self.workout_repository: WorkoutRepository = WorkoutRepository()
        self.day_repository: DayRepository = DayRepository()
        self.exercise_repository: ExerciseRepository = ExerciseRepository()

    def get_workout(self, workout_id: str) -> Optional[Workout]:
        """
        Retrieves a workout by workout_id

        :param workout_id: The ID of the workout to retrieve
        :return: The Workout object if found, else None
        """
        workout_data = self.workout_repository.get_workout(workout_id)

        if not workout_data:
            return None
        
        # Iterate through key-value pair in workout data only for pairs where the key is not "exercises"
        workout = Workout(**{k: v for k, v in workout_data.items() if k != "exercises"})

        # Load completed exercises if they exist
        if "exercises" in workout_data:
            for exercise_data in workout_data["exercises"]:
                workout.exercises.append(CompletedExercise(**exercise_data))

        return workout
    
    def get_workout_by_day(self, athlete_id: str, day_id: str) -> Optional[Workout]:
        """
        Retrieves a workout by athlete_id and day_id

        :param athlete_id: The ID of the athlete
        :param day_id: The ID of the day
        :return: The Workout object if found, else None
        """
        workout_data = self.workout_repository.get_workout_by_day(athlete_id, day_id)

        if not workout_data:
            return None

        # Iterate through key-value pair in workout data only for pairs where the key is not "exercises"
        workout = Workout(**{k: v for k, v in workout_data.items() if k != "exercises"})

        # Load completed exercises if they exist
        if "exercises" in workout_data:
            for exercise_data in workout_data["exercises"]:
                workout.exercises.append(CompletedExercise(**exercise_data))

        return workout
    
    def log_workout(self, athlete_id: str, day_id: str, date: str, 
                    completed_exercises: List[Dict[str, Any]], 
                    notes: Optional[str] = None, 
                    status: str = "completed") -> Workout:
        """
        Logs a completed workout for an athlete

        :param athlete_id: The ID of the athlete
        :param day_id: The ID of the day
        :param date: The date of the workout in ISO formate
        :param completed_exercises: A list of completed exercises
        :param notes: Optional notes for the workout
        :param status: The status of the workout ("complete", "partial", "skipped")
        :return: The created Workout object
        """
        VALID_STATUS = {"completed", "partial", "skipped"}

        if status not in VALID_STATUS:
            raise ValueError(f"Invalid status. Must be one of {VALID_STATUS}")
        
        existing = self.get_workout_by_day(athlete_id, day_id)

        if existing:
            # Update existing workout instead
            return self.update_workout(
                existing.workout_id,
                {
                    "date": date,
                    "notes": notes,
                    "status": status,
                    "exercises": completed_exercises
                }
            )
        
        # Create a new workout
        workout = Workout(
            workout_id=str(uuid.uuid4()),
            athlete_id=athlete_id,
            day_id=day_id,
            date=date,
            notes=notes,
            status=status
        )

        # Add completed exercises
        for i, exercise_data in enumerate(completed_exercises):
            completed = CompletedExercise(
                completed_id=str(uuid.uuid4()),
                workout_id=workout.workout_id,
                exercise_id=exercise_data.get("exercise_id"),
                actual_sets=exercise_data.get("actual_sets"),
                actual_reps=exercise_data.get("actual_reps"),
                actual_weight=exercise_data.get("actual_weight"),
                actual_rpe=exercise_data.get("actual_rpe"),
                notes=exercise_data.get("notes")
            )

            workout.exercises.append(completed)

        # Save everything in one operation
        workout_dict = workout.to_dict()
        self.workout_repository.create_workout(workout_dict)

        return workout
    
    def update_workout(self, workout_id: str, update_data: Dict[str, Any]) -> Optional[Workout]:
        """
        Updates a workout by workout_id

        :param workout_id: The ID of the workout to update
        :param update_data: The data to update the workout with
        :return: The updated Workout object if found, else None
        """
        self.workout_repository.update_workout(workout_id, update_data)
        return self.get_workout(workout_id)
    
    def delete_workout(self, workout_id: str) -> bool:
        """
        Deletes a workout by workout_id

        :param workout_id: The ID of the workout to delete
        :return: True if the workout was deleted, else False
        """
        response = self.workout_repository.delete_workout(workout_id)

        return bool(response)