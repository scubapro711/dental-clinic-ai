"""
Treatment Category Model.

Represents treatment categories for dental procedures, enabling
structured classification, financial analysis, and Marcus AI insights.

Categories include:
- Preventive (cleanings, exams, fluoride)
- Restorative (fillings, crowns, bridges)
- Cosmetic (whitening, veneers, bonding)
- Orthodontic (braces, aligners, retainers)
- Endodontic (root canals, apicoectomy)
- Periodontic (gum treatment, scaling, grafts)
- Prosthodontic (dentures, implants)
- Oral Surgery (extractions, wisdom teeth)
- Pediatric (child-specific treatments)
- Emergency (urgent care, pain relief)

Each category tracks:
- Financial metrics (revenue, costs, profitability)
- Volume metrics (procedures, patients)
- Marcus AI analysis (insights, recommendations, trends)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
import enum

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
)
from app.core.database_types import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TreatmentCategoryType(str, enum.Enum):
    """Treatment category types."""
    
    PREVENTIVE = "preventive"
    RESTORATIVE = "restorative"
    COSMETIC = "cosmetic"
    ORTHODONTIC = "orthodontic"
    ENDODONTIC = "endodontic"
    PERIODONTIC = "periodontic"
    PROSTHODONTIC = "prosthodontic"
    ORAL_SURGERY = "oral_surgery"
    PEDIATRIC = "pediatric"
    EMERGENCY = "emergency"
    OTHER = "other"


class TreatmentCategory(Base):
    """Treatment category model."""
    
    __tablename__ = "treatment_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Organization (multi-tenant)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Basic info
    name = Column(String(255), nullable=False)  # e.g., "Root Canal Therapy"
    category_type = Column(Enum(TreatmentCategoryType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Codes
    ada_code = Column(String(20), nullable=True, index=True)  # ADA procedure code
    insurance_code = Column(String(50), nullable=True)
    
    # Financial data (aggregate)
    average_price = Column(Float, nullable=True)  # Average price charged
    average_cost = Column(Float, nullable=True)  # Average cost to provide
    average_profit_margin = Column(Float, nullable=True)  # %
    
    total_revenue_ytd = Column(Float, default=0.0)  # Year-to-date revenue
    total_revenue_mtd = Column(Float, default=0.0)  # Month-to-date revenue
    total_procedures_ytd = Column(Integer, default=0)
    total_procedures_mtd = Column(Integer, default=0)
    
    # Metrics
    average_duration_minutes = Column(Integer, nullable=True)
    success_rate_percent = Column(Float, nullable=True)
    patient_satisfaction_score = Column(Float, nullable=True)  # 1-5
    
    # Marcus AI analysis
    marcus_analyzed = Column(Boolean, default=False)
    marcus_analysis_date = Column(DateTime, nullable=True)
    marcus_profitability_score = Column(Integer, nullable=True)  # 0-100
    marcus_demand_score = Column(Integer, nullable=True)  # 0-100
    marcus_recommendations = Column(JSON, nullable=True)  # List[Dict]
    marcus_insights = Column(JSON, nullable=True)  # Dict
    marcus_alerts = Column(JSON, nullable=True)  # List[Dict]
    marcus_confidence = Column(Integer, nullable=True)  # 0-100
    
    # Trends (Marcus tracking)
    revenue_trend = Column(String(20), nullable=True)  # "increasing", "decreasing", "stable"
    volume_trend = Column(String(20), nullable=True)
    profitability_trend = Column(String(20), nullable=True)
    
    # Flags
    is_high_value = Column(Boolean, default=False)  # High revenue generator
    is_high_demand = Column(Boolean, default=False)  # Frequently requested
    is_underutilized = Column(Boolean, default=False)  # Low volume despite profitability
    is_loss_leader = Column(Boolean, default=False)  # Low/negative margin
    requires_specialist = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at = Column(DateTime, nullable=True)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    last_updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="treatment_categories")
    
    def __repr__(self) -> str:
        return f"<TreatmentCategory {self.name} ({self.category_type.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "name": self.name,
            "category_type": self.category_type.value,
            "description": self.description,
            "ada_code": self.ada_code,
            "insurance_code": self.insurance_code,
            "average_price": self.average_price,
            "average_cost": self.average_cost,
            "average_profit_margin": self.average_profit_margin,
            "total_revenue_ytd": self.total_revenue_ytd,
            "total_revenue_mtd": self.total_revenue_mtd,
            "total_procedures_ytd": self.total_procedures_ytd,
            "total_procedures_mtd": self.total_procedures_mtd,
            "average_duration_minutes": self.average_duration_minutes,
            "success_rate_percent": self.success_rate_percent,
            "patient_satisfaction_score": self.patient_satisfaction_score,
            "marcus_analyzed": self.marcus_analyzed,
            "marcus_analysis_date": self.marcus_analysis_date.isoformat() if self.marcus_analysis_date else None,
            "marcus_profitability_score": self.marcus_profitability_score,
            "marcus_demand_score": self.marcus_demand_score,
            "marcus_recommendations": self.marcus_recommendations,
            "marcus_insights": self.marcus_insights,
            "marcus_alerts": self.marcus_alerts,
            "marcus_confidence": self.marcus_confidence,
            "revenue_trend": self.revenue_trend,
            "volume_trend": self.volume_trend,
            "profitability_trend": self.profitability_trend,
            "is_high_value": self.is_high_value,
            "is_high_demand": self.is_high_demand,
            "is_underutilized": self.is_underutilized,
            "is_loss_leader": self.is_loss_leader,
            "requires_specialist": self.requires_specialist,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @property
    def profitability_status(self) -> str:
        """Get profitability status."""
        if not self.average_profit_margin:
            return "unknown"
        
        if self.average_profit_margin >= 50:
            return "excellent"
        elif self.average_profit_margin >= 30:
            return "good"
        elif self.average_profit_margin >= 10:
            return "fair"
        elif self.average_profit_margin >= 0:
            return "poor"
        else:
            return "loss"
    
    @property
    def demand_status(self) -> str:
        """Get demand status based on volume."""
        if self.total_procedures_mtd >= 50:
            return "very_high"
        elif self.total_procedures_mtd >= 20:
            return "high"
        elif self.total_procedures_mtd >= 10:
            return "medium"
        elif self.total_procedures_mtd >= 5:
            return "low"
        else:
            return "very_low"
    
    @property
    def needs_attention(self) -> bool:
        """Check if category needs attention."""
        return (
            self.is_loss_leader or
            self.is_underutilized or
            (self.revenue_trend == "decreasing") or
            (self.volume_trend == "decreasing")
        )

