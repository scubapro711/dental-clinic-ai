"""
Telegram User Model

Represents a mapping between a Telegram user and a user/patient in the DentaFlow system.
"""

import uuid
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id = Column(BigInteger, nullable=False, index=True)
    telegram_username = Column(String(255), nullable=True)
    telegram_first_name = Column(String(255), nullable=True)
    telegram_last_name = Column(String(255), nullable=True)

    # Link to our system
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    patient_id = Column(BigInteger, nullable=True, index=True) # Odoo Patient ID
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Preferences
    language = Column(String(10), default='he')
    notifications_enabled = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("telegram_user_id", "organization_id", name="uq_telegram_user_org"),)

    def __repr__(self):
        return f"<TelegramUser(telegram_id={self.telegram_user_id}, org_id={self.organization_id})>"




# Enum for Telegram User Status
from enum import Enum

class TelegramUserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"
    INACTIVE = "inactive"

