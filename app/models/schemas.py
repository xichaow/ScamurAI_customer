"""
Pydantic models for request/response validation.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ChatStartRequest(BaseModel):
    """Request model for starting a new chat session."""
    session_id: str


class ChatStartResponse(BaseModel):
    """Response model for chat session start."""
    success: bool
    message: str
    session_id: Optional[str] = None


class ChatResponseRequest(BaseModel):
    """Request model for chat responses."""
    session_id: str
    message: str


class ChatResponseResponse(BaseModel):
    """Response model for chat responses."""
    success: bool
    message: str
    completed: bool = False
    fraud_analysis: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Response model for session status."""
    success: bool
    session_id: Optional[str] = None
    current_question_index: Optional[int] = None
    completed: Optional[bool] = None
    answers_count: Optional[int] = None
    message: Optional[str] = None


class FraudQuestion(BaseModel):
    """Model for fraud detection questions."""
    id: str
    question: str
    validation: str


class ConversationSession(BaseModel):
    """Model for conversation session data."""
    session_id: str
    current_question_index: int = 0
    answers: Dict[str, str] = {}
    retry_count: int = 0
    completed: bool = False
    start_time: float