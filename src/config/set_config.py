from src.config.base_config import BaseConfig


class SetConfig(BaseConfig):
    """
    Set resource configuration.

    Contains table names, index names, and other configuration specific to
    the Set domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("SETS_TABLE", "Sets")

    # DynamoDB Global Secondary Index Names
    EXERCISE_INDEX = "exercise-index"
    WORKOUT_INDEX = "workout-index"

    # API Rate Limits (per minute)
    SET_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env("SET_CREATE_RATE_LIMIT", 100)
    SET_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env("SET_UPDATE_RATE_LIMIT", 100)

    # For API Gateway/Lambda throttling (per second)
    SET_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "SET_CREATE_RATE_LIMIT_PER_SEC", 20
    )
    SET_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "SET_UPDATE_RATE_LIMIT_PER_SEC", 20
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("SET_MAX_ITEMS", 20)  # Maximum sets per exercise

    # Validation Constants
    MIN_SET_NUMBER = 1
    MAX_SET_NUMBER = 50
    MIN_REPS = 1
    MAX_REPS = 100
    MIN_WEIGHT = 0
    MAX_WEIGHT = 2000  # Reasonable max weight in pounds
    MIN_RPE = 0
    MAX_RPE = 10
    MAX_NOTES_LENGTH = 200
