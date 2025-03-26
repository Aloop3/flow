from typing import Dict, Any, Optional, Union

class ExerciseSet:
    def __init__(self, set_id: str, exercise_id: str, set_number: int, reps: int, weight: float, completed: bool = False, rpe: Optional[Union[int, float]] = None, notes: Optional[str] = None):
        """
        Initialize an exercise set.
        
        :param set_id: Unique identifier for the set
        :param exercise_id: ID of the parent exercise
        :param set_number: The number of this set within the exercise (e.g. 1 for first set)
        :param reps: Number of repetitions
        :param weight: Weight used (in pounds/kg)
        :param completed: Whether this set has been completed
        :param rpe: Rate of Perceived Exertion (0-10 scale)
        :param notes: Optional notes for this set
        """

        # Validation
        if not set_id:
            raise ValueError("set_id cannot be empty")
        if not exercise_id:
            raise ValueError("exercise_id cannot be empty")
        if set_number <= 0:
            raise ValueError("set_number must be positive")
        if reps <= 0:
            raise ValueError("reps must be positive")
        if weight <= 0:
            raise ValueError("weight must be positive")
        if rpe is not None and (rpe < 0  or rpe > 10):
            raise ValueError("rpe must be between 0 and 10")

        self.set_id: str = set_id
        self.exercise_id: str = exercise_id
        self.set_number: int = set_number
        self.reps: int = reps
        self.weight: float = weight
        self.rpe: Optional[Union[int, float]] = rpe
        self.notes: Optional[str] = notes
        self.completed: bool = completed
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the set to a dictionary for serialization.
        
        :return: Dictionary representation of the set
        """

        return {
            "set_id": self.set_id,
            "exercise_id": self.exercise_id,
            "set_number": self.set_number,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "notes": self.notes,
            "completed": self.completed
        }