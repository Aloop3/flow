from src.config.base_config import BaseConfig


class WorkoutConfig(BaseConfig):
    """
    Workout resource configuration.

    Contains table names, index names, and other configuration specific to
    the Workout domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("WORKOUTS_TABLE", "Workouts")
    COMPLETED_EXERCISES_TABLE = BaseConfig.get_env(
        "COMPLETED_EXERCISES_TABLE", "CompletedExercises"
    )

    # DynamoDB Global Secondary Index Names
    ATHLETE_INDEX = "athlete-index"
    DAY_INDEX = "day-index"
    WORKOUT_INDEX = "workout-index"
    EXERCISE_INDEX = "exercise-index"

    # API Rate Limits (per minute)
    WORKOUT_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "WORKOUT_CREATE_RATE_LIMIT", 10
    )
    WORKOUT_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "WORKOUT_UPDATE_RATE_LIMIT", 20
    )

    # For API Gateway/Lambda throttling (per second)
    WORKOUT_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "WORKOUT_CREATE_RATE_LIMIT_PER_SEC", 2
    )
    WORKOUT_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "WORKOUT_UPDATE_RATE_LIMIT_PER_SEC", 5
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("WORKOUT_MAX_ITEMS", 25)

    # Workout Status Options
    STATUS_OPTIONS = ["completed", "partial", "skipped"]

    # Validation Constants
    MAX_NOTES_LENGTH = 1000
