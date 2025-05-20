from typing import Dict, Literal, Any, Optional
import datetime as dt


class Relationship:
    def __init__(
        self,
        relationship_id: str,
        coach_id: str,
        athlete_id: Optional[str] = None,
        status: Literal["pending", "active", "ended"] = "pending",
        created_at: str = None,
        invitation_code: Optional[str] = None,
        expiration_time: Optional[int] = None,
    ):
        self.relationship_id: str = relationship_id
        self.coach_id: str = coach_id
        self.athlete_id: Optional[str] = athlete_id
        self.status: Literal["pending", "active", "ended"] = status
        self.created_at: str = created_at or dt.datetime.now().isoformat()
        self.invitation_code: Optional[str] = invitation_code
        self.expiration_time: Optional[int] = expiration_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "coach_id": self.coach_id,
            "athlete_id": self.athlete_id,
            "status": self.status,
            "created_at": self.created_at,
            "invitation_code": self.invitation_code,
            "expiration_time": self.expiration_time,
        }
