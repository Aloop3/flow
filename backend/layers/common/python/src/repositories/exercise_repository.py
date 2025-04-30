from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional, List
from src.config.exercise_config import ExerciseConfig


class ExerciseRepository(BaseRepository):
    def __init__(self):
        super().__init__(ExerciseConfig.TABLE_NAME)

    def get_exercise(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an exercise by its ID

        :param exercise_id: The ID of the exercise to get
        :return: The exercise data, or None if not found
        """
        return self.get_by_id("exercise_id", exercise_id)

    def get_exercises_by_workout(self, workout_id: str) -> List[Dict[str, Any]]:
        """
        Get all exercises for a given workout_id

        :param workout_id: The workout_id to filter exercises by
        :return: A list of exercises for the given workout_id
        """
        response = self.table.query(
            IndexName=ExerciseConfig.WORKOUT_INDEX,
            KeyConditionExpression=Key("workout_id").eq(workout_id),
            Limit=ExerciseConfig.MAX_ITEMS,
        )

        return response.get("Items", [])

    def get_exercises_by_day(self, day_id: str) -> List[Dict[str, Any]]:
        """
        Get all exercises for a given day_id

        :param day_id: The day_id to filter exercises by
        :return: A list of exercises for the given day_id
        """
        response = self.table.query(
            IndexName=ExerciseConfig.DAY_INDEX,
            KeyConditionExpression=Key("day_id").eq(day_id),
            Limit=ExerciseConfig.MAX_ITEMS,
        )

        return response.get("Items", [])

    def get_completed_exercises_by_type(
        self, athlete_id: str, exercise_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get all completed exercises of a specific type

        :param athlete_id: The athlete's ID
        :param exercise_type: The type of exercise to filter by
        :return: A list of completed exercises
        """
        # This would need to join with the workout table
        # Consider implementing a denormalized data pattern for better performance
        pass

    def create_exercise(self, exercise_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new exercise

        :param exercise_dict: The exercise to create
        :return: The created exercise dictionary
        """
        return self.create(exercise_dict)

    def update_exercise(
        self, exercise_id: str, update_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing exercise by exercise_id

        :param exercise_id: The ID of the exercise to update
        :param update_dict: A dictionary containing the updated exercise data
        :return: The updated exercise dictionary
        """
        update_expression = "set "
        expression_values = {}
        expression_attribute_names = {}

        for key, value in update_dict.items():
            attr_name = f"#{key}"
            expression_attribute_names[attr_name] = key
            update_expression += f"{attr_name} = :{key}, "
            expression_values[f":{key}"] = value

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update(
            {"exercise_id": exercise_id},
            update_expression,
            expression_values,
            expression_attribute_names,
        )

    def delete_exercise(self, exercise_id: str) -> Dict[str, Any]:
        """
        Delete an exercise by exercise_id

        :param exercise_id: The ID of the exercise to delete
        :return: The deleted exercise dictionary
        """
        return self.delete({"exercise_id": exercise_id})

    def delete_exercises_by_workout(self, workout_id: str) -> int:
        """
        Delete all exercises associated with a given workout_id (cascading delete)

        :param workout_id: The workout_id to filter exercises by
        :return: The number of exercises deleted
        """
        exercises = self.get_exercises_by_workout(workout_id)

        # Batch delete all exercises
        with self.table.batch_writer() as batch:
            for exercise in exercises:
                batch.delete_item(Key={"exercise_id": exercise["exercise_id"]})

        return len(exercises)

    def delete_exercises_by_day(self, day_id: str) -> int:
        """
        Delete all exercises associated with a given day_id (cascading delete)

        :param day_id: The day_id to filter exercises by
        :return: The number of exercises deleted
        """
        exercises = self.get_exercises_by_day(day_id)

        # Batch delete all exercises
        with self.table.batch_writer() as batch:
            for exercise in exercises:
                batch.delete_item(Key={"exercise_id": exercise["exercise_id"]})

        return len(exercises)
