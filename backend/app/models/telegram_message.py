"""
Telegram Message Model

Store message history for Telegram conversations.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class MessageDirection(str, enum.Enum):
    """Message direction enum."""
    INCOMING = "INCOMING"  # From patient to clinic
    OUTGOING = "OUTGOING"  # From clinic to patient


class TelegramMessage(Base):
    """
    Telegram message model.
    
    Stores all messages exchanged in Telegram conversations.
    """
    __tablename__ = "telegram_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("telegram_conversations.id"), nullable=False, index=True)
    telegram_message_id = Column(Integer, nullable=True)  # Telegram's message ID
    
    # Message content
    text = Column(Text, nullable=True)
    message_type = Column(String(50), default="text")  # text, photo, document, etc.
    
    # Direction
    direction = Column(SQLEnum(MessageDirection), nullable=False, index=True)
    from_clinic = Column(Boolean, default=False)  # True if sent by clinic admin
    
    # Sender info
    sender_telegram_id = Column(Integer, nullable=True)  # Telegram user ID of sender
    sender_name = Column(String(255), nullable=True)  # Display name of sender
    
    # Status
    is_sent = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("TelegramConversation", back_populates="messages")
    
    def __repr__(self):
        direction_str = "→" if self.direction == MessageDirection.OUTGOING else "←"
        return f"<TelegramMessage {self.id} {direction_str} {self.text[:50]}>"

