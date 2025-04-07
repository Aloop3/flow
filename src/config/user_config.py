from src.config.base_config import BaseConfig


class UserConfig(BaseConfig):
    """
    User resource configuration.

    Contains table names, index names, and other configuration specific to
    the User domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("USERS_TABLE", "Users")

    # DynamoDB Global Secondary Index Names
    EMAIL_INDEX = "email-index"

    # API Rate Limits (per minute)
    USER_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "USER_CREATE_RATE_LIMIT", 10
    )
    USER_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "USER_UPDATE_RATE_LIMIT", 20
    )

    # For API Gateway/Lambda throttling (per second)
    USER_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "USER_CREATE_RATE_LIMIT_PER_SEC", 2
    )
    USER_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "USER_UPDATE_RATE_LIMIT_PER_SEC", 5
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("USER_MAX_ITEMS", 100)

    # Validation Constants
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    ROLE_OPTIONS = ["athlete", "coach"]
