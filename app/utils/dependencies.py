"""
Dependency injection utilities for FastAPI.
"""
import os
import openai
from dotenv import load_dotenv
from ..services.conversation_engine import ConversationEngine

# Load environment variables
load_dotenv()

# Global instances
_conversation_engine = None


def get_openai_client():
    """
    Get OpenAI client configured with API key.
    
    Returns:
        configured openai module
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    openai.api_key = api_key
    return openai


def get_conversation_engine() -> ConversationEngine:
    """
    Get conversation engine instance (singleton).
    
    Returns:
        ConversationEngine: Conversation engine instance.
    """
    global _conversation_engine
    
    if _conversation_engine is None:
        openai_client = get_openai_client()
        _conversation_engine = ConversationEngine(openai_client)
    
    return _conversation_engine