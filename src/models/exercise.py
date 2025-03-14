from typing import Dict, Any, Optional, Union

class Exercise:
    def __init__(self, exercise_id: str, day_id: str, exercise_type: str, sets: int, reps: int, weight: Optional[float] = None, rpe: Optional[Union[int, float]] = None, notes: Optional[str] = None, order: Optional[int] = None):
        self.exercise_id: str = exercise_id
        self.day_id: str = day_id
        self.exercise_type: str = exercise_type # "squat", "bench", "deadlift"
        self.sets: int = sets # Planned sets
        self.reps: int = reps # Planned reps
        self.weight: Optional[float] = weight # Planned weight
        self.rpe: Optional[Union[int, float]] = rpe # Planned RPE
        self.notes: Optional[str] = notes
        self.order: Optional[int] = order # Sequence in workout
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "exercise_id": self.exercise_id,
            "day_id": self.day_id,
            "exercise_type": self.exercise_type,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "notes": self.notes,
            "order": self.order
        }