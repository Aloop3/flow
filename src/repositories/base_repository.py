import boto3
import os
from boto3.dynamodb.conditions import Key, Attr

class BaseRepository:
    """
    A base repository class for interacting with an AWS DynamoDB table.

    This will be inherited by other entities (e.g., User, Block, etc) to resuse functionalities.
    """
    def __init__(self, table_name):
        """
        :param table_name: Name of DynamoDB table.
        """
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
    
    def get_by_id(self, id_name, id_value):
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
    
    def create(self, item):
        """
        Inserts a new item into DynamoDB table. 
        """
        response = self.table.put_item(
            Item=item
        )
    
    def update(self, key, update_expression, expression_values):
        """
        Updates an existing item in the table.

        :param key: A dictionary specifying the primary key of the item to update.
        :param update_expression: A DynamoDB update expression defining the update.
        :param expression_values: A dictionary mapping expression attribute names to values.
        :return: The response containing the updated attributes.
        """
        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        return response
    
    def delete(self, key):
        """
        Deletes an item from the table.

        :param key: A dictionary specifying the primary key of the item to delete.
        :return: The response from the delete operation.
        """
        response = self.table.delete_item(
            Key=key
        )
        return response