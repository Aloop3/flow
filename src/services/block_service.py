import uuid
import datetime as dt
from typing import Dict, Any, Optional, List, Literal
from src.repositories.block_repository import BlockRepository
from src.repositories.week_repository import WeekRepository
from src.models.block import Block

class BlockService:
    def __init__(self):
        self.block_repository: BlockRepository = BlockRepository()
        self.week_repository: WeekRepository = WeekRepository()

    def get_block(self, block_id: str) -> Optional[Block]:
        """
        Retrieves a block by block_id

        :param block_id: The ID of the block to retrieve
        :return: The Block object if found, else None
        """
        block_data = self.block_repository.get_block(block_id)

        if block_data:
            return Block(**block_data)
        return None
    
    def get_blocks_for_athlete(self, athlete_id: str) -> List[Block]:
        """
        Retrieves all blocks for an athlete

        :param athlete_id: The ID of the athlete
        :return: A list of Block objects for the athlete
        """
        block_data = self.block_repository.get_blocks_by_athlete(athlete_id)
        return [Block(**block) for block in block_data]
    
    def create_block(self, athlete_id: str, title: str, description: str, start_date: str, end_date: str, coach_id: Optional[str] = None, status: Literal["draft", "active", "completed"] = "draft") -> Block:
        """
        Creates a new training block

        :param athlete_id: The ID of the athlete
        :param title: The title of the block
        :param description: The description of the block
        :param start_date: The start date of the block in ISO format
        :param end_date: The end date of the block in ISO format
        :param coach_id: The ID of the coach (optional), None for self-coached athletes
        :param status: The status of the block (default is "draft")
        :return: The created Block object
        """
        block = Block(
            block_id=str(uuid.uuid4()),
            athlete_id=athlete_id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            coach_id=coach_id,
            status=status
        )

        self.block_repository.create_block(block.to_dict())

        return block
    
    def update_block(self, block_id: str, update_data: Dict[str, Any]) -> Optional[Block]:
        """
        Updates an existing training block

        :param block_id: The ID of the block to update
        :param update_data: A dictionary containing the fields to update
        :return: The updated Block object if found, else None
        """
        self.block_repository.update_block(block_id, update_data)

        return self.get_block(block_id)
    
    def delete_block(self, block_id: str) -> bool:
        """
        Deletes a training block

        :param block_id: The ID of the block to delete
        :return: True if the block was successfully deleted, else False
        """
        try:
            # First delete all weeks associated with this block (which will cascade delete days and exercises)
            self.week_repository.delete_weeks_by_block(block_id)

            # Then delete the block itself
            response = self.block_repository.delete_block(block_id)
            return bool(response)
        except Exception as e:
            print(f"Error deleting block: {e}")
            return False
    