"""
Pilot Application Model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status enum"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    WAITLIST = "waitlist"


class PilotApplication(Base):
    """Pilot Application model for controlled pilot entry"""
    __tablename__ = "pilot_applications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Step 1: Basic Info
    clinic_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    
    # Step 2: Clinic Details
    clinic_size = Column(String(50), nullable=False)  # solo, small, medium, large
    monthly_patients = Column(String(50), nullable=False)  # 0-50, 51-200, 201-500, 500+
    current_software = Column(String(255), nullable=True)
    team_size = Column(String(50), nullable=False)  # 1-3, 4-10, 11-25, 25+
    
    # Step 3: AI Readiness
    ai_experience = Column(String(50), nullable=False)  # none, basic, intermediate, advanced
    primary_goal = Column(String(100), nullable=False)  # efficiency, patient-experience, revenue, automation
    timeline = Column(String(50), nullable=False)  # immediate, 1-3-months, 3-6-months, 6+-months
    budget = Column(String(50), nullable=True)  # 0-500, 500-1000, 1000-2500, 2500+
    
    # Step 4: Commitment
    willing_to_provide_feedback = Column(Boolean, default=False)
    willing_to_be_referenced = Column(Boolean, default=False)
    agreed_to_terms = Column(Boolean, default=False, nullable=False)
    
    # Application Management
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    score = Column(Integer, nullable=True)  # Qualification score (0-100)
    notes = Column(Text, nullable=True)  # Admin notes
    reviewed_by = Column(Integer, nullable=True)  # User ID of reviewer
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PilotApplication {self.id}: {self.clinic_name} - {self.status}>"

    def calculate_score(self) -> int:
        """
        Calculate qualification score based on application data
        Returns: Score from 0-100
        """
        score = 0
        
        # Clinic size (20 points)
        size_scores = {"solo": 10, "small": 15, "medium": 20, "large": 18}
        score += size_scores.get(self.clinic_size, 0)
        
        # Monthly patients (20 points)
        patient_scores = {"0-50": 10, "51-200": 15, "201-500": 20, "500+": 18}
        score += patient_scores.get(self.monthly_patients, 0)
        
        # Team size (15 points)
        team_scores = {"1-3": 10, "4-10": 15, "11-25": 13, "25+": 12}
        score += team_scores.get(self.team_size, 0)
        
        # AI experience (15 points)
        ai_scores = {"none": 8, "basic": 12, "intermediate": 15, "advanced": 14}
        score += ai_scores.get(self.ai_experience, 0)
        
        # Primary goal (10 points)
        goal_scores = {
            "efficiency": 10,
            "patient-experience": 9,
            "revenue": 8,
            "automation": 10
        }
        score += goal_scores.get(self.primary_goal, 0)
        
        # Timeline (10 points)
        timeline_scores = {
            "immediate": 10,
            "1-3-months": 8,
            "3-6-months": 6,
            "6+-months": 4
        }
        score += timeline_scores.get(self.timeline, 0)
        
        # Budget (10 points)
        if self.budget:
            budget_scores = {
                "0-500": 5,
                "500-1000": 7,
                "1000-2500": 10,
                "2500+": 10
            }
            score += budget_scores.get(self.budget, 0)
        
        return min(score, 100)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "clinic_name": self.clinic_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "clinic_size": self.clinic_size,
            "monthly_patients": self.monthly_patients,
            "current_software": self.current_software,
            "team_size": self.team_size,
            "ai_experience": self.ai_experience,
            "primary_goal": self.primary_goal,
            "timeline": self.timeline,
            "budget": self.budget,
            "willing_to_provide_feedback": self.willing_to_provide_feedback,
            "willing_to_be_referenced": self.willing_to_be_referenced,
            "agreed_to_terms": self.agreed_to_terms,
            "status": self.status.value if self.status else None,
            "score": self.score,
            "notes": self.notes,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

