from typing import Dict, Any, Optional, Union
from src.models.exercise_type import ExerciseType, ExerciseCategory


class Exercise:
    def __init__(self, exercise_id: str, day_id: str, exercise_type: Union[str, ExerciseType], sets: int, reps: int, weight: float, rpe: Optional[Union[int, float]] = None, notes: Optional[str] = None, order: Optional[int] = None):
        # Validate IDs
        if not exercise_id:
            raise ValueError("exercise_id cannot be empty")
        if not day_id:
            raise ValueError("day_id cannot be empty")
            
        # Validate numerical values
        if sets <= 0:
            raise ValueError("sets must be positive")
        if reps <= 0:
            raise ValueError("reps must be positive")
        if weight <= 0:
            raise ValueError("weight must be positive")
        if rpe is not None and (rpe < 0 or rpe > 10):
            raise ValueError("rpe must be between 0 and 10")
        if order is not None and order < 0:
            raise ValueError("order cannot be negative")
        
        # Handle exercise_type parameter
        if isinstance(exercise_type, str):
            self.exercise_type = ExerciseType(exercise_type)
        elif isinstance(exercise_type, ExerciseType):
            self.exercise_type = exercise_type
        else:
            raise TypeError("exercise_type must be a string or ExerciseType object")

        self.exercise_id: str = exercise_id
        self.day_id: str = day_id
        self.sets: int = sets # Planned sets
        self.reps: int = reps # Planned reps
        self.weight: float = weight # Planned weight
        self.rpe: Optional[Union[int, float]] = rpe # Planned RPE
        self.notes: Optional[str] = notes
        self.order: Optional[int] = order # Sequence in workout
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Exercise object to a dictionary for storage
        """
        return {
            "exercise_id": self.exercise_id,
            "day_id": self.day_id,
            "exercise_type": self.exercise_type.name,
            "exercise_category": self.exercise_type.category.value,
            "is_predefined": self.exercise_type.is_predefined,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "notes": self.notes,
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Exercise":
        """
        Create an Exercise object from a dictionary

        :param data: Dictionary containing exercise data
        :return: Exercise object
        """
        # Create ExerciseType instance with category if provided
        exercise_category = (
            ExerciseCategory(data["exercise_category"]) if "exercise_category" in data else None
        )
        exercise_type = ExerciseType(data["exercise_type"], category=exercise_category)

        return cls(
            exercise_id=data["exercise_id"],
            day_id=data["day_id"],
            exercise_type=exercise_type,
            sets=data["sets"],
            reps=data["reps"],
            weight=data["weight"],
            rpe=data.get("rpe"),
            notes=data.get("notes"),
            order=data.get("order")
        )