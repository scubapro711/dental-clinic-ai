"""
Telegram Conversation Model

Stores the context and state of a conversation with a user on Telegram.
"""

import uuid
from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base

class TelegramConversation(Base):
    __tablename__ = "telegram_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id = Column(BigInteger, ForeignKey("telegram_users.telegram_user_id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True) # Links to the main conversations table

    # Context
    current_flow = Column(String(100), nullable=True)  # e.g., 'appointment_booking', 'inquiry'
    flow_state = Column(JSONB, nullable=True)  # Stores the current state of the conversation flow

    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    message_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<TelegramConversation(convo_id={self.conversation_id}, user_id={self.telegram_user_id})>"

