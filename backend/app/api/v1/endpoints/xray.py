"""
X-Ray Management API Endpoints.

Provides endpoints for managing dental X-ray images,
metadata, and Sarah AI analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
import os
import uuid as uuid_lib

from app.core.database import get_db
from app.models.user import User
from app.models.xray import (
    XRay,
    XRayType,
    XRayQuality,
    XRayFindingSeverity,
)
from app.api.v1.endpoints.auth import get_current_user


router = APIRouter()


# Pydantic schemas

class XRayCreate(BaseModel):
    """Create X-ray request."""
    patient_id: UUID
    patient_name: Optional[str] = None
    xray_type: XRayType
    xray_date: Optional[datetime] = None
    tooth_number: Optional[str] = None
    tooth_numbers: Optional[List[str]] = None
    appointment_id: Optional[UUID] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_baseline: bool = False


class XRayUpdate(BaseModel):
    """Update X-ray request."""
    patient_name: Optional[str] = None
    xray_type: Optional[XRayType] = None
    xray_date: Optional[datetime] = None
    tooth_number: Optional[str] = None
    tooth_numbers: Optional[List[str]] = None
    quality: Optional[XRayQuality] = None
    quality_notes: Optional[str] = None
    needs_retake: Optional[bool] = None
    retake_reason: Optional[str] = None
    findings: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_recommended: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_baseline: Optional[bool] = None
    compared_with_xray_id: Optional[UUID] = None


class XRayResponse(BaseModel):
    """X-ray response."""
    id: UUID
    organization_id: UUID
    patient_id: UUID
    patient_name: Optional[str]
    appointment_id: Optional[UUID]
    taken_by: Optional[UUID]
    reviewed_by: Optional[UUID]
    xray_type: str
    xray_date: str
    tooth_number: Optional[str]
    tooth_numbers: Optional[List[str]]
    image_url: str
    image_filename: str
    image_size_bytes: Optional[int]
    image_format: Optional[str]
    thumbnail_url: Optional[str]
    quality: Optional[str]
    quality_notes: Optional[str]
    needs_retake: bool
    retake_reason: Optional[str]
    findings: Optional[str]
    diagnosis: Optional[str]
    treatment_recommended: Optional[str]
    sarah_analyzed: bool
    sarah_analysis_date: Optional[str]
    sarah_findings: Optional[List[dict]]
    sarah_severity: Optional[str]
    sarah_recommendations: Optional[List[dict]]
    sarah_confidence: Optional[int]
    sarah_alerts: Optional[List[dict]]
    notes: Optional[str]
    tags: Optional[List[str]]
    is_baseline: bool
    compared_with_xray_id: Optional[UUID]
    has_critical_findings: bool
    requires_immediate_attention: bool
    has_comparison: bool
    created_at: str
    updated_at: str


# Endpoints

@router.get("/patient/{patient_id}", response_model=List[XRayResponse])
async def get_patient_xrays(
    patient_id: UUID,
    xray_type: Optional[XRayType] = None,
    tooth_number: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all X-rays for a patient."""
    query = db.query(XRay).filter(
        XRay.organization_id == current_user.organization_id,
        XRay.patient_id == patient_id,
        XRay.deleted_at == None
    )
    
    if xray_type:
        query = query.filter(XRay.xray_type == xray_type)
    
    if tooth_number:
        query = query.filter(XRay.tooth_number == tooth_number)
    
    xrays = query.order_by(XRay.xray_date.desc()).all()
    
    return [XRayResponse(**xray.to_dict(), 
                         has_critical_findings=xray.has_critical_findings,
                         requires_immediate_attention=xray.requires_immediate_attention,
                         has_comparison=xray.has_comparison) 
            for xray in xrays]


@router.get("/{xray_id}", response_model=XRayResponse)
async def get_xray(
    xray_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific X-ray by ID."""
    xray = db.query(XRay).filter(
        XRay.id == xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    
    # Log view for HIPAA compliance
    if not xray.viewed_by:
        xray.viewed_by = []
    if str(current_user.id) not in xray.viewed_by:
        xray.viewed_by.append(str(current_user.id))
        db.commit()
    
    return XRayResponse(**xray.to_dict(),
                       has_critical_findings=xray.has_critical_findings,
                       requires_immediate_attention=xray.requires_immediate_attention,
                       has_comparison=xray.has_comparison)


@router.post("/upload", response_model=XRayResponse, status_code=status.HTTP_201_CREATED)
async def upload_xray(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    patient_name: Optional[str] = Form(None),
    xray_type: str = Form(...),
    xray_date: Optional[str] = Form(None),
    tooth_number: Optional[str] = Form(None),
    appointment_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    is_baseline: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload X-ray image."""
    
    # Validate file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".dcm", ".dicom"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid_lib.uuid4()}{file_ext}"
    
    # Save file (TODO: implement S3 upload)
    # For now, save to local uploads directory
    upload_dir = "/home/ubuntu/dental-clinic-ai/backend/uploads/xrays"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create X-ray record
    xray = XRay(
        organization_id=current_user.organization_id,
        patient_id=UUID(patient_id),
        patient_name=patient_name,
        xray_type=XRayType(xray_type),
        xray_date=datetime.fromisoformat(xray_date) if xray_date else datetime.utcnow(),
        tooth_number=tooth_number,
        appointment_id=UUID(appointment_id) if appointment_id else None,
        image_url=file_path,  # TODO: Use S3 URL
        image_filename=unique_filename,
        image_size_bytes=len(content),
        image_format=file_ext.replace(".", ""),
        notes=notes,
        is_baseline=is_baseline,
        taken_by=current_user.id,
        created_by=current_user.id,
        last_updated_by=current_user.id
    )
    
    db.add(xray)
    db.commit()
    db.refresh(xray)
    
    return XRayResponse(**xray.to_dict(),
                       has_critical_findings=xray.has_critical_findings,
                       requires_immediate_attention=xray.requires_immediate_attention,
                       has_comparison=xray.has_comparison)


@router.put("/{xray_id}", response_model=XRayResponse)
async def update_xray(
    xray_id: UUID,
    data: XRayUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update X-ray metadata and findings."""
    xray = db.query(XRay).filter(
        XRay.id == xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    
    # Update fields
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(xray, field, value)
    
    xray.last_updated_by = current_user.id
    xray.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(xray)
    
    return XRayResponse(**xray.to_dict(),
                       has_critical_findings=xray.has_critical_findings,
                       requires_immediate_attention=xray.requires_immediate_attention,
                       has_comparison=xray.has_comparison)


@router.post("/{xray_id}/review", response_model=XRayResponse)
async def review_xray(
    xray_id: UUID,
    findings: str = Form(...),
    diagnosis: Optional[str] = Form(None),
    treatment_recommended: Optional[str] = Form(None),
    quality: Optional[XRayQuality] = Form(None),
    needs_retake: bool = Form(False),
    retake_reason: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dentist reviews X-ray and adds findings."""
    xray = db.query(XRay).filter(
        XRay.id == xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    
    xray.findings = findings
    xray.diagnosis = diagnosis
    xray.treatment_recommended = treatment_recommended
    xray.quality = quality
    xray.needs_retake = needs_retake
    xray.retake_reason = retake_reason
    xray.reviewed_by = current_user.id
    xray.last_updated_by = current_user.id
    xray.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(xray)
    
    return XRayResponse(**xray.to_dict(),
                       has_critical_findings=xray.has_critical_findings,
                       requires_immediate_attention=xray.requires_immediate_attention,
                       has_comparison=xray.has_comparison)


@router.post("/{xray_id}/sarah-analyze")
async def sarah_analyze_xray(
    xray_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger Sarah AI analysis of X-ray."""
    xray = db.query(XRay).filter(
        XRay.id == xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    
    # TODO: Implement Sarah AI analysis
    # For now, return mock analysis
    
    xray.sarah_analyzed = True
    xray.sarah_analysis_date = datetime.utcnow()
    xray.sarah_findings = [
        {"finding": "Normal tooth structure", "location": "crown", "confidence": 95},
        {"finding": "No visible decay", "location": "all", "confidence": 90}
    ]
    xray.sarah_severity = XRayFindingSeverity.NORMAL
    xray.sarah_recommendations = [
        {"recommendation": "Continue routine monitoring", "priority": "low"}
    ]
    xray.sarah_confidence = 90
    xray.last_updated_by = current_user.id
    
    db.commit()
    db.refresh(xray)
    
    return {
        "xray_id": str(xray_id),
        "analyzed": True,
        "analysis_date": xray.sarah_analysis_date.isoformat(),
        "findings": xray.sarah_findings,
        "severity": xray.sarah_severity.value,
        "recommendations": xray.sarah_recommendations,
        "confidence": xray.sarah_confidence
    }


@router.get("/{xray_id}/compare/{previous_xray_id}")
async def compare_xrays(
    xray_id: UUID,
    previous_xray_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare two X-rays (current vs previous)."""
    xray = db.query(XRay).filter(
        XRay.id == xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    previous_xray = db.query(XRay).filter(
        XRay.id == previous_xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    if not xray or not previous_xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    
    if xray.patient_id != previous_xray.patient_id:
        raise HTTPException(status_code=400, detail="X-rays are from different patients")
    
    # Mark comparison
    xray.compared_with_xray_id = previous_xray_id
    db.commit()
    
    # TODO: Implement Sarah comparison analysis
    
    return {
        "current_xray": XRayResponse(**xray.to_dict(),
                                    has_critical_findings=xray.has_critical_findings,
                                    requires_immediate_attention=xray.requires_immediate_attention,
                                    has_comparison=xray.has_comparison),
        "previous_xray": XRayResponse(**previous_xray.to_dict(),
                                     has_critical_findings=previous_xray.has_critical_findings,
                                     requires_immediate_attention=previous_xray.requires_immediate_attention,
                                     has_comparison=previous_xray.has_comparison),
        "comparison": {
            "changes_detected": False,
            "progression": "stable",
            "sarah_notes": "No significant changes detected between X-rays"
        }
    }


@router.delete("/{xray_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_xray(
    xray_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete X-ray."""
    xray = db.query(XRay).filter(
        XRay.id == xray_id,
        XRay.organization_id == current_user.organization_id,
        XRay.deleted_at == None
    ).first()
    
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    
    xray.deleted_at = datetime.utcnow()
    xray.last_updated_by = current_user.id
    
    db.commit()
    
    return None

