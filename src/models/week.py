class Week:
    def __init__(self, week_id, block_id, week_number, notes):
        self.week_id = week_id
        self.block_id = block_id
        self.week_number = week_number
        self.notes = notes

    def to_dict(self):
        return {
            "week_id": self.week_id,
            "block_id": self.block_id,
            "week_number": self.week_number,
            "notes": self.notes
        }