from typing import Dict, Literal, Any, Optional

class Block:
    def __init__(self, block_id: str, athlete_id: str, title: str, description: str, start_date: str, end_date: str, status: Literal["draft", "active", "completed"], coach_id: Optional[str] = None):
        self.block_id: str = block_id
        self.athlete_id: str = athlete_id
        self.coach_id: Optional[str] = coach_id
        self.title: str = title
        self.description: str = description
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.status: Literal["draft", "active", "completed"] = status
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "athlete_id": self.athlete_id,
            "coach_id": self.coach_id,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status
        }
