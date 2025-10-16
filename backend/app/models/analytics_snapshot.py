"""
Analytics Snapshot Model

Stores pre-calculated analytics snapshots for performance optimization.
Daily/weekly/monthly snapshots are calculated in background jobs.
"""

from sqlalchemy import Column, Integer, Date, DateTime, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class SnapshotType(str, Enum):
    """Types of analytics snapshots."""
    DAILY_REVENUE = "daily_revenue"
    WEEKLY_COHORT = "weekly_cohort"
    MONTHLY_CHURN = "monthly_churn"
    USAGE_SUMMARY = "usage_summary"
    COST_SUMMARY = "cost_summary"
    HEALTH_SCORES = "health_scores"


class AnalyticsSnapshot(Base):
    """
    Analytics Snapshot Model
    
    Stores pre-calculated analytics data to improve dashboard performance.
    Background jobs calculate and store snapshots daily/weekly/monthly.
    
    Attributes:
        id: Primary key
        snapshot_type: Type of snapshot (revenue, cohort, churn, etc.)
        snapshot_date: Date of the snapshot
        data: Snapshot data (JSON)
        created_at: Timestamp when snapshot was created
    
    Indexes:
        - (snapshot_type, snapshot_date) for efficient retrieval
    
    Example:
        # Store daily revenue snapshot
        snapshot = AnalyticsSnapshot(
            snapshot_type=SnapshotType.DAILY_REVENUE,
            snapshot_date=date.today(),
            data={
                "mrr": 8165.0,
                "arr": 97980.0,
                "active_subscriptions": 10,
                "trial_subscriptions": 5,
                "growth_rate": 15.5
            }
        )
    """
    
    __tablename__ = "analytics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_type = Column(SQLEnum(SnapshotType), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_analytics_snapshots_type_date', 'snapshot_type', 'snapshot_date'),
        Index('ix_analytics_snapshots_date', 'snapshot_date'),
    )
    
    def __repr__(self):
        return f"<AnalyticsSnapshot(id={self.id}, type={self.snapshot_type}, date={self.snapshot_date})>"

