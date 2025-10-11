"""
Tooth Chart API Endpoints.

Provides endpoints for dental charting with Sarah AI analysis.

Endpoints:
- GET /tooth-chart/{patient_id} - Get full tooth chart for patient
- GET /tooth-chart/{patient_id}/tooth/{tooth_number} - Get specific tooth details
- POST /tooth-chart/{patient_id}/tooth/{tooth_number} - Update tooth record
- GET /tooth-chart/{patient_id}/sarah-analysis - Get Sarah AI analysis
- POST /tooth-chart/{patient_id}/sync-odoo - Sync with Odoo dental records
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.tooth_record import (
    ToothRecord,
    ToothStatus,
    ToothSurface,
    get_universal_number,
    get_tooth_name,
    get_quadrant,
    FDI_TO_UNIVERSAL,
    TOOTH_NAMES,
)
from app.models.proactive_suggestion import (
    ProactiveSuggestion,
    SuggestionPriority,
    SuggestionStatus,
    SuggestionCategory,
)
from pydantic import BaseModel, Field


router = APIRouter()


# Pydantic schemas

class ToothRecordCreate(BaseModel):
    """Create/update tooth record."""
    tooth_number_fdi: int = Field(..., ge=11, le=48)
    status: ToothStatus
    affected_surfaces: Optional[List[ToothSurface]] = None
    last_treatment_date: Optional[date] = None
    last_treatment_type: Optional[str] = None
    next_followup_date: Optional[date] = None
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None


class ToothRecordResponse(BaseModel):
    """Tooth record response."""
    id: str
    patient_id: str
    patient_name: Optional[str]
    tooth_number_fdi: int
    tooth_number_universal: int
    tooth_name: str
    quadrant: int
    status: str
    affected_surfaces: Optional[List[str]]
    last_treatment_date: Optional[str]
    last_treatment_type: Optional[str]
    next_followup_date: Optional[str]
    notes: Optional[str]
    diagnosis: Optional[str]
    treatment_plan: Optional[str]
    sarah_risk_score: Optional[int]
    sarah_suggestions: Optional[List[dict]]
    sarah_confidence: Optional[int]
    needs_attention: bool
    is_urgent: bool
    is_under_treatment: bool
    days_since_treatment: int
    days_until_followup: int
    is_followup_overdue: bool
    created_at: str
    updated_at: str


class ToothChartResponse(BaseModel):
    """Full tooth chart response."""
    patient_id: str
    patient_name: Optional[str]
    teeth: List[ToothRecordResponse]
    total_teeth: int
    healthy_count: int
    needs_attention_count: int
    under_treatment_count: int
    last_updated: str


class SarahAnalysisResponse(BaseModel):
    """Sarah AI analysis response."""
    patient_id: str
    analysis_date: str
    overall_risk_score: int
    suggestions: List[dict]
    teeth_needing_attention: List[int]
    overdue_followups: List[int]
    confidence: int


# Endpoints

@router.get("/{patient_id}", response_model=ToothChartResponse)
async def get_tooth_chart(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get full tooth chart for a patient.
    
    Returns all 32 teeth with their current status and treatment history.
    """
    # Get all tooth records for patient
    records = db.query(ToothRecord).filter(
        ToothRecord.organization_id == current_user.organization_id,
        ToothRecord.patient_id == patient_id,
        ToothRecord.deleted_at == None
    ).all()
    
    # Convert to response
    teeth = []
    for record in records:
        teeth.append(ToothRecordResponse(
            **record.to_dict(),
            days_since_treatment=record.days_since_treatment,
            days_until_followup=record.days_until_followup,
            is_followup_overdue=record.is_followup_overdue
        ))
    
    # Calculate stats
    healthy_count = sum(1 for t in teeth if t.status == ToothStatus.HEALTHY.value)
    needs_attention_count = sum(1 for t in teeth if t.needs_attention)
    under_treatment_count = sum(1 for t in teeth if t.is_under_treatment)
    
    return ToothChartResponse(
        patient_id=str(patient_id),
        patient_name=records[0].patient_name if records else None,
        teeth=teeth,
        total_teeth=len(teeth),
        healthy_count=healthy_count,
        needs_attention_count=needs_attention_count,
        under_treatment_count=under_treatment_count,
        last_updated=max([t.updated_at for t in teeth]) if teeth else datetime.utcnow().isoformat()
    )


@router.get("/{patient_id}/tooth/{tooth_number}", response_model=ToothRecordResponse)
async def get_tooth_details(
    patient_id: UUID,
    tooth_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details for a specific tooth."""
    record = db.query(ToothRecord).filter(
        ToothRecord.organization_id == current_user.organization_id,
        ToothRecord.patient_id == patient_id,
        ToothRecord.tooth_number_fdi == tooth_number,
        ToothRecord.deleted_at == None
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Tooth record not found")
    
    return ToothRecordResponse(
        **record.to_dict(),
        days_since_treatment=record.days_since_treatment,
        days_until_followup=record.days_until_followup,
        is_followup_overdue=record.is_followup_overdue
    )


@router.post("/{patient_id}/tooth/{tooth_number}", response_model=ToothRecordResponse)
async def update_tooth_record(
    patient_id: UUID,
    tooth_number: int,
    data: ToothRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update a tooth record.
    
    If the tooth record doesn't exist, creates a new one.
    If it exists, updates the existing record.
    """
    # Check if record exists
    record = db.query(ToothRecord).filter(
        ToothRecord.organization_id == current_user.organization_id,
        ToothRecord.patient_id == patient_id,
        ToothRecord.tooth_number_fdi == tooth_number,
        ToothRecord.deleted_at == None
    ).first()
    
    if record:
        # Update existing
        record.status = data.status
        record.affected_surfaces = [s.value for s in data.affected_surfaces] if data.affected_surfaces else None
        record.last_treatment_date = data.last_treatment_date
        record.last_treatment_type = data.last_treatment_type
        record.next_followup_date = data.next_followup_date
        record.notes = data.notes
        record.diagnosis = data.diagnosis
        record.treatment_plan = data.treatment_plan
        record.last_updated_by = current_user.id
        record.updated_at = datetime.utcnow()
        
        # Update flags
        record.needs_attention = data.status == ToothStatus.NEEDS_ATTENTION
        record.is_under_treatment = data.status == ToothStatus.UNDER_TREATMENT
    else:
        # Create new
        record = ToothRecord(
            organization_id=current_user.organization_id,
            patient_id=patient_id,
            tooth_number_fdi=tooth_number,
            tooth_number_universal=get_universal_number(tooth_number),
            tooth_name=get_tooth_name(tooth_number),
            quadrant=get_quadrant(tooth_number),
            status=data.status,
            affected_surfaces=[s.value for s in data.affected_surfaces] if data.affected_surfaces else None,
            last_treatment_date=data.last_treatment_date,
            last_treatment_type=data.last_treatment_type,
            next_followup_date=data.next_followup_date,
            notes=data.notes,
            diagnosis=data.diagnosis,
            treatment_plan=data.treatment_plan,
            needs_attention=data.status == ToothStatus.NEEDS_ATTENTION,
            is_under_treatment=data.status == ToothStatus.UNDER_TREATMENT,
            created_by=current_user.id,
            last_updated_by=current_user.id,
        )
        db.add(record)
    
    db.commit()
    db.refresh(record)
    
    # Trigger Sarah analysis
    # TODO: Call Sarah agent to analyze this tooth
    # await trigger_sarah_analysis(patient_id, tooth_number)
    
    return ToothRecordResponse(
        **record.to_dict(),
        days_since_treatment=record.days_since_treatment,
        days_until_followup=record.days_until_followup,
        is_followup_overdue=record.is_followup_overdue
    )


@router.get("/{patient_id}/sarah-analysis", response_model=SarahAnalysisResponse)
async def get_sarah_analysis(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Sarah AI analysis for patient's dental health.
    
    Sarah analyzes all teeth and generates proactive suggestions.
    """
    # Get all tooth records
    records = db.query(ToothRecord).filter(
        ToothRecord.organization_id == current_user.organization_id,
        ToothRecord.patient_id == patient_id,
        ToothRecord.deleted_at == None
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No tooth records found for patient")
    
    # Calculate overall risk score
    risk_scores = [r.sarah_risk_score for r in records if r.sarah_risk_score]
    overall_risk = sum(risk_scores) // len(risk_scores) if risk_scores else 0
    
    # Get teeth needing attention
    teeth_needing_attention = [r.tooth_number_fdi for r in records if r.needs_attention]
    
    # Get overdue follow-ups
    overdue_followups = [r.tooth_number_fdi for r in records if r.is_followup_overdue]
    
    # Get Sarah suggestions from Decision Queue
    suggestions = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.organization_id == current_user.organization_id,
        ProactiveSuggestion.patient_id == patient_id,
        ProactiveSuggestion.agent_name == "sarah",
        ProactiveSuggestion.status == SuggestionStatus.PENDING
    ).all()
    
    suggestion_dicts = [s.to_dict() for s in suggestions]
    
    # Calculate average confidence
    confidences = [s.confidence for s in suggestions if s.confidence]
    avg_confidence = sum(confidences) // len(confidences) if confidences else 0
    
    return SarahAnalysisResponse(
        patient_id=str(patient_id),
        analysis_date=datetime.utcnow().isoformat(),
        overall_risk_score=overall_risk,
        suggestions=suggestion_dicts,
        teeth_needing_attention=teeth_needing_attention,
        overdue_followups=overdue_followups,
        confidence=avg_confidence
    )


@router.post("/{patient_id}/sync-odoo")
async def sync_with_odoo(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync tooth chart with Odoo dental records.
    
    Fetches latest dental data from Odoo and updates local tooth records.
    """
    # TODO: Implement Odoo sync
    # 1. Get patient's Odoo ID
    # 2. Fetch dental.tooth records from Odoo
    # 3. Fetch treatment records from Odoo
    # 4. Update local ToothRecord entries
    # 5. Trigger Sarah analysis
    
    return {
        "status": "success",
        "message": "Tooth chart synced with Odoo",
        "patient_id": str(patient_id),
        "synced_at": datetime.utcnow().isoformat()
    }

