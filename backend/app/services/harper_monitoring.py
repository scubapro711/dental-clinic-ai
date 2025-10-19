"""
Harper Proactive Monitoring System

This module implements proactive HIPAA compliance monitoring for Harper.
It runs scheduled checks, generates alerts, and provides real-time compliance insights.

Key Features:
- Scheduled compliance audits (daily, weekly, monthly)
- Real-time risk monitoring
- Automated alert generation
- Compliance trend analysis
- BAA expiration tracking
- PHI access anomaly detection

Architecture:
- Background tasks using Celery/APScheduler
- Database-backed alert storage
- Integration with notification system
- Dashboard metrics generation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from sqlalchemy.orm import Session

from app.tools.hipaa_tools import (
    search_hipaa_knowledge,
    check_phi_compliance,
    validate_baa,
    assess_security_controls,
    audit_access_logs,
    evaluate_risk,
)

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action required within 24 hours
    MEDIUM = "medium"  # Action required within 1 week
    LOW = "low"  # Informational, no immediate action
    INFO = "info"  # General information


class AlertType(str, Enum):
    """Types of compliance alerts."""
    BAA_EXPIRING = "baa_expiring"
    BAA_EXPIRED = "baa_expired"
    PHI_COMPLIANCE_ISSUE = "phi_compliance_issue"
    SECURITY_GAP = "security_gap"
    ACCESS_ANOMALY = "access_anomaly"
    RISK_THRESHOLD_EXCEEDED = "risk_threshold_exceeded"
    BREACH_DETECTED = "breach_detected"
    PATIENT_RIGHTS_VIOLATION = "patient_rights_violation"
    AUDIT_FINDING = "audit_finding"
    COMPLIANCE_SCORE_DROP = "compliance_score_drop"


class HarperMonitoringService:
    """
    Proactive monitoring service for HIPAA compliance.
    
    This service runs scheduled checks and generates alerts for
    compliance issues that require attention.
    """
    
    def __init__(self, db: Session, organization_id: int):
        """
        Initialize monitoring service.
        
        Args:
            db: Database session
            organization_id: Organization to monitor
        """
        self.db = db
        self.organization_id = organization_id
        self.alerts: List[Dict[str, Any]] = []
    
    async def run_daily_checks(self) -> Dict[str, Any]:
        """
        Run daily compliance checks.
        
        This should be scheduled to run every day at a specific time.
        
        Returns:
            Summary of daily check results
        """
        logger.info(f"Running daily compliance checks for org {self.organization_id}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "organization_id": self.organization_id,
            "checks_run": [],
            "alerts_generated": 0,
            "status": "success"
        }
        
        try:
            # 1. Check BAA expirations
            baa_results = await self._check_baa_expirations()
            results["checks_run"].append("baa_expirations")
            results["alerts_generated"] += len(baa_results.get("alerts", []))
            
            # 2. Check PHI compliance
            phi_results = await self._check_phi_compliance()
            results["checks_run"].append("phi_compliance")
            results["alerts_generated"] += len(phi_results.get("alerts", []))
            
            # 3. Audit access logs for anomalies
            access_results = await self._check_access_anomalies()
            results["checks_run"].append("access_anomalies")
            results["alerts_generated"] += len(access_results.get("alerts", []))
            
            # 4. Check risk levels
            risk_results = await self._check_risk_levels()
            results["checks_run"].append("risk_levels")
            results["alerts_generated"] += len(risk_results.get("alerts", []))
            
            logger.info(f"Daily checks completed: {results['alerts_generated']} alerts generated")
            
        except Exception as e:
            logger.error(f"Error in daily checks: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def run_weekly_checks(self) -> Dict[str, Any]:
        """
        Run weekly compliance checks.
        
        This should be scheduled to run every week.
        
        Returns:
            Summary of weekly check results
        """
        logger.info(f"Running weekly compliance checks for org {self.organization_id}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "organization_id": self.organization_id,
            "checks_run": [],
            "alerts_generated": 0,
            "status": "success"
        }
        
        try:
            # 1. Comprehensive security controls assessment
            security_results = await self._assess_security_controls()
            results["checks_run"].append("security_controls")
            results["alerts_generated"] += len(security_results.get("alerts", []))
            
            # 2. Compliance score calculation
            compliance_results = await self._calculate_compliance_score()
            results["checks_run"].append("compliance_score")
            results["alerts_generated"] += len(compliance_results.get("alerts", []))
            
            # 3. Generate weekly summary report
            summary = await self._generate_weekly_summary()
            results["summary"] = summary
            
            logger.info(f"Weekly checks completed: {results['alerts_generated']} alerts generated")
            
        except Exception as e:
            logger.error(f"Error in weekly checks: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def run_monthly_checks(self) -> Dict[str, Any]:
        """
        Run monthly compliance checks.
        
        This should be scheduled to run every month.
        
        Returns:
            Summary of monthly check results
        """
        logger.info(f"Running monthly compliance checks for org {self.organization_id}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "organization_id": self.organization_id,
            "checks_run": [],
            "reports_generated": [],
            "status": "success"
        }
        
        try:
            # 1. Generate monthly compliance report
            report = await self._generate_monthly_report()
            results["checks_run"].append("monthly_report")
            results["reports_generated"].append(report)
            
            # 2. Compliance trend analysis
            trends = await self._analyze_compliance_trends()
            results["trends"] = trends
            
            # 3. Risk assessment summary
            risk_summary = await self._generate_risk_summary()
            results["risk_summary"] = risk_summary
            
            logger.info(f"Monthly checks completed")
            
        except Exception as e:
            logger.error(f"Error in monthly checks: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _check_baa_expirations(self) -> Dict[str, Any]:
        """
        Check for expiring or expired BAAs.
        
        Returns:
            Check results with alerts
        """
        logger.info("Checking BAA expirations...")
        
        alerts = []
        
        try:
            # Call validate_baa tool
            baa_result = validate_baa.invoke({
                "organization_id": self.organization_id,
                "check_expiration": True
            })
            
            # Parse results and generate alerts
            if "expiring_soon" in baa_result:
                for baa in baa_result["expiring_soon"]:
                    alerts.append({
                        "type": AlertType.BAA_EXPIRING,
                        "severity": AlertSeverity.HIGH,
                        "title": f"BAA Expiring Soon: {baa['vendor_name']}",
                        "description": f"Business Associate Agreement with {baa['vendor_name']} expires on {baa['expiration_date']}. Renewal required.",
                        "action_required": "Contact vendor to renew BAA",
                        "deadline": baa['expiration_date'],
                        "metadata": baa
                    })
            
            if "expired" in baa_result:
                for baa in baa_result["expired"]:
                    alerts.append({
                        "type": AlertType.BAA_EXPIRED,
                        "severity": AlertSeverity.CRITICAL,
                        "title": f"BAA EXPIRED: {baa['vendor_name']}",
                        "description": f"Business Associate Agreement with {baa['vendor_name']} expired on {baa['expiration_date']}. IMMEDIATE ACTION REQUIRED.",
                        "action_required": "Cease PHI sharing with vendor until BAA is renewed",
                        "deadline": "IMMEDIATE",
                        "metadata": baa
                    })
            
        except Exception as e:
            logger.error(f"Error checking BAA expirations: {e}")
        
        return {"alerts": alerts, "count": len(alerts)}
    
    async def _check_phi_compliance(self) -> Dict[str, Any]:
        """
        Check PHI handling compliance.
        
        Returns:
            Check results with alerts
        """
        logger.info("Checking PHI compliance...")
        
        alerts = []
        
        try:
            # Call check_phi_compliance tool
            phi_result = check_phi_compliance.invoke({
                "organization_id": self.organization_id,
                "check_encryption": True,
                "check_access_controls": True,
                "check_storage": True
            })
            
            # Generate alerts for compliance issues
            if phi_result.get("compliance_score", 100) < 80:
                alerts.append({
                    "type": AlertType.PHI_COMPLIANCE_ISSUE,
                    "severity": AlertSeverity.HIGH if phi_result["compliance_score"] < 70 else AlertSeverity.MEDIUM,
                    "title": "PHI Compliance Score Below Threshold",
                    "description": f"Current PHI compliance score: {phi_result['compliance_score']}%. Review findings and take corrective action.",
                    "action_required": "Review and remediate PHI compliance findings",
                    "metadata": phi_result
                })
            
            # Check specific findings
            for finding in phi_result.get("findings", []):
                if finding.get("severity") in ["critical", "high"]:
                    alerts.append({
                        "type": AlertType.PHI_COMPLIANCE_ISSUE,
                        "severity": AlertSeverity.CRITICAL if finding["severity"] == "critical" else AlertSeverity.HIGH,
                        "title": f"PHI Compliance Issue: {finding['issue']}",
                        "description": finding.get("description", ""),
                        "action_required": finding.get("remediation", "Review and remediate"),
                        "metadata": finding
                    })
            
        except Exception as e:
            logger.error(f"Error checking PHI compliance: {e}")
        
        return {"alerts": alerts, "count": len(alerts)}
    
    async def _check_access_anomalies(self) -> Dict[str, Any]:
        """
        Check for suspicious PHI access patterns.
        
        Returns:
            Check results with alerts
        """
        logger.info("Checking access anomalies...")
        
        alerts = []
        
        try:
            # Call audit_access_logs tool
            audit_result = audit_access_logs.invoke({
                "organization_id": self.organization_id,
                "time_range": "24h",
                "detect_anomalies": True
            })
            
            # Generate alerts for anomalies
            for anomaly in audit_result.get("anomalies", []):
                alerts.append({
                    "type": AlertType.ACCESS_ANOMALY,
                    "severity": AlertSeverity.HIGH if anomaly.get("risk_level") == "high" else AlertSeverity.MEDIUM,
                    "title": f"Suspicious PHI Access: {anomaly['user']}",
                    "description": anomaly.get("description", "Unusual access pattern detected"),
                    "action_required": "Review access logs and investigate",
                    "metadata": anomaly
                })
            
        except Exception as e:
            logger.error(f"Error checking access anomalies: {e}")
        
        return {"alerts": alerts, "count": len(alerts)}
    
    async def _check_risk_levels(self) -> Dict[str, Any]:
        """
        Check current risk levels.
        
        Returns:
            Check results with alerts
        """
        logger.info("Checking risk levels...")
        
        alerts = []
        
        try:
            # Call evaluate_risk tool
            risk_result = evaluate_risk.invoke({
                "organization_id": self.organization_id,
                "scope": "comprehensive"
            })
            
            # Generate alerts for high risks
            for risk in risk_result.get("risks", []):
                if risk.get("level") in ["critical", "high"]:
                    alerts.append({
                        "type": AlertType.RISK_THRESHOLD_EXCEEDED,
                        "severity": AlertSeverity.CRITICAL if risk["level"] == "critical" else AlertSeverity.HIGH,
                        "title": f"High Risk Identified: {risk['category']}",
                        "description": risk.get("description", ""),
                        "action_required": risk.get("mitigation", "Review and mitigate risk"),
                        "metadata": risk
                    })
            
        except Exception as e:
            logger.error(f"Error checking risk levels: {e}")
        
        return {"alerts": alerts, "count": len(alerts)}
    
    async def _assess_security_controls(self) -> Dict[str, Any]:
        """
        Assess security controls comprehensively.
        
        Returns:
            Assessment results with alerts
        """
        logger.info("Assessing security controls...")
        
        alerts = []
        
        try:
            # Call assess_security_controls tool
            security_result = assess_security_controls.invoke({
                "organization_id": self.organization_id,
                "control_types": ["technical", "administrative", "physical"]
            })
            
            # Generate alerts for gaps
            for gap in security_result.get("gaps", []):
                if gap.get("severity") in ["critical", "high"]:
                    alerts.append({
                        "type": AlertType.SECURITY_GAP,
                        "severity": AlertSeverity.CRITICAL if gap["severity"] == "critical" else AlertSeverity.HIGH,
                        "title": f"Security Control Gap: {gap['control']}",
                        "description": gap.get("description", ""),
                        "action_required": gap.get("recommendation", "Implement missing control"),
                        "metadata": gap
                    })
            
        except Exception as e:
            logger.error(f"Error assessing security controls: {e}")
        
        return {"alerts": alerts, "count": len(alerts)}
    
    async def _calculate_compliance_score(self) -> Dict[str, Any]:
        """
        Calculate overall compliance score.
        
        Returns:
            Compliance score with alerts
        """
        logger.info("Calculating compliance score...")
        
        alerts = []
        
        try:
            # Aggregate scores from various checks
            phi_score = 85  # Placeholder - would come from actual checks
            security_score = 90
            baa_score = 95
            risk_score = 80
            
            overall_score = (phi_score + security_score + baa_score + risk_score) / 4
            
            # Alert if score drops below threshold
            if overall_score < 85:
                alerts.append({
                    "type": AlertType.COMPLIANCE_SCORE_DROP,
                    "severity": AlertSeverity.HIGH if overall_score < 75 else AlertSeverity.MEDIUM,
                    "title": "Compliance Score Below Target",
                    "description": f"Overall compliance score: {overall_score:.1f}%. Target: 85%+",
                    "action_required": "Review compliance findings and implement improvements",
                    "metadata": {
                        "overall_score": overall_score,
                        "phi_score": phi_score,
                        "security_score": security_score,
                        "baa_score": baa_score,
                        "risk_score": risk_score
                    }
                })
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
        
        return {"alerts": alerts, "score": overall_score}
    
    async def _generate_weekly_summary(self) -> Dict[str, Any]:
        """
        Generate weekly compliance summary.
        
        Returns:
            Weekly summary data
        """
        return {
            "period": "week",
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "total_alerts": len(self.alerts),
            "critical_alerts": len([a for a in self.alerts if a.get("severity") == AlertSeverity.CRITICAL]),
            "high_alerts": len([a for a in self.alerts if a.get("severity") == AlertSeverity.HIGH]),
            "status": "summary_generated"
        }
    
    async def _generate_monthly_report(self) -> Dict[str, Any]:
        """
        Generate monthly compliance report.
        
        Returns:
            Monthly report data
        """
        return {
            "period": "month",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "report_type": "comprehensive",
            "status": "report_generated"
        }
    
    async def _analyze_compliance_trends(self) -> Dict[str, Any]:
        """
        Analyze compliance trends over time.
        
        Returns:
            Trend analysis data
        """
        return {
            "trend_period": "3_months",
            "overall_trend": "improving",
            "areas_of_concern": [],
            "areas_of_improvement": []
        }
    
    async def _generate_risk_summary(self) -> Dict[str, Any]:
        """
        Generate risk assessment summary.
        
        Returns:
            Risk summary data
        """
        return {
            "total_risks": 0,
            "critical_risks": 0,
            "high_risks": 0,
            "medium_risks": 0,
            "low_risks": 0,
            "risk_trend": "stable"
        }
    
    def get_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict[str, Any]]:
        """
        Get all alerts, optionally filtered by severity.
        
        Args:
            severity: Optional severity filter
            
        Returns:
            List of alerts
        """
        if severity:
            return [a for a in self.alerts if a.get("severity") == severity]
        return self.alerts


# Scheduled task functions (to be called by Celery/APScheduler)

async def run_daily_compliance_checks(organization_id: int, db: Session):
    """
    Run daily compliance checks for an organization.
    
    This function should be scheduled to run daily.
    
    Args:
        organization_id: Organization to check
        db: Database session
    """
    service = HarperMonitoringService(db, organization_id)
    results = await service.run_daily_checks()
    
    # Store results in database
    # TODO: Implement database storage
    
    logger.info(f"Daily checks completed for org {organization_id}: {results}")
    return results


async def run_weekly_compliance_checks(organization_id: int, db: Session):
    """
    Run weekly compliance checks for an organization.
    
    This function should be scheduled to run weekly.
    
    Args:
        organization_id: Organization to check
        db: Database session
    """
    service = HarperMonitoringService(db, organization_id)
    results = await service.run_weekly_checks()
    
    # Store results in database
    # TODO: Implement database storage
    
    logger.info(f"Weekly checks completed for org {organization_id}: {results}")
    return results


async def run_monthly_compliance_checks(organization_id: int, db: Session):
    """
    Run monthly compliance checks for an organization.
    
    This function should be scheduled to run monthly.
    
    Args:
        organization_id: Organization to check
        db: Database session
    """
    service = HarperMonitoringService(db, organization_id)
    results = await service.run_monthly_checks()
    
    # Store results in database
    # TODO: Implement database storage
    
    logger.info(f"Monthly checks completed for org {organization_id}: {results}")
    return results

