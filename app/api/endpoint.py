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

@router.post("", dependencies=[], response_model=AgentResponse)
async def handle_ottomator_event(
    request: EventSchema,
    session: Session = Depends(db_session),
    authenticated: bool = Depends(otto_db.verify_token)
) -> Response:
    """Handles incoming event submissions.

    This endpoint receives events, stores them in the database,
    and queues them for asynchronous processing. It implements
    a non-blocking pattern to ensure API responsiveness.

    Args:
        request: The event data, validated against EventSchema
        session: Database session injected by FastAPI dependency
                 for access to the internal database
        authenticated: Boolean indicating if the request is authenticated

    Returns:
        Response: 202 Accepted response with task ID

    Note:
        The endpoint returns immediately after queueing the task.
        Use the task ID in the response to check processing status.
    """

    try:
        # Fetch conversation history from the DB
        conversation_history = await otto_db.fetch_conversation_history(request.session_id)

        print(conversation_history)
        
        # Convert conversation history to format expected by agent
        # This will be different depending on your framework (Pydantic AI, LangChain, etc.)
        messages = [
            {"role": msg["message"]["type"], "content": msg["message"]["content"]}
            for msg in conversation_history
        ]

        print(messages)

        # Register event in internal db
        event = register_event(session, request)

        # Queue processing task
        task_id = queue_task(event)

        # Store user's query from ottomator
        await otto_db.store_message(
            session_id=request.session_id,
            message_type="human",
            content=request.query,
            data={"request_id": request.request_id, "event_id": event.id, "task_id": task_id}
        )            

        """
        TODO:
        This is where you insert the custom logic to get the response from your agent.
        Your agent can also insert more records into the database to communicate
        actions/status as it is handling the user's question/request.
        Additionally:
            - Use the 'messages' array defined about for the chat history. This won't include the latest message from the user.
            - Use request.query for the user's prompt.
            - Use request.session_id if you need to insert more messages into the DB in the agent logic.
        """
        agent_response = "This is a sample agent response..."

        # Store agent's response, display in ottomator
        await otto_db.store_message(
            session_id=request.session_id,
            message_type="ai",
            content=agent_response,
            data={"request_id": request.request_id, "event_id": event.id, "task_id": task_id}
        )

        return AgentResponse(success=True)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # Store error message, display in ottomator
        error_message = {
                "session_id": request.session_id,
                "message_type": "ai", 
                "content": "I apologize, but I encountered an error processing your request.",
                "data": {"error": str(e), "request_id": request.request_id, "event_id": event.id, "task_id": task_id}
        }

        await otto_db.store_message(
            **error_message
        )

        return AgentResponse(success=False)
