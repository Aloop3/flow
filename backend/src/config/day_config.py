from src.config.base_config import BaseConfig


class DayConfig(BaseConfig):
    """
    Day resource configuration.

    Contains table names, index names, and other configuration specific to
    the Day domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("DAYS_TABLE", "Days")

    # DynamoDB Global Secondary Index Names
    WEEK_INDEX = "week-index"

    # API Rate Limits (per minute)
    DAY_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env("DAY_CREATE_RATE_LIMIT", 30)
    DAY_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env("DAY_UPDATE_RATE_LIMIT", 30)

    # For API Gateway/Lambda throttling (per second)
    DAY_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "DAY_CREATE_RATE_LIMIT_PER_SEC", 10
    )
    DAY_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "DAY_UPDATE_RATE_LIMIT_PER_SEC", 10
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("DAY_MAX_ITEMS", 7)  # Maximum days in a week

    # Day Focus Options
    FOCUS_OPTIONS = ["squat", "bench", "deadlift", "cardio", "rest"]

    # Validation Constants
    MIN_DAY_NUMBER = 1
    MAX_DAY_NUMBER = 7
    MAX_NOTES_LENGTH = 500
