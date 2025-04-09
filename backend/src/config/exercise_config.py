from src.config.base_config import BaseConfig


class ExerciseConfig(BaseConfig):
    """
    Exercise resource configuration.

    Contains table names, index names, and other configuration specific to
    the Exercise domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("EXERCISES_TABLE", "Exercises")

    # DynamoDB Global Secondary Index Names
    DAY_INDEX = "day-index"
    WORKOUT_INDEX = "workout-index"

    # API Rate Limits (per minute)
    EXERCISE_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "EXERCISE_CREATE_RATE_LIMIT", 50
    )
    EXERCISE_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "EXERCISE_UPDATE_RATE_LIMIT", 50
    )

    # For API Gateway/Lambda throttling (per second)
    EXERCISE_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "EXERCISE_CREATE_RATE_LIMIT_PER_SEC", 15
    )
    EXERCISE_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "EXERCISE_UPDATE_RATE_LIMIT_PER_SEC", 15
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env(
        "EXERCISE_MAX_ITEMS", 20
    )  # Maximum exercises per workout

    # Exercise Category Options
    CATEGORY_OPTIONS = [
        "barbell",
        "dumbbell",
        "bodyweight",
        "machine",
        "cable",
        "custom",
    ]

    # Validation Constants
    MAX_NOTES_LENGTH = 500
    MIN_SETS = 1
    MAX_SETS = 20
    MIN_REPS = 1
    MAX_REPS = 100
    MIN_WEIGHT = 0
    MAX_WEIGHT = 2000  # Reasonable max weight in pounds
    MIN_RPE = 0
    MAX_RPE = 10
