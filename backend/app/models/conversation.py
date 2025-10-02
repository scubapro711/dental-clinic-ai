"""
Conversation model for tracking agent interactions with patients.

This model stores all conversations between patients and AI agents.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ConversationStatus(str, enum.Enum):
    """Conversation status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"  # Escalated to human
    FAILED = "failed"


class ConversationChannel(str, enum.Enum):
    """Communication channel."""

    WEB_CHAT = "web_chat"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SMS = "sms"


class Conversation(Base):
    """Conversation model."""

    __tablename__ = "conversations"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Multi-tenancy
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Patient info (nullable for anonymous conversations)
    patient_name = Column(String(255), nullable=True)
    patient_email = Column(String(255), nullable=True)
    patient_phone = Column(String(20), nullable=True)

    # Conversation metadata
    status = Column(
        Enum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE
    )
    channel = Column(
        Enum(ConversationChannel), nullable=False, default=ConversationChannel.WEB_CHAT
    )

    # Agent routing
    primary_agent = Column(
        String(50), nullable=False
    )  # dana, michal, yosef, sarah
    escalated_to_agent = Column(String(50), nullable=True)

    # LangGraph state
    langgraph_thread_id = Column(String(255), nullable=False, unique=True, index=True)
    langgraph_state = Column(JSON, nullable=True)  # Current state snapshot

    # Summary
    summary = Column(Text, nullable=True)  # AI-generated summary
    tags = Column(JSON, nullable=True)  # ["appointment", "billing", etc.]

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at = Column(DateTime, nullable=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Conversation {self.id} - {self.primary_agent}>"
