"""
Weight conversion utilities
All weights are stored in kg internally and converted at API boundaries.
"""


def lb_to_kg(weight_lb: float) -> float:
    """
    Convert pounds to kilograms.

    :param weight_lb: Weight in pounds
    :return: Weight in kilograms, rounded to 2 decimal places
    """
    return round(weight_lb * 0.453592, 2)


def kg_to_lb(weight_kg: float) -> float:
    """
    Convert kilograms to pounds.

    :param weight_kg: Weight in kilograms
    :return: Weight in pounds, rounded to 2 decimal places
    """
    return round(weight_kg * 2.20462, 2)


def convert_weight_to_kg(weight: float, from_unit: str) -> float:
    """
    Convert weight from any unit to kilograms (internal storage format).

    :param weight: Weight value
    :param from_unit: Source unit ("kg" or "lb")
    :return: Weight in kilograms
    """
    if from_unit.lower() == "lb":
        return lb_to_kg(weight)
    elif from_unit.lower() == "kg":
        return weight
    else:
        raise ValueError(f"Unsupported weight unit: {from_unit}")


def convert_weight_from_kg(weight_kg: float, to_unit: str) -> float:
    """
    Convert weight from kilograms (internal storage) to display unit.

    :param weight_kg: Weight in kilograms
    :param to_unit: Target unit ("kg" or "lb")
    :return: Weight in target unit
    """
    if to_unit.lower() == "lb":
        return kg_to_lb(weight_kg)
    elif to_unit.lower() == "kg":
        return weight_kg
    else:
        raise ValueError(f"Unsupported weight unit: {to_unit}")


def get_exercise_default_unit(exercise_type, user_preference="auto"):
    """
    Determine the appropriate weight unit for an exercise

    :param exercise_type: ExerciseType object or string name of the exercise
    :param user_preference: User's weight preference ("auto", "kg", "lb")
    :return: "kg" or "lb"
    """
    if user_preference == "kg":
        return "kg"
    elif user_preference == "lb":
        return "lb"

    # Handle both ExerciseType objects and strings
    if hasattr(exercise_type, "name"):
        exercise_name = exercise_type.name
    else:
        exercise_name = str(exercise_type)

    # Auto behavior: Big 3 → kg, accessories → lb
    exercise_lower = exercise_name.lower()

    big_three_keywords = ["squat", "bench press", "deadlift"]
    is_big_three = any(keyword in exercise_lower for keyword in big_three_keywords)

    return "kg" if is_big_three else "lb"
