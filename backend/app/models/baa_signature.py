"""
Business Associate Agreement (BAA) signature model.

Stores electronic signatures for HIPAA BAA agreements.
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, String, ForeignKey, Text
from app.core.database_types import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class BAASignature(Base):
    """Business Associate Agreement signature record."""
    
    __tablename__ = "baa_signatures"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Organization reference (who signed)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    organization = relationship("Organization", back_populates="baa_signatures")
    
    # Signatory details (the person who signed)
    signatory_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    signatory_user = relationship("User")
    signatory_name = Column(String(255), nullable=False)  # Full legal name
    signatory_title = Column(String(255), nullable=False)  # e.g., "Clinic Owner", "CEO"
    signatory_email = Column(String(255), nullable=False)
    
    # Signature data
    signature_method = Column(String(50), default="electronic", nullable=False)  # "electronic" or "digital"
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/device info
    
    # BAA version and content
    baa_version = Column(String(50), default="1.0", nullable=False)
    baa_content_hash = Column(String(64), nullable=False)  # SHA-256 hash of BAA text
    
    # Timestamps
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Audit trail
    consent_text = Column(Text, nullable=False)  # "I have read and agree to..."
    
    def __repr__(self) -> str:
        return f"<BAASignature {self.signatory_name} for {self.organization_id}>"
