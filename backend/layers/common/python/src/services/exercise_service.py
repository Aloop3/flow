import uuid
from typing import List, Dict, Any, Optional, Union, Literal
from src.repositories.exercise_repository import ExerciseRepository
from src.models.exercise import Exercise
from src.services.user_service import UserService
from src.utils.weight_defaults import get_default_unit


class ExerciseService:
    def __init__(self):
        self.exercise_repository: ExerciseRepository = ExerciseRepository()
        self.user_service: UserService = UserService()

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """
        Retrieves an exercise by exercise_id

        :param exercise_id: The ID of the exercise to retrieve
        :return: The Exercise object if found, else None
        """
        exercise_data = self.exercise_repository.get_exercise(exercise_id)

        if exercise_data:
            return Exercise.from_dict(exercise_data)
        return None

    def get_exercises_for_workout(self, workout_id: str) -> List[Exercise]:
        """
        Retrieves all exercises for a given workout_id

        :param workout_id: The ID of the workout to retrieve exercises for
        :return: A list of Exercise objects
        """
        exercises_data = self.exercise_repository.get_exercises_by_workout(workout_id)

        # Sort by order
        exercises_data.sort(key=lambda x: x.get("order", 999))
        return [Exercise.from_dict(exercise_data) for exercise_data in exercises_data]

    def create_exercise(
        self,
        workout_id: str,
        exercise_type: str,
        sets: int,
        reps: int,
        weight_value: float = 0.0,
        athlete_id: Optional[str] = None,
        weight_unit: Optional[str] = None,
        rpe: Optional[Union[int, float]] = None,
        status: Optional[Literal["planned", "completed", "skipped"]] = "planned",
        notes: Optional[str] = None,
        order: Optional[int] = None,
        exercise_category: Optional[str] = None,
    ) -> Exercise:
        """
        Creates a new exercise with weight unit defaults

        :param workout_id: The ID of the workout to create the exercise for
        :param exercise_type: The type of exercise
        :param sets: The number of sets
        :param reps: The number of reps
        :param weight_value: The weight value
        :param athlete_id: The athlete's ID (for weight preference lookup)
        :param weight_unit: Explicit unit override ('kg' or 'lb')
        :param rpe: The RPE rating
        :param status: The status of the exercise
        :param exercise_category: The category of the exercise
        :param notes: Any additional notes
        :param order: The order of the exercise
        :return: The created Exercise object
        """
        # Find the highest order if not specified
        if order is None:
            existing_exercises = self.exercise_repository.get_exercises_by_workout(
                workout_id
            )
            order = (
                max([ex.get("order", 0) for ex in existing_exercises], default=0) + 1
            )

        # Determine weight unit using defaults
        if weight_unit and weight_unit in ["kg", "lb"]:
            final_unit = weight_unit
        elif athlete_id:
            user_preference = self.user_service.get_user_weight_unit_preference(
                athlete_id
            )
            final_unit = get_default_unit(exercise_type, user_preference)
        else:
            final_unit = get_default_unit(exercise_type, "lb")  # Default fallback

        # Create weight_data structure
        weight_data = {"value": weight_value, "unit": final_unit}

        exercise = Exercise(
            exercise_id=str(uuid.uuid4()),
            workout_id=workout_id,
            exercise_type=exercise_type,
            sets=sets,
            reps=reps,
            weight_data=weight_data,
            rpe=rpe,
            status=status,
            notes=notes,
            order=order,
        )

        self.exercise_repository.create_exercise(exercise.to_dict())
        return exercise

    def update_exercise(
        self, exercise_id: str, update_data: Dict[str, Any]
    ) -> Optional[Exercise]:
        """
        Updates the exercise data by exercise_id

        :param exercise_id: The ID of the exercise to update
        :param update_data: A dictionary containing the updated data
        :return: The updated Exercise object if found, else None
        """
        self.exercise_repository.update_exercise(exercise_id, update_data)
        return self.get_exercise(exercise_id)

    def delete_exercise(self, exercise_id: str) -> bool:
        """
        Deletes the exercise by exercise_id

        :param exercise_id: The ID of the exercise to delete
        :return: True if the exercise was successfully deleted, else False
        """
        response = self.exercise_repository.delete_exercise(exercise_id)
        return bool(response)

    def track_set(
        self,
        exercise_id: str,
        set_number: int,
        reps: int,
        weight_value: float,
        weight_unit: Optional[str] = None,
        rpe: Optional[Union[int, float]] = None,
        completed: bool = True,
        notes: Optional[str] = None,
    ) -> Optional[Exercise]:
        """
        Track a specific set within an exercise with weight unit support
        """
        # Get the exercise
        exercise = self.get_exercise(exercise_id)
        if not exercise:
            return None

        # Determine weight unit (use exercise default if not specified)
        final_unit = weight_unit or exercise.weight_data.get("unit", "lb")
        if final_unit not in ["kg", "lb"]:
            final_unit = "lb"  # Fallback

        # Prepare set data with weight_data structure
        set_data = {
            "set_number": set_number,
            "reps": reps,
            "weight_data": {"value": weight_value, "unit": final_unit},
            "completed": completed,
        }

        if rpe is not None:
            set_data["rpe"] = rpe
        if notes:
            set_data["notes"] = notes

        # Add set data to exercise
        exercise.add_set_data(set_data)

        # Calculate the actual number of completed sets
        completed_sets = len(
            [s for s in exercise.sets_data if s.get("completed", False)]
        )
        highest_set_number = max(
            [s.get("set_number", 0) for s in exercise.sets_data] or [0]
        )

        # Use the maximum of highest set number and completed sets count
        actual_sets_count = max(completed_sets, highest_set_number)

        # Update exercise data
        update_data = {
            "sets_data": [s for s in exercise.sets_data],
            "sets": actual_sets_count,
        }

        if completed and exercise.status == "planned":
            update_data["status"] = "in_progress"

        # Update in repository and return
        self.exercise_repository.update_exercise(exercise_id, update_data)
        return self.get_exercise(exercise_id)

    def delete_set(self, exercise_id: str, set_number: int) -> Optional[Exercise]:
        """
        Delete a specific set from an exercise

        :param exercise_id: ID of the exercise
        :param set_number: Number of the set to delete
        :return: Updated Exercise object if found, else None
        """
        # Get the exercise
        exercise = self.get_exercise(exercise_id)

        if not exercise or not exercise.sets_data:
            return None

        # Create a filtered list of sets without the set to delete
        updated_sets_data = [
            set_data
            for set_data in exercise.sets_data
            if set_data.get("set_number") != set_number
        ]

        # If we didn't remove any sets, return early
        if len(updated_sets_data) == len(exercise.sets_data):
            return exercise

        # Reorder set numbers to ensure they're sequential
        for i, set_data in enumerate(
            sorted(updated_sets_data, key=lambda s: s.get("set_number", 0))
        ):
            set_data["set_number"] = i + 1

        # Calculate the new number of sets based on the updated data
        new_set_count = len(updated_sets_data)

        # Update the exercise with the new sets_data
        update_data = {
            "sets_data": updated_sets_data,
            "sets": new_set_count,
        }

        # Automatically recalculate exercise status based on remaining sets
        if not updated_sets_data:
            update_data["status"] = "planned"
        elif all(set_data.get("completed", False) for set_data in updated_sets_data):
            update_data["status"] = "completed"
        else:
            update_data["status"] = "in_progress"

        # Update the exercise in the database
        return self.update_exercise(exercise_id, update_data)
