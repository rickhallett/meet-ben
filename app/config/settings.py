from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from config.llm_config import LLMConfig
from config.database_config import DatabaseConfig

load_dotenv()

"""
Main settings for the application using Pydantic Settings.
"""


class Settings(BaseSettings):
    """Main settings for the application."""

    app_name: str = "GenAI Project Template"
    llm: LLMConfig = LLMConfig()
    database: DatabaseConfig = DatabaseConfig()


@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()
