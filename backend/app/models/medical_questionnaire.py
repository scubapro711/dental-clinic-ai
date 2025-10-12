"""
Medical Questionnaire Model.

Stores patient medical history and health questionnaires.

Used by Sarah agent for:
- Risk factor identification
- Treatment planning
- Proactive health alerts
- Contraindication detection

Part of comprehensive patient health management.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum, ForeignKey, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class QuestionnaireStatus(str, enum.Enum):
    """Status of questionnaire."""
    DRAFT = "draft"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    OUTDATED = "outdated"


class RiskLevel(str, enum.Enum):
    """Risk level assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MedicalQuestionnaire(Base):
    """
    Medical Questionnaire Model.
    
    Stores comprehensive medical history for patients.
    """
    
    __tablename__ = "medical_questionnaires"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Organization (multi-tenant)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Patient
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    patient_name = Column(String(200), nullable=True)
    
    # Questionnaire metadata
    status = Column(SQLEnum(QuestionnaireStatus), nullable=False, default=QuestionnaireStatus.DRAFT, index=True)
    version = Column(Integer, nullable=False, default=1)  # Questionnaire version
    completed_date = Column(DateTime, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_date = Column(DateTime, nullable=True)
    
    # Medical History
    # Stored as JSON for flexibility
    medical_conditions = Column(JSON, nullable=True)  # Array of conditions
    medications = Column(JSON, nullable=True)  # Array of medications
    allergies = Column(JSON, nullable=True)  # Array of allergies
    previous_surgeries = Column(JSON, nullable=True)  # Array of surgeries
    family_history = Column(JSON, nullable=True)  # Family medical history
    
    # Dental-specific
    dental_anxiety = Column(Boolean, default=False)
    dental_anxiety_level = Column(Integer, nullable=True)  # 1-10
    previous_dental_issues = Column(JSON, nullable=True)
    gum_disease_history = Column(Boolean, default=False)
    teeth_grinding = Column(Boolean, default=False)
    jaw_pain = Column(Boolean, default=False)
    
    # Lifestyle
    smoking = Column(Boolean, default=False)
    smoking_frequency = Column(String(50), nullable=True)  # e.g., "1 pack/day"
    alcohol = Column(Boolean, default=False)
    alcohol_frequency = Column(String(50), nullable=True)
    
    # Pregnancy/Women's Health
    is_pregnant = Column(Boolean, default=False)
    pregnancy_trimester = Column(Integer, nullable=True)  # 1, 2, or 3
    is_breastfeeding = Column(Boolean, default=False)
    
    # Emergency Contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)
    
    # Sarah AI Risk Assessment
    sarah_risk_level = Column(SQLEnum(RiskLevel), nullable=True, index=True)
    sarah_risk_score = Column(Integer, nullable=True)  # 0-100
    sarah_risk_factors = Column(JSON, nullable=True)  # Array of identified risk factors
    sarah_contraindications = Column(JSON, nullable=True)  # Array of treatment contraindications
    sarah_recommendations = Column(JSON, nullable=True)  # Array of recommendations
    sarah_last_analysis_date = Column(DateTime, nullable=True)
    sarah_confidence = Column(Integer, nullable=True)  # 0-100
    
    # Notes
    patient_notes = Column(Text, nullable=True)  # Patient's additional notes
    clinician_notes = Column(Text, nullable=True)  # Clinician's notes
    
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
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_updated_by_user = relationship("User", foreign_keys=[last_updated_by])
    
    def __repr__(self):
        return f"<MedicalQuestionnaire(patient={self.patient_name}, status={self.status}, risk={self.sarah_risk_level})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "patient_id": str(self.patient_id),
            "patient_name": self.patient_name,
            "status": self.status.value,
            "version": self.version,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "reviewed_by": str(self.reviewed_by) if self.reviewed_by else None,
            "reviewed_date": self.reviewed_date.isoformat() if self.reviewed_date else None,
            "medical_conditions": self.medical_conditions,
            "medications": self.medications,
            "allergies": self.allergies,
            "previous_surgeries": self.previous_surgeries,
            "family_history": self.family_history,
            "dental_anxiety": self.dental_anxiety,
            "dental_anxiety_level": self.dental_anxiety_level,
            "previous_dental_issues": self.previous_dental_issues,
            "gum_disease_history": self.gum_disease_history,
            "teeth_grinding": self.teeth_grinding,
            "jaw_pain": self.jaw_pain,
            "smoking": self.smoking,
            "smoking_frequency": self.smoking_frequency,
            "alcohol": self.alcohol,
            "alcohol_frequency": self.alcohol_frequency,
            "is_pregnant": self.is_pregnant,
            "pregnancy_trimester": self.pregnancy_trimester,
            "is_breastfeeding": self.is_breastfeeding,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "emergency_contact_relationship": self.emergency_contact_relationship,
            "sarah_risk_level": self.sarah_risk_level.value if self.sarah_risk_level else None,
            "sarah_risk_score": self.sarah_risk_score,
            "sarah_risk_factors": self.sarah_risk_factors,
            "sarah_contraindications": self.sarah_contraindications,
            "sarah_recommendations": self.sarah_recommendations,
            "sarah_last_analysis_date": self.sarah_last_analysis_date.isoformat() if self.sarah_last_analysis_date else None,
            "sarah_confidence": self.sarah_confidence,
            "patient_notes": self.patient_notes,
            "clinician_notes": self.clinician_notes,
            "created_by": str(self.created_by) if self.created_by else None,
            "last_updated_by": str(self.last_updated_by) if self.last_updated_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @property
    def has_high_risk_conditions(self) -> bool:
        """Check if patient has high-risk medical conditions."""
        if not self.medical_conditions:
            return False
        
        high_risk_conditions = [
            "diabetes", "heart disease", "hypertension", "bleeding disorder",
            "hemophilia", "cancer", "hiv", "aids", "hepatitis", "kidney disease",
            "liver disease", "stroke", "heart attack", "pacemaker", "blood thinner"
        ]
        
        for condition in self.medical_conditions:
            condition_lower = condition.get("name", "").lower()
            if any(risk in condition_lower for risk in high_risk_conditions):
                return True
        
        return False
    
    @property
    def has_dental_anxiety(self) -> bool:
        """Check if patient has significant dental anxiety."""
        return self.dental_anxiety and (self.dental_anxiety_level or 0) >= 7
    
    @property
    def requires_antibiotic_prophylaxis(self) -> bool:
        """Check if patient requires antibiotic prophylaxis."""
        if not self.medical_conditions:
            return False
        
        prophylaxis_conditions = [
            "heart valve", "prosthetic valve", "endocarditis", "congenital heart",
            "heart transplant", "joint replacement", "artificial joint"
        ]
        
        for condition in self.medical_conditions:
            condition_lower = condition.get("name", "").lower()
            if any(pc in condition_lower for pc in prophylaxis_conditions):
                return True
        
        return False
    
    @property
    def has_bleeding_risk(self) -> bool:
        """Check if patient has bleeding risk."""
        if not self.medications:
            return False
        
        blood_thinners = [
            "warfarin", "coumadin", "aspirin", "plavix", "clopidogrel",
            "heparin", "xarelto", "eliquis", "pradaxa"
        ]
        
        for medication in self.medications:
            med_lower = medication.get("name", "").lower()
            if any(bt in med_lower for bt in blood_thinners):
                return True
        
        return False


# Common medical conditions for reference
COMMON_MEDICAL_CONDITIONS = [
    "Diabetes",
    "Hypertension (High Blood Pressure)",
    "Heart Disease",
    "Asthma",
    "Arthritis",
    "Osteoporosis",
    "Thyroid Disorder",
    "Kidney Disease",
    "Liver Disease",
    "Cancer",
    "HIV/AIDS",
    "Hepatitis",
    "Bleeding Disorder",
    "Stroke",
    "Epilepsy",
    "Mental Health Condition",
]

# Common medications
COMMON_MEDICATIONS = [
    "Aspirin",
    "Warfarin (Coumadin)",
    "Metformin",
    "Lisinopril",
    "Atorvastatin (Lipitor)",
    "Levothyroxine",
    "Omeprazole",
    "Albuterol",
    "Metoprolol",
    "Amlodipine",
]

# Common allergies
COMMON_ALLERGIES = [
    "Penicillin",
    "Latex",
    "Lidocaine",
    "Codeine",
    "Ibuprofen",
    "Aspirin",
    "Sulfa drugs",
    "Local anesthetics",
]

