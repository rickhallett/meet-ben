from contextlib import contextmanager

from api.dependencies import db_session
from api.event_schema import EventSchema
from config.celery_config import celery_app
from database.event import Event
from database.repository import GenericRepository
from pipelines.registry import PipelineRegistry

"""
Pipeline Task Processing Module

This module handles asynchronous processing of pipeline events using Celery.
It manages the lifecycle of event processing from database retrieval through
pipeline execution and result storage.
"""


@celery_app.task(name="process_incoming_event")
def process_incoming_event(event_id: str):
    """Processes an incoming event through its designated pipeline.

    This Celery task handles the asynchronous processing of events by:
    1. Retrieving the event from the database
    2. Determining the appropriate pipeline
    3. Executing the pipeline
    4. Storing the results

    Args:
        event_id: Unique identifier of the event to process
    """
    with contextmanager(db_session)() as session:
        # Initialize repository for database operations
        repository = GenericRepository(session=session, model=Event)

        # Retrieve event from database
        db_event = repository.get(id=event_id)
        if db_event is None:
            raise ValueError(f"Event with id {event_id} not found")

        # Convert to schema and determine pipeline
        event = EventSchema(**db_event.data)
        pipeline = PipelineRegistry.get_pipeline(event)

        # Execute pipeline and store results
        task_context = pipeline.run(event).model_dump(mode="json")
        db_event.task_context = task_context

        # Update event with processing results
        repository.update(obj=db_event)
