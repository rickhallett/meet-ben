import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base

"""
Database Models Module

This module defines the SQLAlchemy models for storing data in the database.
"""

class UserSession(Base):
    """SQLAlchemy model for storing user sessions.

    Attributes:
        id: Auto-incremented integer primary key.
        user_id: String identifier for the user.
        created_at: Timestamp of when the session was created.
    """

    __tablename__ = "user_sessions"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the user session",
    )
    user_id = Column(
        String,
        nullable=False,
        doc="Unique identifier for the user",
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        doc="Timestamp when the session was created",
    )

class ActiveSession(Base):
    """SQLAlchemy model for tracking active user sessions.

    Attributes:
        user_id: String identifier for the user (primary key).
        session_id: Associated session ID from UserSession.
        created_at: Timestamp of when the active session was started.
    """

    __tablename__ = "active_sessions"

    user_id = Column(
        String,
        primary_key=True,
        doc="Unique identifier for the user",
    )
    session_id = Column(
        Integer,
        ForeignKey("user_sessions.id"),
        nullable=False,
        doc="Identifier for the user session",
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        doc="Timestamp when the active session was started",
    )
