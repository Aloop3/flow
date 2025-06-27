from src.config.base_config import BaseConfig


class NotificationConfig(BaseConfig):
    """
    Notification resource configuration.

    Contains table names, index names, and other configuration specific to
    the Notification domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("NOTIFICATIONS_TABLE", "Notifications")

    # DynamoDB Global Secondary Index Names
    COACH_INDEX = "coach-index"

    # API Rate Limits (per minute)
    NOTIFICATION_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "NOTIFICATION_CREATE_RATE_LIMIT", 30
    )
    NOTIFICATION_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "NOTIFICATION_UPDATE_RATE_LIMIT", 50
    )

    # For API Gateway/Lambda throttling (per second)
    NOTIFICATION_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "NOTIFICATION_CREATE_RATE_LIMIT_PER_SEC", 5
    )
    NOTIFICATION_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "NOTIFICATION_UPDATE_RATE_LIMIT_PER_SEC", 10
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("NOTIFICATION_MAX_ITEMS", 50)

    # Notification Type Options
    TYPE_OPTIONS = ["workout_completion"]

    # Validation Constants
    MAX_DAY_INFO_LENGTH = 50
    MAX_ATHLETE_NAME_LENGTH = 100
