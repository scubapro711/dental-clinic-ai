"""
Usage Metric Model

Tracks usage metrics for each organization to monitor consumption,
enforce limits, and provide analytics for the Super Admin Dashboard.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index, Enum as SQLEnum, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


class UsageMetricType(str, Enum):
    """Types of usage metrics tracked per organization."""
    AI_CONVERSATIONS = "ai_conversations"
    APPOINTMENTS_BOOKED = "appointments_booked"
    PATIENTS_ADDED = "patients_added"
    ACTIVE_USERS = "active_users"
    STORAGE_USED_MB = "storage_used_mb"
    API_CALLS = "api_calls"
    TELEGRAM_MESSAGES = "telegram_messages"
    SMS_SENT = "sms_sent"
    EMAILS_SENT = "emails_sent"


class UsageMetric(Base):
    """
    Usage Metric Model
    
    Stores daily usage metrics for each organization to track consumption,
    enforce plan limits, and provide analytics.
    
    Attributes:
        id: Primary key
        organization_id: Foreign key to organizations table
        metric_type: Type of metric (AI conversations, appointments, etc.)
        value: Numeric value of the metric
        date: Date of the metric
        metadata: Additional metadata (JSON)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    
    Indexes:
        - (organization_id, date) for efficient org-specific queries
        - (metric_type, date) for efficient metric-type queries
    
    Example:
        # Record AI conversations for an organization
        metric = UsageMetric(
            organization_id=1,
            metric_type=UsageMetricType.AI_CONVERSATIONS,
            value=150,
            date=date.today(),
            metadata={"agent": "alex", "successful": 145, "failed": 5}
        )
    """
    
    __tablename__ = "usage_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(SQLEnum(UsageMetricType), nullable=False)
    value = Column(Integer, nullable=False, default=0)
    date = Column(Date, nullable=False)
    metric_metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_metrics")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_usage_metrics_org_date', 'organization_id', 'date'),
        Index('ix_usage_metrics_type_date', 'metric_type', 'date'),
        Index('ix_usage_metrics_org_type_date', 'organization_id', 'metric_type', 'date'),
    )
    
    def __repr__(self):
        return f"<UsageMetric(id={self.id}, org={self.organization_id}, type={self.metric_type}, value={self.value}, date={self.date})>"

