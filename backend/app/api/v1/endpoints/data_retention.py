"""
Data Retention API Endpoints
Admin interface for managing HIPAA-compliant data lifecycle
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.dependencies import get_db, get_current_user, require_super_admin
from app.models.user import User
from app.services.data_retention_service import DataRetentionService

router = APIRouter()


# ==================== Request/Response Models ====================

class PatientDeletionRequest(BaseModel):
    """Request to delete patient data."""
    patient_id: int = Field(..., description="Patient ID to delete")
    reason: str = Field(..., description="Reason for deletion")
    confirm: bool = Field(..., description="Confirmation flag")


class PatientDeletionResponse(BaseModel):
    """Response after patient data deletion."""
    success: bool
    patient_id: int
    deletion_date: str
    records_deleted: Dict[str, int]
    message: str


class RetentionReportResponse(BaseModel):
    """Data retention status report."""
    report_date: str
    retention_periods: Dict[str, int]
    statistics: Dict[str, Any]


class ExpiredRecordResponse(BaseModel):
    """Expired patient record information."""
    patient_id: int
    patient_name: str
    last_visit_date: str | None
    is_minor: bool
    organization_id: int
    eligible_for_deletion: bool
    reason: str


# ==================== Endpoints ====================

@router.get(
    "/report",
    response_model=RetentionReportResponse,
    summary="Get data retention report",
    description="Generate comprehensive report of data retention status"
)
async def get_retention_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Generate data retention status report.
    
    **Permissions:** Super Admin only
    
    Returns:
        - Retention periods
        - Statistics on expired records
        - Records eligible for deletion
    """
    try:
        service = DataRetentionService(db)
        report = service.generate_retention_report()
        
        return RetentionReportResponse(**report)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating retention report: {str(e)}"
        )


@router.get(
    "/expired-patients",
    response_model=List[ExpiredRecordResponse],
    summary="List expired patient records",
    description="Get list of patient records that have exceeded retention period"
)
async def list_expired_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    List patient records eligible for deletion.
    
    **Permissions:** Super Admin only
    
    Returns:
        List of expired patient records with metadata
    """
    try:
        service = DataRetentionService(db)
        expired_patients = service.identify_expired_patient_records()
        
        return [ExpiredRecordResponse(**patient) for patient in expired_patients]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing expired patients: {str(e)}"
        )


@router.post(
    "/delete-patient",
    response_model=PatientDeletionResponse,
    summary="Delete patient data",
    description="Securely delete patient PHI and related records"
)
async def delete_patient_data(
    request: PatientDeletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Delete patient data according to retention policy.
    
    **Permissions:** Super Admin only
    
    **HIPAA Compliance:**
    - Creates audit log entry
    - Anonymizes related audit logs
    - Checks for litigation holds
    - Verifies retention period
    
    Args:
        request: Deletion request with patient ID and reason
        
    Returns:
        Deletion summary with counts
    """
    try:
        if not request.confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation required for data deletion"
            )
        
        service = DataRetentionService(db)
        
        # Perform deletion
        summary = service.delete_expired_patient_data(
            patient_id=request.patient_id,
            performed_by=current_user.email,
            reason=request.reason
        )
        
        return PatientDeletionResponse(
            success=True,
            patient_id=summary["patient_id"],
            deletion_date=summary["deletion_date"],
            records_deleted=summary["records_deleted"],
            message=f"Successfully deleted patient {summary['patient_name']} data"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting patient data: {str(e)}"
        )


@router.post(
    "/archive-audit-logs",
    summary="Archive expired audit logs",
    description="Archive audit logs to cold storage"
)
async def archive_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Archive expired audit logs to GCS bucket.
    
    **Permissions:** Super Admin only
    
    **Process:**
    1. Identify logs older than 6 years
    2. Export to GCS bucket
    3. Verify upload
    4. Delete from database
    
    Returns:
        Archive summary
    """
    try:
        service = DataRetentionService(db)
        result = service.archive_expired_audit_logs()
        
        return {
            "success": True,
            "archived_count": result["archived_count"],
            "archive_date": result["archive_date"],
            "message": f"Archived {result['archived_count']} audit logs"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error archiving audit logs: {str(e)}"
        )


@router.post(
    "/cleanup-inactive-users",
    summary="Delete inactive user accounts",
    description="Anonymize user accounts inactive for 2+ years"
)
async def cleanup_inactive_users(
    days_inactive: int = 730,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Delete (anonymize) inactive user accounts.
    
    **Permissions:** Super Admin only
    
    Args:
        days_inactive: Number of days of inactivity (default: 730 = 2 years)
        
    Returns:
        List of deleted user accounts
    """
    try:
        service = DataRetentionService(db)
        deleted_users = service.delete_inactive_user_accounts(days_inactive)
        
        return {
            "success": True,
            "deleted_count": len(deleted_users),
            "deleted_users": deleted_users,
            "message": f"Anonymized {len(deleted_users)} inactive user accounts"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting inactive users: {str(e)}"
        )


@router.get(
    "/expired-audit-logs-count",
    summary="Count expired audit logs",
    description="Get count of audit logs exceeding 6-year retention"
)
async def count_expired_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Count audit logs eligible for archival.
    
    **Permissions:** Super Admin only
    
    Returns:
        Count of expired audit logs
    """
    try:
        service = DataRetentionService(db)
        count = service.identify_expired_audit_logs()
        
        return {
            "success": True,
            "expired_count": count,
            "message": f"Found {count} expired audit logs"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting expired audit logs: {str(e)}"
        )


# ==================== Scheduled Job Endpoints ====================

@router.post(
    "/jobs/daily-check",
    summary="Run daily retention check",
    description="Scheduled job to check for expired data (called by Cloud Scheduler)"
)
async def run_daily_check(
    db: Session = Depends(get_db),
    # Note: This endpoint should be secured with Cloud Scheduler service account
):
    """
    Daily scheduled job to check for expired data.
    
    **Called by:** Cloud Scheduler
    
    **Actions:**
    - Generate retention report
    - Identify expired records
    - Send notifications if action required
    
    Returns:
        Daily check summary
    """
    try:
        from app.services.data_retention_service import run_daily_retention_check
        
        report = run_daily_retention_check(db)
        
        return {
            "success": True,
            "report": report,
            "message": "Daily retention check completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in daily retention check: {str(e)}"
        )


@router.post(
    "/jobs/monthly-cleanup",
    summary="Run monthly data cleanup",
    description="Scheduled job to perform automated data cleanup (called by Cloud Scheduler)"
)
async def run_monthly_cleanup(
    db: Session = Depends(get_db),
    # Note: This endpoint should be secured with Cloud Scheduler service account
):
    """
    Monthly scheduled job to perform automated data cleanup.
    
    **Called by:** Cloud Scheduler
    
    **Actions:**
    - Archive expired audit logs
    - Delete inactive user accounts
    - Generate cleanup report
    
    Returns:
        Monthly cleanup summary
    """
    try:
        from app.services.data_retention_service import run_monthly_data_cleanup
        
        result = run_monthly_data_cleanup(db)
        
        return {
            "success": True,
            "result": result,
            "message": "Monthly data cleanup completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in monthly cleanup: {str(e)}"
        )

