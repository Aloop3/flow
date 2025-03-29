import uuid
from typing import Dict, List, Any, Optional
from src.repositories.workout_repository import WorkoutRepository
from src.repositories.day_repository import DayRepository
from src.repositories.exercise_repository import ExerciseRepository
from src.services.set_service import SetService
from src.models.workout import Workout
from src.models.completed_exercise import CompletedExercise
from src.models.set import Set


class WorkoutService:
    def __init__(self):
        self.workout_repository: WorkoutRepository = WorkoutRepository()
        self.day_repository: DayRepository = DayRepository()
        self.exercise_repository: ExerciseRepository = ExerciseRepository()
        self.set_service: SetService = SetService()

    def get_workout(self, workout_id: str) -> Optional[Workout]:
        """
        Retrieves a workout by workout_id with all its sets

        :param workout_id: The ID of the workout to retrieve
        :return: The Workout object if found, else None
        """
        workout_data = self.workout_repository.get_workout(workout_id)

        if not workout_data:
            return None

        # Create Workout object with base data
        workout = Workout(**{k: v for k, v in workout_data.items() if k != "exercises"})

        # Load completed exercises with their sets
        if "exercises" in workout_data:
            for exercise_data in workout_data["exercises"]:
                # Create base exercise object
                completed_exercise = CompletedExercise(
                    completed_id=exercise_data.get("completed_id"),
                    workout_id=exercise_data.get("workout_id"),
                    exercise_id=exercise_data.get("exercise_id"),
                    notes=exercise_data.get("notes"),
                )

                # Add sets if they exist
                if "sets" in exercise_data:
                    for set_data in exercise_data["sets"]:
                        exercise_set = Set(
                            set_id=set_data.get("set_id"),
                            completed_exercise_id=set_data.get("completed_exercise_id"),
                            workout_id=set_data.get("workout_id"),
                            set_number=set_data.get("set_number"),
                            reps=set_data.get("reps"),
                            weight=set_data.get("weight"),
                            rpe=set_data.get("rpe"),
                            notes=set_data.get("notes"),
                        )
                        completed_exercise.add_set(exercise_set)

                # Add exercise to workout
                workout.add_exercise(completed_exercise)

        return workout

    def get_workout_by_day(self, athlete_id: str, day_id: str) -> Optional[Workout]:
        """
        Retrieves a workout by athlete_id and day_id with all its sets

        :param athlete_id: The ID of the athlete
        :param day_id: The ID of the day
        :return: The Workout object if found, else None
        """
        workout_data = self.workout_repository.get_workout_by_day(athlete_id, day_id)

        if not workout_data:
            return None

        # Create Workout object with base data
        workout = Workout(**{k: v for k, v in workout_data.items() if k != "exercises"})

        # Load completed exercises with their sets
        if "exercises" in workout_data:
            for exercise_data in workout_data["exercises"]:
                # Create base exercise object
                completed_exercise = CompletedExercise(
                    completed_id=exercise_data.get("completed_id"),
                    workout_id=exercise_data.get("workout_id"),
                    exercise_id=exercise_data.get("exercise_id"),
                    notes=exercise_data.get("notes"),
                )

                # Add sets if they exist
                if "sets" in exercise_data:
                    for set_data in exercise_data["sets"]:
                        exercise_set = Set(
                            set_id=set_data.get("set_id"),
                            completed_exercise_id=set_data.get("completed_exercise_id"),
                            workout_id=set_data.get("workout_id"),
                            set_number=set_data.get("set_number"),
                            reps=set_data.get("reps"),
                            weight=set_data.get("weight"),
                            rpe=set_data.get("rpe"),
                            notes=set_data.get("notes"),
                        )
                        completed_exercise.add_set(exercise_set)

                # Add exercise to workout
                workout.add_exercise(completed_exercise)

        return workout

    def log_workout(
        self,
        athlete_id: str,
        day_id: str,
        date: str,
        completed_exercises: List[Dict[str, Any]],
        notes: Optional[str] = None,
        status: str = "completed",
    ) -> Workout:
        """
        Logs a completed workout for an athlete

        :param athlete_id: The ID of the athlete
        :param day_id: The ID of the day
        :param date: The date of the workout in ISO format
        :param completed_exercises: A list of completed exercises
        :param notes: Optional notes for the workout
        :param status: The status of the workout ("completed", "partial", "skipped")
        :return: The created Workout object
        """
        VALID_STATUS = {"completed", "partial", "skipped"}

        if status not in VALID_STATUS:
            raise ValueError(f"Invalid status. Must be one of {VALID_STATUS}")

        existing = self.get_workout_by_day(athlete_id, day_id)

        if existing:
            # Update existing workout instead
            return self.update_workout(
                existing.workout_id,
                {
                    "date": date,
                    "notes": notes,
                    "status": status,
                    "exercises": completed_exercises,
                },
            )

        # Create a new workout
        workout = Workout(
            workout_id=str(uuid.uuid4()),
            athlete_id=athlete_id,
            day_id=day_id,
            date=date,
            notes=notes,
            status=status,
        )

        # Add completed exercises and sets
        for i, exercise_data in enumerate(completed_exercises):
            # Create the completed exercise
            completed_id = str(uuid.uuid4())

            completed = CompletedExercise(
                completed_id=completed_id,
                workout_id=workout.workout_id,
                exercise_id=exercise_data.get("exercise_id"),
                notes=exercise_data.get("notes"),
            )

            # Add any sets if they exist
            if "sets" in exercise_data:
                for j, set_data in enumerate(exercise_data["sets"]):
                    set_number = set_data.get("set_number", j + 1)

                    # Create the exercise set
                    exercise_set = Set(
                        set_id=str(uuid.uuid4()),
                        completed_exercise_id=completed_id,
                        workout_id=workout.workout_id,
                        set_number=set_number,
                        reps=set_data.get("reps"),
                        weight=set_data.get("weight"),
                        rpe=set_data.get("rpe"),
                        notes=set_data.get("notes"),
                    )

                    # Add to the completed exercise
                    completed.add_set(exercise_set)

            # Add to the workout
            workout.add_exercise(completed)

        # Save everything in one operation
        workout_dict = workout.to_dict()
        self.workout_repository.create_workout(workout_dict)

        return workout

    def update_workout(
        self, workout_id: str, update_data: Dict[str, Any]
    ) -> Optional[Workout]:
        """
        Updates a workout by workout_id, including set-level changes

        :param workout_id: The ID of the workout to update
        :param update_data: The data to update the workout with
        :return: The updated Workout object if found, else None
        """
        # Get the existing workout to see what's being updated
        existing_workout = self.get_workout(workout_id)

        if not existing_workout:
            return None

        # Handle exercises and sets separately if they're in the update
        exercises_data = update_data.pop("exercises", None)

        if exercises_data:
            # Map of existing exercises by ID for quick lookup
            existing_exercises = {
                ex.completed_id: ex for ex in existing_workout.exercises
            }

            for exercise_data in exercises_data:
                exercise_id = exercise_data.get("completed_id")

                # If this is an existing exercise, update it
                if exercise_id and exercise_id in existing_exercises:
                    # Handle sets if they're included
                    sets_data = exercise_data.pop("sets", None)

                    if sets_data:
                        # Map existing sets by ID
                        existing_sets = {
                            s.set_id: s for s in existing_exercises[exercise_id].sets
                        }

                        for set_data in sets_data:
                            set_id = set_data.get("set_id")

                            # If this is an existing set, update it
                            if set_id and set_id in existing_sets:
                                self.set_service.update_set(set_id, set_data)
                            else:
                                # Create a new set
                                set_number = set_data.get(
                                    "set_number",
                                    len(existing_exercises[exercise_id].sets) + 1,
                                )

                                self.set_service.create_set(
                                    completed_exercise_id=exercise_id,
                                    workout_id=workout_id,
                                    set_number=set_number,
                                    reps=set_data.get("reps"),
                                    weight=set_data.get("weight"),
                                    rpe=set_data.get("rpe"),
                                    notes=set_data.get("notes"),
                                )
                else:
                    # This is a new exercise to add
                    sets_data = exercise_data.pop("sets", None)

                    # Create the completed exercise
                    completed_id = str(uuid.uuid4())

                    completed = CompletedExercise(
                        completed_id=completed_id,
                        workout_id=workout_id,
                        exercise_id=exercise_data.get("exercise_id"),
                        notes=exercise_data.get("notes"),
                    )

                    # Add any sets if they exist
                    if sets_data:
                        for j, set_data in enumerate(sets_data):
                            set_number = set_data.get("set_number", j + 1)

                            # Create the exercise set
                            exercise_set = Set(
                                set_id=str(uuid.uuid4()),
                                completed_exercise_id=completed_id,
                                workout_id=workout_id,
                                set_number=set_number,
                                reps=set_data.get("reps"),
                                weight=set_data.get("weight"),
                                rpe=set_data.get("rpe"),
                                notes=set_data.get("notes"),
                            )

                            # Add to the completed exercise
                            completed.add_set(exercise_set)

                    # Include this completed exercise in the update data
                    if "exercises" not in update_data:
                        update_data["exercises"] = []

                    update_data["exercises"].append(completed.to_dict())

        # Update the workout in the repository
        self.workout_repository.update_workout(workout_id, update_data)

        # Return the updated workout
        return self.get_workout(workout_id)

    def add_set_to_exercise(
        self, workout_id: str, exercise_id: str, set_data: Dict[str, Any]
    ) -> Optional[Set]:
        """
        Adds a new set to an exercise in a workout

        :param workout_id: The ID of the workout
        :param exercise_id: The ID of the exercise to add the set to
        :param set_data: The data for the new set
        :return: The created Set if successful, else None
        """
        # Get the workout and exercise
        workout = self.get_workout(workout_id)

        if not workout:
            return None

        # Find the exercise
        exercise = next(
            (ex for ex in workout.exercises if ex.completed_id == exercise_id), None
        )

        if not exercise:
            return None

        # Create the set
        set_number = set_data.get("set_number", len(exercise.sets) + 1)

        exercise_set = self.set_service.create_set(
            completed_exercise_id=exercise_id,
            workout_id=workout_id,
            set_number=set_number,
            reps=set_data.get("reps"),
            weight=set_data.get("weight"),
            rpe=set_data.get("rpe"),
            notes=set_data.get("notes"),
        )

        # Add to workout model and update status
        workout.add_set_to_exercise(exercise_id, exercise_set)

        # Update the workout status in the repository
        self.workout_repository.update_workout(workout_id, {"status": workout.status})

        return exercise_set

    def update_set(self, set_id: str, update_data: Dict[str, Any]) -> Optional[Set]:
        """
        Updates an existing set

        :param set_id: The ID of the set to update
        :param update_data: The data to update the set with
        :return: The updated Set if successful, else None
        """
        # Update the set using set service
        return self.set_service.update_set(set_id, update_data)

    def delete_set(self, set_id: str) -> bool:
        """
        Deletes a set from a workout

        :param set_id: The ID of the set to delete
        :return: True if successful, else False
        """
        # Get the set to find its workout_id and exercise_id
        set_obj = self.set_service.get_set(set_id)

        if not set_obj:
            return False

        # Delete the set
        result = self.set_service.delete_set(set_id)

        if result:
            # Update the workout status
            workout = self.get_workout(set_obj.workout_id)
            if workout:
                self.workout_repository.update_workout(
                    workout.workout_id, {"status": workout.status}
                )

        return result

    def get_workout_sets(self, workout_id: str) -> Dict[str, List[Set]]:
        """
        Gets all sets for a workout, organized by exercise

        :param workout_id: The ID of the workout
        :return: Dictionary mapping exercise IDs to lists of sets
        """
        workout = self.get_workout(workout_id)

        if not workout:
            return {}

        result = {}
        for exercise in workout.exercises:
            result[exercise.completed_id] = exercise.sets

        return result

    def get_exercise_sets(self, exercise_id: str) -> List[Set]:
        """
        Gets all sets for a specific exercise

        :param exercise_id: The ID of the exercise
        :return: List of sets for the exercise
        """
        return self.set_service.get_sets_for_exercise(exercise_id)

    def delete_workout(self, workout_id: str) -> bool:
        """
        Deletes a workout by workout_id, including all its sets

        :param workout_id: The ID of the workout to delete
        :return: True if the workout was deleted, else False
        """
        response = self.workout_repository.delete_workout(workout_id)

        return bool(response)
