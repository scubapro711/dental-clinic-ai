"""
Plan Configuration Model

Dynamic plan configuration for Super Admin management.
Allows Super Admin to create, update, and manage subscription plans.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Numeric, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class PlanConfiguration(Base):
    """
    Plan Configuration Model
    
    Stores dynamic plan configurations that can be managed by Super Admin.
    Replaces hardcoded PLAN_PRICING in stripe_service.py.
    
    Attributes:
        id: Primary key
        plan_key: Unique plan identifier (e.g., "starter", "professional", "enterprise")
        name: Display name (e.g., "DentaFlow Starter")
        description: Plan description
        amount: Monthly price in minor units (e.g., 163300 for ₪1,633.00)
        currency: Currency code (e.g., "ILS")
        billing_interval: Billing interval (e.g., "month", "year")
        trial_days: Default trial period in days
        max_users: Maximum users allowed (null = unlimited)
        max_patients: Maximum patients allowed (null = unlimited)
        features: JSON array of feature keys
        is_active: Whether plan is currently available
        is_default: Whether this is the default plan
        sort_order: Display order (lower = first)
        stripe_product_id: Stripe product ID (nullable, created on-demand)
        stripe_price_id: Stripe price ID (nullable, created on-demand)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "plan_configurations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plan identification
    plan_key = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "starter"
    name = Column(String(255), nullable=False)  # e.g., "DentaFlow Starter"
    description = Column(Text, nullable=True)
    
    # Pricing
    amount = Column(Numeric(10, 2), nullable=False)  # Monthly price
    currency = Column(String(3), default="ILS", nullable=False)
    billing_interval = Column(String(20), default="month", nullable=False)  # "month" or "year"
    
    # Trial
    trial_days = Column(Integer, default=30, nullable=False)
    
    # Limits
    max_users = Column(Integer, nullable=True)  # null = unlimited
    max_patients = Column(Integer, nullable=True)  # null = unlimited
    
    # Features (JSON array of feature keys)
    features = Column(JSON, nullable=False, default=list)
    # Example: ["basic_ai", "patient_portal", "email_support"]
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Stripe integration (created on-demand)
    stripe_product_id = Column(String(255), nullable=True, unique=True)
    stripe_price_id = Column(String(255), nullable=True, unique=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PlanConfiguration(key={self.plan_key}, name={self.name}, amount={self.amount})>"
    
    @property
    def amount_display(self) -> str:
        """Format amount for display"""
        return f"{self.currency} {self.amount:,.2f}"
    
    @property
    def limits_display(self) -> dict:
        """Get limits as a display-friendly dict"""
        return {
            "users": self.max_users if self.max_users else "Unlimited",
            "patients": self.max_patients if self.max_patients else "Unlimited"
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "plan_key": self.plan_key,
            "name": self.name,
            "description": self.description,
            "amount": float(self.amount),
            "currency": self.currency,
            "billing_interval": self.billing_interval,
            "trial_days": self.trial_days,
            "max_users": self.max_users,
            "max_patients": self.max_patients,
            "features": self.features,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "sort_order": self.sort_order,
            "amount_display": self.amount_display,
            "limits_display": self.limits_display,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

