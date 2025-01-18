from fastapi import APIRouter

from api.endpoint import router as endpoint_router

"""
API Router Module

This module sets up the API router and includes all defined endpoints.
It uses FastAPI's APIRouter to group related endpoints and provide a prefix.
"""

router = APIRouter()

router.include_router(endpoint_router, prefix="/api/ben")
