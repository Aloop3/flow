import unittest
import os
from unittest.mock import patch

from src.config.base_config import BaseConfig
from src.config.user_config import UserConfig
from src.config.block_config import BlockConfig
from src.config.app_config import AppConfig


class TestBaseConfig(unittest.TestCase):
    """Test suite for the BaseConfig class"""

    def test_get_env(self):
        """Test get_env method"""
        # Test with a non-existent env var
        self.assertIsNone(BaseConfig.get_env("NON_EXISTENT_VAR"))

        # Test with a non-existent env var and default value
        self.assertEqual(BaseConfig.get_env("NON_EXISTENT_VAR", "default"), "default")

        # Test with an existing env var
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            self.assertEqual(BaseConfig.get_env("TEST_VAR"), "test_value")
            # Default should be ignored if env var exists
            self.assertEqual(BaseConfig.get_env("TEST_VAR", "default"), "test_value")

    def test_get_bool_env(self):
        """Test get_bool_env method"""
        # Test with non-existent env var
        self.assertFalse(BaseConfig.get_bool_env("NON_EXISTENT_VAR"))
        self.assertTrue(BaseConfig.get_bool_env("NON_EXISTENT_VAR", True))

        # Test with truthy values
        for value in ["true", "True", "TRUE", "yes", "YES", "y", "Y", "1"]:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                self.assertTrue(BaseConfig.get_bool_env("BOOL_VAR"))
                self.assertTrue(BaseConfig.get_bool_env("BOOL_VAR", False))

        # Test with falsy values
        for value in ["false", "False", "FALSE", "no", "NO", "n", "N", "0", "random"]:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                self.assertFalse(BaseConfig.get_bool_env("BOOL_VAR"))
                self.assertFalse(BaseConfig.get_bool_env("BOOL_VAR", True))

    def test_get_int_env(self):
        """Test get_int_env method"""
        # Test with non-existent env var
        self.assertEqual(BaseConfig.get_int_env("NON_EXISTENT_VAR"), 0)
        self.assertEqual(BaseConfig.get_int_env("NON_EXISTENT_VAR", 42), 42)

        # Test with valid int
        with patch.dict(os.environ, {"INT_VAR": "123"}):
            self.assertEqual(BaseConfig.get_int_env("INT_VAR"), 123)
            self.assertEqual(BaseConfig.get_int_env("INT_VAR", 42), 123)

        # Test with invalid int
        with patch.dict(os.environ, {"INT_VAR": "not_an_int"}):
            self.assertEqual(BaseConfig.get_int_env("INT_VAR"), 0)
            self.assertEqual(BaseConfig.get_int_env("INT_VAR", 42), 42)


class TestResourceConfig(unittest.TestCase):
    """Test suite for resource-specific configuration classes"""

    def test_user_config(self):
        """Test UserConfig attributes"""
        # Save original value
        original_table_name = UserConfig.TABLE_NAME

        try:
            # Reset to expected default for this test
            UserConfig.TABLE_NAME = "Users-Test"

            # Test default values
            self.assertEqual(UserConfig.TABLE_NAME, "Users-Test")
            self.assertEqual(UserConfig.EMAIL_INDEX, "email-index")

            # Test with environment variables
            with patch.dict(
                os.environ, {"USERS_TABLE": "CustomUsers", "USER_MAX_ITEMS": "75"}
            ):
                # Reload the module to pick up new env vars
                import importlib
                import src.config.user_config

                importlib.reload(src.config.user_config)
                from src.config.user_config import UserConfig as ReloadedUserConfig

                self.assertEqual(ReloadedUserConfig.TABLE_NAME, "CustomUsers")
                self.assertEqual(ReloadedUserConfig.MAX_ITEMS, 75)
        finally:
            # Restore original
            UserConfig.TABLE_NAME = original_table_name

            # Reload the module to reset other changes
            import importlib
            import src.config.user_config

            importlib.reload(src.config.user_config)

    def test_block_config(self):
        """Test BlockConfig attributes"""
        # Save original value
        original_table_name = BlockConfig.TABLE_NAME

        try:
            # Reset to expected default for this test
            BlockConfig.TABLE_NAME = "Blocks-Test"

            # Test default values
            self.assertEqual(BlockConfig.TABLE_NAME, "Blocks-Test")
            self.assertEqual(BlockConfig.ATHLETE_INDEX, "athlete-index")
            self.assertEqual(BlockConfig.COACH_INDEX, "coach-index")
            self.assertEqual(BlockConfig.MAX_ITEMS, 50)
            self.assertEqual(
                BlockConfig.STATUS_OPTIONS, ["draft", "active", "completed"]
            )

            # Test with environment variables
            with patch.dict(
                os.environ, {"BLOCKS_TABLE": "CustomBlocks", "BLOCK_MAX_ITEMS": "25"}
            ):
                # Reload the module to pick up new env vars
                import importlib
                import src.config.block_config

                importlib.reload(src.config.block_config)
                from src.config.block_config import BlockConfig as ReloadedBlockConfig

                self.assertEqual(ReloadedBlockConfig.TABLE_NAME, "CustomBlocks")
                self.assertEqual(ReloadedBlockConfig.MAX_ITEMS, 25)
        finally:
            # Restore original
            BlockConfig.TABLE_NAME = original_table_name

            # Reload the module to reset other changes
            import importlib
            import src.config.block_config

            importlib.reload(src.config.block_config)

    def test_app_config(self):
        """Test AppConfig attributes and methods"""
        # Test default values
        self.assertEqual(AppConfig.ENVIRONMENT, "development")
        self.assertEqual(AppConfig.AWS_REGION, "us-east-1")
        self.assertEqual(AppConfig.LOG_LEVEL, "INFO")
        self.assertTrue(AppConfig.CACHE_ENABLED)
        self.assertEqual(AppConfig.CACHE_TTL, 300)

        # Test environment check methods
        self.assertTrue(AppConfig.is_development())
        self.assertFalse(AppConfig.is_production())
        self.assertFalse(AppConfig.is_test())

        # Test with different environment
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            # Reload the module to pick up new env vars
            import importlib
            import src.config.app_config

            importlib.reload(src.config.app_config)
            from src.config.app_config import AppConfig as ReloadedAppConfig

            self.assertEqual(ReloadedAppConfig.ENVIRONMENT, "production")
            self.assertTrue(ReloadedAppConfig.is_production())
            self.assertFalse(ReloadedAppConfig.is_development())

    def test_get_int_env(self):
        """Test get_int_env method"""
        # Test with non-existent env var
        self.assertEqual(BaseConfig.get_int_env("NON_EXISTENT_VAR"), 0)
        self.assertEqual(BaseConfig.get_int_env("NON_EXISTENT_VAR", 42), 42)

        # Test with valid int
        with patch.dict(os.environ, {"INT_VAR": "123"}):
            self.assertEqual(BaseConfig.get_int_env("INT_VAR"), 123)
            self.assertEqual(BaseConfig.get_int_env("INT_VAR", 42), 123)

        # Test with invalid int
        with patch.dict(os.environ, {"INT_VAR": "not_an_int"}):
            self.assertEqual(BaseConfig.get_int_env("INT_VAR"), 0)
            self.assertEqual(BaseConfig.get_int_env("INT_VAR", 42), 42)

    def test_get_config(self):
        """Test get_config method"""
        # Test that get_config returns an instance of the configuration class
        config = BaseConfig.get_config()
        self.assertIsInstance(config, BaseConfig)

        # Test with a derived class
        class TestConfig(BaseConfig):
            TEST_VALUE = "test"

        derived_config = TestConfig.get_config()
        self.assertIsInstance(derived_config, TestConfig)
        self.assertEqual(derived_config.TEST_VALUE, "test")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
