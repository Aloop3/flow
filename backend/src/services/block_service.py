import uuid
import datetime as dt
from typing import Dict, Any, Optional, List, Literal
from src.repositories.block_repository import BlockRepository
from src.repositories.week_repository import WeekRepository
from src.models.block import Block
from src.services.week_service import WeekService
from src.services.day_service import DayService


class BlockService:
    def __init__(self):
        self.block_repository: BlockRepository = BlockRepository()
        self.week_repository: WeekRepository = WeekRepository()
        self.week_service: WeekService = WeekService()
        self.day_service: DayService = DayService()

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

    def create_block(
        self,
        athlete_id: str,
        title: str,
        description: str,
        start_date: str,
        end_date: str,
        coach_id: Optional[str] = None,
        status: Literal["draft", "active", "completed"] = "draft",
        number_of_weeks: int = 4,
    ) -> Block:
        """
        Creates a new training block

        :param athlete_id: The ID of the athlete
        :param title: The title of the block
        :param description: The description of the block
        :param start_date: The start date of the block in ISO format
        :param end_date: The end date of the block in ISO format
        :param coach_id: The ID of the coach (optional), None for self-coached athletes
        :param status: The status of the block (default is "draft")
        :param number_of_weeks: Number of weeks to auto-generate (default is 4)
        :return: The created Block object
        """
        # Ensure number_of_weeks is between 4 - 12
        if number_of_weeks < 4 or number_of_weeks > 12:
            number_of_weeks = 4

        # Calculate end_date based on start_date and number_of_weeks
        start_date_obj = dt.datetime.fromisoformat(
            start_date.replace("Z", "+00:00") if "Z" in start_date else start_date
        )

        # Force start date to be in UTC, no matter the time zone in the input
        start_date_utc = start_date_obj.astimezone(dt.timezone.utc)
        start_date_str = start_date_obj.strftime("%Y-%m-%d")

        end_date_obj = start_date_obj + dt.timedelta(days=(number_of_weeks * 7) - 1)
        calculated_end_date = end_date_obj.strftime("%Y-%m-%d")

        # Create block with calculated_end_date
        block = Block(
            block_id=str(uuid.uuid4()),
            athlete_id=athlete_id,
            title=title,
            description=description,
            start_date=start_date_str,
            end_date=calculated_end_date,
            coach_id=coach_id,
            status=status,
            number_of_weeks=number_of_weeks,
        )

        # Save block to database
        self.block_repository.create_block(block.to_dict())

        # Auto-generate weeks and days
        for week_number in range(1, number_of_weeks + 1):
            # Create week
            week = self.week_service.create_week(
                block_id=block.block_id,
                week_number=week_number,
                notes=f"Week {week_number}",
            )

            for day_number in range(1, 8):
                # Calculate the date for the day
                current_date = start_date_utc + dt.timedelta(
                    days=((week_number - 1) * 7) + (day_number - 1)
                )
                formatted_date = current_date.strftime("%Y-%m-%d")

                # Create day
                self.day_service.create_day(
                    week_id=week.week_id,
                    day_number=day_number,
                    date=formatted_date,
                    focus=None,
                    notes=f"Day {day_number}",
                )

        return block

    def update_block(
        self, block_id: str, update_data: Dict[str, Any]
    ) -> Optional[Block]:
        """
        Updates an existing training block

        :param block_id: The ID of the block to update
        :param update_data: A dictionary containing the fields to update
        :return: The updated Block object if found, else None
        """
        # Get existing block to access its data
        existing_block = self.get_block(block_id)
        if not existing_block:
            return None

        # Check if we need to recalculate end_date
        if "start_date" in update_data or "number_of_weeks" in update_data:
            # Get the values to use, prioritize new values from update_data
            start_date = update_data.get("start_date", existing_block.start_date)
            number_of_weeks = update_data.get(
                "number_of_weeks", existing_block.number_of_weeks
            )

            # Calculate new end_date
            start_date_obj = dt.datetime.fromisoformat(
                start_date.replace("Z", "+00:00") if "Z" in start_date else start_date
            )

            # Force start date to be in UTC
            start_date_utc = start_date_obj.astimezone(dt.timezone.utc)
            start_date_str = start_date_utc.strftime("%Y-%m-%d")

            end_date_obj = start_date_obj + dt.timedelta(days=(number_of_weeks * 7) - 1)
            calculated_end_date = end_date_obj.strftime("%Y-%m-%d")

            # Update start_date and end_date in the update_data
            update_data["start_date"] = start_date_str
            update_data["end_date"] = calculated_end_date

        # Proceed with update to database
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
