"""
Super Admin HIPAA Compliance Endpoints

Provides endpoints for monitoring HIPAA compliance across all organizations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models.user import User
from app.models.organization import Organization
from app.services.baa_service import BAAService
from app.services.data_retention_service import DataRetentionService

router = APIRouter()


@router.get("/baa-status")
async def get_all_baa_status(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get BAA status for all organizations
    
    Returns comprehensive BAA compliance information including:
    - Signed, pending, and expired BAAs
    - Signature dates and signers
    - Reminder counts
    """
    baa_service = BAAService(db)
    
    # Get all organizations
    organizations = db.query(Organization).all()
    
    org_data = []
    for org in organizations:
        # Get BAA status for this organization
        baa_status = await baa_service.get_baa_status(org.id)
        
        org_data.append({
            "id": org.id,
            "name": org.name,
            "baa_status": baa_status.get("status", "pending"),
            "signed_date": baa_status.get("signed_date"),
            "signed_by": baa_status.get("signed_by_name"),
            "expires_date": baa_status.get("expires_date"),
            "reminder_count": baa_status.get("reminder_count", 0),
            "last_reminder_date": baa_status.get("last_reminder_date")
        })
    
    # Calculate summary stats
    total = len(org_data)
    signed = len([o for o in org_data if o["baa_status"] == "signed"])
    pending = len([o for o in org_data if o["baa_status"] == "pending"])
    expired = len([o for o in org_data if o["baa_status"] == "expired"])
    
    return {
        "organizations": org_data,
        "summary": {
            "total": total,
            "signed": signed,
            "pending": pending,
            "expired": expired,
            "compliance_rate": (signed / total * 100) if total > 0 else 0
        }
    }


@router.post("/baa-reminder/{organization_id}")
async def send_baa_reminder(
    organization_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Send BAA reminder to an organization
    """
    baa_service = BAAService(db)
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        return {"success": False, "message": "Organization not found"}
    
    # Send reminder
    result = await baa_service.send_baa_reminder(organization_id)
    
    return {
        "success": True,
        "message": f"BAA reminder sent to {org.name}",
        "reminder_count": result.get("reminder_count", 0)
    }


@router.get("/data-retention-status")
async def get_all_data_retention_status(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get data retention status for all organizations
    
    Returns information about:
    - Total patient records
    - Expired records needing deletion
    - Last cleanup date
    - Compliance status
    """
    retention_service = DataRetentionService(db)
    
    # Get all organizations
    organizations = db.query(Organization).all()
    
    org_data = []
    for org in organizations:
        # Get retention status for this organization
        status = await retention_service.get_retention_status(org.id)
        
        # Determine status level
        expired_count = status.get("expired_records", 0)
        if expired_count == 0:
            status_level = "ok"
        elif expired_count < 10:
            status_level = "action_needed"
        else:
            status_level = "critical"
        
        org_data.append({
            "id": org.id,
            "name": org.name,
            "total_patients": status.get("total_patients", 0),
            "expired_records": expired_count,
            "last_cleanup": status.get("last_cleanup_date"),
            "status": status_level
        })
    
    # Calculate summary stats
    total = len(org_data)
    ok = len([o for o in org_data if o["status"] == "ok"])
    action_needed = len([o for o in org_data if o["status"] == "action_needed"])
    critical = len([o for o in org_data if o["status"] == "critical"])
    total_expired = sum([o["expired_records"] for o in org_data])
    
    return {
        "organizations": org_data,
        "summary": {
            "total": total,
            "ok": ok,
            "action_needed": action_needed,
            "critical": critical,
            "total_expired_records": total_expired,
            "compliance_rate": (ok / total * 100) if total > 0 else 0
        }
    }


@router.get("/compliance-scores")
async def get_compliance_scores(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get overall HIPAA compliance scores for all organizations
    
    Combines BAA status, data retention, and security metrics
    into a single compliance score.
    """
    baa_service = BAAService(db)
    retention_service = DataRetentionService(db)
    
    # Get all organizations
    organizations = db.query(Organization).all()
    
    org_scores = []
    for org in organizations:
        # Get BAA status (40% weight)
        baa_status = await baa_service.get_baa_status(org.id)
        baa_score = 100 if baa_status.get("status") == "signed" else 0
        
        # Get data retention status (40% weight)
        retention_status = await retention_service.get_retention_status(org.id)
        expired_count = retention_status.get("expired_records", 0)
        retention_score = max(0, 100 - (expired_count * 5))  # -5 points per expired record
        
        # Security incidents (20% weight) - placeholder for now
        security_score = 100  # Will be implemented with real incident data
        
        # Calculate weighted score
        total_score = (
            baa_score * 0.4 +
            retention_score * 0.4 +
            security_score * 0.2
        )
        
        org_scores.append({
            "organization_id": org.id,
            "organization_name": org.name,
            "compliance_score": round(total_score, 1),
            "baa_compliant": baa_status.get("status") == "signed",
            "data_retention_compliant": expired_count == 0,
            "security_compliant": True,  # Placeholder
            "trend": 0  # Placeholder for historical comparison
        })
    
    # Sort by score (lowest first - need attention)
    org_scores.sort(key=lambda x: x["compliance_score"])
    
    return {
        "organizations": org_scores,
        "platform_average": sum([o["compliance_score"] for o in org_scores]) / len(org_scores) if org_scores else 0
    }

