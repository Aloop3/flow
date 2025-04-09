from .base_repository import BaseRepository
from .set_repository import SetRepository
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, Optional, List
from src.config.workout_config import WorkoutConfig


class WorkoutRepository(BaseRepository):
    def __init__(self):
        super().__init__(WorkoutConfig.TABLE_NAME)
        self.set_repository = SetRepository()

    def get_workout(self, workout_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a workout by its ID with all its sets.

        :param workout_id: The ID of the workout to retrieve.
        :return: A dictionary containing the workout data if found, None otherwise.
        """

        workout = self.get_by_id("workout_id", workout_id)

        if not workout:
            return None

        # Fetch all sets for this workout
        sets = self.set_repository.get_sets_by_workout(workout_id)

        # Group sets by completed_exercise_id
        sets_by_exercise = {}
        for set_item in sets:
            exercise_id = set_item["completed_exercise_id"]
            if exercise_id not in sets_by_exercise:
                sets_by_exercise[exercise_id] = []
            sets_by_exercise[exercise_id].append(set_item)

        # Add sets to their respective exercises
        if "exercises" in workout:
            for exercise in workout["exercises"]:
                exercise_id = exercise["completed_id"]
                if exercise_id in sets_by_exercise:
                    exercise["sets"] = sets_by_exercise[exercise_id]

        return workout

    def get_workouts_by_athlete(self, athlete_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all workouts for a specific athlete.

        :param athlete_id: The ID of the athlete.
        :return: A list of dictionaries containing the workout data.
        """
        response = self.table.query(
            IndexName=WorkoutConfig.ATHLETE_INDEX,
            KeyConditionExpression=Key("athlete_id").eq(athlete_id),
            Limit=WorkoutConfig.MAX_ITEMS,
        )

        workouts = response.get("Items", [])

        # For each workout, fetch its sets
        for workout in workouts:
            workout_id = workout["workout_id"]
            sets = self.set_repository.get_sets_by_workout(workout_id)

            # Group sets by completed_exercise_id
            sets_by_exercise = {}
            for set_item in sets:
                exercise_id = set_item["completed_exercise_id"]
                if exercise_id not in sets_by_exercise:
                    sets_by_exercise[exercise_id] = []
                sets_by_exercise[exercise_id].append(set_item)

            # Add sets to their respective exercises
            if "exercises" in workout:
                for exercise in workout["exercises"]:
                    exercise_id = exercise["completed_id"]
                    if exercise_id in sets_by_exercise:
                        exercise["sets"] = sets_by_exercise[exercise_id]

        return workouts

    def get_workout_by_day(
        self, athlete_id: str, day_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves a workout logged for a specific athlete on a specific day.

        :param athlete_id: The ID of the athlete.
        :param day_id: The ID of the day.
        :return: A dictionary containing the workout data if found, None otherwise.
        """
        response = self.table.scan(
            FilterExpression=Attr("athlete_id").eq(athlete_id)
            & Attr("day_id").eq(day_id)
        )

        items = response.get("Items", [])
        if not items:
            return None

        workout = items[0]
        workout_id = workout["workout_id"]

        # Fetch all sets for this workout
        sets = self.set_repository.get_sets_by_workout(workout_id)

        # Group sets by completed_exercise_id
        sets_by_exercise = {}
        for set_item in sets:
            exercise_id = set_item["completed_exercise_id"]
            if exercise_id not in sets_by_exercise:
                sets_by_exercise[exercise_id] = []
            sets_by_exercise[exercise_id].append(set_item)

        # Add sets to their respective exercises
        if "exercises" in workout:
            for exercise in workout["exercises"]:
                exercise_id = exercise["completed_id"]
                if exercise_id in sets_by_exercise:
                    exercise["sets"] = sets_by_exercise[exercise_id]

        return workout

    def get_completed_workouts_since(
        self, athlete_id: str, start_date: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all completed workouts for a specific athlete since a given date.

        :param athlete_id: The ID of the athlete.
        :param start_date: The start date in ISO format (YYYY-MM-DD).
        :return: A list of dictionaries containing the completed workout data.
        """
        response = self.table.query(
            IndexName=WorkoutConfig.ATHLETE_INDEX,
            KeyConditionExpression=Key("athlete_id").eq(athlete_id),
            FilterExpression=Attr("date").gte(start_date)
            & Attr("status").eq("completed"),
            Limit=WorkoutConfig.MAX_ITEMS,
        )

        workouts = response.get("Items", [])

        # For each workout, fetch its sets
        for workout in workouts:
            workout_id = workout["workout_id"]
            sets = self.set_repository.get_sets_by_workout(workout_id)

            # Group sets by completed_exercise_id
            sets_by_exercise = {}
            for set_item in sets:
                exercise_id = set_item["completed_exercise_id"]
                if exercise_id not in sets_by_exercise:
                    sets_by_exercise[exercise_id] = []
                sets_by_exercise[exercise_id].append(set_item)

            # Add sets to their respective exercises
            if "exercises" in workout:
                for exercise in workout["exercises"]:
                    exercise_id = exercise["completed_id"]
                    if exercise_id in sets_by_exercise:
                        exercise["sets"] = sets_by_exercise[exercise_id]

        return workouts

    def get_completed_exercises_by_type(
        self, athlete_id: str, exercise_type: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all completed exercises of a specific type for a specific athlete.
        This is a more complex query that requires fetching workouts first then filtering exercises from those workouts.

        :param athlete_id: The ID of the athlete.
        :param exercise_type: The type of exercise to filter by.
        :return: A list of dictionaries containing the completed exercise data.
        """
        # Get all workouts for the athlete
        workouts = self.get_workouts_by_athlete(athlete_id)

        # Filter for completed exercises of the requested type
        completed_exercises: List[Dict[str, Any]] = []

        for workout in workouts:
            for exercise in workout.get("exercises", []):
                # Check if this is the exercise type we're looking for
                if exercise.get("type") == exercise_type:
                    # Add workout date and status to the exercise data
                    exercise_data = {**exercise}
                    exercise_data["date"] = workout["date"]
                    exercise_data["workout_status"] = workout["status"]
                    completed_exercises.append(exercise_data)

                    # Include set data if available
                    if "sets" in exercise:
                        exercise_data["sets"] = exercise["sets"]

        return completed_exercises

    def create_workout(self, workout_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new workout and its associated sets.

        :param workout_dict: A dictionary containing the workout data.
        :return: The created workout data.
        """

        # Extract sets from exercises to save separately
        exercises = workout_dict.get("exercises", [])
        sets_to_create = []

        for exercise in exercises:
            exercise_id = exercise.get("completed_id")
            workout_id = workout_dict.get("workout_id")

            if "sets" in exercise:
                sets = exercise.pop("sets")
                for set_item in sets:
                    # Ensure set has required fields
                    set_item["completed_exercise_id"] = exercise_id
                    set_item["workout_id"] = workout_id
                    sets_to_create.append(set_item)

        # Create the workout
        created_workout = self.create(workout_dict)

        # Create all sets
        for set_item in sets_to_create:
            self.set_repository.create_set(set_item)

        return created_workout

    def update_workout(
        self, workout_id: str, update_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing workout and its sets.

        :param workout_id: The ID of the workout to update.
        :param update_dict: A dictionary containing the updated data.
        :return: The updated workout data.
        """

        # Handle updating exercises and their sets
        if "exercises" in update_dict:
            exercises = update_dict.pop("exercises")

            for exercise in exercises:
                exercise_id = exercise.get("completed_id")

                # Handle sets if present
                if "sets" in exercise:
                    sets = exercise.pop("sets")

                    # Get existing sets for this exercise
                    existing_sets = self.set_repository.get_sets_by_exercise(
                        exercise_id
                    )
                    existing_set_ids = {s["set_id"] for s in existing_sets}

                    for set_item in sets:
                        set_id = set_item.get("set_id")

                        # If set exists, update it
                        if set_id and set_id in existing_set_ids:
                            self.set_repository.update_set(set_id, set_item)
                            existing_set_ids.remove(set_id)
                        else:
                            # If new set, create it
                            set_item["completed_exercise_id"] = exercise_id
                            set_item["workout_id"] = workout_id
                            self.set_repository.create_set(set_item)

                    # Delete any remaining sets that weren't updated
                    for set_id in existing_set_ids:
                        self.set_repository.delete_set(set_id)

        # Update the workout
        update_expression = "set "
        expression_values = {}

        for key, value in update_dict.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update(
            {"workout_id": workout_id}, update_expression, expression_values
        )

    def delete_workout(self, workout_id: str) -> Dict[str, Any]:
        """
        Deletes a workout by its ID and all its associated sets.

        :param workout_id: The ID of the workout to delete.
        :return: The deleted workout data.
        """

        # First, delete all sets for this workout
        self.set_repository.delete_sets_by_workout(workout_id)

        # Then delete the workout
        return self.delete({"workout_id": workout_id})
