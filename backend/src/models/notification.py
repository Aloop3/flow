from typing import Dict, Any, Optional
from datetime import datetime
import copy


class Notification:
    def __init__(
        self,
        notification_id: str,
        coach_id: str,
        athlete_id: str,
        athlete_name: str,
        workout_id: str,
        day_info: str,
        workout_data: Dict[str, Any],
        created_at: Optional[str] = None,
        is_read: bool = False,
        notification_type: str = "workout_completion",
    ):
        self.notification_id = notification_id
        self.coach_id = coach_id
        self.athlete_id = athlete_id
        self.athlete_name = athlete_name
        self.workout_id = workout_id
        self.day_info = day_info  # e.g., "Day 5 (2024-06-25)"
        self.workout_data = workout_data  # Full workout object for modal display
        self.created_at = created_at or datetime.now().isoformat() + "Z"
        self.is_read = is_read
        self.notification_type = notification_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary for DynamoDB storage"""
        return {
            "notification_id": self.notification_id,
            "coach_id": self.coach_id,
            "athlete_id": self.athlete_id,
            "athlete_name": self.athlete_name,
            "workout_id": self.workout_id,
            "day_info": self.day_info,
            "workout_data": copy.deepcopy(
                self.workout_data
            ),  # Deep copy to prevent mutation
            "created_at": self.created_at,
            "is_read": self.is_read,
            "notification_type": self.notification_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Create notification instance from DynamoDB data"""
        return cls(
            notification_id=data["notification_id"],
            coach_id=data["coach_id"],
            athlete_id=data["athlete_id"],
            athlete_name=data["athlete_name"],
            workout_id=data["workout_id"],
            day_info=data["day_info"],
            workout_data=data["workout_data"],
            created_at=data.get("created_at"),
            is_read=data.get("is_read", False),
            notification_type=data.get("notification_type", "workout_completion"),
        )

    def mark_as_read(self) -> None:
        """Mark notification as read"""
        self.is_read = True
