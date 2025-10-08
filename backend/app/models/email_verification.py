"""
Email verification token model.

Stores verification tokens for email verification during registration.
"""

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey
from app.core.database_types import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmailVerificationToken(Base):
    """Email verification token for user registration."""
    
    __tablename__ = "email_verification_tokens"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="verification_tokens")
    
    # Token
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expiration to 24 hours from now
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired
    
    def __repr__(self) -> str:
        return f"<EmailVerificationToken {self.token[:8]}... for user {self.user_id}>"
