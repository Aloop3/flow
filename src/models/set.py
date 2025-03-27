from typing import Dict, Any, Optional, Union

class Set:
    """
    Represents a single set within a completed exercise.
    
    This allows for tracking individual set performance rather than just aggregated exercise data.
    """
    def __init__(self, set_id: str, 
                 completed_exercise_id: str,
                 workout_id: str, 
                 set_number: int,
                 reps: int,
                 weight: float,
                 rpe: Optional[Union[int, float]] = None,
                 notes: Optional[str] = None,
                 completed: Optional[bool] = None):
        
        # Validation
        if not set_id:
            raise ValueError("set_id cannot be empty")
        if not completed_exercise_id:
            raise ValueError("completed_exercise_id cannot be empty")
        if not workout_id:
            raise ValueError("workout_id cannot be empty")
        if set_number <= 0:
            raise ValueError("set_number must be positive")
        if reps <= 0:
            raise ValueError("reps must be positive")
        if weight <= 0:
            raise ValueError("weight must be positive")
        if rpe is not None and (rpe < 0 or rpe > 10):
            raise ValueError("rpe must be between 0 and 10")

        self.set_id: str = set_id
        self.completed_exercise_id: str = completed_exercise_id
        self.workout_id: str = workout_id
        self.set_number: int = set_number
        self.reps: int = reps
        self.weight: float = weight
        self.rpe: Optional[Union[int, float]] = rpe
        self.notes: Optional[str] = notes
        self.completed: Optional[bool] = completed

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Set object to a dictionary for storage
        
        :return: Dictionary representation of the Set
        """
        result = {
            "set_id": self.set_id,
            "completed_exercise_id": self.completed_exercise_id,
            "workout_id": self.workout_id,
            "set_number": self.set_number,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "notes": self.notes
        }
        
        if self.completed is not None:
            result["completed"] = self.completed
            
        return result