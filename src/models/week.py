from typing import Dict, Any, Optional

class Week:
    def __init__(self, week_id: str, block_id: str, week_number: int, notes: Optional[str] = None):
        self.week_id: str = week_id
        self.block_id: str = block_id
        self.week_number: int = week_number
        self.notes: str = notes or ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "week_id": self.week_id,
            "block_id": self.block_id,
            "week_number": self.week_number,
            "notes": self.notes
        }