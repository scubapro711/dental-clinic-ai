"""
Medical Questionnaire API Endpoints.

Provides endpoints for managing patient medical questionnaires
and Sarah AI risk analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.models.medical_questionnaire import (
    MedicalQuestionnaire,
    QuestionnaireStatus,
    RiskLevel,
    COMMON_MEDICAL_CONDITIONS,
    COMMON_MEDICATIONS,
    COMMON_ALLERGIES,
)
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


# Pydantic schemas

class MedicalCondition(BaseModel):
    """Medical condition."""
    name: str
    diagnosed_date: Optional[str] = None
    notes: Optional[str] = None


class Medication(BaseModel):
    """Medication."""
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    notes: Optional[str] = None


class Allergy(BaseModel):
    """Allergy."""
    name: str
    severity: Optional[str] = None  # "mild", "moderate", "severe"
    reaction: Optional[str] = None
    notes: Optional[str] = None


class Surgery(BaseModel):
    """Previous surgery."""
    name: str
    date: Optional[str] = None
    notes: Optional[str] = None


class QuestionnaireCreate(BaseModel):
    """Create questionnaire request."""
    patient_id: UUID
    patient_name: Optional[str] = None
    medical_conditions: Optional[List[MedicalCondition]] = []
    medications: Optional[List[Medication]] = []
    allergies: Optional[List[Allergy]] = []
    previous_surgeries: Optional[List[Surgery]] = []
    family_history: Optional[dict] = {}
    dental_anxiety: bool = False
    dental_anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    previous_dental_issues: Optional[List[dict]] = []
    gum_disease_history: bool = False
    teeth_grinding: bool = False
    jaw_pain: bool = False
    smoking: bool = False
    smoking_frequency: Optional[str] = None
    alcohol: bool = False
    alcohol_frequency: Optional[str] = None
    is_pregnant: bool = False
    pregnancy_trimester: Optional[int] = Field(None, ge=1, le=3)
    is_breastfeeding: bool = False
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    patient_notes: Optional[str] = None


class QuestionnaireUpdate(BaseModel):
    """Update questionnaire request."""
    medical_conditions: Optional[List[MedicalCondition]] = None
    medications: Optional[List[Medication]] = None
    allergies: Optional[List[Allergy]] = None
    previous_surgeries: Optional[List[Surgery]] = None
    family_history: Optional[dict] = None
    dental_anxiety: Optional[bool] = None
    dental_anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    previous_dental_issues: Optional[List[dict]] = None
    gum_disease_history: Optional[bool] = None
    teeth_grinding: Optional[bool] = None
    jaw_pain: Optional[bool] = None
    smoking: Optional[bool] = None
    smoking_frequency: Optional[str] = None
    alcohol: Optional[bool] = None
    alcohol_frequency: Optional[str] = None
    is_pregnant: Optional[bool] = None
    pregnancy_trimester: Optional[int] = Field(None, ge=1, le=3)
    is_breastfeeding: Optional[bool] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    patient_notes: Optional[str] = None
    clinician_notes: Optional[str] = None
    status: Optional[QuestionnaireStatus] = None


class QuestionnaireResponse(BaseModel):
    """Questionnaire response."""
    id: UUID
    organization_id: UUID
    patient_id: UUID
    patient_name: Optional[str]
    status: str
    version: int
    completed_date: Optional[str]
    reviewed_by: Optional[UUID]
    reviewed_date: Optional[str]
    medical_conditions: Optional[List[dict]]
    medications: Optional[List[dict]]
    allergies: Optional[List[dict]]
    previous_surgeries: Optional[List[dict]]
    family_history: Optional[dict]
    dental_anxiety: bool
    dental_anxiety_level: Optional[int]
    previous_dental_issues: Optional[List[dict]]
    gum_disease_history: bool
    teeth_grinding: bool
    jaw_pain: bool
    smoking: bool
    smoking_frequency: Optional[str]
    alcohol: bool
    alcohol_frequency: Optional[str]
    is_pregnant: bool
    pregnancy_trimester: Optional[int]
    is_breastfeeding: bool
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]
    sarah_risk_level: Optional[str]
    sarah_risk_score: Optional[int]
    sarah_risk_factors: Optional[List[dict]]
    sarah_contraindications: Optional[List[dict]]
    sarah_recommendations: Optional[List[dict]]
    sarah_last_analysis_date: Optional[str]
    sarah_confidence: Optional[int]
    patient_notes: Optional[str]
    clinician_notes: Optional[str]
    created_by: Optional[UUID]
    last_updated_by: Optional[UUID]
    created_at: str
    updated_at: str


class ReferenceDataResponse(BaseModel):
    """Reference data for questionnaire."""
    common_conditions: List[str]
    common_medications: List[str]
    common_allergies: List[str]


# Endpoints

@router.get("/reference-data", response_model=ReferenceDataResponse)
async def get_reference_data():
    """Get reference data for medical questionnaire (common conditions, medications, allergies)."""
    return ReferenceDataResponse(
        common_conditions=COMMON_MEDICAL_CONDITIONS,
        common_medications=COMMON_MEDICATIONS,
        common_allergies=COMMON_ALLERGIES
    )


@router.get("/{patient_id}", response_model=Optional[QuestionnaireResponse])
async def get_questionnaire(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest medical questionnaire for patient."""
    questionnaire = db.query(MedicalQuestionnaire).filter(
        MedicalQuestionnaire.organization_id == current_user.organization_id,
        MedicalQuestionnaire.patient_id == patient_id,
        MedicalQuestionnaire.deleted_at == None
    ).order_by(MedicalQuestionnaire.created_at.desc()).first()
    
    if not questionnaire:
        return None
    
    return QuestionnaireResponse(**questionnaire.to_dict())


@router.post("/{patient_id}", response_model=QuestionnaireResponse, status_code=status.HTTP_201_CREATED)
async def create_questionnaire(
    patient_id: UUID,
    data: QuestionnaireCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new medical questionnaire for patient."""
    
    # Convert Pydantic models to dicts
    medical_conditions = [c.dict() for c in data.medical_conditions] if data.medical_conditions else []
    medications = [m.dict() for m in data.medications] if data.medications else []
    allergies = [a.dict() for a in data.allergies] if data.allergies else []
    previous_surgeries = [s.dict() for s in data.previous_surgeries] if data.previous_surgeries else []
    
    questionnaire = MedicalQuestionnaire(
        organization_id=current_user.organization_id,
        patient_id=patient_id,
        patient_name=data.patient_name,
        status=QuestionnaireStatus.DRAFT,
        medical_conditions=medical_conditions,
        medications=medications,
        allergies=allergies,
        previous_surgeries=previous_surgeries,
        family_history=data.family_history,
        dental_anxiety=data.dental_anxiety,
        dental_anxiety_level=data.dental_anxiety_level,
        previous_dental_issues=data.previous_dental_issues,
        gum_disease_history=data.gum_disease_history,
        teeth_grinding=data.teeth_grinding,
        jaw_pain=data.jaw_pain,
        smoking=data.smoking,
        smoking_frequency=data.smoking_frequency,
        alcohol=data.alcohol,
        alcohol_frequency=data.alcohol_frequency,
        is_pregnant=data.is_pregnant,
        pregnancy_trimester=data.pregnancy_trimester,
        is_breastfeeding=data.is_breastfeeding,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
        emergency_contact_relationship=data.emergency_contact_relationship,
        patient_notes=data.patient_notes,
        created_by=current_user.id,
        last_updated_by=current_user.id
    )
    
    db.add(questionnaire)
    db.commit()
    db.refresh(questionnaire)
    
    return QuestionnaireResponse(**questionnaire.to_dict())


@router.put("/{questionnaire_id}", response_model=QuestionnaireResponse)
async def update_questionnaire(
    questionnaire_id: UUID,
    data: QuestionnaireUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update medical questionnaire."""
    questionnaire = db.query(MedicalQuestionnaire).filter(
        MedicalQuestionnaire.id == questionnaire_id,
        MedicalQuestionnaire.organization_id == current_user.organization_id,
        MedicalQuestionnaire.deleted_at == None
    ).first()
    
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    # Update fields
    update_data = data.dict(exclude_unset=True)
    
    # Convert Pydantic models to dicts
    if "medical_conditions" in update_data and update_data["medical_conditions"]:
        update_data["medical_conditions"] = [c.dict() for c in data.medical_conditions]
    if "medications" in update_data and update_data["medications"]:
        update_data["medications"] = [m.dict() for m in data.medications]
    if "allergies" in update_data and update_data["allergies"]:
        update_data["allergies"] = [a.dict() for a in data.allergies]
    if "previous_surgeries" in update_data and update_data["previous_surgeries"]:
        update_data["previous_surgeries"] = [s.dict() for s in data.previous_surgeries]
    
    for field, value in update_data.items():
        setattr(questionnaire, field, value)
    
    questionnaire.last_updated_by = current_user.id
    questionnaire.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(questionnaire)
    
    return QuestionnaireResponse(**questionnaire.to_dict())


@router.post("/{questionnaire_id}/complete", response_model=QuestionnaireResponse)
async def complete_questionnaire(
    questionnaire_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark questionnaire as completed and trigger Sarah analysis."""
    questionnaire = db.query(MedicalQuestionnaire).filter(
        MedicalQuestionnaire.id == questionnaire_id,
        MedicalQuestionnaire.organization_id == current_user.organization_id,
        MedicalQuestionnaire.deleted_at == None
    ).first()
    
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    questionnaire.status = QuestionnaireStatus.COMPLETED
    questionnaire.completed_date = datetime.utcnow()
    questionnaire.last_updated_by = current_user.id
    
    db.commit()
    
    # Trigger Sarah analysis (TODO: implement async task)
    # For now, return questionnaire
    
    db.refresh(questionnaire)
    return QuestionnaireResponse(**questionnaire.to_dict())


@router.get("/{patient_id}/sarah-analysis")
async def get_sarah_risk_analysis(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Sarah AI risk analysis for patient's medical questionnaire."""
    questionnaire = db.query(MedicalQuestionnaire).filter(
        MedicalQuestionnaire.organization_id == current_user.organization_id,
        MedicalQuestionnaire.patient_id == patient_id,
        MedicalQuestionnaire.deleted_at == None
    ).order_by(MedicalQuestionnaire.created_at.desc()).first()
    
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    # TODO: Implement Sarah risk analysis
    # For now, return basic analysis
    
    return {
        "patient_id": str(patient_id),
        "questionnaire_id": str(questionnaire.id),
        "risk_level": questionnaire.sarah_risk_level.value if questionnaire.sarah_risk_level else "low",
        "risk_score": questionnaire.sarah_risk_score or 0,
        "risk_factors": questionnaire.sarah_risk_factors or [],
        "contraindications": questionnaire.sarah_contraindications or [],
        "recommendations": questionnaire.sarah_recommendations or [],
        "last_analysis_date": questionnaire.sarah_last_analysis_date.isoformat() if questionnaire.sarah_last_analysis_date else None,
        "confidence": questionnaire.sarah_confidence or 0,
        "has_high_risk_conditions": questionnaire.has_high_risk_conditions,
        "has_dental_anxiety": questionnaire.has_dental_anxiety,
        "requires_antibiotic_prophylaxis": questionnaire.requires_antibiotic_prophylaxis,
        "has_bleeding_risk": questionnaire.has_bleeding_risk
    }


@router.delete("/{questionnaire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_questionnaire(
    questionnaire_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete medical questionnaire."""
    questionnaire = db.query(MedicalQuestionnaire).filter(
        MedicalQuestionnaire.id == questionnaire_id,
        MedicalQuestionnaire.organization_id == current_user.organization_id,
        MedicalQuestionnaire.deleted_at == None
    ).first()
    
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    
    questionnaire.deleted_at = datetime.utcnow()
    questionnaire.last_updated_by = current_user.id
    
    db.commit()
    
    return None

