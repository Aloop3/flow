import uuid
from typing import List, Dict, Any, Optional
from src.repositories.day_repository import DayRepository
from src.repositories.exercise_repository import ExerciseRepository
from src.models.day import Day

class DayService:
    def __init__(self):
        self.day_repository: DayRepository = DayRepository()
        self.exercise_repository: ExerciseRepository = ExerciseRepository()
    
    def get_day(self, day_id: str) -> Optional[Day]:
        """
        Retrieves the day data by day_id

        :param day_id: The ID of the day to retrieve
        :return: A Day object containing the day data
        """
        day_data = self.day_repository.get_day(day_id)

        if day_data:
            return Day(**day_data)
        return None
    
    def get_days_for_week(self, week_id: str) -> List[Day]:
        """
        Retrieves all days for a specific week

        :param week_id: The ID of the week
        :return: A list of Day objects for the specified week
        """
        days_data = self.day_repository.get_days_by_week(week_id)
        return [Day(**day_data) for day_data in days_data]
    
    def create_day(self, week_id: str, day_number: int, date: str, focus: Optional[str] = None, notes: Optional[str] = None) -> Day:
        """
        Creates a new day

        :param week_id: The ID of the week this day belongs to
        :param day_number: The day number within the week
        :param date: The date of the day
        :param focus: The focus for the day
        :param notes: Any additional notes for the day
        :return: The created Day object
        """
        day = Day(
            day_id=str(uuid.uuid4()),
            week_id=week_id,
            day_number=day_number,
            date=date,
            focus=focus,
            notes=notes
        )

        self.day_repository.create_day(day.to_dict())
        return day
    
    def update_day(self, day_id: str, update_data: Dict[str, Any]) -> Optional[Day]:
        """
        Updates the day data by day_id

        :param day_id: The ID of the day to update
        :param update_data: A dictionary containing the updated data
        :return: The updated Day object if found, else None
        """
        self.day_repository.update_day(day_id, update_data)
        return self.get_day(day_id)
    
    def delete_day(self, day_id: str) -> bool:
        """
        Deletes the day by day_id

        :param day_id: The ID of the day to delete
        :return: True if the day was successfully deleted, else False
        """
        # Need to delete all exercises in this day first (cascading delete)
        self.exercise_repository.delete_exercise_by_day(day_id)

        # Delete the day itself
        response = self.day_repository.delete_day(day_id)

        return bool(response)