from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client
from dotenv import load_dotenv
import os

from dotenv import load_dotenv

load_dotenv()

"""
Database Utility Module

This module provides utility functions for database operations.
It includes methods for retrieving connection strings and managing database sessions.
"""

load_dotenv()

class OttomatorDB:
    _client: Optional[Client] = None  # Class-level attribute to store the client

    def __init__(self):
        if OttomatorDB._client is None:
            OttomatorDB._client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_SERVICE_KEY")
            )
        self.client = OttomatorDB._client
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> bool:
        """Verify the bearer token against environment variable."""
        expected_token = os.getenv("API_BEARER_TOKEN")
        if not expected_token:
            raise HTTPException(
                status_code=500,
                detail="API_BEARER_TOKEN environment variable not set"
            )
        if credentials.credentials != expected_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        return True
    
    async def fetch_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch the most recent conversation history for a session."""
        try:
            response = self.client.table("messages") \
                .select("*") \
                .eq("session_id", session_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            # Convert to list and reverse to get chronological order
            messages = response.data[::-1]
            return messages
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch conversation history: {str(e)}")
        
    async def store_message(self, session_id: str, message_type: str, content: str, data: Optional[Dict] = None):
        """Store a message in the Supabase messages table."""
        message_obj = {
            "type": message_type,
            "content": content
        }
        if data:
            message_obj["data"] = data

        try:
            self.client.table("messages").insert({
                "session_id": session_id,
                "message": message_obj
            }).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store message: {str(e)}")
