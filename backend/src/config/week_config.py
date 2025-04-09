from src.config.base_config import BaseConfig


class WeekConfig(BaseConfig):
    """
    Week resource configuration.

    Contains table names, index names, and other configuration specific to
    the Week domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("WEEKS_TABLE", "Weeks")

    # DynamoDB Global Secondary Index Names
    BLOCK_INDEX = "block-index"

    # API Rate Limits (per minute)
    WEEK_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "WEEK_CREATE_RATE_LIMIT", 20
    )
    WEEK_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "WEEK_UPDATE_RATE_LIMIT", 20
    )

    # For API Gateway/Lambda throttling (per second)
    WEEK_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "WEEK_CREATE_RATE_LIMIT_PER_SEC", 5
    )
    WEEK_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "WEEK_UPDATE_RATE_LIMIT_PER_SEC", 5
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("WEEK_MAX_ITEMS", 52)  # Maximum weeks in a year

    # Validation Constants
    MIN_WEEK_NUMBER = 1
    MAX_WEEK_NUMBER = 52
    MAX_NOTES_LENGTH = 500
