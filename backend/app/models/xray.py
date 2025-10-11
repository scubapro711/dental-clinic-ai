"""
X-Ray Model.

Stores dental X-ray images, metadata, and Sarah AI analysis results.

Supports:
- Multiple X-ray types (periapical, bitewing, panoramic, CBCT)
- Image storage (S3/local file system)
- Metadata (date, tooth, findings)
- Sarah AI analysis (findings, recommendations, alerts)
- Integration with treatment planning
- HIPAA compliance (audit trail, encryption)

Part of comprehensive dental records management.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from enum import Enum
import uuid

from app.core.database import Base


class XRayType(str, Enum):
    """X-ray imaging types."""
    PERIAPICAL = "periapical"  # Single tooth root
    BITEWING = "bitewing"  # Crowns of upper/lower teeth
    PANORAMIC = "panoramic"  # Full mouth
    CEPHALOMETRIC = "cephalometric"  # Side profile (orthodontics)
    CBCT = "cbct"  # 3D cone beam CT
    OCCLUSAL = "occlusal"  # Top/bottom of jaw


class XRayQuality(str, Enum):
    """Image quality assessment."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    RETAKE_REQUIRED = "retake_required"


class XRayFindingSeverity(str, Enum):
    """Severity of findings."""
    NORMAL = "normal"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class XRay(Base):
    """X-ray image and analysis model."""
    
    __tablename__ = "xrays"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Reference to Odoo patient
    appointment_id = Column(UUID(as_uuid=True), nullable=True)  # Optional appointment link
    taken_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Staff who took X-ray
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Dentist who reviewed
    
    # Basic info
    patient_name = Column(String(200), nullable=True)  # Denormalized for quick access
    xray_type = Column(SQLEnum(XRayType), nullable=False)
    xray_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    tooth_number = Column(String(10), nullable=True)  # FDI notation (e.g., "11", "36")
    tooth_numbers = Column(JSON, nullable=True)  # Multiple teeth for bitewing/panoramic
    
    # Image storage
    image_url = Column(String(500), nullable=False)  # S3 URL or local path
    image_filename = Column(String(255), nullable=False)
    image_size_bytes = Column(Integer, nullable=True)
    image_format = Column(String(10), nullable=True)  # "jpg", "png", "dicom"
    thumbnail_url = Column(String(500), nullable=True)
    
    # Quality assessment
    quality = Column(SQLEnum(XRayQuality), nullable=True)
    quality_notes = Column(Text, nullable=True)
    needs_retake = Column(Boolean, default=False)
    retake_reason = Column(Text, nullable=True)
    
    # Clinical findings (manual entry)
    findings = Column(Text, nullable=True)  # Dentist's findings
    diagnosis = Column(Text, nullable=True)  # Diagnosis based on X-ray
    treatment_recommended = Column(Text, nullable=True)  # Recommended treatment
    
    # Sarah AI analysis
    sarah_analyzed = Column(Boolean, default=False)
    sarah_analysis_date = Column(DateTime, nullable=True)
    sarah_findings = Column(JSON, nullable=True)  # List of findings with locations
    sarah_severity = Column(SQLEnum(XRayFindingSeverity), nullable=True)
    sarah_recommendations = Column(JSON, nullable=True)  # List of recommendations
    sarah_confidence = Column(Integer, nullable=True)  # 0-100
    sarah_alerts = Column(JSON, nullable=True)  # Proactive alerts generated
    
    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # ["cavity", "root_canal", etc.]
    is_baseline = Column(Boolean, default=False)  # Baseline X-ray for comparison
    compared_with_xray_id = Column(UUID(as_uuid=True), nullable=True)  # Previous X-ray for comparison
    
    # HIPAA compliance
    viewed_by = Column(JSON, nullable=True)  # List of users who viewed
    downloaded_by = Column(JSON, nullable=True)  # List of users who downloaded
    shared_with = Column(JSON, nullable=True)  # External sharing log
    
    # Audit trail
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    organization = relationship("Organization", back_populates="xrays")
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "patient_id": str(self.patient_id),
            "patient_name": self.patient_name,
            "appointment_id": str(self.appointment_id) if self.appointment_id else None,
            "taken_by": str(self.taken_by) if self.taken_by else None,
            "reviewed_by": str(self.reviewed_by) if self.reviewed_by else None,
            "xray_type": self.xray_type.value if self.xray_type else None,
            "xray_date": self.xray_date.isoformat() if self.xray_date else None,
            "tooth_number": self.tooth_number,
            "tooth_numbers": self.tooth_numbers,
            "image_url": self.image_url,
            "image_filename": self.image_filename,
            "image_size_bytes": self.image_size_bytes,
            "image_format": self.image_format,
            "thumbnail_url": self.thumbnail_url,
            "quality": self.quality.value if self.quality else None,
            "quality_notes": self.quality_notes,
            "needs_retake": self.needs_retake,
            "retake_reason": self.retake_reason,
            "findings": self.findings,
            "diagnosis": self.diagnosis,
            "treatment_recommended": self.treatment_recommended,
            "sarah_analyzed": self.sarah_analyzed,
            "sarah_analysis_date": self.sarah_analysis_date.isoformat() if self.sarah_analysis_date else None,
            "sarah_findings": self.sarah_findings,
            "sarah_severity": self.sarah_severity.value if self.sarah_severity else None,
            "sarah_recommendations": self.sarah_recommendations,
            "sarah_confidence": self.sarah_confidence,
            "sarah_alerts": self.sarah_alerts,
            "notes": self.notes,
            "tags": self.tags,
            "is_baseline": self.is_baseline,
            "compared_with_xray_id": str(self.compared_with_xray_id) if self.compared_with_xray_id else None,
            "viewed_by": self.viewed_by,
            "downloaded_by": self.downloaded_by,
            "shared_with": self.shared_with,
            "created_by": str(self.created_by) if self.created_by else None,
            "last_updated_by": str(self.last_updated_by) if self.last_updated_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
    
    @property
    def has_critical_findings(self) -> bool:
        """Check if X-ray has critical findings."""
        return self.sarah_severity == XRayFindingSeverity.CRITICAL
    
    @property
    def requires_immediate_attention(self) -> bool:
        """Check if X-ray requires immediate clinical attention."""
        if self.sarah_severity in [XRayFindingSeverity.SEVERE, XRayFindingSeverity.CRITICAL]:
            return True
        if self.sarah_findings:
            for finding in self.sarah_findings:
                if finding.get("urgent", False):
                    return True
        return False
    
    @property
    def has_comparison(self) -> bool:
        """Check if this X-ray has been compared with a previous one."""
        return self.compared_with_xray_id is not None
    
    def __repr__(self):
        return f"<XRay {self.id} - {self.xray_type.value if self.xray_type else 'unknown'} - Patient {self.patient_id}>"


# Add relationship to Organization model
# This should be added to app/models/organization.py:
# xrays = relationship("XRay", back_populates="organization")

