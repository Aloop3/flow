POWERLIFTING_EXERCISES = ["squat", "bench press", "deadlift"]


def get_default_unit(exercise_type: str, user_preference: str) -> str:
    """
    Simple rule: powerlifting = kg, everything else = user preference

    :param exercise_type: Name of the exercise
    :param user_preference: User's preferred weight unit ('kg' or 'lb')
    :return: Default weight unit for this exercise
    """
    if any(ex in exercise_type.lower() for ex in POWERLIFTING_EXERCISES):
        return "kg"
    return user_preference
