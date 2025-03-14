from typing import Dict, Any, Optional

class Day:
    def __init__(self, day_id: str, week_id: int, day_number: int, date: str, focus: Optional[str] = None, notes: Optional[str] = None):
        self.day_id: str = day_id
        self.week_id: int = week_id
        self.day_number: int = day_number
        self.date: str = date
        self.focus: str = focus or "" # "squat", "bench", "deadlift", "rest"
        self.notes: str = notes or ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day_id": self.day_id,
            "week_id": self.week_id,
            "day_number": self.day_number,
            "date": self.date,
            "focus": self.focus,
            "notes": self.notes
        }