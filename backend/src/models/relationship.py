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
        ttl: Optional[int] = None,
    ):
        self.relationship_id: str = relationship_id
        self.coach_id: str = coach_id
        self.athlete_id: Optional[str] = athlete_id
        self.status: Literal["pending", "active", "ended"] = status
        self.created_at: str = created_at or dt.datetime.now().isoformat()
        self.invitation_code: Optional[str] = invitation_code
        self.ttl: Optional[int] = ttl

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "relationship_id": self.relationship_id,
            "coach_id": self.coach_id,
            "status": self.status,
            "created_at": self.created_at,
        }

        # Only add non-None values
        if self.athlete_id is not None:
            result["athlete_id"] = self.athlete_id

        if self.invitation_code is not None:
            result["invitation_code"] = self.invitation_code

        if self.ttl is not None:
            result["ttl"] = self.ttl

        return result
