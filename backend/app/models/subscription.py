"""
Subscription Model - SaaS Billing

Manages clinic subscriptions to DentaFlow SaaS platform.
Integrates with Stripe for payment processing.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey, Numeric
from app.core.database_types import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum matching Stripe statuses"""
    TRIALING = "trialing"  # In 30-day trial period
    ACTIVE = "active"  # Active paid subscription
    PAST_DUE = "past_due"  # Payment failed, grace period
    CANCELED = "canceled"  # Canceled by user
    UNPAID = "unpaid"  # Payment failed, no grace period
    INCOMPLETE = "incomplete"  # Initial payment pending
    INCOMPLETE_EXPIRED = "incomplete_expired"  # Initial payment failed


class PlanTier(str, enum.Enum):
    """Subscription plan tiers"""
    STARTER = "starter"  # ₪1,633/month - 1 user, 100 patients
    PROFESSIONAL = "professional"  # ₪3,070/month - 5 users, 500 patients
    ENTERPRISE = "enterprise"  # ₪6,141/month - unlimited


class Subscription(Base):
    """
    Subscription Model
    
    Represents a clinic's subscription to DentaFlow SaaS.
    Synced with Stripe subscriptions.
    
    Attributes:
        id: Primary key
        organization_id: FK to Organization
        stripe_subscription_id: Stripe subscription ID
        stripe_customer_id: Stripe customer ID
        plan_tier: Subscription tier (starter/professional/enterprise)
        status: Current subscription status
        current_period_start: Start of current billing period
        current_period_end: End of current billing period
        trial_start: Trial period start (nullable)
        trial_end: Trial period end (nullable)
        cancel_at_period_end: Whether to cancel at period end
        canceled_at: When subscription was canceled (nullable)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "subscriptions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One subscription per organization
        index=True
    )
    
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plan_configurations.id", ondelete="RESTRICT"),
        nullable=True,  # Nullable for backward compatibility
        index=True
    )
    
    # Stripe integration
    stripe_subscription_id = Column(String(255), unique=True, nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    
    # Subscription details
    plan_tier = Column(Enum(PlanTier), nullable=False, default=PlanTier.STARTER)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    
    # Billing period
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Trial period
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    
    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Pricing (stored for historical record)
    amount = Column(Numeric(10, 2), nullable=False)  # Monthly amount in ILS
    currency = Column(String(3), default="ILS", nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    plan = relationship("PlanConfiguration", foreign_keys=[plan_id])
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, org={self.organization_id}, tier={self.plan_tier}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active (including trial)"""
        return self.status in [SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE]
    
    @property
    def is_in_trial(self) -> bool:
        """Check if subscription is in trial period"""
        return self.status == SubscriptionStatus.TRIALING
    
    @property
    def days_until_renewal(self) -> int:
        """Calculate days until next renewal"""
        if not self.current_period_end:
            return 0
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def plan_limits(self) -> dict:
        """Get plan limits based on tier"""
        limits = {
            PlanTier.STARTER: {
                "max_users": 1,
                "max_patients": 100,
                "features": ["basic_ai", "patient_portal", "email_support"]
            },
            PlanTier.PROFESSIONAL: {
                "max_users": 5,
                "max_patients": 500,
                "features": ["advanced_ai", "patient_portal", "sms_notifications", "priority_support", "analytics"]
            },
            PlanTier.ENTERPRISE: {
                "max_users": None,  # Unlimited
                "max_patients": None,  # Unlimited
                "features": ["all_features", "dedicated_support", "custom_integrations", "white_label"]
            }
        }
        return limits.get(self.plan_tier, limits[PlanTier.STARTER])

