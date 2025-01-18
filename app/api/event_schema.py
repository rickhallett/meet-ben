from pydantic import BaseModel, Field

"""
Event Schema Module

This module defines the Pydantic models that FastAPI uses to validate incoming
HTTP requests from Ottomator. It specifies the expected structure and validation rules for
events entering the system through the API endpoints.
"""


class EventSchema(BaseModel):
    """Schema template for incoming requests from Ottomator.

    This schema is designed to handle requests with specific fields.
    The name "EventSchema" reflects how it is used internally within the pipeline as the 
    basis for the event cycle.
    """

    query: str = Field(..., description="The query or action requested by the user")
    user_id: str = Field(..., description="Unique identifier for the user making the request")
    request_id: str = Field(..., description="Unique identifier for the request")
    session_id: str = Field(..., description="Unique identifier for the session")
