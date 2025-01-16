from pydantic import BaseModel

"""
Event Schema Module

This module defines the Pydantic models that FastAPI uses to validate incoming
HTTP requests. It specifies the expected structure and validation rules for
events entering the system through the API endpoints.
"""


class EventSchema(BaseModel):
    """
    Schema template for incoming event requests.
    """

    pass
