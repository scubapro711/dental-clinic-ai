"""
Conversation Service - Handles conversation persistence and retrieval.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Simple in-memory conversation storage.
    In production, this would use a database.
    """
    
    def __init__(self):
        """Initialize conversation storage."""
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.messages: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("ConversationService initialized (in-memory mode)")
    
    def create_conversation(
        self,
        conversation_id: str,
        user_id: str = "default",
        organization_id: str = "default",
        channel: str = "web_chat"
    ) -> Dict[str, Any]:
        """Create a new conversation."""
        conversation = {
            "id": conversation_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "channel": channel,
            "status": "active",
            "primary_agent": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "message_count": 0,
        }
        
        self.conversations[conversation_id] = conversation
        self.messages[conversation_id] = []
        
        logger.info(f"Created conversation: {conversation_id}")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def list_conversations(
        self,
        user_id: str = "default",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List conversations for a user."""
        user_conversations = [
            conv for conv in self.conversations.values()
            if conv["user_id"] == user_id
        ]
        
        # Sort by updated_at descending
        user_conversations.sort(
            key=lambda x: x["updated_at"],
            reverse=True
        )
        
        return user_conversations[:limit]
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a message to a conversation."""
        # Create conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        
        message = {
            "id": str(uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "agent_name": agent_name,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self.messages[conversation_id].append(message)
        
        # Update conversation
        conversation = self.conversations[conversation_id]
        conversation["updated_at"] = datetime.utcnow().isoformat()
        conversation["message_count"] = len(self.messages[conversation_id])
        
        if agent_name and not conversation["primary_agent"]:
            conversation["primary_agent"] = agent_name
        
        logger.debug(f"Added message to conversation {conversation_id}: {role}")
        return message
    
    def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages for a conversation."""
        messages = self.messages.get(conversation_id, [])
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def update_conversation_status(
        self,
        conversation_id: str,
        status: str
    ) -> None:
        """Update conversation status."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["status"] = status
            self.conversations[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        messages = self.get_messages(conversation_id)
        
        # Get first user message as title
        title = "New Conversation"
        for msg in messages:
            if msg["role"] == "user":
                title = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break
        
        return {
            "id": conversation_id,
            "title": title,
            "agent": conversation["primary_agent"],
            "message_count": conversation["message_count"],
            "status": conversation["status"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
        }


# Global instance
conversation_service = ConversationService()
