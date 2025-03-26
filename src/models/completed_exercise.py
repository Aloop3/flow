from typing import Dict, Any, Optional, List, Union
from .exercise_set import ExerciseSet

class CompletedExercise:
    def __init__(self, completed_id: str, workout_id: str, exercise_id: str, notes: Optional[str] = None):
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
        self.sets: List[ExerciseSet] = []
        self.notes: Optional[str] = notes

    def add_set(self, exercise_set: ExerciseSet) -> None:
        """
        Add set to exercise set
        
        :param exercise_set: ExerciseSet object
        :return: None
        """
        self.sets.append(exercise_set)

    def update_set(self, set_id: str, completed: bool, reps: Optional[int] = None, weight: Optional[float] = None, rpe: Optional[Union[int, float]] = None, notes: Optional[str] = None):
        """ 
        Update set
        
        :param set_id: str
        :param completed: bool
        :param reps: int
        :param weight: float
        :param rpe: int
        :param notes: str
        :return: None
        """

        for new_set in self.sets:
            if new_set.set_id == set_id:
                if reps is not None:
                    new_set.reps = reps
                if weight is not None:
                    new_set.weight = weight
                if rpe is not None:
                    new_set.rpe = rpe
                if notes is not None:
                    new_set.notes = notes
                new_set.completed = completed
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "completed_id": self.completed_id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "sets": [set.to_dict() for set in self.sets],
            "notes": self.notes
        }