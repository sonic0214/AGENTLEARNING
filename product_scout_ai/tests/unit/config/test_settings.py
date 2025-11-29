"""
Tests for config/settings.py
"""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Test cases for Settings class."""

    def test_settings_loads_from_env(self):
        """Test that settings loads values from environment variables."""
        with patch.dict(os.environ, {
            "GOOGLE_API_KEY": "test_api_key_12345",
            "MODEL_NAME": "gemini-2.0-pro",
            "APP_NAME": "test_app",
            "LOG_LEVEL": "DEBUG",
        }):
            # Import fresh to pick up new env vars
            from src.config.settings import Settings
            settings = Settings()

            assert settings.GOOGLE_API_KEY == "test_api_key_12345"
            assert settings.MODEL_NAME == "gemini-2.0-pro"
            assert settings.APP_NAME == "test_app"
            assert settings.LOG_LEVEL == "DEBUG"

    def test_settings_has_defaults(self):
        """Test that settings have reasonable default values."""
        with patch.dict(os.environ, {}, clear=True):
            from src.config.settings import Settings
            settings = Settings()

            assert settings.MODEL_NAME == "gemini-2.0-flash"
            assert settings.APP_NAME == "product_scout_ai"
            assert settings.LOG_LEVEL == "INFO"
            assert settings.MAX_RETRIES == 3
            assert settings.SESSION_TTL == 3600
            assert settings.API_HOST == "0.0.0.0"
            assert settings.API_PORT == 8000

    def test_settings_validates_api_key_present(self):
        """Test API key validation when key is present."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "valid_key_12345678901234567890"}):
            from src.config.settings import Settings
            settings = Settings()

            assert settings.validate_api_key() is True

    def test_settings_validates_api_key_missing(self):
        """Test API key validation when key is missing."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=False):
            from src.config.settings import Settings
            settings = Settings()
            # Manually clear for test
            settings.GOOGLE_API_KEY = ""

            assert settings.validate_api_key() is False

    def test_settings_validates_api_key_too_short(self):
        """Test API key validation when key is too short."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "short"}):
            from src.config.settings import Settings
            settings = Settings()
            settings.GOOGLE_API_KEY = "short"

            assert settings.validate_api_key() is False

    def test_settings_require_api_key_raises(self):
        """Test that require_api_key raises error when key is invalid."""
        from src.config.settings import Settings, SettingsError
        settings = Settings()
        settings.GOOGLE_API_KEY = ""

        with pytest.raises(SettingsError) as exc_info:
            settings.require_api_key()

        assert "GOOGLE_API_KEY is required" in str(exc_info.value)

    def test_settings_invalid_log_level(self):
        """Test that invalid log level raises error."""
        from src.config.settings import Settings, SettingsError

        with pytest.raises(SettingsError) as exc_info:
            Settings(LOG_LEVEL="INVALID")

        assert "Invalid LOG_LEVEL" in str(exc_info.value)

    def test_settings_invalid_max_retries(self):
        """Test that negative MAX_RETRIES raises error."""
        from src.config.settings import Settings, SettingsError

        with pytest.raises(SettingsError) as exc_info:
            Settings(MAX_RETRIES=-1)

        assert "MAX_RETRIES must be non-negative" in str(exc_info.value)

    def test_settings_invalid_api_port(self):
        """Test that invalid API_PORT raises error."""
        from src.config.settings import Settings, SettingsError

        with pytest.raises(SettingsError) as exc_info:
            Settings(API_PORT=99999)

        assert "API_PORT must be between" in str(exc_info.value)

    def test_settings_to_dict_excludes_sensitive(self):
        """Test that to_dict excludes sensitive data."""
        from src.config.settings import Settings
        settings = Settings()
        settings.GOOGLE_API_KEY = "secret_key_12345"

        result = settings.to_dict()

        assert "GOOGLE_API_KEY" not in result
        assert "secret_key" not in str(result)
        assert result["HAS_API_KEY"] is True
        assert "MODEL_NAME" in result
        assert "APP_NAME" in result
