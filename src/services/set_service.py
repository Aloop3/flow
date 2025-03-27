import uuid
from typing import List, Dict, Any, Optional, Union
from src.repositories.set_repository import SetRepository
from src.models.exercise_set import ExerciseSet

class SetService:
    """
    Service for managing exercise sets
    """
    def __init__(self):
        self.set_repository: SetRepository = SetRepository()
    
    def get_set(self, set_id: str) -> Optional[ExerciseSet]:
        """
        Retrieve a set by ID
        
        :param set_id: ID of the set to retrieve
        :return: ExerciseSet object if found, else None
        """
        set_data = self.set_repository.get_set(set_id)
        
        if not set_data:
            return None
            
        return ExerciseSet(
            set_id=set_data["set_id"],
            completed_exercise_id=set_data["completed_exercise_id"],
            workout_id=set_data["workout_id"],
            set_number=set_data["set_number"],
            reps=set_data["reps"],
            weight=set_data["weight"],
            rpe=set_data.get("rpe"),
            notes=set_data.get("notes"),
            completed=set_data.get("completed")
        )
    
    def get_sets_for_exercise(self, completed_exercise_id: str) -> List[ExerciseSet]:
        """
        Retrieve all sets for a specific exercise
        
        :param completed_exercise_id: ID of the completed exercise
        :return: List of ExerciseSet objects
        """
        sets_data = self.set_repository.get_sets_by_exercise(completed_exercise_id)
        
        result = []
        for set_data in sets_data:
            result.append(ExerciseSet(
                set_id=set_data["set_id"],
                completed_exercise_id=set_data["completed_exercise_id"],
                workout_id=set_data["workout_id"],
                set_number=set_data["set_number"],
                reps=set_data["reps"],
                weight=set_data["weight"],
                rpe=set_data.get("rpe"),
                notes=set_data.get("notes"),
                completed=set_data.get("completed")
            ))
            
        # Sort by set number
        result.sort(key=lambda x: x.set_number)
        
        return result
    
    def create_set(self, completed_exercise_id: str, workout_id: str, 
                   set_number: int, reps: int, weight: float,
                   rpe: Optional[Union[int, float]] = None,
                   notes: Optional[str] = None,
                   completed: Optional[bool] = None) -> ExerciseSet:
        """
        Create a new exercise set
        
        :param completed_exercise_id: ID of the completed exercise this set belongs to
        :param workout_id: ID of the workout this set belongs to
        :param set_number: Number of this set within the exercise
        :param reps: Number of repetitions performed
        :param weight: Weight used for the set
        :param rpe: Rate of Perceived Exertion (RPE)
        :param notes: Optional notes for this set
        :param completed: Whether this set was completed
        :return: Created ExerciseSet object
        """
        set_id = str(uuid.uuid4())
        
        exercise_set = ExerciseSet(
            set_id=set_id,
            completed_exercise_id=completed_exercise_id,
            workout_id=workout_id,
            set_number=set_number,
            reps=reps,
            weight=weight,
            rpe=rpe,
            notes=notes,
            completed=completed
        )
        
        self.set_repository.create_set(exercise_set.to_dict())
        
        return exercise_set
    
    def update_set(self, set_id: str, update_data: Dict[str, Any]) -> Optional[ExerciseSet]:
        """
        Update an existing exercise set
        
        :param set_id: ID of the set to update
        :param update_data: Dictionary of attributes to update
        :return: Updated ExerciseSet object if found, else None
        """
        # Get the existing set
        existing_set = self.get_set(set_id)
        
        if not existing_set:
            return None
        
        # Update the set in the repository
        self.set_repository.update_set(set_id, update_data)
        
        # Get the updated set
        return self.get_set(set_id)
    
    def delete_set(self, set_id: str) -> bool:
        """
        Delete an exercise set
        
        :param set_id: ID of the set to delete
        :return: True if successful, False otherwise
        """
        result = self.set_repository.delete_set(set_id)
        
        return bool(result)
    
    def delete_sets_for_exercise(self, completed_exercise_id: str) -> int:
        """
        Delete all sets for a specific exercise
        
        :param completed_exercise_id: ID of the completed exercise
        :return: Number of sets deleted
        """
        return self.set_repository.delete_sets_by_exercise(completed_exercise_id)