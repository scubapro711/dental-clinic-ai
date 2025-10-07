"""
Privacy & Data Subject Rights (DSR) API Endpoints
For תיקון 13 compliance
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import json
import os

from app.models.consent import (
    PatientConsent,
    DataSubjectRequest,
    PrivacyPolicyAcceptance,
    ConsentType,
    ConsentStatus,
    DataSubjectRequestType,
    DataSubjectRequestStatus
)
from app.core.audit import AuditLogger

router = APIRouter()


# Pydantic models
class ConsentRequest(BaseModel):
    """Request to grant/revoke consent."""
    consent_type: ConsentType
    granted: bool
    notes: Optional[str] = None


class ConsentResponse(BaseModel):
    """Consent response."""
    id: int
    consent_type: str
    status: str
    granted_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool


class DSRRequest(BaseModel):
    """Data Subject Rights request."""
    request_type: DataSubjectRequestType
    description: Optional[str] = None


class DSRResponse(BaseModel):
    """DSR response."""
    id: int
    request_type: str
    status: str
    requested_at: datetime
    due_date: datetime
    is_overdue: bool
    response: Optional[str]
    export_file_url: Optional[str]


class PrivacyPolicyAcceptanceRequest(BaseModel):
    """Privacy policy acceptance."""
    policy_version: str
    policy_url: str


# Consent Management Endpoints

@router.post("/consents", response_model=ConsentResponse)
async def grant_or_revoke_consent(
    consent_req: ConsentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    Grant or revoke consent.
    
    Patient can grant or revoke consent for various data processing activities.
    """
    # Find existing consent
    existing_consent = db.query(PatientConsent).filter(
        PatientConsent.patient_id == current_patient.id,
        PatientConsent.consent_type == consent_req.consent_type,
        PatientConsent.status.in_([ConsentStatus.GRANTED, ConsentStatus.PENDING])
    ).first()
    
    if consent_req.granted:
        # Grant consent
        if existing_consent:
            # Update existing
            existing_consent.grant(
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            consent = existing_consent
        else:
            # Create new
            consent = PatientConsent(
                patient_id=current_patient.id,
                consent_type=consent_req.consent_type,
                consent_text=get_consent_text(consent_req.consent_type),
                consent_version="1.0"
            )
            consent.grant(
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            db.add(consent)
    else:
        # Revoke consent
        if existing_consent:
            existing_consent.revoke(reason=consent_req.notes)
            consent = existing_consent
        else:
            raise HTTPException(404, "No active consent found to revoke")
    
    db.commit()
    db.refresh(consent)
    
    # Audit log
    AuditLogger.log(
        user_id=current_patient.id,
        user_role="patient",
        action="CONSENT_GRANTED" if consent_req.granted else "CONSENT_REVOKED",
        resource_type="consent",
        resource_id=consent.id,
        details={"consent_type": consent_req.consent_type},
        request=request
    )
    
    return ConsentResponse(
        id=consent.id,
        consent_type=consent.consent_type,
        status=consent.status,
        granted_at=consent.granted_at,
        expires_at=consent.expires_at,
        is_active=consent.is_active
    )


@router.get("/consents", response_model=List[ConsentResponse])
async def list_consents(
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    List all consents for current patient.
    """
    consents = db.query(PatientConsent).filter(
        PatientConsent.patient_id == current_patient.id
    ).all()
    
    return [
        ConsentResponse(
            id=c.id,
            consent_type=c.consent_type,
            status=c.status,
            granted_at=c.granted_at,
            expires_at=c.expires_at,
            is_active=c.is_active
        )
        for c in consents
    ]


# Data Subject Rights (DSR) Endpoints

@router.post("/dsr", response_model=DSRResponse)
async def create_dsr_request(
    dsr_req: DSRRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    Create a Data Subject Rights (DSR) request.
    
    Supports:
    - Right to access (זכות עיון)
    - Right to rectification (זכות תיקון)
    - Right to erasure (זכות מחיקה)
    - Right to data portability (זכות להעברה)
    - Right to object (זכות להתנגד)
    - Right to restriction (זכות להגבלה)
    
    תיקון 13 requires response within 30 days.
    """
    # Create DSR request
    dsr = DataSubjectRequest(
        patient_id=current_patient.id,
        request_type=dsr_req.request_type,
        description=dsr_req.description,
        due_date=datetime.utcnow() + timedelta(days=30),  # 30 days per תיקון 13
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(dsr)
    db.commit()
    db.refresh(dsr)
    
    # Audit log
    AuditLogger.log(
        user_id=current_patient.id,
        user_role="patient",
        action="DSR_REQUESTED",
        resource_type="dsr",
        resource_id=dsr.id,
        details={"request_type": dsr_req.request_type},
        request=request
    )
    
    # Send notification to DPO
    background_tasks.add_task(
        notify_dpo_new_dsr,
        dsr_id=dsr.id,
        patient_name=current_patient.name,
        request_type=dsr_req.request_type
    )
    
    # If request is ACCESS, automatically start export
    if dsr_req.request_type == DataSubjectRequestType.ACCESS:
        background_tasks.add_task(
            export_patient_data,
            dsr_id=dsr.id,
            patient_id=current_patient.id
        )
    
    return DSRResponse(
        id=dsr.id,
        request_type=dsr.request_type,
        status=dsr.status,
        requested_at=dsr.requested_at,
        due_date=dsr.due_date,
        is_overdue=dsr.is_overdue,
        response=None,
        export_file_url=None
    )


@router.get("/dsr", response_model=List[DSRResponse])
async def list_dsr_requests(
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    List all DSR requests for current patient.
    """
    requests = db.query(DataSubjectRequest).filter(
        DataSubjectRequest.patient_id == current_patient.id
    ).order_by(DataSubjectRequest.requested_at.desc()).all()
    
    return [
        DSRResponse(
            id=r.id,
            request_type=r.request_type,
            status=r.status,
            requested_at=r.requested_at,
            due_date=r.due_date,
            is_overdue=r.is_overdue,
            response=r.response,
            export_file_url=f"/api/v1/privacy/dsr/{r.id}/download" if r.export_file_path else None
        )
        for r in requests
    ]


@router.get("/dsr/{dsr_id}", response_model=DSRResponse)
async def get_dsr_request(
    dsr_id: int,
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    Get specific DSR request.
    """
    dsr = db.query(DataSubjectRequest).filter(
        DataSubjectRequest.id == dsr_id,
        DataSubjectRequest.patient_id == current_patient.id
    ).first()
    
    if not dsr:
        raise HTTPException(404, "DSR request not found")
    
    return DSRResponse(
        id=dsr.id,
        request_type=dsr.request_type,
        status=dsr.status,
        requested_at=dsr.requested_at,
        due_date=dsr.due_date,
        is_overdue=dsr.is_overdue,
        response=dsr.response,
        export_file_url=f"/api/v1/privacy/dsr/{dsr.id}/download" if dsr.export_file_path else None
    )


@router.get("/dsr/{dsr_id}/download")
async def download_exported_data(
    dsr_id: int,
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    Download exported patient data (for ACCESS requests).
    """
    dsr = db.query(DataSubjectRequest).filter(
        DataSubjectRequest.id == dsr_id,
        DataSubjectRequest.patient_id == current_patient.id,
        DataSubjectRequest.request_type == DataSubjectRequestType.ACCESS
    ).first()
    
    if not dsr:
        raise HTTPException(404, "DSR request not found")
    
    if not dsr.export_file_path:
        raise HTTPException(404, "Export file not ready yet")
    
    if not os.path.exists(dsr.export_file_path):
        raise HTTPException(404, "Export file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        dsr.export_file_path,
        filename=f"patient_data_{current_patient.id}_{dsr_id}.json",
        media_type="application/json"
    )


# Privacy Policy Acceptance

@router.post("/privacy-policy/accept")
async def accept_privacy_policy(
    acceptance: PrivacyPolicyAcceptanceRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_patient = Depends(get_current_patient)
):
    """
    Record privacy policy acceptance.
    """
    acceptance_record = PrivacyPolicyAcceptance(
        patient_id=current_patient.id,
        policy_version=acceptance.policy_version,
        policy_url=acceptance.policy_url,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(acceptance_record)
    db.commit()
    
    # Audit log
    AuditLogger.log(
        user_id=current_patient.id,
        user_role="patient",
        action="PRIVACY_POLICY_ACCEPTED",
        resource_type="privacy_policy",
        resource_id=acceptance_record.id,
        details={"version": acceptance.policy_version},
        request=request
    )
    
    return {"success": True, "message": "Privacy policy accepted"}


# Helper functions

def get_consent_text(consent_type: ConsentType) -> str:
    """Get consent text for specific type."""
    consent_texts = {
        ConsentType.DATA_PROCESSING: "אני מסכים/ה לעיבוד הנתונים האישיים שלי למטרות ניהול התיק הרפואי.",
        ConsentType.MARKETING: "אני מסכים/ה לקבל חומרי שיווק ופרסום מהמרפאה.",
        ConsentType.THIRD_PARTY_SHARING: "אני מסכים/ה לשיתוף הנתונים שלי עם גורמים חיצוניים (קופות חולים, מעבדות).",
        ConsentType.MEDICAL_RECORDS: "אני מסכים/ה לשמירת התיק הרפואי שלי במערכת דיגיטלית.",
        ConsentType.TELEGRAM_BOT: "אני מסכים/ה לשימוש בבוט טלגרם לתקשורת עם המרפאה.",
        ConsentType.AI_AGENTS: "אני מסכים/ה לשימוש בסוכני בינה מלאכותית לשיפור השירות.",
        ConsentType.ECLAIMS: "אני מסכים/ה לשליחת תביעות אוטומטית לקופת החולים שלי.",
        ConsentType.RESEARCH: "אני מסכים/ה לשימוש בנתונים אנונימיים למחקר."
    }
    return consent_texts.get(consent_type, "")


async def notify_dpo_new_dsr(dsr_id: int, patient_name: str, request_type: str):
    """Send notification to DPO about new DSR request."""
    # TODO: Implement email/Telegram notification to DPO
    logger.info(f"New DSR request: {dsr_id} from {patient_name} - {request_type}")


async def export_patient_data(dsr_id: int, patient_id: int):
    """
    Export all patient data to JSON file.
    
    Includes:
    - Personal information
    - Medical records
    - Appointments
    - Invoices
    - Consents
    - Audit logs
    """
    # TODO: Implement full data export
    # This should collect all patient data from all tables
    # and export to a JSON file
    
    export_data = {
        "patient_id": patient_id,
        "export_date": datetime.utcnow().isoformat(),
        "personal_info": {},
        "medical_records": [],
        "appointments": [],
        "invoices": [],
        "consents": [],
        "audit_logs": []
    }
    
    # Save to file
    export_dir = "/var/lib/dentalai/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    export_file = f"{export_dir}/patient_{patient_id}_dsr_{dsr_id}.json"
    
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    # Update DSR with file path
    db = next(get_db())
    dsr = db.query(DataSubjectRequest).get(dsr_id)
    if dsr:
        dsr.export_file_path = export_file
        dsr.status = DataSubjectRequestStatus.IN_PROGRESS
        db.commit()
    
    logger.info(f"Patient data exported: {export_file}")
