class CompletedExercise:
    def __init__(self, completed_id, workout_id, exercise_id, actual_sets, actual_reps, actual_weight, actual_rpe, notes):
        self.completed_id = completed_id
        self.workout_id = workout_id
        self.exercise_id = exercise_id # Reference to planned exercise
        self.actual_sets = actual_sets
        self.actual_reps = actual_reps
        self.actual_weight = actual_weight
        self.actual_rpe = actual_rpe
        self.notes = notes