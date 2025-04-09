from src.config.base_config import BaseConfig


class BlockConfig(BaseConfig):
    """
    Block resource configuration.

    Contains table names, index names, and other configuration specific to
    the Block domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("BLOCKS_TABLE", "Blocks")

    # DynamoDB Global Secondary Index Names
    ATHLETE_INDEX = "athlete-index"
    COACH_INDEX = "coach-index"

    # API Rate Limits (per minute)
    BLOCK_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "BLOCK_CREATE_RATE_LIMIT", 10
    )
    BLOCK_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "BLOCK_UPDATE_RATE_LIMIT", 20
    )

    # For API Gateway/Lambda throttling (per second)
    BLOCK_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "BLOCK_CREATE_RATE_LIMIT_PER_SEC", 2
    )
    BLOCK_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "BLOCK_UPDATE_RATE_LIMIT_PER_SEC", 5
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("BLOCK_MAX_ITEMS", 50)

    # Block Status Options
    STATUS_OPTIONS = ["draft", "active", "completed"]

    # Validation Constants
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 1000
