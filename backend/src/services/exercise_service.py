import uuid
from typing import List, Dict, Any, Optional, Union, Literal
from src.repositories.exercise_repository import ExerciseRepository
from src.models.exercise import Exercise


class ExerciseService:
    def __init__(self):
        self.exercise_repository: ExerciseRepository = ExerciseRepository()

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """
        Retrieves an exercise by exercise_id

        :param exercise_id: The ID of the exercise to retrieve
        :return: The Exercise object if found, else None
        """
        exercise_data = self.exercise_repository.get_exercise(exercise_id)

        if exercise_data:
            return Exercise(**exercise_data)
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
        return [Exercise(**exercise_data) for exercise_data in exercises_data]

    def create_exercise(
        self,
        workout_id: str,
        exercise_type: str,
        sets: int,
        reps: int,
        weight: float,
        rpe: Optional[Union[int, float]] = None,
        status: Optional[Literal["planned", "completed", "skipped"]] = "planned",
        notes: Optional[str] = None,
        order: Optional[int] = None,
        exercise_category: Optional[str] = None,
    ) -> Exercise:
        """
        Creates a new exercise

        :param workout_id: The ID of the workout to create the exercise for
        :param exercise_type: The type of exercise
        :param sets: The number of sets
        :param reps: The number of reps
        :param weight: The weight used
        :param rpe: The RPE rating
        :param status: The status of the exercise (planned, completed, skipped)
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

        exercise = Exercise(
            exercise_id=str(uuid.uuid4()),
            workout_id=workout_id,
            exercise_type=exercise_type,
            sets=sets,
            reps=reps,
            weight=weight,
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

    def reorder_exercises(
        self, workout_id: str, exercise_order: List[str]
    ) -> List[Exercise]:
        """
        Reorder exercises for a workout

        :param workout_id: The ID of the workout to reorder exercises for
        :param exercise_order: A list of exercise IDs in the desired order
        :return: A list of reordered Exercise objects
        """
        # Get all exercises for the workout
        exercises = self.get_exercises_for_workout(workout_id)
        exercise_dict = {ex.exercise_id: ex for ex in exercises}

        # Update order for each exercise
        for i, exercise_id in enumerate(exercise_order):
            if exercise_id in exercise_dict:
                self.update_exercise(exercise_id, {"order": i + 1})

        return self.get_exercises_for_workout(workout_id)

    def delete_exercises_by_workout(self, workout_id: str) -> int:
        """
        Delete all exercises associated with a given workout_id (cascading delete)

        :param workout_id: The workout_id to filter exercises by
        :return: The number of exercises deleted
        """
        exercises = self.exercise_repository.get_exercises_by_workout(workout_id)

        # Batch delete all exercises
        with self.exercise_repository.table.batch_writer() as batch:
            for exercise in exercises:
                batch.delete_item(Key={"exercise_id": exercise["exercise_id"]})

        return len(exercises)

    def track_set(
        self,
        exercise_id: str,
        set_number: int,
        reps: int,
        weight: float,
        rpe: Optional[Union[int, float]] = None,
        completed: bool = True,
        notes: Optional[str] = None,
    ) -> Optional[Exercise]:
        """
        Track a specific set within an exercise

        :param exercise_id: ID of the exercise
        :param set_number: Number of the set
        :param reps: Number of repetitions performed
        :param weight: Weight used
        :param rpe: Rate of Perceived Exertion (optional)
        :param completed: Whether the set was completed
        :param notes: Additional notes
        :return: Updated Exercise object if found, else None
        """
        # Get the exercise
        exercise = self.get_exercise(exercise_id)

        if not exercise:
            return None

        # Create/update set data
        set_data = {
            "set_number": set_number,
            "reps": reps,
            "weight": weight,
            "completed": completed,
        }

        if rpe is not None:
            set_data["rpe"] = rpe

        if notes:
            set_data["notes"] = notes

        # Add set data to exercise
        exercise.add_set_data(set_data)

        # If this is the first set and it's completed, update exercise status
        if completed and exercise.status == "planned":
            update_data = {"sets_data": exercise.sets_data, "status": "in_progress"}
        else:
            update_data = {"sets_data": exercise.sets_data}

        # Update in repository
        updated_exercise_data = self.exercise_repository.update_exercise(
            exercise_id, update_data
        )

        if not updated_exercise_data:
            return None

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

        # Update the exercise with the new sets_data
        update_data = {"sets_data": updated_sets_data}

        # Automatically recalculate exercise status based on remaining sets
        if not updated_sets_data:
            update_data["status"] = "planned"
        elif all(set_data.get("completed", False) for set_data in updated_sets_data):
            update_data["status"] = "completed"
        else:
            update_data["status"] = "in_progress"

        # Update the exercise in the database
        return self.update_exercise(exercise_id, update_data)
