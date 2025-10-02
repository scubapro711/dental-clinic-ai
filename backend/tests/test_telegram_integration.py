"""
Test Telegram Bot Integration

Tests for Telegram webhook and message handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from app.integrations.telegram_client import TelegramClient
from app.api.v1.endpoints.telegram import handle_message, handle_callback


@pytest.mark.asyncio
async def test_telegram_client_send_message():
    """Test sending a message via Telegram client."""
    client = TelegramClient(bot_token="test_token")
    
    with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {"ok": True, "result": {"message_id": 123}}
        mock_post.return_value.raise_for_status = Mock()
        
        result = await client.send_message(
            chat_id=12345,
            text="Test message"
        )
        
        assert result["ok"] == True
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_handle_message():
    """Test handling incoming Telegram message."""
    message = {
        "chat": {"id": 12345},
        "from": {"id": 67890, "username": "testuser"},
        "text": "Hello"
    }
    
    with patch('app.api.v1.endpoints.telegram.telegram_client') as mock_client, \
         patch('app.api.v1.endpoints.telegram.agent_graph_v2') as mock_agent:
        
        # Mock telegram client
        mock_client.client.post = AsyncMock()
        mock_client.send_message = AsyncMock()
        mock_client.create_quick_reply_buttons = Mock(return_value={"inline_keyboard": []})
        
        # Mock agent response
        mock_agent.process_message = AsyncMock(return_value={
            "agent": "alex",
            "response": "Hello! How can I help you?",
            "requires_human": False,
            "escalation_level": None,
        })
        
        # Handle message
        await handle_message(message)
        
        # Verify agent was called
        mock_agent.process_message.assert_called_once()
        
        # Verify response was sent
        mock_client.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_handle_emergency():
    """Test handling emergency message."""
    message = {
        "chat": {"id": 12345},
        "from": {"id": 67890, "username": "testuser"},
        "text": "I have severe pain and my face is swelling!"
    }
    
    with patch('app.api.v1.endpoints.telegram.telegram_client') as mock_client, \
         patch('app.api.v1.endpoints.telegram.agent_graph_v2') as mock_agent:
        
        # Mock telegram client
        mock_client.client.post = AsyncMock()
        mock_client.send_message = AsyncMock()
        
        # Mock agent response with emergency escalation
        mock_agent.process_message = AsyncMock(return_value={
            "agent": "alex",
            "response": "This sounds like an emergency! I need to connect you with Dr. Smith RIGHT NOW.",
            "requires_human": True,
            "escalation_level": "EMERGENCY",
        })
        
        # Handle message
        await handle_message(message)
        
        # Verify response was sent
        mock_client.send_message.assert_called_once()
        
        # Verify emergency alert was added
        call_args = mock_client.send_message.call_args
        assert "🚨" in call_args[1]["text"]
        assert "EMERGENCY" in call_args[1]["text"]


@pytest.mark.asyncio
async def test_telegram_handle_callback():
    """Test handling button callback."""
    callback_query = {
        "id": "callback123",
        "message": {"chat": {"id": 12345}},
        "from": {"id": 67890},
        "data": "book_appointment"
    }
    
    with patch('app.api.v1.endpoints.telegram.telegram_client') as mock_client, \
         patch('app.api.v1.endpoints.telegram.agent_graph_v2') as mock_agent, \
         patch('app.api.v1.endpoints.telegram.handle_message') as mock_handle:
        
        # Mock telegram client
        mock_client.client.post = AsyncMock()
        mock_handle.return_value = AsyncMock()
        
        # Handle callback
        await handle_callback(callback_query)
        
        # Verify callback was answered
        mock_client.client.post.assert_called_once()
        
        # Verify message handler was called
        mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_start_command():
    """Test /start command."""
    message = {
        "chat": {"id": 12345},
        "from": {"id": 67890, "username": "testuser"},
        "text": "/start"
    }
    
    with patch('app.api.v1.endpoints.telegram.telegram_client') as mock_client:
        mock_client.send_message = AsyncMock()
        mock_client.create_quick_reply_buttons = Mock(return_value={"inline_keyboard": []})
        
        await handle_message(message)
        
        # Verify welcome message was sent
        mock_client.send_message.assert_called_once()
        call_args = mock_client.send_message.call_args
        assert "Welcome" in call_args[1]["text"]


@pytest.mark.asyncio
async def test_telegram_help_command():
    """Test /help command."""
    message = {
        "chat": {"id": 12345},
        "from": {"id": 67890, "username": "testuser"},
        "text": "/help"
    }
    
    with patch('app.api.v1.endpoints.telegram.telegram_client') as mock_client:
        mock_client.send_message = AsyncMock()
        
        await handle_message(message)
        
        # Verify help message was sent
        mock_client.send_message.assert_called_once()
        call_args = mock_client.send_message.call_args
        assert "How to Use" in call_args[1]["text"]


@pytest.mark.asyncio
async def test_telegram_multilingual():
    """Test Hebrew message handling."""
    message = {
        "chat": {"id": 12345},
        "from": {"id": 67890, "username": "testuser"},
        "text": "יש לי כאב שיניים"
    }
    
    with patch('app.api.v1.endpoints.telegram.telegram_client') as mock_client, \
         patch('app.api.v1.endpoints.telegram.agent_graph_v2') as mock_agent:
        
        # Mock telegram client
        mock_client.client.post = AsyncMock()
        mock_client.send_message = AsyncMock()
        mock_client.create_quick_reply_buttons = Mock(return_value={"inline_keyboard": []})
        
        # Mock agent response in Hebrew
        mock_agent.process_message = AsyncMock(return_value={
            "agent": "alex",
            "response": "אני מבין שיש לך כאב שיניים. בוא נקבע לך תור...",
            "requires_human": False,
            "escalation_level": None,
        })
        
        # Handle message
        await handle_message(message)
        
        # Verify agent was called with Hebrew text
        call_args = mock_agent.process_message.call_args
        assert call_args[1]["message"] == "יש לי כאב שיניים"
        
        # Verify response was sent
        mock_client.send_message.assert_called_once()


def test_create_inline_keyboard():
    """Test creating inline keyboard."""
    client = TelegramClient(bot_token="test_token")
    
    buttons = [
        [{"text": "Button 1", "callback_data": "action1"}],
        [{"text": "Button 2", "callback_data": "action2"}],
    ]
    
    keyboard = client.create_inline_keyboard(buttons)
    
    assert "inline_keyboard" in keyboard
    assert len(keyboard["inline_keyboard"]) == 2
    assert keyboard["inline_keyboard"][0][0]["text"] == "Button 1"


def test_create_quick_reply_buttons():
    """Test creating quick reply buttons."""
    client = TelegramClient(bot_token="test_token")
    
    keyboard = client.create_quick_reply_buttons()
    
    assert "inline_keyboard" in keyboard
    assert len(keyboard["inline_keyboard"]) == 2  # 2 rows
    
    # Check button texts
    buttons_flat = [btn for row in keyboard["inline_keyboard"] for btn in row]
    button_texts = [btn["text"] for btn in buttons_flat]
    
    assert "📅 Book Appointment" in button_texts
    assert "💰 Check Invoice" in button_texts
    assert "👨‍⚕️ Talk to Doctor" in button_texts
    assert "📍 Clinic Location" in button_texts


if __name__ == "__main__":
    asyncio.run(test_telegram_client_send_message())
    asyncio.run(test_telegram_handle_message())
    asyncio.run(test_telegram_handle_emergency())
    print("✅ All Telegram tests passed!")
