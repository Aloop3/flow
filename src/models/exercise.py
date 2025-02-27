class Exercise:
    def __init__(self, exercise_id, day_id, exercise_type, sets, reps, weight, rpe, notes, order):
        self.exercise_id = exercise_id
        self.day_id = day_id
        self.exercise_type = exercise_type # "squat", "bench", "deadlift"
        self.sets = sets # Planned sets
        self.reps = reps # Planned reps
        self.weight = weight # Planned weight
        self.rpe = rpe # Planned RPE
        self.notes = notes
        self.order = order # Sequence in workout
    
    def to_dict(self):
        return {
            "exercise_id": self.exercise_id,
            "day_id": self.day_id,
            "exercise_type": self.exercise_type,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
            "rpe": self.rpe,
            "notes": self.notes,
            "order": self.order
        }