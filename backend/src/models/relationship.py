from typing import Dict, Literal, Any


class Relationship:
    def __init__(
        self,
        relationship_id: str,
        coach_id: str,
        athlete_id: str,
        status: Literal["pending", "active", "ended"],
        created_at: str,
    ):
        self.relationship_id: str = relationship_id
        self.coach_id: str = coach_id
        self.athlete_id: str = athlete_id
        self.status: Literal["pending", "active", "ended"] = status
        self.created_at: str = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "coach_id": self.coach_id,
            "athlete_id": self.athlete_id,
            "status": self.status,
            "created_at": self.created_at,
        }
