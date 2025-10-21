"""
Pilot Applications API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.core.database import get_db
from app.models.pilot_application import PilotApplication, ApplicationStatus
from app.core.auth import get_current_user
from app.api.dependencies import require_super_admin
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class PilotApplicationCreate(BaseModel):
    """Schema for creating a pilot application"""
    clinic_name: str
    contact_name: str
    email: EmailStr
    phone: str
    clinic_size: str
    monthly_patients: str
    current_software: Optional[str] = None
    team_size: str
    ai_experience: str
    primary_goal: str
    timeline: str
    budget: Optional[str] = None
    willing_to_provide_feedback: bool = False
    willing_to_be_referenced: bool = False
    agreed_to_terms: bool


class PilotApplicationUpdate(BaseModel):
    """Schema for updating a pilot application (admin only)"""
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    score: Optional[int] = None


class PilotApplicationResponse(BaseModel):
    """Schema for pilot application response"""
    id: int
    clinic_name: str
    contact_name: str
    email: str
    phone: str
    clinic_size: str
    monthly_patients: str
    current_software: Optional[str]
    team_size: str
    ai_experience: str
    primary_goal: str
    timeline: str
    budget: Optional[str]
    willing_to_provide_feedback: bool
    willing_to_be_referenced: bool
    agreed_to_terms: bool
    status: str
    score: Optional[int]
    notes: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=PilotApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_pilot_application(
    application: PilotApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new pilot application (public endpoint)
    """
    # Check if email already applied
    existing = db.query(PilotApplication).filter(
        PilotApplication.email == application.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An application with this email already exists"
        )
    
    # Create new application
    db_application = PilotApplication(**application.dict())
    
    # Calculate qualification score
    db_application.score = db_application.calculate_score()
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # TODO: Send email notification to admin
    # TODO: Send confirmation email to applicant
    
    return db_application


@router.get("/", response_model=List[PilotApplicationResponse])
async def list_pilot_applications(
    status_filter: Optional[ApplicationStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    List all pilot applications (super admin only)
    """
    query = db.query(PilotApplication)
    
    if status_filter:
        query = query.filter(PilotApplication.status == status_filter)
    
    # Order by score (desc) and created_at (desc)
    query = query.order_by(
        PilotApplication.score.desc(),
        PilotApplication.created_at.desc()
    )
    
    applications = query.offset(skip).limit(limit).all()
    return applications


@router.get("/{application_id}", response_model=PilotApplicationResponse)
async def get_pilot_application(
    application_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific pilot application (super admin only)
    """
    application = db.query(PilotApplication).filter(
        PilotApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.patch("/{application_id}", response_model=PilotApplicationResponse)
async def update_pilot_application(
    application_id: int,
    update_data: PilotApplicationUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update a pilot application (super admin only)
    """
    application = db.query(PilotApplication).filter(
        PilotApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(application, field, value)
    
    # Set reviewer info
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(application)
    
    # TODO: Send email notification to applicant about status change
    
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pilot_application(
    application_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a pilot application (super admin only)
    """
    application = db.query(PilotApplication).filter(
        PilotApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(application)
    db.commit()
    
    return None


@router.get("/stats/summary")
async def get_application_stats(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get pilot application statistics (super admin only)
    """
    total = db.query(PilotApplication).count()
    pending = db.query(PilotApplication).filter(
        PilotApplication.status == ApplicationStatus.PENDING
    ).count()
    approved = db.query(PilotApplication).filter(
        PilotApplication.status == ApplicationStatus.APPROVED
    ).count()
    rejected = db.query(PilotApplication).filter(
        PilotApplication.status == ApplicationStatus.REJECTED
    ).count()
    
    # Average score
    from sqlalchemy import func
    avg_score = db.query(func.avg(PilotApplication.score)).scalar() or 0
    
    # Top applicants (score >= 80)
    top_applicants = db.query(PilotApplication).filter(
        PilotApplication.score >= 80,
        PilotApplication.status == ApplicationStatus.PENDING
    ).count()
    
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "average_score": round(avg_score, 1),
        "top_applicants": top_applicants
    }

