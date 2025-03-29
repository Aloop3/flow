from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional, List
import os


class DayRepository(BaseRepository):
    def __init__(self):
        super().__init__(os.environ.get("DAYS_TABLE", "Days"))

    def get_day(self, day_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a day from the DAYS_TABLE by day_id

        :param day_id: The ID of the day to retrieve
        :return: A dictionary representing the day if found, otherwise None
        """
        return self.get_by_id("day_id", day_id)

    def get_days_by_week(self, week_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all days from the DAYS_TABLE for a given week_id

        :param week_id: The ID of the week to retrieve days for
        :return: A list of dictionaries representing the days for the given week
        """
        response = self.table.query(
            IndexName="week-index", KeyConditionExpression=Key("week_id").eq(week_id)
        )

        return response.get("Items", [])

    def create_day(self, day_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new day in the DAYS_TABLE

        :param day_dict: A dictionary containing the day data
        :return: The created day dictionary
        """
        return self.create(day_dict)

    def update_day(self, day_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing day in the DAYS_TABLE

        :param day_id: The ID of the day to update
        :param update_dict: A dictionary containing the updated day data
        :return: The updated day dictionary
        """
        update_expression = "set "
        expression_values = {}

        for key, value in update_dict.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value

        # Remove training comma and space
        update_expression = update_expression[:-2]

        return self.update({"day_id": day_id}, update_expression, expression_values)

    def delete_day(self, day_id: str) -> Dict[str, Any]:
        """
        Deletes a day from the DAYS_TABLE

        :param day_id: The ID of the day to delete
        :return: The deleted day dictionary
        """
        return self.delete({"day_id": day_id})

    def delete_day_by_week(self, week_id: str) -> Dict[str, Any]:
        """
        Delete all days associated with a given week_id (cascading delete)

        :param week_id: The ID of the week to delete days for
        :return: The response from the delete operation
        """
        days = self.get_days_by_week(week_id)

        # Batch delete all days
        with self.table.batch_writer() as batch:
            for day in days:
                batch.delete_item(Key={"day_id": day["day_id"]})

        return len(days)
