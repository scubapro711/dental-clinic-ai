"""
Team invitation model for inviting staff members to organizations.

Allows clinic owners to invite dentists, hygienists, receptionists, etc.
"""

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, ForeignKey, Enum
from app.core.database_types import UUID
from sqlalchemy.orm import relationship
import enum
import secrets

from app.core.database import Base


class InvitationStatus(str, enum.Enum):
    """Invitation status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class TeamInvitation(Base):
    """Team invitation model."""
    
    __tablename__ = "team_invitations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Organization reference
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    organization = relationship("Organization")
    
    # Inviter (who sent the invitation)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    inviter = relationship("User", foreign_keys=[inviter_id])
    
    # Invitee details
    invitee_email = Column(String(255), nullable=False, index=True)
    invitee_role = Column(String(50), nullable=False)  # dentist, hygienist, receptionist, etc.
    invitee_name = Column(String(255), nullable=True)  # Optional: suggested name
    
    # Invitation token (unique, secure)
    token = Column(String(64), unique=True, nullable=False, index=True)
    
    # Status
    status = Column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)
    
    # Accepted by (if accepted)
    accepted_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    accepted_by_user = relationship("User", foreign_keys=[accepted_by_user_id])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Personal message from inviter (optional)
    message = Column(String(500), nullable=True)
    
    def __init__(self, **kwargs):
        """Initialize invitation with token and expiration."""
        super().__init__(**kwargs)
        if not self.token:
            self.token = secrets.token_urlsafe(48)  # 48 bytes = 64 chars base64
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiration
    
    def is_expired(self) -> bool:
        """Check if invitation is expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if invitation is valid (pending and not expired)."""
        return self.status == InvitationStatus.PENDING and not self.is_expired()
    
    def __repr__(self) -> str:
        return f"<TeamInvitation {self.invitee_email} to {self.organization_id} as {self.invitee_role}>"
