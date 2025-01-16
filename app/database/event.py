import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base

"""
Event Database Model Module

This module defines the SQLAlchemy model for storing events in the database.
It provides two main storage components:
1. Raw event data (data column): Stores the original incoming event
2. Processing results (task_context column): Stores the pipeline processing results

This model is used with Alembic to generate the initial database migration.
"""


class Event(Base):
    """SQLAlchemy model for storing events and their processing results.

    This model serves as the primary storage for both incoming events and
    their processing results. It uses JSONB columns for flexible schema
    storage of both raw data and processing context.

    Attributes:
        id: UUID primary key, auto-generated
        data: Raw event data as received by the API
        task_context: Results and metadata from pipeline processing
        created_at: Timestamp of event creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid1,
        doc="Unique identifier for the event",
    )

    data = Column(JSON, doc="Raw event data as received from the API endpoint")
    task_context = Column(JSON, doc="Processing results and metadata from the pipeline")

    created_at = Column(
        DateTime, default=datetime.now, doc="Timestamp when the event was created"
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        doc="Timestamp when the event was last updated",
    )
