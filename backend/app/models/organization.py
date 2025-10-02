"""
Organization model for multi-tenancy.

Each dental clinic is an organization with its own users, patients, and data.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers for pricing."""

    BASIC = "basic"  # Free tier - Core 4 agents only
    PROFESSIONAL = "professional"  # $1,500/month - + CFO & Operations agents
    ENTERPRISE = "enterprise"  # $4,500/month - All 7 executive agents


class Organization(Base):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Basic info
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Contact
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Subscription
    subscription_tier = Column(
        Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.BASIC
    )
    subscription_status = Column(String(50), nullable=False, default="active")
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)

    # Billing
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)

    # Odoo integration
    odoo_db_name = Column(String(255), nullable=True, unique=True)
    odoo_api_key = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    users = relationship("User", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"
