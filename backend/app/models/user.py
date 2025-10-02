"""
User model for authentication and authorization.

This model supports multi-tenancy with organization-based access control.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""

    SUPER_ADMIN = "super_admin"  # Platform owner (you)
    ORG_ADMIN = "org_admin"  # Clinic owner/manager
    ORG_STAFF = "org_staff"  # Clinic staff (dentist, receptionist)
    ORG_VIEWER = "org_viewer"  # Read-only access


class User(Base):
    """User model with multi-tenancy support."""

    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Profile
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Authorization
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ORG_STAFF)

    # Multi-tenancy
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    organization = relationship("Organization", back_populates="users")

    # MFA (optional)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login_at = Column(DateTime, nullable=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
