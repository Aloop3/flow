import boto3
from typing import Dict, Any, Optional
from boto3.resources.base import ServiceResource
from mypy_boto3_dynamodb.service_resource import Table

class BaseRepository:
    """
    A base repository class for interacting with an AWS DynamoDB table.

    This will be inherited by other entities (e.g., User, Block, etc) to resuse functionalities.
    """
    def __init__(self, table_name: str):
        """
        :param table_name: Name of DynamoDB table.
        """
        self.dynamodb: ServiceResource = boto3.resource("dynamodb")
        self.table: Table = self.dynamodb.Table(table_name)
    
    def get_by_id(self, id_name: str, id_value: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an item from the table using its primary key.

        :param id_name: The name of the primary key attribute.
        :param id_value: The value of the primary key for the item to retrieve.
        :return: The retrieved item as a dictionary, or None if not found
        """
        response = self.table.get_item(
            Key={id_name: id_value}
        )
        return response.get("Item")
    
    def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserts a new item into DynamoDB table. 
        """
        response = self.table.put_item(
            Item=item
        )
        return item
    
    def update(self, key: Dict[str, str], update_expression: str, expression_values: Dict[str, Any], expression_attribute_names: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Updates an existing item in the table.

        :param key: A dictionary specifying the primary key of the item to update.
        :param update_expression: A DynamoDB update expression defining the update.
        :param expression_values: A dictionary mapping expression attribute names to values.
        :param expression_attribute_names: 
        :return: The response containing the updated attributes.
        """
        try:
            update_args = {
                "Key": key,
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expression_values,
                "ReturnValues": "ALL_NEW"
            }
            # Only add ExpressionAttributeNames if provided
            if expression_attribute_names:
                update_args["ExpressionAttributeNames"] = expression_attribute_names
            response = self.table.update_item(**update_args)
            return response.get("Attributes", {})
        except Exception as e:
            print(f"Error updating item: {e}")
            raise 
    
    def delete(self, key: Dict[str, str]) -> Dict[str, Any]:
        """
        Deletes an item from the table.

        :param key: A dictionary specifying the primary key of the item to delete.
        :return: The response from the delete operation.
        """
        try:
            response = self.table.delete_item(
                Key=key,
                ReturnValues="ALL_OLD"
            )
            return response.get("Attributes", {})
        except Exception as e:
            print(f"Error deleting item: {e}")
            raise