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
        status: Optional[Literal["planned", "completed", "skipped"]] = "planned",
        notes: Optional[str] = None,
        order: Optional[int] = None,
        exercise_category: Optional[ExerciseCategory] = None,
        is_predefined: Optional[bool] = None,
        sets_data: Optional[List[Dict[str, Any]]] = None,
    ):
        # Validate IDs
        if not exercise_id:
            raise ValueError("exercise_id cannot be empty")
        if not workout_id:
            raise ValueError("workout_id cannot be empty")

        # Validate numerical values
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

        # Handle exercise_type parameter
        if isinstance(exercise_type, str):
            self.exercise_type = ExerciseType(exercise_type)
        elif isinstance(exercise_type, ExerciseType):
            self.exercise_type = exercise_type
        else:
            raise TypeError("exercise_type must be a string or ExerciseType object")

        # Use the is_predefined from ExerciseType
        self.is_predefined = self.exercise_type.is_predefined

        # Handle exercise_category based on the type
        if exercise_category is not None:
            if isinstance(exercise_category, str):
                # Convert string to ExerciseCategory
                for category in list(ExerciseCategory):
                    if category.value == exercise_category:
                        self.exercise_category = category
                        break
                else:
                    self.exercise_category = ExerciseCategory.CUSTOM
            else:
                self.exercise_category = exercise_category
        elif self.is_predefined:
            # For predefined exercises, get category from ExerciseType
            self.exercise_category = self.exercise_type.category
        else:
            # For custom exercises
            self.exercise_category = ExerciseCategory.CUSTOM

        self.exercise_id: str = exercise_id
        self.workout_id: str = workout_id
        self.sets: int = sets  # Planned sets
        self.reps: int = reps  # Planned reps
        self.weight: float = weight  # Planned weight
        self.rpe: Optional[Union[int, float]] = rpe  # Planned RPE
        self.status: Literal["planned", "completed", "skipped"] = status
        self.notes: Optional[str] = notes
        self.order: Optional[int] = order  # Sequence in workout
        self.sets_data: Optional[List[Dict[str, Any]]] = sets_data

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Exercise object to a dictionary for storage
        """
        result = {
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
        }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Exercise":
        """
        Create an Exercise object from a dictionary

        :param data: Dictionary containing exercise data
        :return: Exercise object
        """
        # Handle exercise category if provided
        exercise_category = None
        if "exercise_category" in data:
            category_value = data["exercise_category"]
            for category in list(ExerciseCategory):
                if category.value == category_value:
                    exercise_category = category
                    break

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
            is_predefined=data.get("is_predefined"),
            sets_data=data.get("sets_data"),
        )

    def add_set_data(self, set_data: Dict[str, Any]) -> None:
        """
        Add set data to the exercise

        :param set_data: Dictionary containing set information
        """
        # Initialize sets_data if None
        if self.sets_data is None:
            self.sets_data = []

        # Check if set with this number already exists
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
            # Update existing set
            self.sets_data[existing_set_index] = set_data
        else:
            # Add new set
            self.sets_data.append(set_data)

        # Sort sets by set number
        self.sets_data.sort(key=lambda x: x.get("set_number", 0))

    def get_set_data(self, set_number: int) -> Optional[Dict[str, Any]]:
        """
        Get set data by set number

        :param set_number: Number of the set to retrieve
        :return: Set data if found, else None
        """
        for set_data in self.sets_data:
            if set_data.get("set_number") == set_number:
                return set_data
        return None
