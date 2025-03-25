from typing import Dict, Any, Optional, Union

class ExerciseSet:
    def __init__(self, set_id: str, completed_id: str, set_number: int, reps: int, weight: float, completed: bool = False, rpe: Optional[Union[int, float]] = None, notes: Optional[str] = None):
        if not set_id:
            raise ValueError("set_id cannot be empty")
        if not completed_id:
            raise ValueError("completed_id cannot be empty")
        if set_number <= 0:
            raise ValueError("set_number must be positive")
        if reps <= 0:
            raise ValueError("reps must be positive")
        if weight <= 0:
            raise ValueError("weight must be positive")
        if rpe is not None and (rpe < 0  or rpe > 10):
            raise ValueError("rpe must be between 0 and 10")

        self.set_id: str = set_id
        self.completed_id: str = completed_id
        self.set_number: int = set_number
        self.reps: int = reps
        self.weight: float = weight
        self.rpe: Optional[Union[int, float]] = rpe
        self.notes: Optional[str] = notes
        self.completed: bool = completed
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_id": self.set_id,
            "completed_id": self.completed_id,
            "set_number": self.set_number,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "notes": self.notes,
            "completed": self.completed
        }