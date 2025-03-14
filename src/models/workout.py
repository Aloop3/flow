from typing import Dict, List, Literal, Any, Optional
from .completed_exercise import CompletedExercise

class Workout:
    def __init__(self, workout_id: str, athlete_id: str, day_id: str, date: str, notes: Optional[str] = None, status: Literal["completed", "partial", "skipped"] = "completed"):
        self.workout_id: str = workout_id
        self.athlete_id: str = athlete_id
        self.day_id: str = day_id
        self.date: str = date
        self.notes: Optional[str] = notes
        self.status: Literal["completed", "partial", "skipped"] = status
        self.exercises: List[CompletedExercise] = [] # List of CompletedExercise objects

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workout_id": self.workout_id,
            "athlete_id": self.athlete_id,
            "day_id": self.day_id,
            "date": self.date,
            "notes": self.notes,
            "status": self.status,
            "exercises": [ex.to_dict() for ex in self.exercises]
        }