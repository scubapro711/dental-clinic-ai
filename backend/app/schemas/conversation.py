"""
Conversation schemas for request/response validation.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Create a new message in a conversation."""
    
    content: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    """Message response model."""
    
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    agent_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Create a new conversation."""
    
    channel: str = Field(default="web")  # web, whatsapp, telegram
    title: Optional[str] = Field(None, max_length=255)


class ConversationResponse(BaseModel):
    """Conversation response model."""
    
    id: UUID
    organization_id: UUID
    channel: str
    status: str
    title: Optional[str] = None
    primary_agent: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Conversation with messages."""
    
    messages: List[MessageResponse]


class ChatRequest(BaseModel):
    """Chat request with message content."""
    
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Chat response from AI agent."""
    
    conversation_id: UUID
    message_id: UUID
    response: str
    agent: str
    requires_human: bool = False
