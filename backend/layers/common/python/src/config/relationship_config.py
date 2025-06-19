from src.config.base_config import BaseConfig


class RelationshipConfig(BaseConfig):
    """
    Relationship resource configuration.

    Contains table names, index names, and other configuration specific to
    the Relationship domain.
    """

    # DynamoDB Table Name
    TABLE_NAME = BaseConfig.get_env("RELATIONSHIPS_TABLE", "Relationships")

    # DynamoDB Global Secondary Index Names
    COACH_INDEX = "coach-index"
    ATHLETE_INDEX = "athlete-index"
    COACH_ATHLETE_INDEX = "coach-athlete-index"

    # TTL Configuration
    INVITATION_CODE_TTL_HOURS = BaseConfig.get_int_env("INVITATION_CODE_TTL_HOURS", 24)
    ENDED_RELATIONSHIP_TTL_DAYS = BaseConfig.get_int_env(
        "ENDED_RELATIONSHIP_TTL_DAYS", 60
    )

    # API Rate Limits (per minute)
    RELATIONSHIP_CREATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "RELATIONSHIP_CREATE_RATE_LIMIT", 10
    )
    RELATIONSHIP_UPDATE_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env(
        "RELATIONSHIP_UPDATE_RATE_LIMIT", 10
    )

    # For API Gateway/Lambda throttling (per second)
    RELATIONSHIP_CREATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "RELATIONSHIP_CREATE_RATE_LIMIT_PER_SEC", 2
    )
    RELATIONSHIP_UPDATE_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env(
        "RELATIONSHIP_UPDATE_RATE_LIMIT_PER_SEC", 2
    )

    # Query Limits (maximum items per request)
    MAX_ITEMS = BaseConfig.get_int_env("RELATIONSHIP_MAX_ITEMS", 100)
    MAX_ATHLETES_PER_COACH = BaseConfig.get_int_env("MAX_ATHLETES_PER_COACH", 50)
    MAX_COACHES_PER_ATHLETE = BaseConfig.get_int_env("MAX_COACHES_PER_ATHLETE", 3)

    # Relationship Status Options
    STATUS_OPTIONS = ["pending", "active", "ended"]
