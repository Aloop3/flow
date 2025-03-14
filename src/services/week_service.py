import uuid
from typing import List, Dict, Any, Optional
from src.repositories.week_repository import WeekRepository
from src.repositories.day_repository import DayRepository
from src.models.week import Week

class WeekService:
    def __init__(self):
        self.week_repository: WeekRepository = WeekRepository()
        self.day_repository: DayRepository = DayRepository()
    
    def get_week(self, week_id: str) -> Optional[Week]:
        """
        Retrieves the week data by week_id

        :param week_id: The ID of the week to retrieve.
        :return: A Week object containing the week data.
        """
        week_data = self.week_repository.get_week(week_id)
        if week_data:
            return Week(**week_data)
        return None
    
    def get_weeks_for_block(self, block_id: str) -> List[Week]:
        """
        Retrieves all the weeks associated with a specific training block by block_id

        :param block_id: The ID of the training block
        :return: A list of Week objects if found, else an empty list will be returned
        """
        weeks_data = self.week_repository.get_weeks_by_block(block_id)
        return [Week(**week_data) for week_data in weeks_data]
    
    def create_week(self, block_id: str, week_number: int, notes: Optional[str] = None) -> Week:
        """
        Creates a new week and associates it with a training block

        :param block_id: The ID of the training block to associate the week with
        :param week_number: The number of the week
        :param notes: Optional notes for the week
        :return: The created Week object
        """
        week = Week(
            week_id=str(uuid.uuid4()),
            block_id=block_id,
            week_number=week_number,
            notes=notes
        )
        
        self.week_repository.create_week(week.to_dict())
        return week
    
    def update_week(self, week_id: str, update_data: Dict[str, Any]) -> Optional[Week]:
        """
        Updates the week data by week_id

        :param week_id: The ID of the week to update
        :param update_data: A dictionary containing the updated data
        :return: The updated Week object if found, else None
        """
        self.week_repository.update_week(week_id, update_data)
        return self.get_week(week_id)
    
    def delete_week(self, week_id: str) -> bool:
        """
        Deletes the week by week_id

        :param week_id: The ID of the week to delete
        :return: True if the week was successfully deleted, else False
        """

        # Need to delete all days in this week first (cascading delete)
        self.day_repository.delete_days_by_week(week_id)

        # Delete the week itself
        response = self.week_repository.delete_week(week_id)

        return bool(response)