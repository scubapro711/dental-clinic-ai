"""
Telegram Invite Code Model

Represents an invite code that can be used to join a specific clinic via Telegram.
"""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from app.core.database_types import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class TelegramInviteCode(Base):
    __tablename__ = "telegram_invite_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)

    # Settings
    max_uses = Column(Integer, nullable=True)  # NULL = unlimited
    current_uses = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<TelegramInviteCode(code=\"{self.code}\", org_id={self.organization_id})>"




# Enum for Invite Code Status
from enum import Enum

class InviteCodeStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"
    DISABLED = "disabled"

