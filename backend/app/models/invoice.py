"""
Invoice Model - SaaS Billing

Tracks subscription invoices.
Synced with Stripe invoices.

Note: This is for SaaS billing invoices, not patient treatment invoices.
Patient invoices are managed in Odoo.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status enum matching Stripe statuses"""
    DRAFT = "draft"  # Invoice created but not finalized
    OPEN = "open"  # Invoice finalized, awaiting payment
    PAID = "paid"  # Invoice paid
    VOID = "void"  # Invoice voided
    UNCOLLECTIBLE = "uncollectible"  # Marked as uncollectible


class Invoice(Base):
    """
    Invoice Model (SaaS Billing)
    
    Represents subscription invoices for clinic billing.
    Synced with Stripe invoices.
    
    Attributes:
        id: Primary key
        subscription_id: FK to Subscription
        stripe_invoice_id: Stripe invoice ID
        invoice_number: Human-readable invoice number
        amount_due: Total amount due
        amount_paid: Amount paid
        amount_remaining: Amount remaining
        currency: Currency code (ILS)
        status: Invoice status
        description: Invoice description
        invoice_pdf: URL to PDF invoice
        hosted_invoice_url: Stripe hosted invoice URL
        due_date: Payment due date
        paid_at: When invoice was paid (nullable)
        created_at: Creation timestamp
    """
    
    __tablename__ = "invoices"
    
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
    stripe_invoice_id = Column(String(255), unique=True, nullable=False, index=True)
    invoice_number = Column(String(100), unique=True, nullable=True)  # e.g., "INV-2025-001"
    
    # Invoice amounts
    amount_due = Column(Numeric(10, 2), nullable=False)
    amount_paid = Column(Numeric(10, 2), default=0, nullable=False)
    amount_remaining = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="ILS", nullable=False)
    
    # Status
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    
    # Description
    description = Column(Text, nullable=True)
    
    # PDF and URLs
    invoice_pdf = Column(String(500), nullable=True)  # URL to PDF
    hosted_invoice_url = Column(String(500), nullable=True)  # Stripe hosted page
    
    # Dates
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number={self.invoice_number}, amount={self.amount_due}, status={self.status})>"
    
    @property
    def is_paid(self) -> bool:
        """Check if invoice is paid"""
        return self.status == InvoiceStatus.PAID
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if not self.due_date or self.is_paid:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_until_due(self) -> int:
        """Calculate days until due date"""
        if not self.due_date or self.is_paid:
            return 0
        delta = self.due_date - datetime.utcnow()
        return delta.days

