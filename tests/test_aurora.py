"""
Tests for Aurora's conversational API.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_aurora_agent():
    """Fixture to mock the Aurora agent."""
    with patch('main.create_aurora_agent') as mock_create:
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value='{"message": "This is a mock response."}')
        mock_create.return_value = mock_agent
        yield mock_create

def test_start_aurora_session(mock_aurora_agent):
    """Test starting a new Aurora session."""
    response = client.post(
        "/aurora/start_session",
        json={"recommendations": ["Recommendation 1", "Recommendation 2"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "initial_message" in data
    assert isinstance(data["session_id"], str)
    assert data["initial_message"] == "This is a mock response."

def test_chat_with_aurora(mock_aurora_agent):
    """Test a chat turn with Aurora."""
    # Start a session first
    start_response = client.post(
        "/aurora/start_session",
        json={"recommendations": ["Take a deep breath."]},
    )
    session_id = start_response.json()["session_id"]

    # Now, chat
    chat_response = client.post(
        "/aurora/chat",
        json={"session_id": session_id, "message": "I'm feeling anxious."},
    )
    assert chat_response.status_code == 200
    data = chat_response.json()
    assert data["session_id"] == session_id
    assert data["response"] == "This is a mock response."

def test_chat_with_invalid_session():
    """Test chat with an invalid session ID."""
    response = client.post(
        "/aurora/chat",
        json={"session_id": "invalid-session-id", "message": "Hello?"},
    )
    assert response.status_code == 404

@patch('agents.agent_factory.get_chat_client')
@patch('agents.agent_factory.get_provider_name', return_value='azure_openai')
@patch('agent_framework.ChatAgent')
def test_chat_with_aurora_azure(mock_chat_agent, mock_provider, mock_get_chat_client):
    """Test a chat turn with Aurora using the azure_openai provider."""
    # Mock the chat client and the agent it creates
    mock_chat_client = MagicMock()
    mock_get_chat_client.return_value = mock_chat_client

    # Mock the ChatAgent and its thread
    mock_agent_instance = mock_chat_agent.return_value
    mock_agent_instance.run = AsyncMock(return_value='{"message": "This is a mock azure response."}')
    mock_thread = AsyncMock()
    mock_thread.add_message = AsyncMock()
    mock_agent_instance.get_new_thread = AsyncMock(return_value=mock_thread)

    # Start a session first
    start_response = client.post(
        "/aurora/start_session",
        json={"recommendations": ["Take a deep breath."]},
    )
    session_id = start_response.json()["session_id"]

    # Now, chat
    client.post(
        "/aurora/chat",
        json={"session_id": session_id, "message": "I'm feeling anxious."},
    )

    # Assert that get_new_thread was called and add_message was called on the thread
    mock_agent_instance.get_new_thread.assert_called_once()
    assert mock_thread.add_message.call_count > 0
