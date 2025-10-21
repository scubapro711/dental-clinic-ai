"""
HIPAA Metrics Service - GCP Cloud Monitoring Integration

This service exports HIPAA compliance metrics to Google Cloud Monitoring
for real-time tracking, alerting, and dashboard visualization.

Key Features:
- Real-time metrics export to GCP
- Custom metric types for HIPAA compliance
- Automatic labeling (user, organization, action type)
- Graceful degradation if GCP unavailable
- Comprehensive error handling

Metrics Tracked:
- PHI Access (authorized & unauthorized)
- Authentication Events (login attempts & failures)
- Encryption Operations (success & failures)
- Audit Log Entries
- Breach Incidents
- BAA Status (signed, pending, expired)

Architecture:
- Uses Google Cloud Monitoring API v3
- Metrics stored as time-series data
- Labels for filtering and aggregation
- Cloud Run resource type
- Batch writes for performance

Best Practices:
- Singleton pattern for client reuse
- Type hints for all methods
- Comprehensive docstrings
- Logging for debugging
- Feature flag for enable/disable
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# Only import GCP libraries if monitoring is enabled
if settings.ENABLE_GCP_MONITORING:
    try:
        from google.cloud import monitoring_v3
        from google.api import metric_pb2 as ga_metric
        from google.api import label_pb2 as ga_label
        GCP_AVAILABLE = True
    except ImportError:
        logger.warning("google-cloud-monitoring not installed. HIPAA metrics will not be exported to GCP.")
        GCP_AVAILABLE = False
else:
    GCP_AVAILABLE = False


class HIPAAMetricsService:
    """
    Service for exporting HIPAA compliance metrics to GCP Cloud Monitoring.
    
    This service provides methods to record various HIPAA-related events
    and export them as custom metrics to Google Cloud Monitoring.
    
    Attributes:
        client: GCP Monitoring client (if available)
        project_name: GCP project name for metrics
        metric_prefix: Prefix for all custom metrics
        enabled: Whether GCP monitoring is enabled
    """
    
    _instance: Optional['HIPAAMetricsService'] = None
    
    def __new__(cls):
        """Singleton pattern - reuse client across requests."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize GCP Monitoring client."""
        if self._initialized:
            return
            
        self.enabled = settings.ENABLE_GCP_MONITORING and GCP_AVAILABLE
        
        if self.enabled:
            try:
                self.client = monitoring_v3.MetricServiceClient()
                self.project_name = f"projects/{settings.GCP_PROJECT_ID}"
                self.metric_prefix = "custom.googleapis.com/dentaflow/hipaa"
                logger.info(f"HIPAA Metrics Service initialized for project {settings.GCP_PROJECT_ID}")
            except Exception as e:
                logger.error(f"Failed to initialize GCP Monitoring client: {e}")
                self.enabled = False
        else:
            logger.info("HIPAA Metrics Service disabled (GCP monitoring not available)")
            
        self._initialized = True
    
    def record_phi_access(
        self,
        user_id: str,
        organization_id: str,
        action_type: str,  # read/write/export/delete
        resource_type: str,  # patient/appointment/treatment/medical_record
        authorized: bool = True
    ) -> None:
        """
        Record PHI access event.
        
        This method tracks all access to Protected Health Information (PHI),
        including both authorized and unauthorized attempts.
        
        Args:
            user_id: ID of the user accessing PHI
            organization_id: ID of the organization
            action_type: Type of action (read/write/export/delete)
            resource_type: Type of resource (patient/appointment/treatment/medical_record)
            authorized: Whether the access was authorized (default: True)
        
        Example:
            >>> metrics.record_phi_access(
            ...     user_id="user_123",
            ...     organization_id="org_456",
            ...     action_type="read",
            ...     resource_type="patient",
            ...     authorized=True
            ... )
        """
        if not self.enabled:
            return
            
        metric_type = f"{self.metric_prefix}/phi_access"
        
        if not authorized:
            metric_type = f"{self.metric_prefix}/phi_access_unauthorized"
            logger.warning(f"Unauthorized PHI access attempt: user={user_id}, org={organization_id}, action={action_type}, resource={resource_type}")
            
        self._write_metric(
            metric_type=metric_type,
            value=1,
            labels={
                "user_id": user_id,
                "organization_id": organization_id,
                "action_type": action_type,
                "resource_type": resource_type,
            }
        )
    
    def record_authentication_event(
        self,
        user_id: str,
        user_role: str,  # doctor/admin/staff/patient
        auth_method: str,  # password/mfa/sso/google
        success: bool,
        ip_address: str
    ) -> None:
        """
        Record authentication event.
        
        Tracks all login attempts, both successful and failed, for security
        monitoring and anomaly detection.
        
        Args:
            user_id: ID of the user attempting to authenticate
            user_role: Role of the user
            auth_method: Authentication method used
            success: Whether authentication succeeded
            ip_address: IP address of the request
        
        Example:
            >>> metrics.record_authentication_event(
            ...     user_id="user_123",
            ...     user_role="doctor",
            ...     auth_method="password",
            ...     success=True,
            ...     ip_address="192.168.1.1"
            ... )
        """
        if not self.enabled:
            return
            
        metric_type = f"{self.metric_prefix}/login_attempts"
        
        if not success:
            metric_type = f"{self.metric_prefix}/login_failures"
            logger.warning(f"Failed login attempt: user={user_id}, role={user_role}, method={auth_method}, ip={ip_address}")
            
        self._write_metric(
            metric_type=metric_type,
            value=1,
            labels={
                "user_id": user_id,
                "user_role": user_role,
                "auth_method": auth_method,
                "ip_address": ip_address,
            }
        )
    
    def record_encryption_operation(
        self,
        encryption_type: str,  # at_rest/in_transit
        algorithm: str,  # AES-256/RSA-2048/TLS-1.3
        success: bool
    ) -> None:
        """
        Record encryption operation.
        
        Tracks all encryption operations to ensure data is properly
        encrypted both at rest and in transit.
        
        Args:
            encryption_type: Type of encryption (at_rest/in_transit)
            algorithm: Encryption algorithm used
            success: Whether encryption succeeded
        
        Example:
            >>> metrics.record_encryption_operation(
            ...     encryption_type="at_rest",
            ...     algorithm="AES-256",
            ...     success=True
            ... )
        """
        if not self.enabled:
            return
            
        metric_type = f"{self.metric_prefix}/encryption_operations"
        
        if not success:
            metric_type = f"{self.metric_prefix}/encryption_failures"
            logger.error(f"Encryption failure: type={encryption_type}, algorithm={algorithm}")
            
        self._write_metric(
            metric_type=metric_type,
            value=1,
            labels={
                "encryption_type": encryption_type,
                "algorithm": algorithm,
            }
        )
    
    def record_audit_log_entry(
        self,
        log_type: str,  # access/modification/export/deletion
        severity: str,  # info/warning/error/critical
        user_id: str,
        organization_id: str
    ) -> None:
        """
        Record audit log entry.
        
        Tracks all audit log entries for compliance reporting and
        incident investigation.
        
        Args:
            log_type: Type of audit log (access/modification/export/deletion)
            severity: Severity level (info/warning/error/critical)
            user_id: ID of the user who performed the action
            organization_id: ID of the organization
        
        Example:
            >>> metrics.record_audit_log_entry(
            ...     log_type="access",
            ...     severity="info",
            ...     user_id="user_123",
            ...     organization_id="org_456"
            ... )
        """
        if not self.enabled:
            return
            
        metric_type = f"{self.metric_prefix}/audit_log_entries"
        
        self._write_metric(
            metric_type=metric_type,
            value=1,
            labels={
                "log_type": log_type,
                "severity": severity,
                "user_id": user_id,
                "organization_id": organization_id,
            }
        )
    
    def record_breach_incident(
        self,
        breach_type: str,  # unauthorized_access/data_loss/malware/phishing
        affected_records: int,
        organization_id: str,
        severity: str = "critical"
    ) -> None:
        """
        Record breach incident.
        
        Tracks all security breach incidents for immediate alerting
        and compliance reporting.
        
        Args:
            breach_type: Type of breach
            affected_records: Number of records affected
            organization_id: ID of the organization
            severity: Severity level (default: critical)
        
        Example:
            >>> metrics.record_breach_incident(
            ...     breach_type="unauthorized_access",
            ...     affected_records=10,
            ...     organization_id="org_456",
            ...     severity="critical"
            ... )
        """
        if not self.enabled:
            return
            
        metric_type = f"{self.metric_prefix}/breach_incidents"
        
        logger.critical(f"BREACH INCIDENT: type={breach_type}, affected_records={affected_records}, org={organization_id}")
        
        self._write_metric(
            metric_type=metric_type,
            value=1,
            labels={
                "breach_type": breach_type,
                "affected_records": str(affected_records),
                "organization_id": organization_id,
                "severity": severity,
            }
        )
    
    def record_baa_status(
        self,
        vendor_type: str,  # cloud/software/service/hardware
        baa_status: str,  # active/pending/expired
        organization_id: str,
        vendor_name: Optional[str] = None
    ) -> None:
        """
        Record BAA (Business Associate Agreement) status.
        
        Tracks the status of all BAAs to ensure compliance with
        HIPAA requirements for third-party vendors.
        
        Args:
            vendor_type: Type of vendor
            baa_status: Status of the BAA
            organization_id: ID of the organization
            vendor_name: Name of the vendor (optional)
        
        Example:
            >>> metrics.record_baa_status(
            ...     vendor_type="cloud",
            ...     baa_status="active",
            ...     organization_id="org_456",
            ...     vendor_name="Google Cloud"
            ... )
        """
        if not self.enabled:
            return
            
        metric_type = f"{self.metric_prefix}/baa_signed_count"
        
        if baa_status == "pending":
            metric_type = f"{self.metric_prefix}/baa_pending_count"
            logger.warning(f"BAA pending: vendor_type={vendor_type}, vendor={vendor_name}, org={organization_id}")
        elif baa_status == "expired":
            metric_type = f"{self.metric_prefix}/baa_expired_count"
            logger.error(f"BAA expired: vendor_type={vendor_type}, vendor={vendor_name}, org={organization_id}")
            
        labels = {
            "vendor_type": vendor_type,
            "baa_status": baa_status,
            "organization_id": organization_id,
        }
        
        if vendor_name:
            labels["vendor_name"] = vendor_name
            
        self._write_metric(
            metric_type=metric_type,
            value=1,
            labels=labels
        )
    
    def _write_metric(
        self,
        metric_type: str,
        value: float,
        labels: Dict[str, str]
    ) -> None:
        """
        Write metric to Cloud Monitoring.
        
        This is an internal method that handles the actual writing
        of metrics to GCP Cloud Monitoring.
        
        Args:
            metric_type: Full metric type path
            value: Metric value
            labels: Dictionary of labels
        
        Note:
            Errors are logged but do not raise exceptions to avoid
            disrupting the main application flow.
        """
        if not self.enabled:
            return
            
        try:
            # Create time series
            series = monitoring_v3.TimeSeries()
            series.metric.type = metric_type
            
            # Set resource type to Cloud Run
            series.resource.type = "cloud_run_revision"
            series.resource.labels["project_id"] = settings.GCP_PROJECT_ID
            series.resource.labels["service_name"] = "dentaflow-backend"
            series.resource.labels["revision_name"] = settings.CLOUD_RUN_REVISION or "unknown"
            series.resource.labels["location"] = settings.GCP_REGION
            
            # Add custom labels
            for key, val in labels.items():
                series.metric.labels[key] = str(val)
                
            # Create time series point
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            point = monitoring_v3.Point(
                {"interval": interval, "value": {"double_value": value}}
            )
            series.points = [point]
            
            # Write to Cloud Monitoring
            self.client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
            
            logger.debug(f"Wrote metric {metric_type} with value {value} and labels {labels}")
            
        except Exception as e:
            # Log error but don't fail the request
            logger.error(f"Error writing metric {metric_type}: {e}", exc_info=True)


# Global singleton instance - DO NOT instantiate at import time!
# Let endpoints create instances on-demand to avoid import failures
# hipaa_metrics = HIPAAMetricsService()  # REMOVED: causes import-time GCP connection

