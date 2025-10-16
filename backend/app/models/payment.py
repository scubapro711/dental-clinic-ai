"""
Payment Model - SaaS Billing

Tracks individual payments for subscriptions.
Synced with Stripe payment intents.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enum matching Stripe statuses"""
    SUCCEEDED = "succeeded"  # Payment successful
    PENDING = "pending"  # Payment processing
    FAILED = "failed"  # Payment failed
    CANCELED = "canceled"  # Payment canceled
    REQUIRES_ACTION = "requires_action"  # Requires customer action (3D Secure)


class Payment(Base):
    """
    Payment Model
    
    Represents individual payments for subscriptions.
    Synced with Stripe payment intents.
    
    Attributes:
        id: Primary key
        subscription_id: FK to Subscription
        stripe_payment_intent_id: Stripe payment intent ID
        stripe_charge_id: Stripe charge ID (nullable)
        amount: Payment amount
        currency: Currency code (ILS)
        status: Payment status
        payment_method: Payment method type
        payment_method_details: Additional payment method info
        failure_code: Failure code if payment failed
        failure_message: Failure message if payment failed
        created_at: Creation timestamp
    """
    
    __tablename__ = "payments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Stripe integration
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=False, index=True)
    stripe_charge_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="ILS", nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Payment method
    payment_method = Column(String(50), nullable=True)  # e.g., "card", "bank_transfer"
    payment_method_details = Column(Text, nullable=True)  # JSON string with details
    
    # Failure information
    failure_code = Column(String(100), nullable=True)
    failure_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    succeeded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, subscription={self.subscription_id}, amount={self.amount}, status={self.status})>"
    
    @property
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == PaymentStatus.SUCCEEDED
    
    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING
    
    @property
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED

