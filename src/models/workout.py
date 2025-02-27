class Workout:
    def __init__(self, workout_id, athlete_id, day_id, date, notes, status):
        self.workout_id = workout_id
        self.athlete_id = athlete_id
        self.day_id = day_id
        self.date = date
        self.notes = notes
        self.status = status # "completed", "partial", "skipped"
        self.exercises = [] # List of CompletedExercise objects

    def to_dict(self):
        return {
            "workout_id": self.workout_id,
            "athlete_id": self.athlete_id,
            "day_id": self.day_id,
            "date": self.date,
            "notes": self.notes,
            "status": self.status,
            "exercises": [ex.to_dict() for ex in self.exercises]
        }