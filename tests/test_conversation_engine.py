"""
Unit tests for conversation engine.
"""
import pytest
from unittest.mock import Mock, AsyncMock
import time

from app.services.conversation_engine import ConversationEngine, FRAUD_QUESTIONS
from app.models.schemas import ConversationSession


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_client.chat = Mock()
    mock_client.chat.completions = Mock()
    mock_client.chat.completions.create = AsyncMock()
    return mock_client


@pytest.fixture
def conversation_engine(mock_openai_client):
    """Create conversation engine with mock OpenAI client."""
    return ConversationEngine(mock_openai_client)


class TestConversationEngine:
    """Test cases for ConversationEngine class."""
    
    def test_start_session_success(self, conversation_engine):
        """Test successful session start."""
        session_id = "test_session_123"
        
        result = conversation_engine.start_session(session_id)
        
        assert result.success is True
        assert result.session_id == session_id
        assert result.message == FRAUD_QUESTIONS[0].question
        assert session_id in conversation_engine.sessions
    
    def test_start_session_creates_valid_session(self, conversation_engine):
        """Test that starting a session creates proper session data."""
        session_id = "test_session_123"
        
        conversation_engine.start_session(session_id)
        session = conversation_engine.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert session.current_question_index == 0
        assert session.answers == {}
        assert session.retry_count == 0
        assert session.completed is False
        assert isinstance(session.start_time, float)
    
    def test_get_session_nonexistent(self, conversation_engine):
        """Test getting a session that doesn't exist."""
        result = conversation_engine.get_session("nonexistent_session")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_response_invalid_session(self, conversation_engine):
        """Test processing response for invalid session."""
        result = await conversation_engine.process_response("invalid_session", "test message")
        
        assert result.success is False
        assert "Session not found" in result.message
    
    @pytest.mark.asyncio
    async def test_process_response_completed_session(self, conversation_engine):
        """Test processing response for already completed session."""
        session_id = "test_session"
        conversation_engine.start_session(session_id)
        
        # Mark session as completed
        session = conversation_engine.get_session(session_id)
        session.completed = True
        
        result = await conversation_engine.process_response(session_id, "test message")
        
        assert result.success is True
        assert result.completed is True
        assert "assessment has been completed" in result.message
    
    @pytest.mark.asyncio
    async def test_process_response_valid_answer(self, conversation_engine, mock_openai_client):
        """Test processing valid response moves to next question."""
        # Mock OpenAI response for validation
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "true"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        session_id = "test_session"
        conversation_engine.start_session(session_id)
        
        result = await conversation_engine.process_response(session_id, "Valid company name")
        
        assert result.success is True
        assert result.message == FRAUD_QUESTIONS[1].question  # Next question
        
        session = conversation_engine.get_session(session_id)
        assert session.current_question_index == 1
        assert "payment_recipient" in session.answers
    
    @pytest.mark.asyncio
    async def test_process_response_invalid_answer_retry(self, conversation_engine, mock_openai_client):
        """Test processing invalid response triggers retry."""
        # Mock OpenAI response for validation
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "false"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        session_id = "test_session"
        conversation_engine.start_session(session_id)
        
        result = await conversation_engine.process_response(session_id, "yes")
        
        assert result.success is True
        assert "more specific answer" in result.message
        
        session = conversation_engine.get_session(session_id)
        assert session.current_question_index == 0  # Still on first question
        assert session.retry_count == 1
    
    @pytest.mark.asyncio
    async def test_process_response_max_retries(self, conversation_engine, mock_openai_client):
        """Test that max retries moves to next question."""
        # Mock OpenAI response for validation
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "false"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        session_id = "test_session"
        conversation_engine.start_session(session_id)
        session = conversation_engine.get_session(session_id)
        session.retry_count = 2  # Set to 2, next fail will trigger max retry
        
        result = await conversation_engine.process_response(session_id, "invalid")
        
        assert result.success is True
        assert result.message == FRAUD_QUESTIONS[1].question  # Moved to next question
        
        session = conversation_engine.get_session(session_id)
        assert session.current_question_index == 1
        assert session.retry_count == 0  # Reset retry count
        assert "unable to provide relevant answer" in session.answers["payment_recipient"]
    
    @pytest.mark.asyncio
    async def test_process_response_all_questions_completed(self, conversation_engine, mock_openai_client):
        """Test completing all questions triggers fraud analysis."""
        # Mock OpenAI responses
        validation_response = Mock()
        validation_response.choices = [Mock()]
        validation_response.choices[0].message = Mock()
        validation_response.choices[0].message.content = "true"
        
        analysis_response = Mock()
        analysis_response.choices = [Mock()]
        analysis_response.choices[0].message = Mock()
        analysis_response.choices[0].message.content = "RISK LEVEL: LOW\nANALYSIS: Test analysis"
        
        mock_openai_client.chat.completions.create.side_effect = [
            validation_response, analysis_response
        ]
        
        session_id = "test_session"
        conversation_engine.start_session(session_id)
        session = conversation_engine.get_session(session_id)
        
        # Set session to last question
        session.current_question_index = len(FRAUD_QUESTIONS) - 1
        session.answers = {
            "payment_recipient": "Test Company",
            "purpose_of_payment": "Test Service", 
            "source_of_payment_link": "Email from company"
        }
        
        result = await conversation_engine.process_response(session_id, "https://testcompany.com")
        
        assert result.success is True
        assert result.completed is True
        assert result.fraud_analysis is not None
        assert "RISK LEVEL" in result.fraud_analysis
        
        session = conversation_engine.get_session(session_id)
        assert session.completed is True
    
    def test_cleanup_old_sessions(self, conversation_engine):
        """Test cleanup of old sessions."""
        # Create old session
        old_session_id = "old_session"
        conversation_engine.start_session(old_session_id)
        old_session = conversation_engine.get_session(old_session_id)
        old_session.start_time = time.time() - 7200  # 2 hours ago
        
        # Create recent session
        recent_session_id = "recent_session"
        conversation_engine.start_session(recent_session_id)
        
        # Run cleanup
        conversation_engine.cleanup_old_sessions()
        
        # Check results
        assert conversation_engine.get_session(old_session_id) is None
        assert conversation_engine.get_session(recent_session_id) is not None
    
    def test_get_question_context(self, conversation_engine):
        """Test question context mapping."""
        # Test with known question ID
        question = FRAUD_QUESTIONS[0]  # payment_recipient
        context = conversation_engine._get_question_context(question)
        assert context == "who you are paying"
        
        # Test with unknown question ID
        unknown_question = Mock()
        unknown_question.id = "unknown_question"
        context = conversation_engine._get_question_context(unknown_question)
        assert context == "this question"