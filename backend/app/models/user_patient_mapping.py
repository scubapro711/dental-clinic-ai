"""
User-Patient Mapping Model

Maps DentaFlow users to Odoo patients for efficient data retrieval.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Index
from app.core.database_types import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class UserPatientMapping(Base):
    """
    Maps DentaFlow users to Odoo patients.
    
    This table provides a fast lookup between our internal user IDs
    and Odoo patient IDs, eliminating the need for email-based searches.
    
    Attributes:
        id: Primary key
        user_id: DentaFlow user UUID
        odoo_patient_id: Odoo res.partner ID
        email: User email (for reference and validation)
        full_name: Patient full name (cached from Odoo)
        is_active: Whether the mapping is active
        created_at: When the mapping was created
        updated_at: When the mapping was last updated
        last_synced_at: When data was last synced with Odoo
    """
    
    __tablename__ = "user_patient_mappings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User identification
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
    
    # Odoo patient identification
    odoo_patient_id = Column(Integer, nullable=False, index=True)
    
    # Cached data for quick reference
    email = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_id_active', 'user_id', 'is_active'),
        Index('idx_odoo_patient_id_active', 'odoo_patient_id', 'is_active'),
        Index('idx_email_active', 'email', 'is_active'),
    )
    
    def __repr__(self):
        return f"<UserPatientMapping(user_id={self.user_id}, odoo_patient_id={self.odoo_patient_id}, email={self.email})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'odoo_patient_id': self.odoo_patient_id,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
        }

