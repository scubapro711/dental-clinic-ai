"""
Patient Portal API Endpoints

Provides patient-facing endpoints for the patient portal
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.integrations.odoo_client_v3 import OdooClientV3

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/patient/profile")
async def get_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current patient profile"""
    try:
        # In a real implementation, fetch from Odoo
        # For now, return mock data based on user
        return {
            "id": current_user.id,
            "name": current_user.full_name or "Sarah Johnson",
            "email": current_user.email,
            "phone": "+1 (555) 123-4567",
            "date_of_birth": "1985-03-15",
            "address": "123 Main St, New York, NY 10001",
            "insurance": {
                "provider": "HealthCare Plus",
                "policy_number": "HC123456789",
                "group_number": "GRP001"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching patient profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


@router.get("/patient/health-score")
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient's dental health score"""
    try:
        # Calculate health score based on various factors
        # This is a simplified version
        score = 85
        
        return {
            "score": score,
            "message": "Your dental health is in great shape! Keep up the good work.",
            "factors": [
                {"label": "Regular checkups", "status": "good", "value": 95},
                {"label": "Good oral hygiene", "status": "good", "value": 90},
                {"label": "Next cleaning due soon", "status": "warning", "value": 70}
            ],
            "recommendations": [
                "Schedule your next cleaning appointment",
                "Continue brushing twice daily",
                "Floss at least once per day"
            ],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate health score")


@router.get("/appointments")
async def get_appointments(
    status: Optional[str] = Query(None, description="Filter by status: upcoming, past, cancelled, all"),
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient's appointments"""
    try:
        # In production, fetch from Odoo
        # For now, return mock data
        
        all_appointments = [
            {
                "id": 1,
                "date": "2025-10-15",
                "time": "14:00",
                "doctor": "Dr. Sarah Goldstein",
                "type": "Routine Cleaning",
                "duration": "45 min",
                "status": "Confirmed",
                "location": "Main Office - Room 3"
            },
            {
                "id": 2,
                "date": "2025-11-20",
                "time": "10:00",
                "doctor": "Dr. Michael Smith",
                "type": "Checkup",
                "duration": "30 min",
                "status": "Pending",
                "location": "Main Office - Room 1"
            },
            {
                "id": 3,
                "date": "2025-09-01",
                "time": "15:00",
                "doctor": "Dr. Sarah Goldstein",
                "type": "Dental Cleaning",
                "duration": "45 min",
                "status": "Completed",
                "location": "Main Office - Room 3"
            }
        ]
        
        # Filter by status
        if status and status != "all":
            if status == "upcoming":
                filtered = [a for a in all_appointments if a["status"] in ["Confirmed", "Pending"]]
            elif status == "past":
                filtered = [a for a in all_appointments if a["status"] == "Completed"]
            elif status == "cancelled":
                filtered = [a for a in all_appointments if a["status"] == "Cancelled"]
            else:
                filtered = all_appointments
        else:
            filtered = all_appointments
        
        # Apply pagination
        total = len(filtered)
        appointments = filtered[offset:offset + limit]
        
        return {
            "appointments": appointments,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch appointments")


@router.post("/appointments")
async def create_appointment(
    appointment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    try:
        # In production, create in Odoo
        # For now, return mock response
        return {
            "id": 999,
            "status": "success",
            "message": "Appointment created successfully",
            "appointment": {
                **appointment_data,
                "id": 999,
                "status": "Pending",
                "created_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment")


@router.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    try:
        # In production, update in Odoo
        # For now, return mock response
        return {
            "status": "success",
            "message": f"Appointment {appointment_id} cancelled successfully",
            "appointment_id": appointment_id,
            "cancelled_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")


@router.get("/records")
async def get_medical_records(
    record_type: Optional[str] = Query(None, description="Filter by type: xray, report, treatment, all"),
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient's medical records"""
    try:
        # In production, fetch from Odoo
        # For now, return mock data
        
        all_records = [
            {
                "id": 1,
                "type": "xray",
                "title": "Dental X-Ray - Full Mouth",
                "date": "2025-09-01",
                "doctor": "Dr. Sarah Goldstein",
                "description": "Routine full mouth x-ray examination",
                "verified": True,
                "files": [
                    {"name": "xray_full_mouth.jpg", "size": "2.3 MB", "url": "/files/xray1.jpg"}
                ]
            },
            {
                "id": 2,
                "type": "treatment",
                "title": "Dental Cleaning",
                "date": "2025-09-01",
                "doctor": "Dr. Sarah Goldstein",
                "description": "Professional teeth cleaning and polishing",
                "verified": True,
                "notes": "Patient showed excellent oral hygiene. No issues detected."
            },
            {
                "id": 3,
                "type": "report",
                "title": "Annual Checkup Report",
                "date": "2025-09-01",
                "doctor": "Dr. Sarah Goldstein",
                "description": "Annual dental health assessment",
                "verified": True,
                "files": [
                    {"name": "checkup_report_2025.pdf", "size": "450 KB", "url": "/files/report1.pdf"}
                ]
            }
        ]
        
        # Filter by type
        if record_type and record_type != "all":
            filtered = [r for r in all_records if r["type"] == record_type]
        else:
            filtered = all_records
        
        # Apply pagination
        total = len(filtered)
        records = filtered[offset:offset + limit]
        
        return {
            "records": records,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch records")


@router.get("/records/{record_id}")
async def get_record_detail(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific record"""
    try:
        # In production, fetch from Odoo
        # For now, return mock data
        return {
            "id": record_id,
            "type": "xray",
            "title": "Dental X-Ray - Full Mouth",
            "date": "2025-09-01",
            "doctor": "Dr. Sarah Goldstein",
            "description": "Routine full mouth x-ray examination",
            "verified": True,
            "files": [
                {"name": "xray_full_mouth.jpg", "size": "2.3 MB", "url": "/files/xray1.jpg"}
            ],
            "notes": "All teeth appear healthy. No cavities detected.",
            "created_at": "2025-09-01T15:30:00",
            "updated_at": "2025-09-01T15:30:00"
        }
    except Exception as e:
        logger.error(f"Error fetching record detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch record")


@router.get("/billing/overview")
async def get_billing_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing overview for patient"""
    try:
        # In production, fetch from Odoo
        # For now, return mock data
        return {
            "balance_due": 150.00,
            "last_payment": {
                "amount": 200.00,
                "date": "2025-09-28",
                "method": "Credit Card"
            },
            "insurance": {
                "provider": "HealthCare Plus",
                "coverage": "80%",
                "remaining_benefit": 1500.00
            },
            "summary": {
                "total_billed": 2500.00,
                "total_paid": 2350.00,
                "insurance_paid": 1800.00,
                "patient_paid": 550.00
            }
        }
    except Exception as e:
        logger.error(f"Error fetching billing overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch billing overview")


@router.get("/billing/invoices")
async def get_invoices(
    status: Optional[str] = Query(None, description="Filter by status: paid, unpaid, overdue, all"),
    limit: Optional[int] = Query(10, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient's invoices"""
    try:
        # In production, fetch from Odoo
        # For now, return mock data
        
        all_invoices = [
            {
                "id": 1,
                "number": "INV-2025-001",
                "date": "2025-09-01",
                "due_date": "2025-10-01",
                "amount": 150.00,
                "status": "Unpaid",
                "description": "Dental Cleaning",
                "items": [
                    {"description": "Routine Cleaning", "quantity": 1, "price": 150.00}
                ]
            },
            {
                "id": 2,
                "number": "INV-2025-002",
                "date": "2025-08-15",
                "due_date": "2025-09-15",
                "amount": 200.00,
                "status": "Paid",
                "description": "Checkup & X-Ray",
                "paid_date": "2025-09-28",
                "items": [
                    {"description": "Annual Checkup", "quantity": 1, "price": 100.00},
                    {"description": "Full Mouth X-Ray", "quantity": 1, "price": 100.00}
                ]
            }
        ]
        
        # Filter by status
        if status and status != "all":
            filtered = [i for i in all_invoices if i["status"].lower() == status.lower()]
        else:
            filtered = all_invoices
        
        # Apply pagination
        total = len(filtered)
        invoices = filtered[offset:offset + limit]
        
        return {
            "invoices": invoices,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")

