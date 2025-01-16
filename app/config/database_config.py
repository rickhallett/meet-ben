import os
from datetime import timedelta

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

"""
Configuration for the VectorStore.
"""


class VectorStoreConfig(BaseSettings):
    """Settings for the VectorStore."""

    table_name: str = "embeddings"
    embedding_dimensions: int = 1536
    time_partition_interval: timedelta = timedelta(days=7)


class DatabaseConfig(BaseSettings):
    """Settings for the database."""

    host: str = os.getenv("DATABASE_HOST", "launchpad_database")
    port: str = os.getenv("DATABASE_PORT", "5432")
    name: str = os.getenv("DATABASE_NAME", "launchpad")
    pg_user: str = os.getenv("DATABASE_USER", "postgres")
    password: str = os.getenv("DATABASE_PASSWORD")
    local: bool = False

    @property
    def service_url(self) -> str:
        """Generate the service URL based on the environment."""
        if self.local:
            return f"postgres://{self.pg_user}:{self.password}@localhost:{self.port}/{self.name}"
        return f"postgres://{self.pg_user}:{self.password}@{self.host}:{self.port}/{self.name}"

    vector_store: VectorStoreConfig = VectorStoreConfig()
