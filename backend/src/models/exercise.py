from typing import Dict, Any, Optional, Union, Literal, List
from .exercise_type import ExerciseType, ExerciseCategory


class Exercise:
    def __init__(
        self,
        exercise_id: str,
        workout_id: str,
        exercise_type: Union[str, ExerciseType],
        sets: int,
        reps: int,
        weight: float,
        rpe: Optional[Union[int, float]] = None,
        status: Optional[Literal["planned", "in_progress", "completed"]] = "planned",
        notes: Optional[str] = None,
        order: Optional[int] = None,
        exercise_category: Optional[Union[str, ExerciseCategory]] = None,
        sets_data: Optional[List[Dict[str, Any]]] = None,
        planned_sets_data: Optional[List[Dict[str, Any]]] = None,
    ):
        if not exercise_id:
            raise ValueError("exercise_id cannot be empty")
        if not workout_id:
            raise ValueError("workout_id cannot be empty")
        if sets <= 0:
            raise ValueError("sets must be positive")
        if reps <= 0:
            raise ValueError("reps must be positive")
        if weight < 0:
            raise ValueError("weight must be non-negative")
        if rpe is not None and (rpe < 0 or rpe > 10):
            raise ValueError("rpe must be between 0 and 10")
        if order is not None and order < 0:
            raise ValueError("order cannot be negative")
        if status not in {"planned", "in_progress", "completed"}:
            raise ValueError("status must be 'planned', 'in_progress', or 'completed'")

        if isinstance(exercise_type, str):
            self.exercise_type = ExerciseType(exercise_type)
        elif isinstance(exercise_type, ExerciseType):
            self.exercise_type = exercise_type
        else:
            raise TypeError("exercise_type must be a string or ExerciseType")

        self.is_predefined = self.exercise_type.is_predefined

        if isinstance(exercise_category, ExerciseCategory):
            self.exercise_category = exercise_category
        elif isinstance(exercise_category, str):
            try:
                self.exercise_category = ExerciseCategory(exercise_category.lower())
            except ValueError:
                self.exercise_category = ExerciseCategory.CUSTOM
        elif self.is_predefined:
            self.exercise_category = self.exercise_type.category
        else:
            self.exercise_category = ExerciseCategory.CUSTOM

        self.exercise_id: str = exercise_id
        self.workout_id: str = workout_id
        self.sets: int = sets
        self.reps: int = reps
        self.weight: float = weight
        self.rpe: Optional[Union[int, float]] = rpe
        self.status: Literal["planned", "in_progress", "completed"] = status
        self.notes: Optional[str] = notes
        self.order: Optional[int] = order
        self.sets_data: Optional[List[Dict[str, Any]]] = sets_data
        self.planned_sets_data: Optional[List[Dict[str, Any]]] = planned_sets_data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exercise_id": self.exercise_id,
            "workout_id": self.workout_id,
            "exercise_type": str(self.exercise_type),
            "exercise_category": self.exercise_category.value,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "status": self.status,
            "notes": self.notes,
            "order": self.order,
            "is_predefined": self.is_predefined,
            "sets_data": self.sets_data,
            "planned_sets_data": self.planned_sets_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Exercise":
        exercise_category = None
        if "exercise_category" in data:
            try:
                exercise_category = ExerciseCategory(data["exercise_category"].lower())
            except ValueError:
                exercise_category = ExerciseCategory.CUSTOM

        return cls(
            exercise_id=data["exercise_id"],
            workout_id=data["workout_id"],
            exercise_type=data["exercise_type"],
            sets=data["sets"],
            reps=data["reps"],
            weight=data["weight"],
            rpe=data.get("rpe"),
            status=data.get("status"),
            notes=data.get("notes"),
            order=data.get("order"),
            exercise_category=exercise_category,
            sets_data=data.get("sets_data"),
            planned_sets_data=data.get("planned_sets_data"),
        )

    def add_set_data(self, set_data: Dict[str, Any]) -> None:
        if self.sets_data is None:
            self.sets_data = []

        set_number = set_data.get("set_number")
        existing_set_index = next(
            (
                i
                for i, s in enumerate(self.sets_data)
                if s.get("set_number") == set_number
            ),
            None,
        )

        if existing_set_index is not None:
            self.sets_data[existing_set_index] = set_data
        else:
            self.sets_data.append(set_data)

        self.sets_data.sort(key=lambda x: x.get("set_number", 0))

    def get_set_data(self, set_number: int) -> Optional[Dict[str, Any]]:
        if self.sets_data is None:
            return None
        for set_data in self.sets_data:
            if set_data.get("set_number") == set_number:
                return set_data
        return None
