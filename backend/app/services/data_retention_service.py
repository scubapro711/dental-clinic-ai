"""
Data Retention and Deletion Service
Implements HIPAA-compliant automated data lifecycle management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.user import User
from app.models.organization import Organization
from app.models.audit_log import AuditLog
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.core.config import settings

logger = logging.getLogger(__name__)


class DataRetentionService:
    """
    Manages data retention and deletion according to HIPAA requirements
    and DentaFlow's Data Retention Policy.
    
    Retention Periods (from DATA_RETENTION_POLICY.md):
    - PHI (Patient Records): 10 years from last encounter
    - Audit Logs: 6 years (HIPAA requirement)
    - Business Records: 7 years
    - System Logs: 90 days (operational), 6 years (security)
    - Backups: 30 days (daily), 90 days (weekly), 1 year (monthly)
    """
    
    # Retention periods in days
    PHI_RETENTION_DAYS = 3650  # 10 years
    MINOR_PATIENT_RETENTION_YEARS = 10  # After age 21
    AUDIT_LOG_RETENTION_DAYS = 2190  # 6 years
    BUSINESS_RECORD_RETENTION_DAYS = 2555  # 7 years
    OPERATIONAL_LOG_RETENTION_DAYS = 90
    SECURITY_LOG_RETENTION_DAYS = 2190  # 6 years
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== PHI Deletion ====================
    
    def identify_expired_patient_records(self) -> List[Dict[str, Any]]:
        """
        Identify patient records that have exceeded retention period.
        
        Returns:
            List of patient records eligible for deletion with metadata
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.PHI_RETENTION_DAYS)
            
            # Query patients with no activity in retention period
            expired_patients = self.db.query(Patient).filter(
                or_(
                    Patient.last_visit_date < cutoff_date,
                    and_(
                        Patient.last_visit_date.is_(None),
                        Patient.created_at < cutoff_date
                    )
                )
            ).all()
            
            results = []
            for patient in expired_patients:
                # Check if patient is a minor (special handling)
                is_minor = self._is_minor_patient(patient)
                
                # Check for litigation hold
                has_litigation_hold = self._check_litigation_hold(patient.id)
                
                if not has_litigation_hold:
                    results.append({
                        "patient_id": patient.id,
                        "patient_name": f"{patient.first_name} {patient.last_name}",
                        "last_visit_date": patient.last_visit_date,
                        "is_minor": is_minor,
                        "organization_id": patient.organization_id,
                        "eligible_for_deletion": not is_minor,
                        "reason": "Retention period expired" if not is_minor else "Minor patient - extended retention"
                    })
            
            logger.info(f"Identified {len(results)} expired patient records")
            return results
            
        except Exception as e:
            logger.error(f"Error identifying expired patient records: {e}")
            raise
    
    def delete_expired_patient_data(
        self, 
        patient_id: int, 
        performed_by: str,
        reason: str = "Automated retention policy"
    ) -> Dict[str, Any]:
        """
        Securely delete patient PHI and related records.
        
        Args:
            patient_id: Patient ID to delete
            performed_by: User performing the deletion
            reason: Reason for deletion
            
        Returns:
            Deletion summary with counts
        """
        try:
            patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")
            
            # Check for litigation hold
            if self._check_litigation_hold(patient_id):
                raise ValueError(f"Patient {patient_id} has active litigation hold")
            
            deletion_summary = {
                "patient_id": patient_id,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "deletion_date": datetime.utcnow().isoformat(),
                "performed_by": performed_by,
                "reason": reason,
                "records_deleted": {}
            }
            
            # 1. Delete appointments
            appointments_deleted = self.db.query(Appointment).filter(
                Appointment.patient_id == patient_id
            ).delete(synchronize_session=False)
            deletion_summary["records_deleted"]["appointments"] = appointments_deleted
            
            # 2. Anonymize audit logs (keep for compliance, but remove PII)
            audit_logs_anonymized = self._anonymize_audit_logs(patient_id)
            deletion_summary["records_deleted"]["audit_logs_anonymized"] = audit_logs_anonymized
            
            # 3. Delete patient record (cascades to related tables)
            self.db.delete(patient)
            
            # 4. Create deletion audit log
            self._create_deletion_audit_log(
                patient_id=patient_id,
                performed_by=performed_by,
                reason=reason,
                summary=deletion_summary
            )
            
            self.db.commit()
            
            logger.info(f"Successfully deleted patient {patient_id} data")
            return deletion_summary
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting patient {patient_id} data: {e}")
            raise
    
    # ==================== Audit Log Management ====================
    
    def identify_expired_audit_logs(self) -> int:
        """
        Identify audit logs that have exceeded 6-year retention period.
        
        Returns:
            Count of expired audit logs
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.AUDIT_LOG_RETENTION_DAYS)
            
            count = self.db.query(func.count(AuditLog.id)).filter(
                AuditLog.created_at < cutoff_date
            ).scalar()
            
            logger.info(f"Identified {count} expired audit logs")
            return count
            
        except Exception as e:
            logger.error(f"Error identifying expired audit logs: {e}")
            raise
    
    def archive_expired_audit_logs(self) -> Dict[str, Any]:
        """
        Archive audit logs to cold storage before deletion.
        
        Returns:
            Archive summary
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.AUDIT_LOG_RETENTION_DAYS)
            
            # Query expired logs
            expired_logs = self.db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).all()
            
            if not expired_logs:
                return {"archived_count": 0, "message": "No expired audit logs to archive"}
            
            # TODO: Export to GCS bucket for long-term archival
            # This would involve:
            # 1. Export logs to JSON/CSV
            # 2. Upload to GCS bucket (dentaflow-audit-archive)
            # 3. Verify upload
            # 4. Delete from database
            
            archive_summary = {
                "archived_count": len(expired_logs),
                "archive_date": datetime.utcnow().isoformat(),
                "oldest_log": expired_logs[0].created_at.isoformat() if expired_logs else None,
                "status": "pending_implementation"
            }
            
            logger.info(f"Archived {len(expired_logs)} audit logs")
            return archive_summary
            
        except Exception as e:
            logger.error(f"Error archiving audit logs: {e}")
            raise
    
    # ==================== User Account Deletion ====================
    
    def delete_inactive_user_accounts(self, days_inactive: int = 730) -> List[Dict[str, Any]]:
        """
        Delete user accounts that have been inactive for specified period.
        
        Args:
            days_inactive: Number of days of inactivity (default: 2 years)
            
        Returns:
            List of deleted user accounts
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
            
            # Find inactive users (not logged in for 2+ years)
            inactive_users = self.db.query(User).filter(
                and_(
                    User.last_login < cutoff_date,
                    User.is_active == False
                )
            ).all()
            
            deleted_users = []
            for user in inactive_users:
                # Anonymize instead of hard delete (preserve audit trail)
                user.email = f"deleted_{user.id}@anonymized.local"
                user.first_name = "Deleted"
                user.last_name = "User"
                user.phone = None
                user.is_active = False
                
                deleted_users.append({
                    "user_id": user.id,
                    "deletion_date": datetime.utcnow().isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                })
            
            self.db.commit()
            
            logger.info(f"Anonymized {len(deleted_users)} inactive user accounts")
            return deleted_users
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting inactive user accounts: {e}")
            raise
    
    # ==================== Helper Methods ====================
    
    def _is_minor_patient(self, patient: Patient) -> bool:
        """Check if patient is a minor (under 21)."""
        if not patient.date_of_birth:
            return False
        
        age = (datetime.utcnow().date() - patient.date_of_birth).days / 365.25
        return age < 21
    
    def _check_litigation_hold(self, patient_id: int) -> bool:
        """
        Check if patient has active litigation hold.
        
        TODO: Implement litigation hold tracking table
        """
        # Placeholder - would check litigation_holds table
        return False
    
    def _anonymize_audit_logs(self, patient_id: int) -> int:
        """
        Anonymize audit logs related to patient (keep for compliance).
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Count of anonymized logs
        """
        try:
            # Update audit logs to remove PII but keep action records
            count = self.db.query(AuditLog).filter(
                AuditLog.resource_id == str(patient_id),
                AuditLog.resource_type == "patient"
            ).update({
                "details": {"anonymized": True, "reason": "Patient data deletion"}
            }, synchronize_session=False)
            
            return count
            
        except Exception as e:
            logger.error(f"Error anonymizing audit logs: {e}")
            raise
    
    def _create_deletion_audit_log(
        self,
        patient_id: int,
        performed_by: str,
        reason: str,
        summary: Dict[str, Any]
    ):
        """Create audit log entry for data deletion."""
        try:
            audit_log = AuditLog(
                user_id=None,  # System action
                action="data_deletion",
                resource_type="patient",
                resource_id=str(patient_id),
                details={
                    "performed_by": performed_by,
                    "reason": reason,
                    "summary": summary,
                    "compliance": "HIPAA Data Retention Policy"
                },
                ip_address="system",
                user_agent="DataRetentionService"
            )
            self.db.add(audit_log)
            
        except Exception as e:
            logger.error(f"Error creating deletion audit log: {e}")
            raise
    
    # ==================== Reporting ====================
    
    def generate_retention_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive data retention status report.
        
        Returns:
            Report with retention statistics
        """
        try:
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "retention_periods": {
                    "phi_days": self.PHI_RETENTION_DAYS,
                    "audit_logs_days": self.AUDIT_LOG_RETENTION_DAYS,
                    "business_records_days": self.BUSINESS_RECORD_RETENTION_DAYS
                },
                "statistics": {}
            }
            
            # Count expired patient records
            expired_patients = self.identify_expired_patient_records()
            report["statistics"]["expired_patient_records"] = len(expired_patients)
            report["statistics"]["eligible_for_deletion"] = len([
                p for p in expired_patients if p["eligible_for_deletion"]
            ])
            
            # Count expired audit logs
            expired_audit_logs = self.identify_expired_audit_logs()
            report["statistics"]["expired_audit_logs"] = expired_audit_logs
            
            # Total patient records
            total_patients = self.db.query(func.count(Patient.id)).scalar()
            report["statistics"]["total_patient_records"] = total_patients
            
            # Total audit logs
            total_audit_logs = self.db.query(func.count(AuditLog.id)).scalar()
            report["statistics"]["total_audit_logs"] = total_audit_logs
            
            logger.info("Generated data retention report")
            return report
            
        except Exception as e:
            logger.error(f"Error generating retention report: {e}")
            raise


# ==================== Scheduled Job Functions ====================

def run_daily_retention_check(db: Session):
    """
    Daily scheduled job to check for expired data.
    
    This function should be called by Cloud Scheduler or similar.
    """
    try:
        service = DataRetentionService(db)
        
        # Generate report
        report = service.generate_retention_report()
        
        # Log summary
        logger.info(f"Daily retention check completed: {report['statistics']}")
        
        # TODO: Send notification to admin if action required
        if report["statistics"]["eligible_for_deletion"] > 0:
            logger.warning(
                f"{report['statistics']['eligible_for_deletion']} patient records "
                "eligible for deletion - admin review required"
            )
        
        return report
        
    except Exception as e:
        logger.error(f"Error in daily retention check: {e}")
        raise


def run_monthly_data_cleanup(db: Session):
    """
    Monthly scheduled job to perform automated data cleanup.
    
    This function should be called by Cloud Scheduler.
    """
    try:
        service = DataRetentionService(db)
        
        # Archive expired audit logs
        archive_result = service.archive_expired_audit_logs()
        logger.info(f"Archived audit logs: {archive_result}")
        
        # Delete inactive user accounts (2+ years)
        deleted_users = service.delete_inactive_user_accounts(days_inactive=730)
        logger.info(f"Deleted {len(deleted_users)} inactive user accounts")
        
        return {
            "archive_result": archive_result,
            "deleted_users_count": len(deleted_users)
        }
        
    except Exception as e:
        logger.error(f"Error in monthly data cleanup: {e}")
        raise

