from typing import Dict, List, Literal, Any, Optional
from .exercise import Exercise
import datetime as dt


class Workout:
    def __init__(
        self,
        workout_id: str,
        athlete_id: str,
        day_id: str,
        date: str,
        notes: Optional[str] = None,
        status: Literal[
            "not_started", "in_progress", "completed", "skipped"
        ] = "not_started",
        start_time: Optional[str] = None,
        finish_time: Optional[str] = None,
    ):
        self.workout_id: str = workout_id
        self.athlete_id: str = athlete_id
        self.day_id: str = day_id
        self.date: str = date
        self.notes: Optional[str] = notes
        self._status: Literal[
            "not_started", "in_progress", "completed", "skipped"
        ] = status
        self.exercises: List[Exercise] = []
        self.start_time: Optional[str] = start_time
        self.finish_time: Optional[str] = finish_time

    @property
    def status(self) -> Literal["not_started", "in_progress", "completed", "skipped"]:
        """
        Return the workout status, using explicit status if set

        :return: Status of the workout
        """

        # If status was explicitly set, use it
        if self._status:
            return self._status

        # Calculate status based on exercises
        if not self.exercises:
            return "not_started"

        # Count exercises with "completed" status
        completed_count = sum(1 for ex in self.exercises if ex.status == "completed")
        total_count = len(self.exercises)

        # Debug
        print(f"Completed count: {completed_count}, Total: {total_count}")
        for i, ex in enumerate(self.exercises):
            print(f"Exercise {i+1}: {ex.exercise_id}, Status: {ex.status}")

        # Calculate workout status based on completed exercises
        if completed_count == 0:
            return "not_started"
        elif completed_count == total_count:
            return "completed"
        else:
            return "in_progress"

    @property
    def duration_minutes(self) -> Optional[int]:
        """
        Calculate workout duration in minutes from start_time to finish_time.

        :return: Duration in minutes if both timestamps exist, None otherwise
        """
        if not (self.start_time and self.finish_time):
            return None

        try:
            # Handle both with and without timezone suffixes
            start_str = (
                self.start_time.replace("Z", "+00:00")
                if self.start_time.endswith("Z")
                else self.start_time
            )
            finish_str = (
                self.finish_time.replace("Z", "+00:00")
                if self.finish_time.endswith("Z")
                else self.finish_time
            )

            start = dt.datetime.fromisoformat(start_str)
            finish = dt.datetime.fromisoformat(finish_str)

            duration_seconds = (finish - start).total_seconds()
            return int(duration_seconds / 60)
        except (ValueError, TypeError, AttributeError) as e:
            return None

    @status.setter
    def status(
        self, value: Literal["not_started", "in_progress", "completed", "skipped"]
    ):
        """
        Set the workout status explicitly

        :param value: The status to set
        """

        if value not in ["not_started", "in_progress", "completed", "skipped"]:
            raise ValueError(
                "Status must be one of: not_started, in_progress, completed, skipped"
            )
        self._status = value

    def add_exercise(self, exercise: Exercise) -> None:
        """
        Add an exercise to the workout

        :param exercise: The Exercise object to add
        """

        self.exercises.append(exercise)

    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """
        Get an exercise by its ID.

        :param exercise_id: The ID of the exercise to find
        :return: The Exercise if found, None otherwise
        """
        for exercise in self.exercises:
            if exercise.exercise_id == exercise_id:
                return exercise
        return None

    def remove_exercise(self, exercise_id: str) -> bool:
        """
        Remove an exercise by its ID.

        :param exercise_id: The ID of the exercise to remove
        :return: True if the exercise was found and removed, False otherwise
        """
        for i, exercise in enumerate(self.exercises):
            if exercise.exercise_id == exercise_id:
                self.exercises.pop(i)
                return True
        return False

    def calculate_volume(self) -> float:
        """
        Calculate the total volume of the workout (sets * reps * weight).

        Defensive implementation that handles mixed Decimal/float types
        from DynamoDB to prevent arithmetic errors during exercise completion.

        :return: The total volume
        """
        total_volume = 0.0

        for exercise in self.exercises:
            if exercise.status == "completed":
                # Defensive type conversion for arithmetic safety
                # Converts Decimal types from DynamoDB to float for arithmetic operations
                sets = float(exercise.sets)
                reps = float(exercise.reps)
                weight = float(exercise.weight)

                total_volume += sets * reps * weight

        return total_volume

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
        # Find the exercise
        target_exercise = None
        for exercise in self.exercises:
            if exercise.exercise_id == exercise_id:
                target_exercise = exercise
                break

        if not target_exercise:
            return None

        # Update exercise details
        target_exercise.sets = sets
        target_exercise.reps = reps
        target_exercise.weight = weight

        if rpe is not None:
            target_exercise.rpe = rpe

        if notes:
            target_exercise.notes = notes

        # Set status to completed
        target_exercise.status = "completed"

        # Explicitly reset the cached status to force recalculation
        self._status = None

        return target_exercise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert a Workout instance to a dictionary representation.

        This method serializes the Workout instance and its associated data
        (including exercises) into a dictionary format, which can be useful
        for saving to a database, API communication, or debugging.

        :return: Dictionary representation of the Workout instance, including:
                - workout_id: The unique identifier of the workout
                - athlete_id: The unique identifier of the athlete
                - day_id: The unique identifier of the day associated with the workout
                - date: The date of the workout
                - notes: Any notes associated with the workout
                - status: The current status of the workout (e.g., 'not_started', 'completed')
                - exercises: List of dictionaries representing each exercise in the workout
        """
        return {
            "workout_id": self.workout_id,
            "athlete_id": self.athlete_id,
            "day_id": self.day_id,
            "date": self.date,
            "notes": self.notes,
            "status": self.status,
            "exercises": [ex.to_dict() for ex in self.exercises],
            "start_time": self.start_time,
            "finish_time": self.finish_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workout":
        """
        Create a Workout instance from a dictionary of data

        :param data: Dictionary containing workout data
        :return: Workout instance
        """
        # Create the workout object without exercises first
        workout = cls(
            workout_id=data.get("workout_id"),
            athlete_id=data.get("athlete_id"),
            day_id=data.get("day_id"),
            date=data.get("date"),
            notes=data.get("notes"),
            status=data.get("status", "not_started"),
            start_time=data.get("start_time"),
            finish_time=data.get("finish_time"),
        )

        # Add exercises if present
        if "exercises" in data and data["exercises"]:
            for exercise_data in data["exercises"]:
                exercise = Exercise.from_dict(exercise_data)
                workout.add_exercise(exercise)

        return workout
