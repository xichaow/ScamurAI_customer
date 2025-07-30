#!/usr/bin/env python3
"""
Simple smoke test runner for the fraud detection chatbot.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.conversation_engine import ConversationEngine, FRAUD_QUESTIONS
from unittest.mock import Mock

def test_conversation_engine():
    """Test basic conversation engine functionality."""
    print("Testing ConversationEngine...")
    
    # Create mock OpenAI client
    mock_client = Mock()
    engine = ConversationEngine(mock_client)
    
    # Test session start
    result = engine.start_session("test_session")
    assert result.success == True
    assert result.session_id == "test_session"
    assert result.message == FRAUD_QUESTIONS[0].question
    
    # Test session retrieval
    session = engine.get_session("test_session")
    assert session is not None
    assert session.session_id == "test_session"
    assert session.current_question_index == 0
    
    print("✓ ConversationEngine basic functionality works")

def test_fraud_questions():
    """Test that all fraud detection questions are properly defined."""
    print("Testing fraud detection questions...")
    
    assert len(FRAUD_QUESTIONS) == 4
    
    expected_ids = [
        "payment_recipient",
        "purpose_of_payment", 
        "source_of_payment_link",
        "website_verification"
    ]
    
    for i, question in enumerate(FRAUD_QUESTIONS):
        assert question.id == expected_ids[i]
        assert len(question.question) > 10
        assert question.validation is not None
    
    print("✓ All 4 fraud detection questions are properly configured")

def test_fastapi_app():
    """Test FastAPI app initialization."""
    print("Testing FastAPI app...")
    
    from main import app
    assert app is not None
    
    # Check that routes are registered
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    expected_routes = ['/api/chat/start', '/api/chat/respond', '/', '/health']
    
    for expected_route in expected_routes:
        assert any(expected_route in route for route in routes), f"Route {expected_route} not found"
    
    print("✓ FastAPI app initializes correctly with expected routes")

if __name__ == "__main__":
    print("Running smoke tests for Fraud Detection Chatbot...\n")
    
    try:
        test_conversation_engine()
        test_fraud_questions()
        test_fastapi_app()
        
        print("\n🎉 All smoke tests passed!")
        print("\nTo start the application:")
        print("1. Copy .env.example to .env and add your OPENAI_API_KEY")
        print("2. Run: source venv_linux/bin/activate")
        print("3. Run: python main.py")
        print("4. Open: http://localhost:8000")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)