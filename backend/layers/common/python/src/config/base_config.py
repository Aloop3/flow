import os
from typing import Dict, Any, TypeVar, Type

# Type for configuration class instance
T = TypeVar("T", bound="BaseConfig")


class BaseConfig:
    """
    Base configuration class for all resources.

    Provides common functionality for loading environment variables
    and configuration values for different environments.
    """

    # Default configuration values - to be overridden by subclasses
    DEFAULT_CONFIG: Dict[str, Any] = {}

    @classmethod
    def get_env(cls, key: str, default: Any = None) -> Any:
        """
        Get an environment variable with a default fallback.

        :param key: The environment variable key
        :param default: Default value if environment variable is not set
        :return: The environment variable value or default
        """
        return os.environ.get(key, default)

    @classmethod
    def get_bool_env(cls, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable.

        :param key: The environment variable key
        :param default: Default value if environment variable is not set
        :return: True if the value is 'true', 'yes', '1', 'y' (case insensitive)
        """
        value = cls.get_env(key)
        if value is None:
            return default
        return value.lower() in ("true", "yes", "1", "y")

    @classmethod
    def get_int_env(cls, key: str, default: int = 0) -> int:
        """
        Get an integer environment variable.

        :param key: The environment variable key
        :param default: Default value if environment variable is not set
        :return: The environment variable value as integer
        """
        try:
            return int(cls.get_env(key, default))
        except ValueError:
            return default

    @classmethod
    def get_config(cls: Type[T]) -> T:
        """
        Get an instance of the configuration class.

        :return: An instance of the configuration class
        """
        return cls()
