from pydantic import BaseModel
from config.celery_config import celery_app
from database.event import Event
from database.repository import GenericRepository
from database.ottomator_db import OttomatorDB
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
from api.dependencies import db_session
from api.event_schema import EventSchema
from rich import print

"""
Event Submission Endpoint Module

This module defines the primary FastAPI endpoint for event ingestion.
It implements the initial handling of incoming events by:
1. Validating the incoming event data
2. Persisting the event to the database
3. Queuing an asynchronous processing task
4. Returning an acceptance response

The endpoint follows the "accept-and-delegate" pattern where:
- Events are immediately accepted if valid
- Processing is handled asynchronously via Celery
- A 202 Accepted response indicates successful queueing

This pattern ensures high availability and responsiveness of the API
while allowing for potentially long-running processing operations.
"""

class AgentResponse(BaseModel):
    success: bool

router = APIRouter()

otto_db = OttomatorDB()

def register_event(session: Session, request: EventSchema) -> Event:
    repository = GenericRepository(
        session=session,
        model=Event,
    )
    event = Event(data=request.model_dump(mode="json"))
    repository.create(obj=event)
    return event

def queue_task(event: Event) -> str:
    task_id = celery_app.send_task(
        "process_incoming_event",
        args=[str(event.id)],
    )
    return task_id

@router.get("/")
async def test_endpoint():
    return AgentResponse(success=True)

@router.post("/")
async def handle_ottomator_event(
    request: EventSchema,
    session: Session = Depends(db_session),
    authenticated: bool = Depends(otto_db.verify_token)
) -> Response:
    """Handles incoming event submissions with granular error handling."""
    
    conversation_history = None
    messages = []
    event = None

    try:
        # Fetch conversation history
        try:
            conversation_history = await otto_db.fetch_conversation_history(request.session_id)
            print(f"Conversation history fetched: {conversation_history}")
        except Exception as e:
            print(f"Error fetching conversation history: {str(e)}")
            raise Exception(f"Failed to fetch conversation history: {str(e)}")

        # Convert conversation history
        try:
            messages = [
                {"role": msg["message"]["type"], "content": msg["message"]["content"]}
                for msg in conversation_history
            ]
            print(f"Messages converted: {messages}")
        except Exception as e:
            print(f"Error converting conversation history: {str(e)}")
            raise Exception(f"Failed to convert conversation history: {str(e)}")

        # Register event
        try:
            event = register_event(session, request)
            print(f"Event registered: {event}")
        except Exception as e:
            print(f"Error registering event: {str(e)}")
            raise Exception(f"Failed to register event: {str(e)}")

        # Queue processing task
        try:
            task = queue_task(event)
            print(f"Task queued: {task}")
        except Exception as e:
            print(f"Error queuing task: {str(e)}")
            raise Exception(f"Failed to queue task: {str(e)}")
        
        print(task)
        print(type(task))
        # Store user's query
        try:
            await otto_db.store_message(
                session_id=str(request.session_id),
                message_type="human",
                content=str(request.query),
                data={
                    "request_id": str(request.request_id),
                    "event_id": str(event.id),
                    "task_id": str(task)
                }
            )
        except Exception as e:
            print(f"Error storing user message: {str(e)}")
            raise Exception(f"Failed to store user message: {str(e)}")

        # Get agent response (placeholder)
        try:
            agent_response = "Processing your request..."
            print(f"Agent response generated: {agent_response}")
        except Exception as e:
            print(f"Error generating agent response: {str(e)}")
            raise Exception(f"Failed to generate agent response: {str(e)}")

        # Store agent's response
        try:
            await otto_db.store_message(
                session_id=str(request.session_id),
                message_type="ai",
                content=agent_response,
                data={
                    "request_id": str(request.request_id),
                    "event_id": str(event.id),
                    "task_id": str(task.id)
                }
            )
        except Exception as e:
            print(f"Error storing agent response: {str(e)}")
            raise Exception(f"Failed to store agent response: {str(e)}")

        return AgentResponse(success=True)

    except Exception as e:
        print(f"Global error handling: {str(e)}")
        # Store error message
        try:
            await otto_db.store_message(
                session_id=str(request.session_id),
                message_type="ai",
                content="I apologize, but I encountered an error processing your request.",
                data={
                    "error": str(e),
                    "request_id": str(request.request_id),
                    "event_id": str(event.id) if event else None,
                    "task_id": str(task.id)
                }
            )
        except Exception as store_error:
            print(f"Error storing error message: {str(store_error)}")
            # If we can't even store the error message, log it but don't raise
            # as we're already in the global error handler

        return AgentResponse(success=False)
