"""
Audit Logger Service
Centralized logging for all auditable actions
"""

import time
import logging
from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog, AuditAction, SecurityEvent

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging service.
    
    Usage:
        from app.core.audit import AuditLogger
        
        AuditLogger.log(
            db=db,
            action=AuditAction.READ,
            user_id=current_user.id,
            user_role="doctor",
            resource_type="patient",
            resource_id=patient_id,
            details={"fields": ["name", "phone"]},
            request=request
        )
    """
    
    @staticmethod
    def log(
        db: Session,
        action: AuditAction,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
        user_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        request: Optional[Request] = None,
        response_status: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[int] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            action: Type of action (AuditAction enum)
            user_id: ID of user performing action
            user_role: Role of user (patient, doctor, admin, owner)
            user_email: Email of user
            resource_type: Type of resource (patient, appointment, etc.)
            resource_id: ID of resource
            details: Additional details (dict)
            error_message: Error message if action failed
            request: FastAPI Request object (optional)
            response_status: HTTP response status code
            response_time_ms: Response time in milliseconds
            session_id: Session ID
            tenant_id: Tenant ID (for multi-tenancy)
            
        Returns:
            AuditLog: Created audit log entry
        """
        try:
            # Extract request details if provided
            ip_address = None
            user_agent = None
            request_method = None
            request_path = None
            request_params = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                request_method = request.method
                request_path = str(request.url.path)
                request_params = dict(request.query_params) if request.query_params else None
            
            # Create audit log
            audit_log = AuditLog(
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
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            # Log to application logger
            logger.info(
                f"Audit: {action} by user {user_id} ({user_role}) on {resource_type}:{resource_id}"
            )
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Don't raise - audit logging should never break the application
            return None
    
    @staticmethod
    def log_security_event(
        db: Session,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        related_audit_log_ids: Optional[list] = None
    ) -> SecurityEvent:
        """
        Log a security event.
        
        Args:
            db: Database session
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            description: Description of the event
            user_id: User ID involved (if applicable)
            ip_address: IP address involved
            details: Additional details
            related_audit_log_ids: List of related audit log IDs
            
        Returns:
            SecurityEvent: Created security event
        """
        try:
            security_event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                description=description,
                user_id=user_id,
                ip_address=ip_address,
                details=details,
                related_audit_log_ids=related_audit_log_ids
            )
            
            db.add(security_event)
            db.commit()
            db.refresh(security_event)
            
            # Log to application logger
            logger.warning(
                f"Security Event [{severity}]: {event_type} - {description}"
            )
            
            # TODO: Send alert to security team if severity is high or critical
            if severity in ["high", "critical"]:
                AuditLogger._send_security_alert(security_event)
            
            return security_event
            
        except Exception as e:
            logger.error(f"Failed to create security event: {e}")
            return None
    
    @staticmethod
    def _send_security_alert(security_event: SecurityEvent):
        """
        Send security alert to security team.
        
        TODO: Implement email/Telegram/Slack notification
        """
        logger.critical(
            f"SECURITY ALERT: {security_event.event_type} - {security_event.description}"
        )


class AuditMiddleware:
    """
    FastAPI middleware for automatic audit logging.
    
    Logs all API requests and responses.
    """
    
    def __init__(self, app, db_session_factory):
        self.app = app
        self.db_session_factory = db_session_factory
    
    async def __call__(self, request: Request, call_next):
        """Process request and log audit trail."""
        start_time = time.time()
        
        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        user_role = getattr(request.state, "user_role", None)
        user_email = getattr(request.state, "user_email", None)
        session_id = getattr(request.state, "session_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Determine action type from HTTP method
        action_map = {
            "GET": AuditAction.READ,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE
        }
        action = action_map.get(request.method, AuditAction.READ)
        
        # Extract resource info from path
        resource_type, resource_id = AuditMiddleware._extract_resource_from_path(
            request.url.path
        )
        
        # Log to database
        db = self.db_session_factory()
        try:
            AuditLogger.log(
                db=db,
                action=action,
                user_id=user_id,
                user_role=user_role,
                user_email=user_email,
                resource_type=resource_type,
                resource_id=resource_id,
                request=request,
                response_status=response.status_code,
                response_time_ms=response_time_ms,
                session_id=session_id,
                tenant_id=tenant_id
            )
        finally:
            db.close()
        
        return response
    
    @staticmethod
    def _extract_resource_from_path(path: str) -> tuple:
        """
        Extract resource type and ID from URL path.
        
        Examples:
            /api/v1/patients/123 -> ("patient", 123)
            /api/v1/appointments/456 -> ("appointment", 456)
        """
        parts = path.strip("/").split("/")
        
        resource_type = None
        resource_id = None
        
        # Look for resource type (plural noun) followed by ID (number)
        for i in range(len(parts) - 1):
            if parts[i + 1].isdigit():
                resource_type = parts[i].rstrip("s")  # Remove plural 's'
                resource_id = int(parts[i + 1])
                break
        
        return resource_type, resource_id


# Decorator for automatic audit logging
def audit_log(
    action: AuditAction,
    resource_type: str,
    get_resource_id: callable = None
):
    """
    Decorator for automatic audit logging.
    
    Usage:
        @audit_log(
            action=AuditAction.READ,
            resource_type="patient",
            get_resource_id=lambda kwargs: kwargs.get("patient_id")
        )
        async def get_patient(patient_id: int, db: Session, current_user: User):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get database session from kwargs
            db = kwargs.get("db")
            request = kwargs.get("request")
            current_user = kwargs.get("current_user")
            
            # Get resource ID
            resource_id = None
            if get_resource_id:
                resource_id = get_resource_id(kwargs)
            
            # Execute function
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                error_message = None
                response_status = 200
            except Exception as e:
                error_message = str(e)
                response_status = 500
                raise
            finally:
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Log audit
                if db:
                    AuditLogger.log(
                        db=db,
                        action=action,
                        user_id=current_user.id if current_user else None,
                        user_role=current_user.role if current_user else None,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        request=request,
                        response_status=response_status,
                        response_time_ms=response_time_ms,
                        error_message=error_message
                    )
            
            return result
        
        return wrapper
    return decorator
