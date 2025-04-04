from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional, List
from src.config.set_config import SetConfig


class SetRepository(BaseRepository):
    """
    Repository class for handling set-level database operations in DynamoDB.

    Extends BaseRepository to provide methods for retrieving, creating, updating, and deleting set data.
    """

    def __init__(self):
        super().__init__(SetConfig.TABLE_NAME)

    def get_set(self, set_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a set by its ID.

        :param set_id: The ID of the set to retrieve.
        :return: A dictionary containing the set data if found, None otherwise.
        """

        return self.get_by_id("set_id", set_id)

    def get_sets_by_exercise(self, completed_exercise_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all sets for a specific completed exercise.

        :param completed_exercise_id: The ID of the completed exercise.
        :return: A list of dictionaries containing the sets data.
        """

        response = self.table.query(
            IndexName=SetConfig.EXERCISE_INDEX,
            KeyConditionExpression=Key("completed_exercise_id").eq(
                completed_exercise_id
            ),
            Limit=SetConfig.MAX_ITEMS,
        )

        return response.get("Items", [])

    def get_sets_by_workout(self, workout_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all sets for a specific workout.

        :param workout_id: The ID of the workout.
        :return: A list of dictionaries containing the sets data.
        """

        response = self.table.query(
            IndexName=SetConfig.WORKOUT_INDEX,
            KeyConditionExpression=Key("workout_id").eq(workout_id),
            Limit=SetConfig.MAX_ITEMS,
        )
        return response.get("Items", [])

    def create_set(self, set_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new set.

        :param set_dict: A dictionary containing the set data.
        :return: The created set data.
        """

        return self.create(set_dict)

    def update_set(self, set_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing set.

        :param set_id: The ID of the set to update.
        :param update_dict: A dictionary containing the updated data.
        :return: The updated set data.
        """

        update_expression = "set "
        expression_values = {}

        for key, value in update_dict.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update({"set_id": set_id}, update_expression, expression_values)

    def delete_set(self, set_id: str) -> Dict[str, Any]:
        """
        Deletes a set by its ID.

        :param set_id: The ID of the set to delete.
        :return: The deleted set data.
        """

        return self.delete({"set_id": set_id})

    def delete_sets_by_exercise(self, completed_exercise_id: str) -> int:
        """
        Deletes all sets for a specific completed exercise (cascading delete).

        :param completed_exercise_id: The ID of the completed exercise.
        :return: The number of sets deleted.
        """

        sets = self.get_sets_by_exercise(completed_exercise_id)

        # Batch delete all sets
        with self.table.batch_writer() as batch:
            for set_item in sets:
                batch.delete_item(Key={"set_id": set_item["set_id"]})

        return len(sets)

    def delete_sets_by_workout(self, workout_id: str) -> int:
        """
        Deletes all sets for a specific workout (cascading delete).

        :param workout_id: The ID of the workout to delete sets for.
        :return: The number of sets deleted.
        """
        sets = self.get_sets_by_workout(workout_id)

        # Batch delete all sets
        with self.table.batch_writer() as batch:
            for set_item in sets:
                batch.delete_item(Key={"set_id": set_item["set_id"]})

        return len(sets)
