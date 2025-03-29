from typing import Dict, List, Literal, Any, Optional
from .completed_exercise import CompletedExercise
from .set import Set

class Workout:
    def __init__(self, workout_id: str, athlete_id: str, day_id: str, date: str, notes: Optional[str] = None, status: Literal["completed", "partial", "skipped"] = None):
        self.workout_id: str = workout_id
        self.athlete_id: str = athlete_id
        self.day_id: str = day_id
        self.date: str = date
        self.notes: Optional[str] = notes
        self._status: Literal["completed", "partial", "skipped"] = status
        self.exercises: List[CompletedExercise] = [] # List of CompletedExercise objects

    @property
    def status(self) -> Literal["completed", "partial", "skipped"]:
        """
        Return the workout status, using explicit status if set
        
        :return: Status of the workout
        """

        # If status was explicitly set, use it
        if self._status:
            return self._status
        
        # Default to partial if no status was explicitly set
        return "partial"
    
    @status.setter
    def status(self, value: Literal["completed", "partial", "skipped"]):
        """
        Set the workout status explicitly

        :param value: The status to set
        """

        if value not in ["completed", "partial", "skipped"]:
            raise ValueError("Status must be one of: completed, partial, skipped")
        self._status = value
    
    def add_exercise(self, exercise: CompletedExercise) -> None:
        """
        Add a completed exercise to the workout
        
        :param exercise: The CompletedExercise object to add
        """

        self.exercises.append(exercise)

    def add_set_to_exercise(self, exercise_id: str, exercise_set: Set) -> bool:
        """
        Add a set to a specific exercise in this workout
        
        :param exercise_id: ID of the exercise to add the set to
        :param exercise_set: The Set to add
        :return: True if the set was added, False if the exercise wasn't found
        """
        exercise = next((ex for ex in self.exercises if ex.completed_id == exercise_id), None)
        
        if not exercise:
            return False
            
        exercise.add_set(exercise_set)
            
        return True

    
    def get_exercise(self, exercise_id: str) -> Optional[CompletedExercise]:
        """
        Get a completed exercise by its ID.
        
        :param exercise_id: The ID of the exercise to find
        :return: The CompletedExercise if found, None otherwise
        """
        for exercise in self.exercises:
            if exercise.exercise_id == exercise_id:
                return exercise
        return None
    
    def remove_exercise(self, exercise_id: str) -> bool:
        """
        Remove a completed exercise by its ID.
        
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
            for exercise_set in exercise.sets:
                if exercise_set.completed:
                    total_volume += exercise_set.reps * exercise_set.weight
        
        return total_volume

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workout_id": self.workout_id,
            "athlete_id": self.athlete_id,
            "day_id": self.day_id,
            "date": self.date,
            "notes": self.notes,
            "status": self.status,
            "exercises": [ex.to_dict() for ex in self.exercises],
            "total_volume": self.calculate_volume()
        }