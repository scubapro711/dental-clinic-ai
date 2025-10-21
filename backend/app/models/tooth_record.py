"""
Tooth Record Model.

Stores dental records for individual teeth, including:
- Status (healthy, cavity, filling, crown, etc.)
- Treatment history
- Notes and observations
- Integration with Odoo dental records

Part of the Tooth Chart feature for Sarah agent proactive analysis.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum, ForeignKey, JSON, Date
from app.core.database_types import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from app.core.database import Base


class ToothStatus(str, enum.Enum):
    """Status of a tooth."""
    HEALTHY = "healthy"
    CAVITY = "cavity"
    FILLING = "filling"
    CROWN = "crown"
    ROOT_CANAL = "root_canal"
    EXTRACTION = "extraction"
    MISSING = "missing"
    IMPLANT = "implant"
    BRIDGE = "bridge"
    NEEDS_ATTENTION = "needs_attention"
    UNDER_TREATMENT = "under_treatment"


class ToothSurface(str, enum.Enum):
    """Tooth surfaces for detailed charting."""
    OCCLUSAL = "occlusal"  # Chewing surface
    MESIAL = "mesial"  # Front surface (towards midline)
    DISTAL = "distal"  # Back surface (away from midline)
    BUCCAL = "buccal"  # Cheek-side surface
    LINGUAL = "lingual"  # Tongue-side surface
    INCISAL = "incisal"  # Biting edge (for front teeth)


class ToothRecord(Base):
    """
    Tooth Record Model.
    
    Stores detailed information about individual teeth for dental charting.
    Integrates with Odoo dental records and provides data for Sarah agent analysis.
    """
    
    __tablename__ = "tooth_records"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Organization (multi-tenant)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Patient
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Can be Odoo ID or internal
    patient_name = Column(String(200), nullable=True)  # Cached for quick display
    
    # Tooth identification
    tooth_number_fdi = Column(Integer, nullable=False, index=True)  # FDI notation (11-48)
    tooth_number_universal = Column(Integer, nullable=True)  # Universal notation (1-32)
    tooth_name = Column(String(100), nullable=True)  # e.g., "Central Incisor", "First Molar"
    quadrant = Column(Integer, nullable=False)  # 1-4 (FDI quadrants)
    
    # Current status
    status = Column(SQLEnum(ToothStatus), nullable=False, default=ToothStatus.HEALTHY, index=True)
    
    # Affected surfaces (JSON array)
    # Example: ["occlusal", "mesial"] for a filling on top and front surfaces
    affected_surfaces = Column(JSON, nullable=True)
    
    # Treatment details
    last_treatment_date = Column(Date, nullable=True, index=True)
    last_treatment_type = Column(String(200), nullable=True)  # e.g., "Composite filling", "Porcelain crown"
    next_followup_date = Column(Date, nullable=True, index=True)  # When to check again
    
    # Clinical notes
    notes = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    
    # Odoo integration
    odoo_tooth_id = Column(Integer, nullable=True, index=True)  # Link to Odoo dental.tooth record
    odoo_treatment_ids = Column(JSON, nullable=True)  # Array of Odoo treatment IDs
    
    # Sarah AI analysis
    sarah_last_analysis_date = Column(DateTime, nullable=True)
    sarah_risk_score = Column(Integer, nullable=True)  # 0-100, higher = more attention needed
    sarah_suggestions = Column(JSON, nullable=True)  # Array of AI suggestions
    sarah_confidence = Column(Integer, nullable=True)  # 0-100
    
    # Flags
    needs_attention = Column(Boolean, default=False, nullable=False, index=True)
    is_urgent = Column(Boolean, default=False, nullable=False)
    is_under_treatment = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_updated_by_user = relationship("User", foreign_keys=[last_updated_by])
    
    def __repr__(self):
        return f"<ToothRecord(patient={self.patient_name}, tooth={self.tooth_number_fdi}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "patient_id": str(self.patient_id),
            "patient_name": self.patient_name,
            "tooth_number_fdi": self.tooth_number_fdi,
            "tooth_number_universal": self.tooth_number_universal,
            "tooth_name": self.tooth_name,
            "quadrant": self.quadrant,
            "status": self.status.value,
            "affected_surfaces": self.affected_surfaces,
            "last_treatment_date": self.last_treatment_date.isoformat() if self.last_treatment_date else None,
            "last_treatment_type": self.last_treatment_type,
            "next_followup_date": self.next_followup_date.isoformat() if self.next_followup_date else None,
            "notes": self.notes,
            "diagnosis": self.diagnosis,
            "treatment_plan": self.treatment_plan,
            "odoo_tooth_id": self.odoo_tooth_id,
            "odoo_treatment_ids": self.odoo_treatment_ids,
            "sarah_last_analysis_date": self.sarah_last_analysis_date.isoformat() if self.sarah_last_analysis_date else None,
            "sarah_risk_score": self.sarah_risk_score,
            "sarah_suggestions": self.sarah_suggestions,
            "sarah_confidence": self.sarah_confidence,
            "needs_attention": self.needs_attention,
            "is_urgent": self.is_urgent,
            "is_under_treatment": self.is_under_treatment,
            "created_by": str(self.created_by) if self.created_by else None,
            "last_updated_by": str(self.last_updated_by) if self.last_updated_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @property
    def days_since_treatment(self) -> int:
        """Calculate days since last treatment."""
        if not self.last_treatment_date:
            return 0
        return (date.today() - self.last_treatment_date).days
    
    @property
    def days_until_followup(self) -> int:
        """Calculate days until next follow-up."""
        if not self.next_followup_date:
            return 0
        return (self.next_followup_date - date.today()).days
    
    @property
    def is_followup_overdue(self) -> bool:
        """Check if follow-up is overdue."""
        if not self.next_followup_date:
            return False
        return date.today() > self.next_followup_date


# FDI to Universal conversion mapping
FDI_TO_UNIVERSAL = {
    18: 1, 17: 2, 16: 3, 15: 4, 14: 5, 13: 6, 12: 7, 11: 8,
    21: 9, 22: 10, 23: 11, 24: 12, 25: 13, 26: 14, 27: 15, 28: 16,
    38: 17, 37: 18, 36: 19, 35: 20, 34: 21, 33: 22, 32: 23, 31: 24,
    48: 25, 47: 26, 46: 27, 45: 28, 44: 29, 43: 30, 42: 31, 41: 32,
}

# Tooth names by FDI number
TOOTH_NAMES = {
    # Upper right (quadrant 1)
    11: 'Central Incisor', 12: 'Lateral Incisor', 13: 'Canine', 14: 'First Premolar',
    15: 'Second Premolar', 16: 'First Molar', 17: 'Second Molar', 18: 'Third Molar',
    # Upper left (quadrant 2)
    21: 'Central Incisor', 22: 'Lateral Incisor', 23: 'Canine', 24: 'First Premolar',
    25: 'Second Premolar', 26: 'First Molar', 27: 'Second Molar', 28: 'Third Molar',
    # Lower left (quadrant 3)
    31: 'Central Incisor', 32: 'Lateral Incisor', 33: 'Canine', 34: 'First Premolar',
    35: 'Second Premolar', 36: 'First Molar', 37: 'Second Molar', 38: 'Third Molar',
    # Lower right (quadrant 4)
    41: 'Central Incisor', 42: 'Lateral Incisor', 43: 'Canine', 44: 'First Premolar',
    45: 'Second Premolar', 46: 'First Molar', 47: 'Second Molar', 48: 'Third Molar',
}


def get_universal_number(fdi_number: int) -> int:
    """Convert FDI notation to Universal notation."""
    return FDI_TO_UNIVERSAL.get(fdi_number, 0)


def get_tooth_name(fdi_number: int) -> str:
    """Get tooth name from FDI number."""
    return TOOTH_NAMES.get(fdi_number, "Unknown")


def get_quadrant(fdi_number: int) -> int:
    """Get quadrant from FDI number."""
    return int(str(fdi_number)[0])

