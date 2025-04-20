from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, Optional, List
from src.config.workout_config import WorkoutConfig


class WorkoutRepository(BaseRepository):
    def __init__(self):
        super().__init__(WorkoutConfig.TABLE_NAME)

    def get_workout(self, workout_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a workout by its ID with all its exercises.

        :param workout_id: The ID of the workout to retrieve.
        :return: A dictionary containing the workout data if found, None otherwise.
        """

        return self.get_by_id("workout_id", workout_id)

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

        return response.get("Items", [])

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

        return items[0]

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

        return response.get("Items", [])

    def get_exercises_by_type(
        self, athlete_id: str, exercise_type: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all exercises of a specific type for a specific athlete.

        :param athlete_id: The ID of the athlete.
        :param exercise_type: The type of exercise to filter by.
        :return: A list of dictionaries containing the exercise data.
        """
        # Get all workouts for the athlete
        workouts = self.get_workouts_by_athlete(athlete_id)

        # Filter for exercises of the requested type
        matching_exercises: List[Dict[str, Any]] = []

        for workout in workouts:
            for exercise in workout.get("exercises", []):
                # Check if this is the exercise type we're looking for
                if exercise.get("exercise_type") == exercise_type:
                    # Add workout date and status to the exercise data
                    exercise_data = {**exercise}
                    exercise_data["date"] = workout["date"]
                    exercise_data["workout_status"] = workout["status"]
                    matching_exercises.append(exercise_data)

        return matching_exercises

    def create_workout(self, workout_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new workout with its exercises.

        :param workout_dict: A dictionary containing the workout data.
        :return: The created workout data.
        """
        return self.create(workout_dict)

    def update_workout(
        self, workout_id: str, update_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing workout and its exercises.

        :param workout_id: The ID of the workout to update.
        :param update_dict: A dictionary containing the updated data.
        :return: The updated workout data.
        """
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
        Deletes a workout by its ID and all its associated exercises.

        :param workout_id: The ID of the workout to delete.
        :return: The deleted workout data.
        """
        return self.delete({"workout_id": workout_id})
