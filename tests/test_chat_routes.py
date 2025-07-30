"""
Unit tests for chat routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from main import app
from app.services.conversation_engine import ConversationEngine


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_conversation_engine():
    """Mock conversation engine."""
    return Mock(spec=ConversationEngine)


class TestChatRoutes:
    """Test cases for chat routes."""
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_start_conversation_success(self, mock_get_engine, client, mock_conversation_engine):
        """Test successful conversation start."""
        # Setup mock
        mock_get_engine.return_value = mock_conversation_engine
        from app.models.schemas import ChatStartResponse
        mock_conversation_engine.start_session.return_value = ChatStartResponse(
            success=True,
            message="Who are you making this payment to? Please provide the name of the person, organization, or company.",
            session_id="test_session"
        )
        
        # Make request
        response = client.post("/api/chat/start", json={"session_id": "test_session"})
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Who are you making this payment to? Please provide the name of the person, organization, or company."
        assert data["session_id"] == "test_session"
        
        mock_conversation_engine.start_session.assert_called_once_with("test_session")
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_start_conversation_engine_error(self, mock_get_engine, client, mock_conversation_engine):
        """Test conversation start with engine error."""
        # Setup mock to raise exception
        mock_get_engine.return_value = mock_conversation_engine
        mock_conversation_engine.start_session.side_effect = Exception("Engine error")
        
        # Make request
        response = client.post("/api/chat/start", json={"session_id": "test_session"})
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    def test_start_conversation_invalid_request(self, client):
        """Test conversation start with invalid request."""
        # Make request without session_id
        response = client.post("/api/chat/start", json={})
        
        # Assertions
        assert response.status_code == 422  # Validation error
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_process_response_success(self, mock_get_engine, client, mock_conversation_engine):
        """Test successful response processing."""
        # Setup mock
        mock_get_engine.return_value = mock_conversation_engine
        from app.models.schemas import ChatResponseResponse
        mock_conversation_engine.process_response = AsyncMock(return_value=ChatResponseResponse(
            success=True,
            message="Next question",
            completed=False,
            fraud_analysis=None
        ))
        
        # Make request
        response = client.post("/api/chat/respond", json={
            "session_id": "test_session",
            "message": "Test response"
        })
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Next question"
        assert data["completed"] is False
        
        mock_conversation_engine.process_response.assert_called_once_with("test_session", "Test response")
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_process_response_completed(self, mock_get_engine, client, mock_conversation_engine):
        """Test response processing when conversation is completed."""
        # Setup mock
        mock_get_engine.return_value = mock_conversation_engine
        from app.models.schemas import ChatResponseResponse
        mock_conversation_engine.process_response = AsyncMock(return_value=ChatResponseResponse(
            success=True,
            message="Analysis complete",
            completed=True,
            fraud_analysis="RISK LEVEL: LOW"
        ))
        
        # Make request
        response = client.post("/api/chat/respond", json={
            "session_id": "test_session",
            "message": "Final response"
        })
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["completed"] is True
        assert data["fraud_analysis"] == "RISK LEVEL: LOW"
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_process_response_engine_error(self, mock_get_engine, client, mock_conversation_engine):
        """Test response processing with engine error."""
        # Setup mock to raise exception
        mock_get_engine.return_value = mock_conversation_engine
        mock_conversation_engine.process_response = AsyncMock(side_effect=Exception("Processing error"))
        
        # Make request
        response = client.post("/api/chat/respond", json={
            "session_id": "test_session",
            "message": "Test response"
        })
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    def test_process_response_invalid_request(self, client):
        """Test response processing with invalid request."""
        # Make request without message
        response = client.post("/api/chat/respond", json={"session_id": "test_session"})
        
        # Assertions
        assert response.status_code == 422  # Validation error
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_get_session_status_success(self, mock_get_engine, client, mock_conversation_engine):
        """Test successful session status retrieval."""
        # Setup mock
        mock_session = Mock()
        mock_session.session_id = "test_session"
        mock_session.current_question_index = 1
        mock_session.completed = False
        mock_session.answers = {"question1": "answer1"}
        
        mock_get_engine.return_value = mock_conversation_engine
        mock_conversation_engine.get_session.return_value = mock_session
        
        # Make request
        response = client.get("/api/chat/status/test_session")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test_session"
        assert data["current_question_index"] == 1
        assert data["completed"] is False
        assert data["answers_count"] == 1
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_get_session_status_not_found(self, mock_get_engine, client, mock_conversation_engine):
        """Test session status for non-existent session."""
        # Setup mock
        mock_get_engine.return_value = mock_conversation_engine
        mock_conversation_engine.get_session.return_value = None
        
        # Make request
        response = client.get("/api/chat/status/nonexistent_session")
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "Session not found" in data["detail"]
    
    @patch('app.routes.chat.get_conversation_engine')
    def test_get_session_status_engine_error(self, mock_get_engine, client, mock_conversation_engine):
        """Test session status with engine error."""
        # Setup mock to raise exception
        mock_get_engine.return_value = mock_conversation_engine
        mock_conversation_engine.get_session.side_effect = Exception("Status error")
        
        # Make request
        response = client.get("/api/chat/status/test_session")
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]