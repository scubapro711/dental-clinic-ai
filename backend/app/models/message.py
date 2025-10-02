"""
Message model for conversation history.

This model stores individual messages within conversations.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MessageRole(str, enum.Enum):
    """Message role."""

    USER = "user"  # Patient message
    ASSISTANT = "assistant"  # AI agent message
    SYSTEM = "system"  # System message


class Message(Base):
    """Message model."""

    __tablename__ = "messages"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Message content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    agent_name = Column(String(50), nullable=True)  # dana, michal, yosef, sarah

    # Metadata (renamed to avoid SQLAlchemy reserved word)
    message_metadata = Column(JSON, nullable=True)  # Tool calls, function results, etc.
    tokens_used = Column(Integer, nullable=True)  # LLM tokens used
    latency_ms = Column(Integer, nullable=True)  # Response latency

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Message {self.id} - {self.role}>"
