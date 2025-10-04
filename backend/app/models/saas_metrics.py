"""
SaaS Metrics Models for Super Admin Dashboard

These models track platform-level metrics for multi-tenant management:
- Subscriptions and billing
- Usage metrics per organization
- System costs and profitability
- Customer health scores
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class BillingCycle(str, enum.Enum):
    """Billing cycle options."""

    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status options."""

    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class Subscription(Base):
    """Subscription model for tracking billing."""

    __tablename__ = "subscriptions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Subscription details
    plan = Column(String(50), nullable=False)  # basic, professional, enterprise
    price = Column(Numeric(10, 2), nullable=False)  # Monthly price
    billing_cycle = Column(Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIAL)

    # Billing periods
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)

    # Payment
    last_payment_date = Column(DateTime, nullable=True)
    last_payment_amount = Column(Numeric(10, 2), nullable=True)
    payment_method = Column(String(50), nullable=True)  # credit_card, bank_transfer, etc.

    # Stripe integration
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", backref="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription {self.plan} - {self.status}>"


class UsageMetric(Base):
    """Daily usage metrics per organization."""

    __tablename__ = "usage_metrics"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Date
    metric_date = Column(Date, nullable=False, index=True)

    # Usage metrics
    api_calls = Column(Integer, default=0, nullable=False)
    storage_gb = Column(Numeric(10, 2), default=0, nullable=False)
    active_users = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    appointments_created = Column(Integer, default=0, nullable=False)

    # Agent usage
    alex_messages = Column(Integer, default=0, nullable=False)
    cfo_queries = Column(Integer, default=0, nullable=False)
    admin_tasks = Column(Integer, default=0, nullable=False)

    # Performance
    avg_response_time_ms = Column(Integer, nullable=True)
    error_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    organization = relationship("Organization", backref="usage_metrics")

    # Unique constraint
    __table_args__ = (
        {"schema": None},
    )

    def __repr__(self) -> str:
        return f"<UsageMetric {self.metric_date} - Org {self.organization_id}>"


class CostCategory(str, enum.Enum):
    """Cost category options."""

    INFRASTRUCTURE = "infrastructure"  # AWS, servers, databases
    AI_LLM = "ai_llm"  # OpenAI API costs
    SUPPORT = "support"  # Customer support costs
    DEVELOPMENT = "development"  # Development costs
    MARKETING = "marketing"  # Marketing and sales
    OTHER = "other"


class SystemCost(Base):
    """System costs for profitability tracking."""

    __tablename__ = "system_costs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Date
    cost_date = Column(Date, nullable=False, index=True)

    # Cost details
    category = Column(Enum(CostCategory), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)

    # Attribution (optional - for per-clinic costs)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True
    )

    # Metadata
    vendor = Column(String(255), nullable=True)  # AWS, OpenAI, etc.
    invoice_id = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    organization = relationship("Organization", backref="costs")

    def __repr__(self) -> str:
        return f"<SystemCost {self.category} - ${self.amount}>"


class CustomerHealthScore(Base):
    """Customer health scores for churn prediction."""

    __tablename__ = "customer_health_scores"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Date
    score_date = Column(Date, nullable=False, index=True)

    # Health score (0-100)
    overall_score = Column(Integer, nullable=False)

    # Component scores
    usage_score = Column(Integer, nullable=False)  # Based on daily active usage
    engagement_score = Column(Integer, nullable=False)  # Based on feature adoption
    satisfaction_score = Column(Integer, nullable=True)  # Based on NPS/feedback
    payment_score = Column(Integer, nullable=False)  # Based on payment history

    # Risk indicators
    is_at_risk = Column(Boolean, default=False, nullable=False)
    churn_probability = Column(Numeric(5, 2), nullable=True)  # 0-100%
    risk_factors = Column(Text, nullable=True)  # JSON array of risk factors

    # Opportunities
    upsell_opportunity = Column(Boolean, default=False, nullable=False)
    upsell_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    organization = relationship("Organization", backref="health_scores")

    def __repr__(self) -> str:
        return f"<CustomerHealthScore {self.overall_score} - Org {self.organization_id}>"


class SupportTicket(Base):
    """Support tickets for tracking customer issues."""

    __tablename__ = "support_tickets"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )

    # Ticket details
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")  # low, medium, high, urgent
    status = Column(String(20), nullable=False, default="open")  # open, in_progress, resolved, closed
    category = Column(String(50), nullable=True)  # technical, billing, feature_request, etc.

    # Assignment
    assigned_to = Column(String(255), nullable=True)
    
    # Resolution
    resolved_at = Column(DateTime, nullable=True)
    resolution_time_hours = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    organization = relationship("Organization", backref="support_tickets")

    def __repr__(self) -> str:
        return f"<SupportTicket {self.subject} - {self.status}>"
