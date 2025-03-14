import uuid
from typing import List, Dict, Any, Optional, Union
from src.repositories.exercise_repository import ExerciseRepository
from src.models.exercise import Exercise

class ExerciseService:
    def __init__(self):
        self.exercise_repository: ExerciseRepository = ExerciseRepository()

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """
        Retrieves an exercise by exercise_id

        :param exercise_id: The ID of the exercise to retrieve
        :return: The Exercise object if found, else None
        """
        exercise_data = self.exercise_repository.get_exercise(exercise_id)
        
        if exercise_data:
            return Exercise(**exercise_data)
        return None
    
    def get_exercises_for_day(self, day_id: str) -> List[Exercise]:
        """
        Retrieves all exercises for a given day_id

        :param day_id: The ID of the day to retrieve exercises for
        :return: A list of Exercise objects
        """
        exercises_data = self.exercise_repository.get_exercises_by_day(day_id)
        
        # Sort by order
        exercises_data.sort(key=lambda x: x.get("order", 999))
        return [Exercise(**exercise_data) for exercise_data in exercises_data]
    
    def create_exercise(self, day_id: str, exercise_ype: str, sets: int, reps: int, 
                        weight: Optional[float] = None, 
                        rpe: Optional[Union[int, float]] = None, 
                        notes: Optional[str] = None,
                        order: Optional[int] = None) -> Exercise:
        """
        Creates a new exercise

        :param day_id: The ID of the day to create the exercise for
        :param exercise_ype: The type of exercise
        :param sets: The number of sets
        :param reps: The number of reps
        :param weight: The weight used 
        :param rpe: The RPE rating 
        :param notes: Any additional notes
        :param order: The order of the exercise
        :return: The created Exercise object
        """
        # Find the highest order if not specified 
        if order is None:
            existing_exercises = self.exercise_repository.get_exercises_by_day(day_id)
            order = max([ex.get("order", 0) for ex in existing_exercises], default=0) + 1
        
        exercise = Exercise(
            exercise_id=str(uuid.uuid4()),
            day_id=day_id,
            exercise_type=exercise_ype,
            sets=sets,
            reps=reps,
            weight=weight,
            rpe=rpe,
            notes=notes,
            order=order
        )

        self.exercise_repository.create_exercise(exercise.to_dict())

        return exercise
    
    def update_exercise(self, exercise_id: str, update_data: Dict[str, Any]) -> Optional[Exercise]:
        """
        Updates the exercise data by exercise_id

        :param exercise_id: The ID of the exercise to update
        :param update_data: A dictionary containing the updated data
        :return: The updated Exercise object if found, else None
        """
        self.exercise_repository.update_exercise(exercise_id, update_data)
        return self.get_exercise(exercise_id)
    
    def delete_exercise(self, exercise_id: str) -> bool:
        """
        Deletes the exercise by exercise_id

        :param exercise_id: The ID of the exercise to delete
        :return: True if the exercise was successfully deleted, else False
        """
        response = self.exercise_repository.delete_exercise(exercise_id)
        return bool(response)
    
    def reorder_exercises(self, day_id: str, exercise_order: List[str]) -> List[Exercise]:
        """
        Reorder exercises for a day 

        :param day_id: The ID of the day to reorder exercises for
        :param exercise_order: A list of exercise IDs in the desired order
        :return: A list of reordered Exercise objects
        """
        # Get all exercises for the day
        exercises = self.get_exercises_for_day(day_id)
        exercise_dict = {ex.exercise_id: ex for ex in exercises}

        # Update order for each exercise
        for i, exercise_id in enumerate(exercise_order):
            if exercise_id in exercise_dict:
                self.update_exercise(exercise_id, {"order": i + 1})

        return self.get_exercises_for_day(day_id)
    