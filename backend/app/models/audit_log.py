"""
Audit Logging System
For compliance and security monitoring
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index, Boolean, ForeignKey
from datetime import datetime
from enum import Enum
from app.core.database import Base


class AuditAction(str, Enum):
    """Types of auditable actions."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    
    # Data operations
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    
    # Privacy
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    DSR_REQUESTED = "dsr_requested"
    DSR_COMPLETED = "dsr_completed"
    PRIVACY_POLICY_ACCEPTED = "privacy_policy_accepted"
    
    # Agent actions
    AGENT_CHAT = "agent_chat"
    AGENT_ACTION = "agent_action"
    AGENT_TOOL_CALL = "agent_tool_call"
    
    # System
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"


class AuditLog(Base):
    """
    Comprehensive audit log for all system activities.
    
    Required for:
    - תיקון 13 compliance (data access tracking)
    - Security monitoring
    - Troubleshooting
    - Legal compliance
    
    Retention: 7 years (as per Israeli law)
    """
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # User information
    user_id = Column(Integer, index=True)  # User who performed the action
    user_role = Column(String(50))  # patient, doctor, admin, owner, agent
    user_email = Column(String(255))
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # AuditAction enum
    resource_type = Column(String(50), index=True)  # patient, appointment, invoice, etc.
    resource_id = Column(Integer, index=True)  # ID of the resource
    
    # Request details
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    request_method = Column(String(10))  # GET, POST, PUT, DELETE
    request_path = Column(String(500))
    request_params = Column(JSON)  # Query parameters
    
    # Response details
    response_status = Column(Integer)  # HTTP status code
    response_time_ms = Column(Integer)  # Response time in milliseconds
    
    # Additional context
    details = Column(JSON)  # Additional details (e.g., fields accessed, changes made)
    error_message = Column(Text)  # Error message if applicable
    
    # Security
    session_id = Column(String(255))  # Session ID
    tenant_id = Column(Integer, index=True)  # For multi-tenancy
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_resource', 'resource_type', 'resource_id'),
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_tenant_timestamp', 'tenant_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} by {self.user_id} at {self.timestamp}>"
    
    @classmethod
    def log(
        cls,
        action: AuditAction,
        user_id: int = None,
        user_role: str = None,
        user_email: str = None,
        resource_type: str = None,
        resource_id: int = None,
        ip_address: str = None,
        user_agent: str = None,
        request_method: str = None,
        request_path: str = None,
        request_params: dict = None,
        response_status: int = None,
        response_time_ms: int = None,
        details: dict = None,
        error_message: str = None,
        session_id: str = None,
        tenant_id: int = None
    ):
        """
        Create an audit log entry.
        
        Usage:
            AuditLog.log(
                action=AuditAction.READ,
                user_id=current_user.id,
                user_role="doctor",
                resource_type="patient",
                resource_id=patient_id,
                details={"fields": ["name", "phone", "medical_history"]}
            )
        """
        return cls(
            action=action,
            user_id=user_id,
            user_role=user_role,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            request_params=request_params,
            response_status=response_status,
            response_time_ms=response_time_ms,
            details=details,
            error_message=error_message,
            session_id=session_id,
            tenant_id=tenant_id
        )


class SecurityEvent(Base):
    """
    Security-specific events that require immediate attention.
    
    Examples:
    - Multiple failed login attempts
    - Unauthorized access attempts
    - Suspicious activity patterns
    - Data breach attempts
    """
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20))  # low, medium, high, critical
    
    # User/IP involved
    user_id = Column(Integer, index=True)
    ip_address = Column(String(45), index=True)
    
    # Description
    description = Column(Text)
    details = Column(JSON)
    
    # Response
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer)  # User ID who resolved
    resolution_notes = Column(Text)
    
    # Related audit logs
    related_audit_log_ids = Column(JSON)  # List of related audit log IDs
    
    @property
    def created_at(self):
        """Alias for timestamp for backward compatibility."""
        return self.timestamp
    
    def __repr__(self):
        return f"<SecurityEvent {self.id}: {self.event_type} - {self.severity}>"
