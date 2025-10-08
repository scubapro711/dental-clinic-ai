"""
SMS verification code model.

Stores verification codes for phone number verification.
"""

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Integer
from app.core.database_types import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SMSVerificationCode(Base):
    """SMS verification code for phone verification."""
    
    __tablename__ = "sms_verification_codes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # User reference
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="sms_verification_codes")
    
    # Phone number
    phone_number = Column(String(20), nullable=False, index=True)
    
    # Verification code (6 digits)
    code = Column(String(6), nullable=False)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Attempts counter (max 3 attempts)
    attempts = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expiration to 10 minutes from now
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    @property
    def is_expired(self) -> bool:
        """Check if code is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if code is valid (not used, not expired, and attempts < 3)."""
        return not self.is_used and not self.is_expired and self.attempts < 3
    
    def __repr__(self) -> str:
        return f"<SMSVerificationCode {self.code} for {self.phone_number}>"
