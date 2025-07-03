import uuid
from typing import Dict, List, Any, Optional
from src.repositories.workout_repository import WorkoutRepository
from src.repositories.day_repository import DayRepository
from src.repositories.exercise_repository import ExerciseRepository
from src.models.workout import Workout
from src.models.exercise import Exercise
from src.services.exercise_service import ExerciseService
import datetime as dt
from src.services.notification_service import NotificationService


class WorkoutService:
    def __init__(self):
        self.workout_repository: WorkoutRepository = WorkoutRepository()
        self.day_repository: DayRepository = DayRepository()
        self.exercise_repository: ExerciseRepository = ExerciseRepository()
        self.exercise_service: ExerciseService = ExerciseService()

    def get_workout(self, workout_id: str) -> Optional[Workout]:
        """
        Retrieves a workout by workout_id with all its exercises

        :param workout_id: The ID of the workout to retrieve
        :return: The Workout object if found, else None
        """
        workout_data = self.workout_repository.get_workout(workout_id)

        if not workout_data:
            return None

        # Create the workout object
        workout = Workout.from_dict(workout_data)

        # Use ExerciseService to fetch exercises for this workout
        exercises = self.exercise_service.get_exercises_for_workout(workout.workout_id)

        # Add exercises to the workout
        for exercise in exercises:
            workout.add_exercise(exercise)

        return workout

    def get_workout_by_day(self, athlete_id: str, day_id: str) -> Optional[Workout]:
        """
        Retrieves a workout by athlete_id and day_id with all its exercises

        :param athlete_id: The ID of the athlete
        :param day_id: The ID of the day
        :return: The Workout object if found, else None
        """
        # Retrieve workout data
        workout_data = self.workout_repository.get_workout_by_day(athlete_id, day_id)

        if not workout_data:
            return None

        # Create the workout object
        workout = Workout.from_dict(workout_data)

        # Use ExerciseService to fetch exercises for this workout
        exercises = self.exercise_service.get_exercises_for_workout(workout.workout_id)

        # Add exercises to the Workout object
        for exercise in exercises:
            workout.add_exercise(exercise)

        return workout

    def create_workout(
        self,
        athlete_id: str,
        day_id: str,
        date: str,
        exercises: List[Dict[str, Any]],
        notes: Optional[str] = None,
        status: str = "not_started",
    ) -> Workout:
        """
        Creates a new workout with exercises

        :param athlete_id: The ID of the athlete
        :param day_id: The ID of the day
        :param date: The date of the workout in ISO format
        :param exercises: A list of exercise data
        :param notes: Optional notes for the workout
        :param status: The status of the workout
        :return: The created Workout object
        """
        VALID_STATUS = {"not_started", "in_progress", "completed", "skipped"}

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
                    "exercises": exercises,
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

        # First, create the workout without exercises
        workout_dict = workout.to_dict()
        # Remove exercises from the dict before saving
        workout_dict.pop("exercises", None)
        self.workout_repository.create_workout(workout_dict)

        # Then create exercises separately in the ExerciseTable
        for i, exercise_data in enumerate(exercises):
            exercise = Exercise(
                exercise_id=str(uuid.uuid4()),
                workout_id=workout.workout_id,
                exercise_type=exercise_data.get("exercise_type"),
                sets=exercise_data.get("sets"),
                reps=exercise_data.get("reps"),
                weight=exercise_data.get("weight"),
                status=exercise_data.get("status", "planned"),
                rpe=exercise_data.get("rpe"),
                notes=exercise_data.get("notes"),
                order=i + 1,
                exercise_category=exercise_data.get("exercise_category"),
                sets_data=exercise_data.get("sets_data"),
            )

            # Save the exercise in the ExerciseTable
            self.exercise_repository.create_exercise(exercise.to_dict())
            # Also add to the workout object for the return
            workout.add_exercise(exercise)

        return workout

    def update_workout(
        self, workout_id: str, update_data: Dict[str, Any]
    ) -> Optional[Workout]:
        """
        Updates a workout by workout_id, including exercise changes

        :param workout_id: The ID of the workout to update
        :param update_data: The data to update the workout with
        :return: The updated Workout object if found, else None
        """
        # Get the existing workout to see what's being updated
        existing_workout = self.get_workout(workout_id)

        if not existing_workout:
            return None

        # Handle exercises separately if they're in the update
        exercises_data = update_data.pop("exercises", None)

        if exercises_data:
            # Map of existing exercises by ID for quick lookup
            existing_exercises = {
                ex.exercise_id: ex for ex in existing_workout.exercises
            }

            # Prepare exercises list for update
            exercises_to_update = []

            for exercise_data in exercises_data:
                exercise_id = exercise_data.get("exercise_id")

                # If this is an existing exercise, include it with updates
                if exercise_id and exercise_id in existing_exercises:
                    # Start with the existing exercise data
                    updated_exercise = existing_exercises[exercise_id].to_dict()
                    # Remove computed properties before updating
                    updated_exercise.pop("is_predefined", None)
                    # Update with new values
                    updated_exercise.update(exercise_data)
                    exercises_to_update.append(updated_exercise)
                else:
                    # This is a new exercise to add
                    new_exercise = {
                        "exercise_id": str(uuid.uuid4()),
                        "workout_id": workout_id,
                        "exercise_type": exercise_data.get("exercise_type"),
                        "sets": exercise_data.get("sets"),
                        "reps": exercise_data.get("reps"),
                        "weight": exercise_data.get("weight"),
                        "status": exercise_data.get("status", "planned"),
                        "rpe": exercise_data.get("rpe"),
                        "notes": exercise_data.get("notes"),
                        "order": len(exercises_to_update) + 1,
                        "exercise_category": exercise_data.get("exercise_category"),
                    }
                    exercises_to_update.append(new_exercise)
            # Add the updated exercises list to the update data
            update_data["exercises"] = exercises_to_update

        # Update the workout in the repository
        self.workout_repository.update_workout(workout_id, update_data)

        # Return the updated workout
        return self.get_workout(workout_id)

    def complete_exercise(
        self,
        exercise_id: str,
        sets: int,
        reps: int,
        weight: float,
        rpe: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Optional[Exercise]:
        """
        Records the completion of an exercise

        :param exercise_id: ID of the exercise
        :param sets: Number of sets completed
        :param reps: Number of reps completed
        :param weight: Weight used
        :param rpe: Rate of Perceived Exertion (optional)
        :param notes: Additional notes (optional)
        :return: Updated Exercise object if found, else None
        """
        # Get the exercise from the repository
        exercise_data = self.exercise_repository.get_exercise(exercise_id)

        if not exercise_data:
            return None

        # Prepare completion data
        completion_data = {
            "status": "completed",
            "sets": sets,
            "reps": reps,
            "weight": weight,
        }

        if rpe is not None:
            completion_data["rpe"] = rpe

        if notes:
            completion_data["notes"] = notes

        # Update the exercise
        updated_exercise_data = self.exercise_repository.update_exercise(
            exercise_id, completion_data
        )

        # Update the workout status
        workout_id = exercise_data.get("workout_id")
        if workout_id:
            self._update_workout_status(workout_id)

        # Convert to Exercise object and return
        if updated_exercise_data:
            exercise_data = updated_exercise_data.copy()
            exercise_data.pop("is_predefined", None)
            return Exercise(**exercise_data)

        return None

    def _update_workout_status(self, workout_id: str) -> None:
        """
        Updates the workout status based on its exercises completion status

        :param workout_id: ID of the workout to update
        """
        workout = self.get_workout(workout_id)
        if not workout:
            return

        # Get all exercises for the workout
        exercises = workout.exercises

        if not exercises:
            return

        # Count completed exercises
        completed_count = sum(1 for e in exercises if e.status == "completed")
        total_count = len(exercises)

        # Determine new status
        if completed_count == total_count:
            new_status = "completed"
        elif completed_count > 0:
            new_status = "in_progress"
        else:
            new_status = "not_started"

        # Only update if status needs to change
        if new_status != workout.status:
            self.workout_repository.update_workout(workout_id, {"status": new_status})

    def _create_completion_notification(self, workout_id: str) -> None:
        """
        Create a notification when a workout is completed

        :param workout_id: ID of the completed workout
        """
        try:
            # Import here to avoid circular imports
            from src.services.notification_service import NotificationService

            # Get the updated workout with completed status
            completed_workout = self.get_workout(workout_id)
            if not completed_workout:
                return

            # Create notification (this method handles all error cases gracefully)
            notification_service = NotificationService()
            notification_service.create_workout_completion_notification(
                completed_workout
            )

        except Exception as e:
            # Log the error but don't break the workout completion flow
            print(f"Error creating workout completion notification: {str(e)}")
            # Notification failure should not impact workout functionality

    def delete_workout(self, workout_id: str) -> bool:
        """
        Deletes a workout by workout_id, including all its exercises

        :param workout_id: The ID of the workout to delete
        :return: True if the workout was deleted, else False
        """
        response = self.workout_repository.delete_workout(workout_id)

        return bool(response)

    def start_workout_session(self, workout_id: str) -> Optional[Workout]:
        """
        Start a workout timing session by recording start_time and updating status

        :param workout_id: The ID of the workout to start timing
        :return: Updated Workout object if found and started, None otherwise
        """
        # Get existing workout to validate
        existing_workout = self.get_workout(workout_id)

        if not existing_workout:
            return None

        # Check if session is already started
        if existing_workout.start_time:
            # Session already started, return the existing workout without changes
            return existing_workout

        # Record the start time and update status to in_progress
        now = dt.datetime.now().isoformat() + "Z"
        update_data = {
            "start_time": now,
            "status": "in_progress",
        }

        # Update the workout in repository
        return self.update_workout(workout_id, update_data)

    def finish_workout_session(self, workout_id: str) -> Optional[Workout]:
        """
        Finish a workout timing session by recording finish_time
        and creating coach notification if all exercises are completed

        :param workout_id: The ID of the workout to finish timing
        :return: Updated Workout object if found and finished, None otherwise
        """
        # Get the existing workout to validate it exists and has started
        existing_workout = self.get_workout(workout_id)

        if not existing_workout:
            return None

        # Check if session was started
        if not existing_workout.start_time:
            # Cannot finish a session that was never started
            return None

        # Check if session is already finished
        if existing_workout.finish_time:
            # Session already finished, return existing workout without changes
            return existing_workout

        # Check if all exercises are completed
        all_exercises_completed = (
            all(
                exercise.status == "completed"
                for exercise in existing_workout.exercises
            )
            if existing_workout.exercises
            else False
        )

        if not all_exercises_completed:
            # Cannot finish workout until all exercises are completed
            return None

        # Record finish time
        now = dt.datetime.now().isoformat() + "Z"
        update_data = {"finish_time": now}

        # Update the workout in repository
        updated_workout = self.update_workout(workout_id, update_data)

        # Create coach notification
        if updated_workout:
            try:
                notification_service = NotificationService()
                notification_service.create_workout_completion_notification(
                    updated_workout
                )
            except Exception:
                # Don't fail workout completion if notification fails
                pass

        return updated_workout
