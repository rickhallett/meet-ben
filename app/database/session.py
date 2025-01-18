from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from database.internal_db import InternalDB

"""
Session Module

This module provides a session for database operations.
"""

engine = create_engine(InternalDB.get_connection_string())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
