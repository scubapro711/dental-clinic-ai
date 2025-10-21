"""
Cost Tracking Model

Tracks infrastructure costs from GCP and allocates them to organizations
for cost analysis and billing purposes.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index, DECIMAL
from app.core.database_types import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class CostTracking(Base):
    """
    Cost Tracking Model
    
    Stores infrastructure costs from GCP Billing API and allocates them
    to organizations for cost analysis, optimization, and billing.
    
    Attributes:
        id: Primary key
        organization_id: Foreign key to organizations (NULL for shared costs)
        service_name: GCP service name (Cloud Run, Cloud SQL, etc.)
        cost_amount: Cost amount in specified currency
        currency: Currency code (USD, ILS, etc.)
        billing_period_start: Start date of billing period
        billing_period_end: End date of billing period
        usage_details: Detailed usage information (JSON)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    
    Indexes:
        - (organization_id, billing_period_start) for org-specific queries
        - (service_name, billing_period_start) for service-specific queries
    
    Example:
        # Record Cloud Run costs for an organization
        cost = CostTracking(
            organization_id=1,
            service_name="Cloud Run",
            cost_amount=45.67,
            currency="USD",
            billing_period_start=date(2025, 10, 1),
            billing_period_end=date(2025, 10, 31),
            usage_details={
                "requests": 1500000,
                "cpu_hours": 120,
                "memory_gb_hours": 240
            }
        )
    """
    
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer, 
        ForeignKey("organizations.id", ondelete="CASCADE"), 
        nullable=True  # NULL for shared/platform costs
    )
    service_name = Column(String(100), nullable=False)
    cost_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default="USD")
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)
    usage_details = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="cost_tracking")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_cost_tracking_org_period', 'organization_id', 'billing_period_start'),
        Index('ix_cost_tracking_service_period', 'service_name', 'billing_period_start'),
        Index('ix_cost_tracking_period', 'billing_period_start', 'billing_period_end'),
    )
    
    def __repr__(self):
        return f"<CostTracking(id={self.id}, org={self.organization_id}, service={self.service_name}, amount={self.cost_amount} {self.currency}, period={self.billing_period_start} to {self.billing_period_end})>"

