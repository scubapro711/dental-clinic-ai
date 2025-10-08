"""
Organization Membership model for multi-tenancy.
Links users to organizations with roles and Odoo integration.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrganizationMembership(Base):
    """
    User membership in organization with Odoo link.
    
    This model enables:
    - Multi-tenancy: Users can belong to multiple organizations
    - Role-based access: Different roles per organization
    - Odoo integration: Link to Odoo res.partner records
    
    Roles:
    - organization_role: owner, manager, staff, patient
    - functional_role: dentist, hygienist, receptionist, etc.
    """
    __tablename__ = "organization_memberships"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Roles
    organization_role = Column(String(50), nullable=False)
    """Organization role: owner, manager, staff, patient"""
    
    functional_role = Column(String(50), nullable=True)
    """Functional role: dentist, hygienist, receptionist, etc."""
    
    # Odoo integration
    odoo_partner_id = Column(Integer, nullable=True, index=True)
    """Link to Odoo res.partner record"""
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_org'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<OrganizationMembership("
            f"user_id={self.user_id}, "
            f"organization_id={self.organization_id}, "
            f"role={self.organization_role}"
            f")>"
        )
