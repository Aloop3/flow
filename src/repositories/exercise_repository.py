from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional, List
import os

class ExerciseRepository(BaseRepository):
    def __init__(self):
        super().__init__(os.environ.get("EXERCISES_TABLE", "Exercises"))

    def get_exercise(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("exercise_id", exercise_id)
    
    def get_exercises_by_day(self, day_id: str) -> List[Dict[str, Any]]:
        """
        Get all exxercises for a given day_id
        
        :param day_id: The day_id to filter exercises by
        :return: A list of exercises for the given day_id
        """
        response = self.table.query(
            IndexName="day-index",
            KeyConditionExpression=Key("day_id").eq(day_id)
        )

        return response.get("Items", [])
    
    def create_exercise(self, exercise_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new exercise

        :param exercis_dict: The exercise to create
        :return: The created exercise dictionary
        """
        return self.create(exercise_dict)
    
    def update_exercise(self, exercise_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing exercise by exercise_id
        
        :param exercise_id: The ID of the exercise to update
        :param update_dict: A dictionary conatining the updated exercise data
        :return: The updated exercise dictionary
        """
        update_expression = "set "
        expression_values = {}

        for key, value in update_dict.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update(
            {"exercise_id": exercise_id},
            update_expression,
            expression_values
        )
    
    def delete_exercise(self, exercise_id: str) -> Dict[str, Any]:
        """
        Delete an exercise by exercise_id

        :param exercise_id: The ID of the exercise to delete
        :return: The deleted exercise dictionary
        """
        return self.delete({"exercise_id": exercise_id})
    
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
                batch.delete_item(
                    Key={"exercise_id": exercise["exercise_id"]}
                )
        
        return len(exercises)
