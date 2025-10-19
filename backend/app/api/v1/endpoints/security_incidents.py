"""
Security Incidents API Endpoints

Provides endpoints for managing and monitoring security incidents.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user, require_super_admin
from app.models.user import User

router = APIRouter()


# Mock data for now (will be replaced with real database queries)
MOCK_INCIDENTS = [
    {
        "id": 1,
        "date": "2025-10-19T05:30:00Z",
        "organization": "Bright Smiles Dental",
        "organization_id": 2,
        "type": "failed_login_attempts",
        "severity": "high",
        "description": "8 failed login attempts from IP 185.220.101.42",
        "status": "active",
        "details": {
            "ip_address": "185.220.101.42",
            "user_email": "admin@brightsmiles.com",
            "attempt_count": 8
        }
    },
    {
        "id": 2,
        "date": "2025-10-18T14:20:00Z",
        "organization": "Smile Dental Clinic",
        "organization_id": 1,
        "type": "bulk_phi_export",
        "severity": "medium",
        "description": "150 patient records exported by Dr. Cohen",
        "status": "resolved",
        "details": {
            "user_id": 5,
            "user_name": "Dr. Sarah Cohen",
            "record_count": 150,
            "export_format": "CSV"
        }
    },
    {
        "id": 3,
        "date": "2025-10-17T09:15:00Z",
        "organization": "Family Dental Care",
        "organization_id": 3,
        "type": "unauthorized_phi_access",
        "severity": "critical",
        "description": "Attempted access to patient records without authorization",
        "status": "active",
        "details": {
            "user_id": 12,
            "user_name": "Jane Smith",
            "patient_id": 4567,
            "access_denied": True
        }
    }
]


@router.get("/security-incidents")
async def get_security_incidents(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of incidents to return"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    current_user: User = Depends(require_super_admin)
):
    """
    Get recent security incidents
    
    Only accessible by super admins.
    """
    # Filter mock data
    filtered_incidents = MOCK_INCIDENTS.copy()
    
    if severity:
        filtered_incidents = [i for i in filtered_incidents if i["severity"] == severity]
    
    if status:
        filtered_incidents = [i for i in filtered_incidents if i["status"] == status]
    
    if organization_id:
        filtered_incidents = [i for i in filtered_incidents if i["organization_id"] == organization_id]
    
    # Limit results
    filtered_incidents = filtered_incidents[:limit]
    
    return {
        "incidents": filtered_incidents,
        "total": len(filtered_incidents),
        "days": days
    }


@router.get("/security-incidents/{incident_id}")
async def get_security_incident(
    incident_id: int,
    current_user: User = Depends(require_super_admin)
):
    """
    Get details of a specific security incident
    """
    incident = next((i for i in MOCK_INCIDENTS if i["id"] == incident_id), None)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@router.put("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: int,
    current_user: User = Depends(require_super_admin)
):
    """
    Mark a security incident as resolved
    """
    incident = next((i for i in MOCK_INCIDENTS if i["id"] == incident_id), None)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update status (in real implementation, this would update the database)
    incident["status"] = "resolved"
    incident["resolved_at"] = datetime.utcnow().isoformat()
    incident["resolved_by_id"] = current_user.id
    
    return {
        "success": True,
        "message": "Incident marked as resolved",
        "incident": incident
    }


@router.get("/security-incidents/stats/summary")
async def get_incidents_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(require_super_admin)
):
    """
    Get summary statistics for security incidents
    """
    incidents = MOCK_INCIDENTS
    
    stats = {
        "total": len(incidents),
        "active": len([i for i in incidents if i["status"] == "active"]),
        "resolved": len([i for i in incidents if i["status"] == "resolved"]),
        "by_severity": {
            "critical": len([i for i in incidents if i["severity"] == "critical"]),
            "high": len([i for i in incidents if i["severity"] == "high"]),
            "medium": len([i for i in incidents if i["severity"] == "medium"]),
            "low": len([i for i in incidents if i["severity"] == "low"])
        },
        "by_type": {}
    }
    
    # Count by type
    for incident in incidents:
        incident_type = incident["type"]
        if incident_type not in stats["by_type"]:
            stats["by_type"][incident_type] = 0
        stats["by_type"][incident_type] += 1
    
    return stats

