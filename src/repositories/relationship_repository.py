from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, Optional, List
import os

class RelationshipRepository(BaseRepository):
    def __init__(self):
        super().__init__(os.environ.get("RELATIONSHIPS_TABLE", "Relationships"))

    def get_relationship(self, relationship_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a relationship by its ID.

        :param relationship_id: The ID of the relationship to retrieve.
        :return: A dictionary containing the relationship data if found, None otherwise.
        """
        return self.get_by_id("relationship_id", relationship_id)
    
    def get_relationships_for_coach(self, coach_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves relationships by coach ID, optionally filtered by status.
        
        :param coach_id: The ID of the coach.
        :param status: The status of the relationship (optional).
        :return: A list of dictionaries containing the relationships data.
        """
        query_params = {
            "IndexName": "coach-index",
            "KeyConditionExpression": Key("coach_id").eq(coach_id)
        }

        if status:
            query_params["FilterExpression"] = Attr("status").eq(status)

        response = self.table.query(**query_params)
        return response.get("Items", [])
    
    def get_active_relationship(self, coach_id: str, athlete_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves active relationship between coac and athlete if exists
        
        :param coach_id: The ID of the coach.
        :param athlete_id: The ID of the athlete.
        :return: A dictionary containing the relationship data if found, None otherwise.
        """
        response = self.table.query(
            IndexName="coach-athlete-index",
            KeyConditionExpression=Key("coach_id").eq(coach_id) & Key("athlete_id").eq(athlete_id),
            FilterExpression=Attr("status").eq("active")
        )

        items = response.get("Items", [])
        return items[0] if items else None
    
    def create_relationship(self, relationship_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new relationship.

        :param relationship_dict: A dictionary containing the relationship data.
        :return: The created relationship data.
        """
        return self.create(relationship_dict)
    
    def update_relationship(self, relationship_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing relationship.

        :param relationship_id: The ID of the relationship to update.
        :param update_dict: A dictionary containing the updated data.
        :return: The updated relationship data.
        """
        update_expression = "set "
        expression_attribute_values = {}
        expression_attribute_names = {}

        for key, value in update_dict.items():
            attribute_placeholder = f"#{key}"
            value_placeholder = f":{key}"

            update_expression += f"{attribute_placeholder} = {value_placeholder}, "
            expression_attribute_values[value_placeholder] = value
            expression_attribute_names[attribute_placeholder] = key

        # Remove trailing comma and space
        update_expression = update_expression[:-2]

        response = self.table.update_item(
            Key={"relationship_id": relationship_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )

        return response.get("Attributes", {})
    
    def delete_relationship(self, relationship_id: str) -> Dict[str, Any]:
        """
        Deletes a relationship by its ID.

        :param relationship_id: The ID of the relationship to delete.
        :return: The deleted relationship data.
        """
        return self.delete({"relationship_id": relationship_id})
    