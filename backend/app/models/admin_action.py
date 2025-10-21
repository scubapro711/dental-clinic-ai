"""
Admin Action Model

Audit log for all Super Admin actions for security, compliance, and accountability.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Enum as SQLEnum
from app.core.database_types import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


class AdminActionType(str, Enum):
    """Types of admin actions."""
    CREATE_ORGANIZATION = "create_organization"
    UPDATE_ORGANIZATION = "update_organization"
    SUSPEND_ORGANIZATION = "suspend_organization"
    DELETE_ORGANIZATION = "delete_organization"
    EXTEND_TRIAL = "extend_trial"
    CHANGE_PLAN = "change_plan"
    IMPERSONATE_USER = "impersonate_user"
    RESET_PASSWORD = "reset_password"
    CHANGE_USER_ROLE = "change_user_role"
    UPDATE_SUBSCRIPTION = "update_subscription"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    REFUND_PAYMENT = "refund_payment"
    VIEW_SENSITIVE_DATA = "view_sensitive_data"


class AdminAction(Base):
    """
    Admin Action Model
    
    Audit log for all Super Admin actions to ensure accountability,
    security, and compliance with regulations.
    
    Attributes:
        id: Primary key
        admin_user_id: Foreign key to users table (the admin who performed the action)
        action_type: Type of action performed
        target_type: Type of target entity (organization, user, subscription)
        target_id: ID of the target entity
        action_details: Additional details about the action (JSON)
        ip_address: IP address of the admin
        user_agent: User agent string
        created_at: Timestamp when action was performed
    
    Indexes:
        - (admin_user_id) for admin-specific queries
        - (target_type, target_id) for target-specific queries
        - (action_type) for action-type queries
        - (created_at) for time-based queries
    
    Example:
        # Log organization suspension
        action = AdminAction(
            admin_user_id=1,
            action_type=AdminActionType.SUSPEND_ORGANIZATION,
            target_type="organization",
            target_id=42,
            action_details={
                "reason": "Payment failed for 3 months",
                "previous_status": "active",
                "new_status": "suspended"
            },
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )
    """
    
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(SQLEnum(AdminActionType), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=False)
    action_details = Column(JSONB, default={})
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_admin_actions_admin_user', 'admin_user_id'),
        Index('ix_admin_actions_target', 'target_type', 'target_id'),
        Index('ix_admin_actions_type', 'action_type'),
        Index('ix_admin_actions_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin={self.admin_user_id}, type={self.action_type}, target={self.target_type}:{self.target_id})>"

