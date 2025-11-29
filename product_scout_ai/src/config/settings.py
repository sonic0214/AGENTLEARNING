"""
Settings module - Application configuration management
"""
import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SettingsError(Exception):
    """Exception raised for settings validation errors."""
    pass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Required settings
    GOOGLE_API_KEY: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))

    # Model settings
    MODEL_NAME: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "gemini-2.0-flash"))

    # Application settings
    APP_NAME: str = field(default_factory=lambda: os.getenv("APP_NAME", "product_scout_ai"))
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    MAX_RETRIES: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))

    # Session settings
    SESSION_TTL: int = field(default_factory=lambda: int(os.getenv("SESSION_TTL", "3600")))

    # API settings (optional)
    API_HOST: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    API_PORT: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))

    # External API keys (optional)
    SERPAPI_KEY: Optional[str] = field(default_factory=lambda: os.getenv("SERPAPI_KEY"))

    def __post_init__(self):
        """Validate settings after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate required settings."""
        # Validate LOG_LEVEL
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.LOG_LEVEL.upper() not in valid_log_levels:
            raise SettingsError(
                f"Invalid LOG_LEVEL: {self.LOG_LEVEL}. Must be one of {valid_log_levels}"
            )

        # Validate numeric values
        if self.MAX_RETRIES < 0:
            raise SettingsError(f"MAX_RETRIES must be non-negative, got {self.MAX_RETRIES}")

        if self.SESSION_TTL < 0:
            raise SettingsError(f"SESSION_TTL must be non-negative, got {self.SESSION_TTL}")

        if self.API_PORT < 1 or self.API_PORT > 65535:
            raise SettingsError(f"API_PORT must be between 1 and 65535, got {self.API_PORT}")

    def validate_api_key(self) -> bool:
        """
        Validate that the Google API key is set and has a valid format.

        Returns:
            bool: True if API key is valid, False otherwise
        """
        if not self.GOOGLE_API_KEY:
            return False

        # Basic format validation (Google API keys are typically 39 characters)
        if len(self.GOOGLE_API_KEY) < 10:
            return False

        return True

    def require_api_key(self) -> None:
        """
        Ensure API key is valid, raise error if not.

        Raises:
            SettingsError: If API key is not set or invalid
        """
        if not self.validate_api_key():
            raise SettingsError(
                "GOOGLE_API_KEY is required. Please set it in your environment or .env file."
            )

    def to_dict(self) -> dict:
        """Convert settings to dictionary (excluding sensitive data)."""
        return {
            "MODEL_NAME": self.MODEL_NAME,
            "APP_NAME": self.APP_NAME,
            "LOG_LEVEL": self.LOG_LEVEL,
            "MAX_RETRIES": self.MAX_RETRIES,
            "SESSION_TTL": self.SESSION_TTL,
            "API_HOST": self.API_HOST,
            "API_PORT": self.API_PORT,
            "HAS_API_KEY": bool(self.GOOGLE_API_KEY),
            "HAS_SERPAPI_KEY": bool(self.SERPAPI_KEY),
        }


# Global settings instance
settings = Settings()
