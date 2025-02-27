from .base_repository import BaseRepository
from boto3.dynamodb.conditions import Key
import os

class BlockRepository(BaseRepository):
    """
    Repository class for handling block-related database operations in DynamoDB.

    Extends BaseRepository to provide methods for retrieving, creating, updating, and deleting training blocks associated with athletes and coaches.
    """
    def __init__(self):
        super().__init__(os.environ.get("BLOCKS_TABLE"))

    def get_block(self, block_id):
        """
        Retrieves a training blcok by its unique block ID.

        :param block_id: The unique identifier of the block.
        :return: A dictionary containing the block details if found, else None.
        """
        return self.get_by_id("block_id", block_id)
    
    def get_blocks_by_athlete(self, athlete_id):
        """
        Retrieves all blocks associated with a specific athlete using a DynamoDB GSI.

        :param athlete_id: The unique identifier of the athlete.
        :return: A list of block dictionaries associated with the athlete.
        """
        response = self.table.query(
            IndexName="athlete-index",
            KeyConditionExpression=Key("athlete_id").eq(athlete_id)
        )
        return response.get("Items", [])
    
    def get_blocks_by_coach(self, coach_id):
        """
        Retrieves all blocks associated with a specific coach using a DynamoDB GSI.

        :param coach_id: The unique identifier of the coach.
        :return: A list of block dictionaries associated with the coach.
        """
        response = self.table.query(
            IndexName="coach-index",
            KeyConditionExpression=Key("coach_id").eq(coach_id)
        )
        return response.get("Items", [])
    
def get_blocks_by_coach_and_athlete(self, coach_id, athlete_id):
    """
    Retrieves all blocks for a specific athlete associated by a specific coach.

    :param coach_id: The unique identifier of the coach.
    :param athlete_id: The unique identifier of the athlete.
    :return: A list of block dictionaries associated with the given athlete and coach.
    """
    response = self.table.query(
        IndexName="athlete-index", # Query using athlete_id
        KeyConditionExpression=Key("athlete_id").eq(athlete_id),
        FilterExpression=Key("coach_id").eq(coach_id) # Filter to match coach_id
    )
    
    def create_block(self, block_dict):
        """
        Creates a new training block in the database.

        :param block_dict: A dictionary containing the block details.
        :return: The response from the create operation.
        """
        return self.create(block_dict)
    
    def update_block(self, block_id, update_dict):
        """
        Updates an existing block in the database.

        :param block_id: The unique identifiedr of the block to update.
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

        return self.update(
            {"block_id": block_id},
            update_expression,
            expression_values
        )
    
    def delete_block(self, block_id):
        """
        Deletes a training block from the database.

        :param block_id: The unique identifier of the block to delete.
        :return: The response from the delete operation.
        """
        return self.delete({"block_id": block_id})