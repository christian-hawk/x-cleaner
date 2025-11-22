"""
Configuration management for X-Cleaner application.

This module centralizes all configuration settings, loading from
environment variables with sensible defaults.
"""

import os
from pathlib import Path


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration.

    Centralizes all configuration settings with environment variable support.
    """

    # X API Configuration
    X_API_BEARER_TOKEN: str = os.getenv("X_API_BEARER_TOKEN", "")
    X_USER_ID: str = os.getenv("X_USER_ID", "")

    # Grok API Configuration
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")

    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/accounts.db")

    # Application Settings
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    CACHE_EXPIRY_DAYS: int = int(os.getenv("CACHE_EXPIRY_DAYS", "7"))

    # Web Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"

    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration values.

        Returns:
            True if all required values are set, False otherwise
        """
        required_fields = {
            "X_API_BEARER_TOKEN": cls.X_API_BEARER_TOKEN,
            "X_USER_ID": cls.X_USER_ID,
            "XAI_API_KEY": cls.XAI_API_KEY,
        }

        missing_fields = [
            field for field, value in required_fields.items() if not value
        ]

        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False

        return True

    @classmethod
    def get_database_path(cls) -> Path:
        """
        Get database path as Path object.

        Returns:
            Path object for database file
        """
        return Path(cls.DATABASE_PATH)

    @classmethod
    def ensure_data_directory(cls) -> None:
        """Ensure data directory exists."""
        data_dir = cls.get_database_path().parent
        data_dir.mkdir(parents=True, exist_ok=True)


# Create a singleton instance
config = Config()
