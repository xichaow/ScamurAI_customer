"""
FastAPI routes for chat functionality.
"""
from fastapi import APIRouter, HTTPException, Depends
from ..models.schemas import (
    ChatStartRequest, ChatStartResponse, 
    ChatResponseRequest, ChatResponseResponse,
    SessionStatusResponse
)
from ..services.conversation_engine import ConversationEngine
from ..utils.dependencies import get_conversation_engine

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/start", response_model=ChatStartResponse)
async def start_conversation(
    request: ChatStartRequest,
    engine: ConversationEngine = Depends(get_conversation_engine)
) -> ChatStartResponse:
    """
    Start a new conversation session.
    
    Args:
        request (ChatStartRequest): Request containing session ID.
        engine (ConversationEngine): Conversation engine dependency.
        
    Returns:
        ChatStartResponse: Response with first question.
        
    Raises:
        HTTPException: If session ID is invalid.
    """
    try:
        result = engine.start_session(request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/respond", response_model=ChatResponseResponse)
async def process_response(
    request: ChatResponseRequest,
    engine: ConversationEngine = Depends(get_conversation_engine)
) -> ChatResponseResponse:
    """
    Process user response and return next question or fraud analysis.
    
    Args:
        request (ChatResponseRequest): Request containing session ID and message.
        engine (ConversationEngine): Conversation engine dependency.
        
    Returns:
        ChatResponseResponse: Next question or fraud analysis result.
        
    Raises:
        HTTPException: If processing fails.
    """
    try:
        result = await engine.process_response(request.session_id, request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    engine: ConversationEngine = Depends(get_conversation_engine)
) -> SessionStatusResponse:
    """
    Get current session status (for debugging).
    
    Args:
        session_id (str): Session identifier.
        engine (ConversationEngine): Conversation engine dependency.
        
    Returns:
        SessionStatusResponse: Current session status.
        
    Raises:
        HTTPException: If session not found.
    """
    try:
        session = engine.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionStatusResponse(
            success=True,
            session_id=session.session_id,
            current_question_index=session.current_question_index,
            completed=session.completed,
            answers_count=len(session.answers)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")