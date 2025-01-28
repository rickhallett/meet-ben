import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base

"""
Database Models Module

This module defines the SQLAlchemy models for storing data in the database.
"""

class UserClients(Base):
    """SQLAlchemy model for storing user clients.

    Attributes:
        id: Auto-incremented integer primary key.
        user_id: String identifier for the user.
        created_at: Timestamp of when the client was created.
    """

    __tablename__ = "user_clients"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the user client",
    )
    user_id = Column(
        String,
        nullable=False,
        doc="Unique identifier for the user",
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        doc="Timestamp when the client was created",
    )

class ActiveClient(Base):
    """SQLAlchemy model for tracking active user clients.

    Attributes:
        user_id: String identifier for the user (primary key).
        client_id: Associated client ID from UserClients.
        created_at: Timestamp of when the active client was started.
    """

    __tablename__ = "active_clients"

    user_id = Column(
        String,
        primary_key=True,
        doc="Unique identifier for the user",
    )
    client_id = Column(
        Integer,
        ForeignKey("user_clients.id"),
        nullable=False,
        doc="Identifier for the user client",
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        doc="Timestamp when the active client was started",
    )
