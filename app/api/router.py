from fastapi import APIRouter

from api import endpoint
from api.endpoint import router as endpoint_router

"""
API Router Module

This module sets up the API router and includes all defined endpoints.
It uses FastAPI's APIRouter to group related endpoints and provide a prefix.
"""

endpoint_router.include_router(endpoint.router, prefix="/api/ben", tags=["events"])
