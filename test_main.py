import pytest
import unittest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from database import Message
from main import verify_api_key, process_message, settings, HTTPException, SYSTEM_PROMPT

@pytest.fixture
def mock_db_session():
    session = Mock(spec=Session)
    return session

@pytest.fixture
def mock_db_messages():
    return [
        Message(id=1, role="user", content="What is the capital of England?", created_at="2024-01-01T00:00:00Z"),
        Message(id=2, role="assistant", content="The capital of England is London.", created_at="2024-01-01T00:01:00Z"),
    ]

@pytest.fixture
def mock_openai_client():
    client = Mock()
    return client

@pytest.fixture
def mock_openai_response():
    response = Mock()
    response.output_text = "The capital of England is London."
    return response

@pytest.mark.asyncio
async def test_verify_api_key_valid(monkeypatch):
    # Mock settings with a valid API key
    monkeypatch.setattr(settings, "api_key", "valid_api_key")
    
    # Call the function with the correct API key
    result = await verify_api_key(x_api_key="valid_api_key")
    assert result == "valid_api_key"

@pytest.mark.asyncio
async def test_verify_api_key_invalid(monkeypatch):
    # Mock settings with a valid API key
    monkeypatch.setattr(settings, "api_key", "valid_api_key")
    
    # Call the function with an incorrect API key and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key="invalid_api_key")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API Key"

@pytest.mark.asyncio
async def test_verify_api_key_not_configured(monkeypatch):
    # Mock settings with no API Key configured
    monkeypatch.setattr(settings, "api_key", None)

    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key="any_api_key")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "API Key not configured on server"

def test_process_message_success(mock_db_session, mock_db_messages, mock_openai_client, mock_openai_response):
    # This is a placeholder for testing the process_message function
    # You would need to mock the OpenAI client and its responses as well
    mock_db_session.query(Message).all.return_value = mock_db_messages
    mock_openai_client.responses.create.return_value = mock_openai_response

    user_input = "What is the capital of England?"

    result = process_message(user_message=user_input, session=mock_db_session, openai_client=mock_openai_client)

    # Assert that DB query was called
    mock_db_session.query(Message).all.assert_called_once()

    # Assert that OpenAI API was called with the correct parameters
    expected_conversation = [
        {"role": "developer", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "What is the capital of England?"},
        {"role": "assistant", "content": "The capital of England is London."},
        {"role": "user", "content": user_input},
    ]

    mock_openai_client.responses.create.assert_called_once_with(
        model="gpt-4.1",
        input=expected_conversation
    )

    # Assert messages were saved to the database
    assert mock_db_session.add_all.call_count == 1 
    saved_messages = mock_db_session.add_all.call_args[0][0]
    assert len(saved_messages) == 2
    assert saved_messages[0].role == "user"
    assert saved_messages[0].content == user_input
    assert saved_messages[1].role == "assistant"
    assert saved_messages[1].content == "The capital of England is London."

    mock_db_session.commit.assert_called_once()

    # Assert session was closed
    mock_db_session.close.assert_called_once()

    # Assert that the result is as expected
    assert result["response"] == "The capital of England is London."