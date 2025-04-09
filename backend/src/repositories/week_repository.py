from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional, List
from src.config.week_config import WeekConfig


class WeekRepository(BaseRepository):
    def __init__(self):
        super().__init__(WeekConfig.TABLE_NAME)

    def get_week(self, week_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a week by its unique week ID.

        :param week_id: The unique identifier of the week.
        :return: A dictionary containing the week details if found, else None.
        """
        return self.get_by_id("week_id", week_id)

    def get_weeks_by_block(self, block_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all weeks associated with a specific block using a DynamoDB GSI.

        :param block_id: The unique identifier of the block.
        :return: A list of week dictionaries associated with the block.
        """
        response = self.table.query(
            IndexName=WeekConfig.BLOCK_INDEX,
            KeyConditionExpression=Key("block_id").eq(block_id),
            Limit=WeekConfig.MAX_ITEMS,
        )
        return response.get("Items", [])

    def create_week(self, week_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new week in the database.

        :param week_dict: A dictionary containing the week details.
        :return: The response from the create operation.
        """
        return self.create(week_dict)

    def update_week(self, week_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing week in the database.

        :param week_id: The unique identifier of the week to update.
        :param update_dict: A dictionary containing the attributes to update.
        :return: The response from the update operation.
        """
        update_expression = "set "
        expression_values = {}

        for key, value in update_dict.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update({"week_id": week_id}, update_expression, expression_values)

    def delete_week(self, week_id: str) -> Dict[str, Any]:
        """
        Deletes a week from the database.

        :param week_id: The unique identifier of the week to delete.
        :return: The response from the delete operation.
        """
        return self.delete({"week_id": week_id})

    def delete_weeks_by_block(self, block_id: str) -> int:
        """
        Deletes all weeks associated with a specific block (cascading delete).

        :param block_id: The unique identifier of the block.
        :return: The number of weeks deleted
        """
        weeks = self.get_weeks_by_block(block_id)

        # Batch delete all weeks
        with self.table.batch_writer() as batch:
            for week in weeks:
                batch.delete_item(Key={"week_id": week["week_id"]})

        return len(weeks)
