"""
Audit Log API endpoints.

Provides read-only access to audit logs for compliance and security monitoring.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, get_organization, require_admin
from app.core.audit_log import (
    AuditLog,
    get_user_audit_trail,
    get_resource_audit_trail,
    get_phi_access_logs,
    get_failed_login_attempts,
    get_audit_statistics
)
from app.models.user import User
from app.models.organization_membership import OrganizationMembership

router = APIRouter()


# ========== Schemas ==========

class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: UUID
    user_id: UUID
    user_email: str
    user_role: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    reason: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    changes: Optional[dict]
    metadata: Optional[dict]
    organization_id: Optional[UUID]
    status: str
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class AuditStatisticsResponse(BaseModel):
    """Audit statistics response."""
    total_events: int
    events_by_action: dict
    phi_access_count: int
    failed_logins: int
    most_active_users: List[dict]


# ========== Endpoints ==========

@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Get audit logs",
    description="Get audit logs for current organization (admin only)"
)
async def get_audit_logs(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_organization),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for organization.
    
    Requires admin role.
    """
    query = db.query(AuditLog).filter(
        AuditLog.organization_id == membership.organization_id
    )
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if user_email:
        query = query.filter(AuditLog.user_email == user_email)
    
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset).all()
    
    return logs


@router.get(
    "/audit-logs/me",
    response_model=List[AuditLogResponse],
    summary="Get my audit logs",
    description="Get audit logs for current user"
)
async def get_my_audit_logs(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for current user.
    
    Users can view their own audit trail.
    """
    logs = get_user_audit_trail(
        db_session=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        action=action
    )
    
    return logs[:limit]


@router.get(
    "/audit-logs/resource/{resource_type}/{resource_id}",
    response_model=List[AuditLogResponse],
    summary="Get resource audit trail",
    description="Get audit trail for a specific resource (admin only)"
)
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_organization),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit trail for a specific resource.
    
    Requires admin role.
    """
    logs = get_resource_audit_trail(
        db_session=db,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Filter by organization
    logs = [log for log in logs if log.organization_id == membership.organization_id]
    
    return logs


@router.get(
    "/audit-logs/patients/{patient_id}/phi-access",
    response_model=List[AuditLogResponse],
    summary="Get PHI access logs for patient",
    description="Get all PHI access logs for a specific patient (admin only)"
)
async def get_patient_phi_access_logs(
    patient_id: UUID,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_organization),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get PHI access logs for a patient.
    
    Shows who accessed patient's protected health information.
    Requires admin role.
    """
    logs = get_phi_access_logs(
        db_session=db,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Filter by organization
    logs = [log for log in logs if log.organization_id == membership.organization_id]
    
    return logs


@router.get(
    "/audit-logs/failed-logins",
    response_model=List[AuditLogResponse],
    summary="Get failed login attempts",
    description="Get failed login attempts (admin only)"
)
async def get_failed_logins(
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    hours: int = Query(24, description="Look back hours"),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get failed login attempts.
    
    Useful for detecting brute force attacks.
    Requires admin role.
    """
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    logs = get_failed_login_attempts(
        db_session=db,
        user_email=user_email,
        ip_address=ip_address,
        start_date=start_date
    )
    
    return logs


@router.get(
    "/audit-logs/statistics",
    response_model=AuditStatisticsResponse,
    summary="Get audit statistics",
    description="Get audit statistics for organization (admin only)"
)
async def get_audit_stats(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_organization),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit statistics for organization.
    
    Provides overview of audit activity.
    Requires admin role.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stats = get_audit_statistics(
        db_session=db,
        organization_id=membership.organization_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return stats


@router.get(
    "/audit-logs/{log_id}",
    response_model=AuditLogResponse,
    summary="Get audit log by ID",
    description="Get specific audit log entry (admin only)"
)
async def get_audit_log_by_id(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_organization),
    _: None = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get specific audit log entry.
    
    Requires admin role.
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    # Verify organization access
    if log.organization_id != membership.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this audit log"
        )
    
    return log
