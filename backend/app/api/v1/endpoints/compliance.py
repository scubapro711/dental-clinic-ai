"""
Harper Compliance API Endpoints

Provides API endpoints for HIPAA compliance monitoring, alerts,
and Harper chat interactions.

Only accessible to clinic_admin and super_admin roles.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.compliance_alert import (
    ComplianceAlert,
    ComplianceMetric,
    AlertSeverity,
    AlertType,
    AlertStatus
)
from app.agents.harper_hipaa import HarperAgent
from app.services.harper_monitoring import HarperMonitoringService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/compliance", tags=["Harper Compliance"])


# ==================== Pydantic Models ====================

class ChatMessage(BaseModel):
    """Chat message model."""
    message: str = Field(..., description="User message to Harper")
    conversation_history: Optional[List[dict]] = Field(default=None, description="Previous conversation messages")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Harper's response")
    suggested_actions: Optional[List[dict]] = Field(default=None, description="Suggested follow-up actions")


class AlertActionRequest(BaseModel):
    """Alert action request model."""
    notes: Optional[str] = Field(default=None, description="Notes for the action")


class ComplianceScoreResponse(BaseModel):
    """Compliance score response model."""
    overall: int = Field(..., description="Overall compliance score (0-100)")
    phi: int = Field(..., description="PHI compliance score")
    security: int = Field(..., description="Security controls score")
    phi_findings: int = Field(..., description="Number of PHI findings")
    security_gaps: int = Field(..., description="Number of security gaps")


class ComplianceMetricsResponse(BaseModel):
    """Compliance metrics response model."""
    overall_score: int
    overall_trend: int
    overall_last_month: int
    phi_score: int
    phi_trend: int
    phi_last_month: int
    security_score: int
    security_trend: int
    security_last_month: int
    baa_score: int
    baa_trend: int
    active_baas: int
    risk_level: str
    total_risks: int
    critical_risks: int
    high_risks: int
    total_findings: int
    findings_trend: int
    resolved_findings: int
    recent_activity: List[dict]


# ==================== Harper Chat ====================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with Harper",
    description="Send a message to Harper, the HIPAA Compliance Agent, and receive guidance on compliance matters.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def chat_with_harper(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with Harper for HIPAA compliance guidance.
    
    Harper can help with:
    - HIPAA regulations and requirements
    - PHI handling and security
    - Business Associate Agreements (BAAs)
    - Breach notification procedures
    - Patient rights and privacy
    - Risk assessments and compliance audits
    """
    try:
        # Initialize Harper agent
        harper = HarperAgent()
        
        # Get response from Harper
        response = await harper.process_message(
            message=message.message,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            conversation_history=message.conversation_history or []
        )
        
        return ChatResponse(
            response=response.get("response", ""),
            suggested_actions=response.get("suggested_actions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# ==================== Compliance Score ====================

@router.get(
    "/score",
    response_model=ComplianceScoreResponse,
    summary="Get compliance score",
    description="Get the current HIPAA compliance score for the organization.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def get_compliance_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current compliance score."""
    try:
        monitoring_service = HarperMonitoringService(db)
        score = await monitoring_service.calculate_compliance_score(current_user.organization_id)
        
        return ComplianceScoreResponse(**score)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching compliance score: {str(e)}")


# ==================== Compliance Alerts ====================

@router.get(
    "/alerts",
    summary="Get compliance alerts",
    description="Get compliance alerts filtered by status, severity, or type.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def get_compliance_alerts(
    status: Optional[AlertStatus] = Query(default=None, description="Filter by alert status"),
    severity: Optional[AlertSeverity] = Query(default=None, description="Filter by severity"),
    alert_type: Optional[AlertType] = Query(default=None, description="Filter by alert type"),
    limit: int = Query(default=50, le=100, description="Maximum number of alerts to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get compliance alerts for the organization."""
    try:
        query = db.query(ComplianceAlert).filter(
            ComplianceAlert.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(ComplianceAlert.status == status)
        if severity:
            query = query.filter(ComplianceAlert.severity == severity)
        if alert_type:
            query = query.filter(ComplianceAlert.alert_type == alert_type)
        
        alerts = query.order_by(ComplianceAlert.created_at.desc()).limit(limit).all()
        
        return [alert.to_dict() for alert in alerts]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")


@router.post(
    "/alerts/{alert_id}/acknowledge",
    summary="Acknowledge alert",
    description="Mark an alert as acknowledged.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def acknowledge_alert(
    alert_id: int,
    action: AlertActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge a compliance alert."""
    try:
        alert = db.query(ComplianceAlert).filter(
            ComplianceAlert.id == alert_id,
            ComplianceAlert.organization_id == current_user.organization_id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.acknowledge(current_user.id)
        db.commit()
        
        return {"message": "Alert acknowledged successfully", "alert": alert.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")


@router.post(
    "/alerts/{alert_id}/start_progress",
    summary="Start working on alert",
    description="Mark an alert as in progress.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def start_alert_progress(
    alert_id: int,
    action: AlertActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start working on a compliance alert."""
    try:
        alert = db.query(ComplianceAlert).filter(
            ComplianceAlert.id == alert_id,
            ComplianceAlert.organization_id == current_user.organization_id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.start_progress()
        db.commit()
        
        return {"message": "Alert marked as in progress", "alert": alert.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating alert: {str(e)}")


@router.post(
    "/alerts/{alert_id}/resolve",
    summary="Resolve alert",
    description="Mark an alert as resolved with optional resolution notes.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def resolve_alert(
    alert_id: int,
    action: AlertActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a compliance alert."""
    try:
        alert = db.query(ComplianceAlert).filter(
            ComplianceAlert.id == alert_id,
            ComplianceAlert.organization_id == current_user.organization_id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.resolve(current_user.id, action.notes)
        db.commit()
        
        return {"message": "Alert resolved successfully", "alert": alert.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")


@router.post(
    "/alerts/{alert_id}/dismiss",
    summary="Dismiss alert",
    description="Dismiss an alert with optional reason.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def dismiss_alert(
    alert_id: int,
    action: AlertActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss a compliance alert."""
    try:
        alert = db.query(ComplianceAlert).filter(
            ComplianceAlert.id == alert_id,
            ComplianceAlert.organization_id == current_user.organization_id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.dismiss(current_user.id, action.notes)
        db.commit()
        
        return {"message": "Alert dismissed successfully", "alert": alert.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error dismissing alert: {str(e)}")


# ==================== Compliance Metrics ====================

@router.get(
    "/metrics",
    response_model=ComplianceMetricsResponse,
    summary="Get compliance metrics",
    description="Get historical compliance metrics and trends.",
    dependencies=[Depends(require_role(["clinic_admin", "super_admin"]))]
)
async def get_compliance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get compliance metrics and trends."""
    try:
        monitoring_service = HarperMonitoringService(db)
        metrics = await monitoring_service.get_compliance_metrics(current_user.organization_id)
        
        return ComplianceMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metrics: {str(e)}")


# ==================== Proactive Monitoring ====================

@router.post(
    "/monitoring/run-checks",
    summary="Run compliance checks",
    description="Manually trigger compliance checks (admin only).",
    dependencies=[Depends(require_role(["super_admin"]))]
)
async def run_compliance_checks(
    check_type: str = Query(..., description="Type of check: daily, weekly, or monthly"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger compliance checks."""
    try:
        monitoring_service = HarperMonitoringService(db)
        
        if check_type == "daily":
            results = await monitoring_service.run_daily_checks(current_user.organization_id)
        elif check_type == "weekly":
            results = await monitoring_service.run_weekly_checks(current_user.organization_id)
        elif check_type == "monthly":
            results = await monitoring_service.run_monthly_checks(current_user.organization_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid check type. Must be: daily, weekly, or monthly")
        
        return {
            "message": f"{check_type.capitalize()} checks completed",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running checks: {str(e)}")

