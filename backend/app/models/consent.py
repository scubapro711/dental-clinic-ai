"""
Patient Consent Management
For תיקון 13 (Amendment 13) compliance
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from uuid import uuid4
from app.core.database import Base


class ConsentType(str, Enum):
    """Types of consent required."""
    DATA_PROCESSING = "data_processing"  # עיבוד נתונים כללי
    MARKETING = "marketing"  # שיווק ופרסום
    THIRD_PARTY_SHARING = "third_party_sharing"  # שיתוף עם צד שלישי
    MEDICAL_RECORDS = "medical_records"  # תיק רפואי דיגיטלי
    TELEGRAM_BOT = "telegram_bot"  # שימוש בבוט טלגרם
    AI_AGENTS = "ai_agents"  # שימוש בסוכני AI
    ECLAIMS = "eclaims"  # שליחת תביעות לקופות חולים
    RESEARCH = "research"  # מחקר (אנונימי)


class ConsentStatus(str, Enum):
    """Consent status."""
    PENDING = "pending"  # ממתין להסכמה
    GRANTED = "granted"  # הוסכם
    DENIED = "denied"  # נדחה
    REVOKED = "revoked"  # בוטל
    EXPIRED = "expired"  # פג תוקף


class PatientConsent(Base):
    """
    Patient consent records.
    
    Tracks all consents given by patients for data processing.
    Required for תיקון 13 compliance.
    """
    __tablename__ = "patient_consents"
    
    id = Column(Integer, primary_key=True)
    # Odoo patient ID (no FK - Odoo is external system)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Consent details
    consent_type = Column(String(50), nullable=False)  # ConsentType enum
    status = Column(String(20), nullable=False, default=ConsentStatus.PENDING)
    
    # Timestamps
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime)
    expires_at = Column(DateTime)  # Optional expiration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    consent_text = Column(Text)  # The actual consent text shown to user
    consent_version = Column(String(20))  # Version of consent text
    
    # Notes
    notes = Column(Text)
    
    def __repr__(self):
        return f"<PatientConsent {self.patient_id} - {self.consent_type}: {self.status}>"
    
    @property
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        if self.status != ConsentStatus.GRANTED:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def grant(self, ip_address: str = None, user_agent: str = None):
        """Grant consent."""
        self.status = ConsentStatus.GRANTED
        self.granted_at = datetime.utcnow()
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def revoke(self, reason: str = None):
        """Revoke consent."""
        self.status = ConsentStatus.REVOKED
        self.revoked_at = datetime.utcnow()
        if reason:
            self.notes = f"{self.notes or ''}\nRevoked: {reason}"
    
    def deny(self, reason: str = None):
        """Deny consent."""
        self.status = ConsentStatus.DENIED
        if reason:
            self.notes = f"{self.notes or ''}\nDenied: {reason}"


class DataSubjectRequestType(str, Enum):
    """Types of data subject requests (DSR)."""
    ACCESS = "access"  # זכות עיון - Right to access
    RECTIFICATION = "rectification"  # זכות תיקון - Right to rectification
    ERASURE = "erasure"  # זכות מחיקה - Right to erasure (right to be forgotten)
    PORTABILITY = "portability"  # זכות להעברה - Right to data portability
    OBJECT = "object"  # זכות להתנגד - Right to object
    RESTRICT = "restrict"  # זכות להגבלה - Right to restriction of processing


class DataSubjectRequestStatus(str, Enum):
    """DSR request status."""
    PENDING = "pending"  # ממתין לטיפול
    IN_PROGRESS = "in_progress"  # בטיפול
    COMPLETED = "completed"  # הושלם
    REJECTED = "rejected"  # נדחה
    CANCELLED = "cancelled"  # בוטל


class DataSubjectRequest(Base):
    """
    Data Subject Rights (DSR) requests.
    
    Handles patient requests for:
    - Access to their data
    - Rectification of incorrect data
    - Erasure (right to be forgotten)
    - Data portability
    - Objection to processing
    - Restriction of processing
    """
    __tablename__ = "data_subject_requests"
    
    id = Column(Integer, primary_key=True)
    # Odoo patient ID (no FK - Odoo is external system)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Request details
    request_type = Column(String(50), nullable=False)  # DataSubjectRequestType enum
    status = Column(String(20), nullable=False, default=DataSubjectRequestStatus.PENDING)
    
    # Description
    description = Column(Text)  # Patient's description of request
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    due_date = Column(DateTime)  # Must respond within 30 days (תיקון 13)
    
    # Processing
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # DPO or admin
    response = Column(Text)  # Response to patient
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Files (for data export)
    export_file_path = Column(String(500))  # Path to exported data file
    
    # Notes
    notes = Column(Text)
    
    # Relationship to assigned user
    assigned_user = relationship("User")
    
    def __repr__(self):
        return f"<DSR {self.patient_id} - {self.request_type}: {self.status}>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if request is overdue (>30 days)."""
        if self.status in [DataSubjectRequestStatus.COMPLETED, DataSubjectRequestStatus.REJECTED]:
            return False
        
        if self.due_date and self.due_date < datetime.utcnow():
            return True
        
        return False
    
    def complete(self, response: str, export_file_path: str = None):
        """Mark request as completed."""
        self.status = DataSubjectRequestStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.response = response
        if export_file_path:
            self.export_file_path = export_file_path
    
    def reject(self, reason: str):
        """Reject request."""
        self.status = DataSubjectRequestStatus.REJECTED
        self.completed_at = datetime.utcnow()
        self.response = reason


class PrivacyPolicyAcceptance(Base):
    """
    Track privacy policy acceptances.
    
    Required to prove that patients have read and accepted the privacy policy.
    """
    __tablename__ = "privacy_policy_acceptances"
    
    id = Column(Integer, primary_key=True)
    # Odoo patient ID (no FK - Odoo is external system)
    patient_id = Column(Integer, nullable=False, index=True)
    
    # Policy details
    policy_version = Column(String(20), nullable=False)
    policy_url = Column(String(500))
    
    # Acceptance
    accepted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    def __repr__(self):
        return f"<PrivacyAcceptance {self.patient_id} - v{self.policy_version}>"


# Add relationships to Patient model
# (This should be added to the existing Patient model)
"""
class Patient(Base):
    # ... existing fields ...
    
    # תיקון 13 relationships
    consents = relationship("PatientConsent", back_populates="patient")
    dsr_requests = relationship("DataSubjectRequest", back_populates="patient")
    privacy_acceptances = relationship("PrivacyPolicyAcceptance", back_populates="patient")
"""
