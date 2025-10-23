"""
Unit Tests for Conversation Service

Tests conversation persistence, message handling, and retrieval.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.services.conversation_service import ConversationService


@pytest.fixture
def service():
    """Create a fresh ConversationService instance for each test."""
    return ConversationService()


@pytest.mark.unit
@pytest.mark.services
class TestConversationService:
    """Test Conversation Service."""
    
    def test_init(self, service):
        """Test service initialization."""
        assert service is not None
        assert isinstance(service.conversations, dict)
        assert isinstance(service.messages, dict)
        assert len(service.conversations) == 0
        assert len(service.messages) == 0
    
    def test_create_conversation(self, service):
        """Test creating a new conversation."""
        conv_id = str(uuid4())
        conversation = service.create_conversation(
            conversation_id=conv_id,
            user_id="user123",
            organization_id="org456",
            channel="web_chat"
        )
        
        assert conversation is not None
        assert conversation["id"] == conv_id
        assert conversation["user_id"] == "user123"
        assert conversation["organization_id"] == "org456"
        assert conversation["channel"] == "web_chat"
        assert conversation["status"] == "active"
        assert conversation["message_count"] == 0
        assert conversation["primary_agent"] is None
        assert "created_at" in conversation
        assert "updated_at" in conversation
    
    def test_get_conversation(self, service):
        """Test retrieving a conversation by ID."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id, user_id="user123")
        
        retrieved = service.get_conversation(conv_id)
        assert retrieved is not None
        assert retrieved["id"] == conv_id
        assert retrieved["user_id"] == "user123"
    
    def test_get_conversation_not_found(self, service):
        """Test retrieving non-existent conversation returns None."""
        result = service.get_conversation("non_existent_id")
        assert result is None
    
    def test_add_message(self, service):
        """Test adding a message to a conversation."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        message = service.add_message(
            conversation_id=conv_id,
            role="user",
            content="Hello, I need help with my appointment",
            metadata={"source": "web"}
        )
        
        assert message is not None
        assert message["conversation_id"] == conv_id
        assert message["role"] == "user"
        assert message["content"] == "Hello, I need help with my appointment"
        assert message["metadata"]["source"] == "web"
        assert "id" in message
        assert "created_at" in message
    
    def test_add_message_auto_creates_conversation(self, service):
        """Test that adding a message auto-creates conversation if needed."""
        conv_id = str(uuid4())
        
        # Add message without creating conversation first
        message = service.add_message(
            conversation_id=conv_id,
            role="user",
            content="Test message"
        )
        
        assert message is not None
        # Verify conversation was auto-created
        conversation = service.get_conversation(conv_id)
        assert conversation is not None
        assert conversation["message_count"] == 1
    
    def test_add_message_with_agent_name(self, service):
        """Test adding a message with agent name sets primary agent."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        service.add_message(
            conversation_id=conv_id,
            role="assistant",
            content="I can help you with that",
            agent_name="Alex"
        )
        
        conversation = service.get_conversation(conv_id)
        assert conversation["primary_agent"] == "Alex"
    
    def test_get_messages(self, service):
        """Test retrieving messages for a conversation."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        # Add multiple messages
        service.add_message(conv_id, "user", "Message 1")
        service.add_message(conv_id, "assistant", "Response 1")
        service.add_message(conv_id, "user", "Message 2")
        
        messages = service.get_messages(conv_id)
        assert len(messages) == 3
        assert messages[0]["content"] == "Message 1"
        assert messages[1]["content"] == "Response 1"
        assert messages[2]["content"] == "Message 2"
    
    def test_get_messages_with_limit(self, service):
        """Test retrieving messages with limit returns last N messages."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        # Add 5 messages
        for i in range(5):
            service.add_message(conv_id, "user", f"Message {i+1}")
        
        # Get last 2 messages
        messages = service.get_messages(conv_id, limit=2)
        assert len(messages) == 2
        assert messages[0]["content"] == "Message 4"
        assert messages[1]["content"] == "Message 5"
    
    def test_get_messages_empty_conversation(self, service):
        """Test getting messages from non-existent conversation returns empty list."""
        messages = service.get_messages("non_existent_id")
        assert messages == []
    
    def test_list_conversations(self, service):
        """Test listing conversations for a user."""
        # Create conversations for different users
        service.create_conversation("conv1", user_id="user123")
        service.create_conversation("conv2", user_id="user123")
        service.create_conversation("conv3", user_id="user456")
        
        # List conversations for user123
        conversations = service.list_conversations(user_id="user123")
        assert len(conversations) == 2
        assert all(conv["user_id"] == "user123" for conv in conversations)
    
    def test_list_conversations_sorted_by_updated(self, service):
        """Test that conversations are sorted by updated_at descending."""
        import time
        
        # Create conversations with slight delay
        conv1_id = "conv1"
        conv2_id = "conv2"
        
        service.create_conversation(conv1_id, user_id="user123")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        service.create_conversation(conv2_id, user_id="user123")
        
        # Update conv1 to make it most recent
        service.add_message(conv1_id, "user", "New message")
        
        conversations = service.list_conversations(user_id="user123")
        assert len(conversations) == 2
        # conv1 should be first (most recently updated)
        assert conversations[0]["id"] == conv1_id
    
    def test_list_conversations_with_limit(self, service):
        """Test listing conversations respects limit parameter."""
        # Create 5 conversations
        for i in range(5):
            service.create_conversation(f"conv{i}", user_id="user123")
        
        # List with limit of 3
        conversations = service.list_conversations(user_id="user123", limit=3)
        assert len(conversations) == 3
    
    def test_update_conversation_status(self, service):
        """Test updating conversation status."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        # Update status
        service.update_conversation_status(conv_id, "closed")
        
        conversation = service.get_conversation(conv_id)
        assert conversation["status"] == "closed"
    
    def test_update_conversation_status_non_existent(self, service):
        """Test updating status of non-existent conversation does nothing."""
        # Should not raise error
        service.update_conversation_status("non_existent_id", "closed")
    
    def test_get_conversation_summary(self, service):
        """Test getting conversation summary."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        # Add messages
        service.add_message(conv_id, "user", "What are your hours?")
        service.add_message(conv_id, "assistant", "We're open 8am-6pm", agent_name="Alex")
        
        summary = service.get_conversation_summary(conv_id)
        
        assert summary is not None
        assert summary["id"] == conv_id
        assert summary["title"] == "What are your hours?"
        assert summary["agent"] == "Alex"
        assert summary["message_count"] == 2
        assert summary["status"] == "active"
        assert "created_at" in summary
        assert "updated_at" in summary
    
    def test_get_conversation_summary_long_title(self, service):
        """Test that summary title is truncated for long messages."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        long_message = "A" * 100  # 100 character message
        service.add_message(conv_id, "user", long_message)
        
        summary = service.get_conversation_summary(conv_id)
        assert len(summary["title"]) <= 53  # 50 chars + "..."
        assert summary["title"].endswith("...")
    
    def test_get_conversation_summary_no_user_messages(self, service):
        """Test summary with no user messages uses default title."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        # Only add assistant message
        service.add_message(conv_id, "assistant", "Hello")
        
        summary = service.get_conversation_summary(conv_id)
        assert summary["title"] == "New Conversation"
    
    def test_get_conversation_summary_non_existent(self, service):
        """Test getting summary of non-existent conversation returns empty dict."""
        summary = service.get_conversation_summary("non_existent_id")
        assert summary == {}
    
    def test_message_count_updates(self, service):
        """Test that message count updates correctly."""
        conv_id = str(uuid4())
        service.create_conversation(conv_id)
        
        conversation = service.get_conversation(conv_id)
        assert conversation["message_count"] == 0
        
        service.add_message(conv_id, "user", "Message 1")
        conversation = service.get_conversation(conv_id)
        assert conversation["message_count"] == 1
        
        service.add_message(conv_id, "assistant", "Response 1")
        conversation = service.get_conversation(conv_id)
        assert conversation["message_count"] == 2

