from typing import Dict, Any, Optional, Union, List
from .exercise_set import ExerciseSet

class CompletedExercise:
    """
    Represents a completed exercise in a workout, with support for individual sets.
    """
    def __init__(self, completed_id: str, workout_id: str, exercise_id: str, 
                 notes: Optional[str] = None):
        # Validation
        if not completed_id:
            raise ValueError("completed_id cannot be empty")
        if not workout_id:
            raise ValueError("workout_id cannot be empty")
        if not exercise_id:
            raise ValueError("exercise_id cannot be empty")

        self.completed_id: str = completed_id
        self.workout_id: str = workout_id
        self.exercise_id: str = exercise_id
        self.notes: Optional[str] = notes
        
        # Field for set-level tracking
        self.sets: List[ExerciseSet] = []

    def add_set(self, exercise_set: ExerciseSet) -> None:
        """
        Add an ExerciseSet to this completed exercise
        
        :param exercise_set: The ExerciseSet to add
        """
        # Validate the set belongs to this exercise
        if exercise_set.completed_exercise_id != self.completed_id:
            raise ValueError("Set does not belong to this exercise")
            
        # Add the set
        self.sets.append(exercise_set)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the CompletedExercise object to a dictionary for storage
        
        :return: Dictionary representation of the CompletedExercise
        """
        result = {
            "completed_id": self.completed_id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "notes": self.notes
        }
        
        # Include sets if available
        if self.sets:
            result["sets"] = [exercise_set.to_dict() for exercise_set in self.sets]
            
        return result
    
    def update_set(self, set_id: str, **update_data) -> bool:
        """
        Update a set in this exercise by its ID
        
        :param set_id: ID of the set to update
        :param update_data: Data to update on the set
        :return: True if set was found and updated, False otherwise
        """
        for exercise_set in self.sets:
            if exercise_set.set_id == set_id:
                # Update set attributes
                for key, value in update_data.items():
                    if hasattr(exercise_set, key):
                        setattr(exercise_set, key, value)
                return True
        return False

    def calculate_volume(self) -> float:
        """
        Calculate the total volume for this exercise based on sets
        
        Volume = sum(sets * reps * weight)
        
        :return: The total volume in weight units
        """
        if not self.sets:
            return 0.0
            
        total_volume = 0.0
        for exercise_set in self.sets:
            volume = exercise_set.reps * exercise_set.weight
            total_volume += volume
        
        return total_volume