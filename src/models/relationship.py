class Relationship:
    def __init__(self, relationship_id, coach_id, athlete_id, status, created_at):
        self.relationship_id = relationship_id
        self.coach_id = coach_id
        self.athlete_id = athlete_id
        self.status = status # "pending", "active", "ended"
        self.created_at = created_at
    
    def to_dict(self):
        return {
            "relationship_id": self.relationship_id,
            "coach_id": self.coach_id,
            "athlete_id": self.athlete_id,
            "status": self.status,
            "created_at": self.created_at
        }