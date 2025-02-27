class Day:
    def __init__(self, day_id, week_id, day_number, date, focus, notes):
        self.day_id = day_id
        self.week_id = week_id
        self.day_number = day_number
        self.date = date
        self.focus = focus # "squat", "bench", "deadlift", "rest"
        self.notes = notes

    def to_dict(self):
        return {
            "day_id": self.day_id,
            "week_id": self.week_id,
            "day_number": self.day_number,
            "date": self.date,
            "focus": self.focus,
            "notes": self.notes
        }