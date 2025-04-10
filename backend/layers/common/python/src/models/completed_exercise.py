from typing import Dict, List, Any, Optional
from .set import Set


class CompletedExercise:
    """
    Represents a completed exercise within a workout.

    This model tracks an exercise that has been performed as part of a workout,
    including all the individual sets performed.
    """

    def __init__(
        self,
        completed_id: str,
        workout_id: str,
        exercise_id: str,
        notes: Optional[str] = None,
    ):
        """
        Initialize a CompletedExercise instance.

        :param completed_id: Unique identifier for this completed exercise
        :param workout_id: ID of the workout this exercise belongs to
        :param exercise_id: ID of the exercise template/definition this is based on
        :param notes: Optional notes about the exercise performance
        """
        if not completed_id:
            raise ValueError("completed_id cannot be empty")
        if not workout_id:
            raise ValueError("workout_id cannot be empty")
        if not exercise_id:
            raise ValueError("exercise_id cannot be empty")

        self.completed_id: str = completed_id
        self.workout_id: str = workout_id
        self.exercise_id: str = exercise_id
        self.notes: Optional[str] = notes
        self.sets: List[Set] = []

    def add_set(self, set_obj: Set) -> None:
        """
        Add a set to this completed exercise

        :param set_obj: The Set object to add
        """
        self.sets.append(set_obj)

        # Sort sets by set_number to maintain order
        self.sets.sort(key=lambda s: s.set_number)

    def get_set(self, set_id: str) -> Optional[Set]:
        """
        Get a set by its ID

        :param set_id: The ID of the set to find
        :return: The Set if found, None otherwise
        """
        for set_obj in self.sets:
            if set_obj.set_id == set_id:
                return set_obj
        return None

    def update_set(self, set_id: str, **update_data) -> bool:
        """
        Update a set in this exercise by its ID

        :param set_id: ID of the set to update
        :param update_data: Data to update on the set
        :return: True if set was found and updated, False otherwise
        """
        for exercise_set in self.sets:
            if exercise_set.set_id == set_id:
                # Update set attributes
                for key, value in update_data.items():
                    if hasattr(exercise_set, key):
                        setattr(exercise_set, key, value)
                return True
        return False

    def remove_set(self, set_id: str) -> bool:
        """
        Remove a set by its ID

        :param set_id: The ID of the set to remove
        :return: True if the set was found and removed, False otherwise
        """
        for i, set_obj in enumerate(self.sets):
            if set_obj.set_id == set_id:
                self.sets.pop(i)
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the CompletedExercise to a dictionary

        :return: Dictionary representation of the CompletedExercise
        """
        result = {
            "completed_id": self.completed_id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "notes": self.notes,
            "sets": [set_obj.to_dict() for set_obj in self.sets],
        }
        return result

    def calculate_volume(self) -> float:
        """
        Calculate the total volume for this exercise based on sets

        Volume = sum(sets * reps * weight)

        :return: The total volume in weight units
        """
        if not self.sets:
            return 0.0

        total_volume = 0.0
        for exercise_set in self.sets:
            volume = exercise_set.reps * exercise_set.weight
            total_volume += volume

        return total_volume
