from typing import Dict, Any, Optional, Union

class CompletedExercise:
    def __init__(self, completed_id: str, workout_id: str, exercise_id: str, actual_sets: int, actual_reps: int, actual_weight: Optional[float] = None, actual_rpe: Optional[Union[int, float]] = None, notes: Optional[str] = None):
        self.completed_id: str = completed_id
        self.workout_id: str = workout_id
        self.exercise_id: str = exercise_id # Reference to planned exercise
        self.actual_sets: int = actual_sets
        self.actual_reps: int = actual_reps
        self.actual_weight: Optional[float] = actual_weight
        self.actual_rpe: Optional[Union[int, float]] = actual_rpe
        self.notes: Optional[str] = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "completed_id": self.completed_id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "actual_sets": self.actual_sets,
            "actual_reps": self.actual_reps,
            "actual_weight": self.actual_weight,
            "actual_rpe": self.actual_rpe,
            "notes": self.notes
        }