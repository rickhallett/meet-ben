# API Layer Documentation

The API layer in GenAI Launchpad serves as the primary entry point for all event-driven operations. Built with FastAPI, this layer transforms incoming HTTP requests into events that flow through the system's event-driven architecture.

## Architectural Overview

The API layer implements an "accept-and-delegate" pattern, where requests are quickly validated, persisted, and delegated to background workers. This design ensures high availability and responsiveness, as the API immediately acknowledges valid requests without waiting for complete processing.

When a request arrives, it flows through the following stages:

1. FastAPI validates the incoming payload against defined schemas
2. The validated event is persisted to PostgreSQL
3. A background task is queued via Celery
4. The API returns a 202 Accepted response with a task ID

## Core Components

### Dependencies (dependencies.py)

The dependencies module provides essential services to API endpoints through FastAPI's dependency injection system. The primary dependency is the database session manager, which ensures proper handling of database connections:

```python
def db_session() -> Generator:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as ex:
        session.rollback()
        raise ex
    finally:
        session.close()
```

This pattern guarantees that database sessions are properly managed regardless of request success or failure.

### Event Schema (event_schema.py)

Event schemas define the contract between API clients and the system. Using Pydantic models, we enforce strict validation of incoming requests before they enter the processing pipeline. The schema system is extensible, allowing you to define custom validation rules for different event types.

#### Pydantic Model Integration

Pydantic models serve as the backbone of our data validation and serialization. These models provide:

- Runtime type checking and validation
- JSON schema generation for OpenAPI documentation
- Automatic serialization/deserialization of complex data types

Example of a typical event schema:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class EventSchema(BaseModel):
    event_type: str = Field(..., description="Type of event being processed")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Optional metadata")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_type": "document_processing",
                "payload": {"document_id": "123", "action": "analyze"},
                "metadata": {"priority": "high"}
            }]
        }
    }
```

For more information about Pydantic models and their capabilities, refer to:
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI's Pydantic Tutorial](https://fastapi.tiangolo.com/tutorial/body/#using-pydantic-models)

### Endpoints (endpoint.py)

The endpoint module implements the core event ingestion logic. It follows RESTful principles and implements the accept-and-delegate pattern:

```python
@router.post("/")
def handle_event(
    data: EventSchema,
    session: Session = Depends(db_session),
) -> Response:
    # Store event
    event = Event(data=data.model_dump(mode="json"))
    repository.create(obj=event)

    # Queue for processing
    task_id = celery_app.send_task(
        "process_incoming_event",
        args=[str(event.id)],
    )

    return Response(
        status_code=HTTPStatus.ACCEPTED
    )
```

### Router Configuration (router.py)

The router module organizes endpoints into logical groups and applies common configurations. This modular approach allows for easy addition of new endpoints while maintaining consistent routing patterns.

## Integration Points

The API layer integrates with several other system components:

### Database Integration
Through the repository pattern, the API layer persists events while maintaining separation of concerns. The database operations are abstracted behind repository interfaces, making the system flexible to database changes.

### Task Queue Integration
The API layer queues tasks for background processing using Celery. This integration point is crucial for the system's event-driven nature, allowing for asynchronous processing of potentially long-running operations.

### Validation Integration
FastAPI's validation system works in concert with Pydantic models to ensure data integrity before events enter the processing pipeline.

## Extending the API

To add new endpoints, follow these steps:

1. Define new schemas in event_schema.py
2. Create endpoint handlers in endpoint.py
3. Update router configuration if needed
4. Implement corresponding pipeline processors

The modular design makes it straightforward to extend the API while maintaining consistency and reliability.
