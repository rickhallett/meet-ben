import os

from dotenv import load_dotenv

"""
Database Utility Module

This module provides utility functions for database operations.
It includes methods for retrieving connection strings and managing database sessions.
"""

load_dotenv()


class DatabaseUtils:
    @staticmethod
    def get_connection_string():
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "postgres")
        db_user = os.getenv("DATABASE_USER", "postgres")
        db_password = os.getenv("DATABASE_PASSWORD", "postgres")

        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
