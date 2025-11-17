"""
Pydantic models for Aurora's conversational API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class AuroraSessionStartRequest(BaseModel):
    """Request model to start a new Aurora session."""
    recommendations: List[str] = Field(..., description="The list of recommendations to provide context for the conversation.")

class AuroraSessionStartResponse(BaseModel):
    """Response model for a new Aurora session."""
    session_id: str = Field(..., description="The unique identifier for the conversation session.")
    initial_message: str = Field(..., description="Aurora's initial welcoming message.")

class AuroraChatRequest(BaseModel):
    """Request model for a chat turn with Aurora."""
    session_id: str = Field(..., description="The session ID for the ongoing conversation.")
    message: str = Field(..., description="The user's message.")

class AuroraChatResponse(BaseModel):
    """Response model for a chat turn with Aurora."""
    session_id: str = Field(..., description="The session ID for the ongoing conversation.")
    response: str = Field(..., description="Aurora's response to the user's message.")
