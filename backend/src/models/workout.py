from typing import Dict, List, Literal, Any, Optional
from .exercise import Exercise


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

        :return: The total volume
        """
        total_volume = 0.0

        for exercise in self.exercises:
            if exercise.status == "completed":
                total_volume += exercise.sets * exercise.reps * exercise.weight

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
        )

        # Add exercises if present
        if "exercises" in data and data["exercises"]:
            for exercise_data in data["exercises"]:
                exercise = Exercise.from_dict(exercise_data)
                workout.add_exercise(exercise)

        return workout
