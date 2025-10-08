"""
Audit Logging System for HIPAA Compliance.

Tracks all access and modifications to Protected Health Information (PHI).

HIPAA Requirements:
- Log all access to PHI
- Log all modifications to PHI
- Log authentication events
- Retain logs for 6 years
- Protect logs from tampering
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
import json
import logging

from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import uuid

from app.core.database import Base

logger = logging.getLogger(__name__)


class AuditLog(Base):
    """
    Audit log entry for HIPAA compliance.
    
    Tracks:
    - Who accessed/modified data
    - What data was accessed/modified
    - When the action occurred
    - Where the action originated (IP address)
    - Why the action was performed (optional)
    - How the action was performed (API endpoint, method)
    """
    
    __tablename__ = 'audit_logs'
    
    # Primary key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Who (user)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(50))
    
    # What (action)
    action = Column(String(50), nullable=False, index=True)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT
    resource_type = Column(String(100), nullable=False, index=True)  # patient, appointment, medical_record, etc.
    resource_id = Column(String(255), index=True)  # ID of the resource
    
    # When
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Where
    ip_address = Column(String(45))  # IPv4: 15 chars, IPv6: 45 chars
    user_agent = Column(String(500))
    
    # Why (optional)
    reason = Column(Text)
    
    # How
    endpoint = Column(String(500))  # API endpoint
    method = Column(String(10))  # GET, POST, PUT, DELETE
    
    # Details
    changes = Column(JSONB)  # Before/after values for updates
    audit_metadata = Column(JSONB)  # Additional context
    
    # Organization (for multi-tenancy)
    organization_id = Column(PGUUID(as_uuid=True), index=True)
    
    # Status
    status = Column(String(20), default='success')  # success, failure, error
    error_message = Column(Text)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('ix_audit_logs_org_timestamp', 'organization_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog(user={self.user_email}, action={self.action}, resource={self.resource_type}:{self.resource_id})>"


# ========== Audit Logging Functions ==========

def log_audit_event(
    db_session,
    user_id: UUID,
    user_email: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_role: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    reason: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    audit_metadata: Optional[Dict[str, Any]] = None,
    organization_id: Optional[UUID] = None,
    status: str = 'success',
    error_message: Optional[str] = None
) -> AuditLog:
    """
    Log an audit event.
    
    Args:
        db_session: Database session
        user_id: User UUID
        user_email: User email
        action: Action performed (CREATE, READ, UPDATE, DELETE, etc.)
        resource_type: Type of resource (patient, appointment, etc.)
        resource_id: ID of the resource
        user_role: User's role
        ip_address: Client IP address
        user_agent: Client user agent
        reason: Reason for action (optional)
        endpoint: API endpoint
        method: HTTP method
        changes: Before/after values for updates
        metadata: Additional context
        organization_id: Organization UUID
        status: Status of action (success, failure, error)
        error_message: Error message if failed
    
    Returns:
        Created AuditLog entry
    """
    audit_entry = AuditLog(
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip_address,
        user_agent=user_agent,
        reason=reason,
        endpoint=endpoint,
        method=method,
        changes=changes,
        audit_metadata=audit_metadata,
        organization_id=organization_id,
        status=status,
        error_message=error_message
    )
    
    db_session.add(audit_entry)
    db_session.commit()
    
    logger.info(
        f"Audit: {user_email} {action} {resource_type}:{resource_id} - {status}",
        extra={
            'user_id': str(user_id),
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'status': status
        }
    )
    
    return audit_entry


def log_phi_access(
    db_session,
    user_id: UUID,
    user_email: str,
    patient_id: UUID,
    fields_accessed: list[str],
    ip_address: Optional[str] = None,
    reason: Optional[str] = None,
    organization_id: Optional[UUID] = None
) -> AuditLog:
    """
    Log access to Protected Health Information (PHI).
    
    Args:
        db_session: Database session
        user_id: User UUID
        user_email: User email
        patient_id: Patient UUID
        fields_accessed: List of PHI fields accessed (ssn, medical_history, etc.)
        ip_address: Client IP address
        reason: Reason for access
        organization_id: Organization UUID
    
    Returns:
        Created AuditLog entry
    """
    return log_audit_event(
        db_session=db_session,
        user_id=user_id,
        user_email=user_email,
        action='READ_PHI',
        resource_type='patient',
        resource_id=str(patient_id),
        ip_address=ip_address,
        reason=reason,
        audit_metadata={'fields_accessed': fields_accessed},
        organization_id=organization_id
    )


def log_phi_modification(
    db_session,
    user_id: UUID,
    user_email: str,
    patient_id: UUID,
    changes: Dict[str, Any],
    ip_address: Optional[str] = None,
    reason: Optional[str] = None,
    organization_id: Optional[UUID] = None
) -> AuditLog:
    """
    Log modification to Protected Health Information (PHI).
    
    Args:
        db_session: Database session
        user_id: User UUID
        user_email: User email
        patient_id: Patient UUID
        changes: Dictionary of changed fields (before/after)
        ip_address: Client IP address
        reason: Reason for modification
        organization_id: Organization UUID
    
    Returns:
        Created AuditLog entry
    """
    return log_audit_event(
        db_session=db_session,
        user_id=user_id,
        user_email=user_email,
        action='UPDATE_PHI',
        resource_type='patient',
        resource_id=str(patient_id),
        ip_address=ip_address,
        reason=reason,
        changes=changes,
        organization_id=organization_id
    )


def log_authentication(
    db_session,
    user_id: UUID,
    user_email: str,
    action: str,  # LOGIN, LOGOUT, LOGIN_FAILED
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = 'success',
    error_message: Optional[str] = None
) -> AuditLog:
    """
    Log authentication event.
    
    Args:
        db_session: Database session
        user_id: User UUID
        user_email: User email
        action: Authentication action (LOGIN, LOGOUT, LOGIN_FAILED)
        ip_address: Client IP address
        user_agent: Client user agent
        status: Status of action
        error_message: Error message if failed
    
    Returns:
        Created AuditLog entry
    """
    return log_audit_event(
        db_session=db_session,
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type='authentication',
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        error_message=error_message
    )


# ========== Query Functions ==========

def get_user_audit_trail(
    db_session,
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None
) -> list[AuditLog]:
    """
    Get audit trail for a specific user.
    
    Args:
        db_session: Database session
        user_id: User UUID
        start_date: Start date for filtering
        end_date: End date for filtering
        action: Filter by action
        resource_type: Filter by resource type
    
    Returns:
        List of AuditLog entries
    """
    query = db_session.query(AuditLog).filter(AuditLog.user_id == user_id)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    return query.order_by(AuditLog.timestamp.desc()).all()


def get_resource_audit_trail(
    db_session,
    resource_type: str,
    resource_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list[AuditLog]:
    """
    Get audit trail for a specific resource (e.g., patient).
    
    Args:
        db_session: Database session
        resource_type: Type of resource
        resource_id: ID of resource
        start_date: Start date for filtering
        end_date: End date for filtering
    
    Returns:
        List of AuditLog entries
    """
    query = db_session.query(AuditLog).filter(
        AuditLog.resource_type == resource_type,
        AuditLog.resource_id == resource_id
    )
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    return query.order_by(AuditLog.timestamp.desc()).all()


def get_phi_access_logs(
    db_session,
    patient_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list[AuditLog]:
    """
    Get all PHI access logs for a patient.
    
    Args:
        db_session: Database session
        patient_id: Patient UUID
        start_date: Start date for filtering
        end_date: End date for filtering
    
    Returns:
        List of AuditLog entries
    """
    query = db_session.query(AuditLog).filter(
        AuditLog.resource_type == 'patient',
        AuditLog.resource_id == str(patient_id),
        AuditLog.action.in_(['READ_PHI', 'UPDATE_PHI', 'CREATE', 'DELETE'])
    )
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    return query.order_by(AuditLog.timestamp.desc()).all()


def get_failed_login_attempts(
    db_session,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    start_date: Optional[datetime] = None
) -> list[AuditLog]:
    """
    Get failed login attempts.
    
    Args:
        db_session: Database session
        user_email: Filter by user email
        ip_address: Filter by IP address
        start_date: Start date for filtering
    
    Returns:
        List of AuditLog entries
    """
    query = db_session.query(AuditLog).filter(
        AuditLog.action == 'LOGIN_FAILED'
    )
    
    if user_email:
        query = query.filter(AuditLog.user_email == user_email)
    
    if ip_address:
        query = query.filter(AuditLog.ip_address == ip_address)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    return query.order_by(AuditLog.timestamp.desc()).all()


# ========== Statistics Functions ==========

def get_audit_statistics(
    db_session,
    organization_id: UUID,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Get audit statistics for an organization.
    
    Args:
        db_session: Database session
        organization_id: Organization UUID
        start_date: Start date
        end_date: End date
    
    Returns:
        Dictionary with statistics
    """
    from sqlalchemy import func
    
    # Total events
    total_events = db_session.query(func.count(AuditLog.id)).filter(
        AuditLog.organization_id == organization_id,
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).scalar()
    
    # Events by action
    events_by_action = db_session.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.organization_id == organization_id,
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).group_by(AuditLog.action).all()
    
    # PHI access count
    phi_access_count = db_session.query(func.count(AuditLog.id)).filter(
        AuditLog.organization_id == organization_id,
        AuditLog.action.in_(['READ_PHI', 'UPDATE_PHI']),
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).scalar()
    
    # Failed logins
    failed_logins = db_session.query(func.count(AuditLog.id)).filter(
        AuditLog.organization_id == organization_id,
        AuditLog.action == 'LOGIN_FAILED',
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).scalar()
    
    # Most active users
    most_active_users = db_session.query(
        AuditLog.user_email,
        func.count(AuditLog.id).label('event_count')
    ).filter(
        AuditLog.organization_id == organization_id,
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).group_by(AuditLog.user_email).order_by(func.count(AuditLog.id).desc()).limit(10).all()
    
    return {
        'total_events': total_events,
        'events_by_action': dict(events_by_action),
        'phi_access_count': phi_access_count,
        'failed_logins': failed_logins,
        'most_active_users': [
            {'email': email, 'event_count': count}
            for email, count in most_active_users
        ]
    }
