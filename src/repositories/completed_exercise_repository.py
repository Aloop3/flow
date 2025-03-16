from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional, List
import os

class CompletedExerciseRepository(BaseRepository):
    def __init__(self):
        super().__init__(os.environ.get("COMPLETED_EXERCISES_TABLE", "CompletedExercises"))
    
    def get_completed_exercise(self, completed_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a completed exercise by its ID.

        :param completed_id: The ID of the completed exercise to retrieve.
        :return: A dictionary containing the completed exercise data, or None if not found.
        """
        return self.get_by_id("completed_id", completed_id)
    
    def get_completed_exercises_by_workout(self, workout_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all completed exercises for a specific workout ID
        
        :param workout_id: The ID of the workout to retrieve completed exercises for.
        :return: A list of dictionaries containing the completed exercises data.
        """
        response = self.table.query(
            IndexName="workout-index",
            KeyConditionExpression=Key("workout_id").eq(workout_id)
        )

        return response.get("Items", [])
    
    def get_completed_exercises_by_exercise(self, exercise_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all logged instances of a specific exercise 
        
        :param exercise_id: The ID of the exercise to retrieve completed exercises for.
        :return: A list of dictionaries containing the completed exercises data.
        """
        response = self.table.query(
            IndexName="exercise-index",
            KeyConditionExpression=Key("exercise_id").eq(exercise_id)
        )

        return response.get("Items", [])
    
    def create_completed_exercise(self, completed_exercise_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new completed exercise in the database.

        :param completed_exercise_data: A dictionary containing the completed exercise data.
        :return: A dictionary containing the created completed exercise data.
        """
        return self.create(completed_exercise_dict)
    
    def update_completed_exercise(self, completed_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing completed exercise by completed_id
        
        :param completed_id: The ID of the completed exercise to update.
        :param update_dict: A dictionary containing the updated data for the completed exercise.
        :return: A dictionary containing the updated completed exercise data.
        """
        update_expression = "set "
        expression_attribute_names = {}
        expression_values = {}

        # Attribute name handling to avoid reserved word conflicts
        for key, value in update_dict.items():
            update_expression += f"#{key} = :{key}, "
            expression_attribute_names[f"#{key}"] = key
            expression_values[f":{key}"] = value
        
        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        return self.update(
            {"completed_id": completed_id},
            update_expression,
            expression_values,
            expression_attribute_names
        )
    
    def delete_completed_exercise(self, completed_id: str) -> Dict[str, Any]:
        """
        Deletes a completed exercise by completed_id

        :param completed_id: The ID of the completed exercise to delete.
        :return: A dictionary containing the deleted completed exercise data.
        """
        return self.delete({"completed_id": completed_id})
    
    def delete_completed_exercises_by_workout(self, workout_id: str) -> int:
        """
        Deletes all completed exercises for a specific workout ID (cascading delete)

        :param workout_id: The ID of the workout to delete completed exercises for.
        :return: The number of completed exercises deleted.
        """
        completed_exercises = self.get_completed_exercises_by_workout(workout_id)

        # Batch delete all completed exercises
        with self.table.batch_writer() as batch:
            for exercise in completed_exercises:
                batch.delete_item(
                    Key={"completed_id": exercise["completed_id"]}
                )
        
        return len(completed_exercises)