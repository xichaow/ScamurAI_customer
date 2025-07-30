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
_openai_client = None
_conversation_engine = None


def get_openai_client() -> openai.OpenAI:
    """
    Get OpenAI client instance (singleton).
    
    Returns:
        openai.OpenAI: OpenAI client instance.
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
    """
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        _openai_client = openai.OpenAI(api_key=api_key)
    
    return _openai_client


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