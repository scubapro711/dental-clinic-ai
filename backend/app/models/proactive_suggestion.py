"""
Proactive Suggestion Model.

Stores AI-generated suggestions that require user decision/approval.
Part of the Decision Queue system for agentic/proactive experience.

Examples:
- "Sarah suggests scheduling follow-up for patient X"
- "Marcus identified revenue optimization opportunity"
- "Alex recommends sending payment reminder"
- "Sophia detected inventory low stock alert"
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SuggestionPriority(str, enum.Enum):
    """Priority levels for suggestions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SuggestionStatus(str, enum.Enum):
    """Status of suggestion."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    DISMISSED = "dismissed"


class SuggestionCategory(str, enum.Enum):
    """Category of suggestion."""
    APPOINTMENT = "appointment"
    TREATMENT = "treatment"
    PAYMENT = "payment"
    FOLLOW_UP = "follow_up"
    INVENTORY = "inventory"
    STAFF = "staff"
    MARKETING = "marketing"
    OPTIMIZATION = "optimization"
    ALERT = "alert"
    OTHER = "other"


class ProactiveSuggestion(Base):
    """
    Proactive Suggestion Model.
    
    Represents an AI-generated suggestion that requires user decision.
    Part of the Decision Queue for transparent agentic experience.
    """
    
    __tablename__ = "proactive_suggestions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Organization (multi-tenant)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Agent who generated this suggestion
    agent_name = Column(String(50), nullable=False, index=True)  # alex, sarah, marcus, sophia
    
    # Suggestion details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(SQLEnum(SuggestionCategory), nullable=False, index=True)
    priority = Column(SQLEnum(SuggestionPriority), nullable=False, default=SuggestionPriority.MEDIUM, index=True)
    
    # Status
    status = Column(SQLEnum(SuggestionStatus), nullable=False, default=SuggestionStatus.PENDING, index=True)
    
    # Actions (JSON array of possible actions)
    # Example: [{"label": "Approve", "action": "approve"}, {"label": "Reject", "action": "reject"}]
    actions = Column(JSON, nullable=True)
    
    # Metadata (JSON object with additional context)
    # Example: {"patient_id": 123, "appointment_date": "2025-10-15", "confidence": 0.89}
    suggestion_metadata = Column(JSON, nullable=True)
    
    # Confidence score (0.0 - 1.0)
    confidence = Column(Integer, nullable=True)  # Store as integer 0-100 for simplicity
    
    # Related entities (optional)
    patient_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    appointment_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    conversation_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Decision tracking
    decided_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    decision_notes = Column(Text, nullable=True)
    
    # Execution tracking
    executed = Column(Boolean, default=False, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    execution_result = Column(JSON, nullable=True)
    
    # Learning feedback
    feedback_provided = Column(Boolean, default=False, nullable=False)
    feedback_rating = Column(Integer, nullable=True)  # 1-5 stars
    feedback_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)  # Suggestions can expire
    
    # Relationships
    organization = relationship("Organization", back_populates="proactive_suggestions")
    decided_by_user = relationship("User", foreign_keys=[decided_by])
    
    def __repr__(self):
        return f"<ProactiveSuggestion(id={self.id}, agent={self.agent_name}, title='{self.title}', status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "agent_name": self.agent_name,
            "title": self.title,
            "message": self.message,
            "category": self.category.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "actions": self.actions,
            "metadata": self.suggestion_metadata,
            "confidence": self.confidence,
            "patient_id": str(self.patient_id) if self.patient_id else None,
            "appointment_id": str(self.appointment_id) if self.appointment_id else None,
            "conversation_id": str(self.conversation_id) if self.conversation_id else None,
            "decided_by": str(self.decided_by) if self.decided_by else None,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "decision_notes": self.decision_notes,
            "executed": self.executed,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_result": self.execution_result,
            "feedback_provided": self.feedback_provided,
            "feedback_rating": self.feedback_rating,
            "feedback_notes": self.feedback_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @property
    def is_expired(self) -> bool:
        """Check if suggestion has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_pending(self) -> bool:
        """Check if suggestion is pending decision."""
        return self.status == SuggestionStatus.PENDING and not self.is_expired
    
    @property
    def age_hours(self) -> float:
        """Get age of suggestion in hours."""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600

