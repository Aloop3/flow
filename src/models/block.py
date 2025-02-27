class Block:
    def __init__(self, block_id, athlete_id, coach_id, title, description, start_date, end_date, status):
        self.block_id = block_id
        self.athlete_id = athlete_id
        self.coach_id = coach_id
        self.title = title
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status # "draft", "active", "completed"
    
    def to_dict(self):
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
