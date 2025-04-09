from src.config.base_config import BaseConfig


class AppConfig(BaseConfig):
    """
    Application-wide configuration.

    Contains global settings, logging configuration, and other application-level
    configurations.
    """

    # Environment
    ENVIRONMENT = BaseConfig.get_env("ENVIRONMENT", "development")

    # Region
    AWS_REGION = BaseConfig.get_env("AWS_REGION", "us-east-1")

    # Logging
    LOG_LEVEL = BaseConfig.get_env("LOG_LEVEL", "INFO")

    # API Gateway
    API_STAGE = BaseConfig.get_env("API_STAGE", "dev")

    # CORS Settings
    CORS_ALLOW_ORIGIN = BaseConfig.get_env("CORS_ALLOW_ORIGIN", "*")
    CORS_ALLOW_HEADERS = BaseConfig.get_env(
        "CORS_ALLOW_HEADERS", "Content-Type,Authorization,X-Amz-Date,X-Api-Key"
    )
    CORS_ALLOW_METHODS = BaseConfig.get_env(
        "CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS"
    )

    # Global Rate Limiting
    RATE_LIMIT_ENABLED = BaseConfig.get_bool_env("RATE_LIMIT_ENABLED", True)
    GLOBAL_RATE_LIMIT_PER_MIN = BaseConfig.get_int_env("GLOBAL_RATE_LIMIT_PER_MIN", 300)
    GLOBAL_RATE_LIMIT_PER_SEC = BaseConfig.get_int_env("GLOBAL_RATE_LIMIT_PER_SEC", 50)

    # Burst Limits (for API Gateway)
    BURST_LIMIT_MULTIPLIER = BaseConfig.get_int_env(
        "BURST_LIMIT_MULTIPLIER", 2
    )  # Typically 2x the rate limit

    # DynamoDB Throttling
    DYNAMODB_MAX_RETRY_ATTEMPTS = BaseConfig.get_int_env(
        "DYNAMODB_MAX_RETRY_ATTEMPTS", 3
    )
    DYNAMODB_RETRY_BASE_DELAY_MS = BaseConfig.get_int_env(
        "DYNAMODB_RETRY_BASE_DELAY_MS", 100
    )
    # Cognito
    USER_POOL_ID = BaseConfig.get_env("USER_POOL_ID", "")
    USER_POOL_CLIENT_ID = BaseConfig.get_env("USER_POOL_CLIENT_ID", "")

    # Feature Flags
    FEATURE_ANALYTICS = BaseConfig.get_bool_env("FEATURE_ANALYTICS", True)
    FEATURE_NOTIFICATIONS = BaseConfig.get_bool_env("FEATURE_NOTIFICATIONS", True)

    # Cache settings
    CACHE_ENABLED = BaseConfig.get_bool_env("CACHE_ENABLED", True)
    CACHE_TTL = BaseConfig.get_int_env("CACHE_TTL", 300)  # 5 minutes

    @classmethod
    def is_production(cls) -> bool:
        """Check if the current environment is production"""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def is_development(cls) -> bool:
        """Check if the current environment is development"""
        return cls.ENVIRONMENT.lower() == "development"

    @classmethod
    def is_test(cls) -> bool:
        """Check if the current environment is test"""
        return cls.ENVIRONMENT.lower() == "test"
