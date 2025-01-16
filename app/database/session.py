from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from database.database_utils import DatabaseUtils

"""
Session Module

This module provides a session for database operations.
"""

engine = create_engine(DatabaseUtils.get_connection_string())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
