"""
Super Admin - Usage Tracking Endpoints

Endpoints for tracking and analyzing usage metrics across all organizations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models import User, Organization, UsageMetric, UsageMetricType
from pydantic import BaseModel


router = APIRouter()


# Pydantic Schemas
class UsageSummary(BaseModel):
    total_users: int
    total_conversations: int
    total_appointments: int
    total_patients: int
    total_storage_mb: int
    total_api_calls: int
    total_telegram_messages: int
    total_sms_sent: int
    total_emails_sent: int


class OrganizationUsage(BaseModel):
    organization_id: str
    organization_name: str
    metric_type: str
    value: int
    limit: Optional[int] = None
    percentage: Optional[float] = None


class UsageTrend(BaseModel):
    date: date
    value: int


class RecordUsageRequest(BaseModel):
    organization_id: str
    metric_type: UsageMetricType
    value: int
    date: Optional[date] = None


# Endpoints
@router.get("/usage/summary", response_model=UsageSummary)
async def get_usage_summary(
    start_date: Optional[date] = Query(None, description="Start date for metrics"),
    end_date: Optional[date] = Query(None, description="End date for metrics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get overall usage summary across all organizations.
    
    **Super Admin Only**
    
    Query Parameters:
    - start_date: Start date for metrics (default: 30 days ago)
    - end_date: End date for metrics (default: today)
    """
    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query usage metrics
    query = db.query(
        UsageMetric.metric_type,
        func.sum(UsageMetric.value).label('total')
    ).filter(
        UsageMetric.date >= start_date,
        UsageMetric.date <= end_date
    ).group_by(UsageMetric.metric_type)
    
    results = query.all()
    
    # Build summary
    summary = {
        "total_users": 0,
        "total_conversations": 0,
        "total_appointments": 0,
        "total_patients": 0,
        "total_storage_mb": 0,
        "total_api_calls": 0,
        "total_telegram_messages": 0,
        "total_sms_sent": 0,
        "total_emails_sent": 0
    }
    
    for metric_type, total in results:
        if metric_type == UsageMetricType.ACTIVE_USERS:
            summary["total_users"] = total
        elif metric_type == UsageMetricType.AI_CONVERSATIONS:
            summary["total_conversations"] = total
        elif metric_type == UsageMetricType.APPOINTMENTS_BOOKED:
            summary["total_appointments"] = total
        elif metric_type == UsageMetricType.PATIENTS_ADDED:
            summary["total_patients"] = total
        elif metric_type == UsageMetricType.STORAGE_USED_MB:
            summary["total_storage_mb"] = total
        elif metric_type == UsageMetricType.API_CALLS:
            summary["total_api_calls"] = total
        elif metric_type == UsageMetricType.TELEGRAM_MESSAGES:
            summary["total_telegram_messages"] = total
        elif metric_type == UsageMetricType.SMS_SENT:
            summary["total_sms_sent"] = total
        elif metric_type == UsageMetricType.EMAILS_SENT:
            summary["total_emails_sent"] = total
    
    return UsageSummary(**summary)


@router.get("/usage/by-organization", response_model=List[OrganizationUsage])
async def get_usage_by_organization(
    metric_type: Optional[UsageMetricType] = Query(None, description="Filter by metric type"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get usage metrics grouped by organization.
    
    **Super Admin Only**
    """
    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Build query
    query = db.query(
        UsageMetric.organization_id,
        UsageMetric.metric_type,
        func.sum(UsageMetric.value).label('total_value')
    ).filter(
        UsageMetric.date >= start_date,
        UsageMetric.date <= end_date
    )
    
    if metric_type:
        query = query.filter(UsageMetric.metric_type == metric_type)
    
    query = query.group_by(
        UsageMetric.organization_id,
        UsageMetric.metric_type
    ).order_by(func.sum(UsageMetric.value).desc())
    
    # Apply pagination
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()
    
    # Enrich with organization names
    usage_list = []
    for org_id, metric_type, total_value in results:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if org:
            usage_list.append(OrganizationUsage(
                organization_id=str(org_id),
                organization_name=org.name,
                metric_type=metric_type,
                value=total_value,
                limit=None,  # TODO: Get from plan limits
                percentage=None  # TODO: Calculate percentage
            ))
    
    return usage_list


@router.get("/usage/organization/{org_id}", response_model=dict)
async def get_organization_usage_details(
    org_id: str,
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get detailed usage metrics for a specific organization.
    
    **Super Admin Only**
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get usage metrics
    metrics = db.query(UsageMetric).filter(
        UsageMetric.organization_id == org_id,
        UsageMetric.date >= start_date,
        UsageMetric.date <= end_date
    ).all()
    
    # Aggregate by metric type
    usage = {}
    trends = {}
    
    for metric in metrics:
        metric_type = metric.metric_type
        
        # Aggregate totals
        if metric_type not in usage:
            usage[metric_type] = 0
        usage[metric_type] += metric.value
        
        # Build trends
        if metric_type not in trends:
            trends[metric_type] = []
        trends[metric_type].append({
            "date": metric.date,
            "value": metric.value
        })
    
    return {
        "organization": {
            "id": str(org.id),
            "name": org.name,
            "subscription_tier": org.subscription_tier
        },
        "usage": usage,
        "trends": trends,
        "limits": {}  # TODO: Get from plan configuration
    }


@router.get("/usage/trends", response_model=dict)
async def get_usage_trends(
    metric_type: UsageMetricType = Query(..., description="Metric type to track"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get usage trends over time for a specific metric type.
    
    **Super Admin Only**
    """
    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query daily totals
    query = db.query(
        UsageMetric.date,
        func.sum(UsageMetric.value).label('total')
    ).filter(
        UsageMetric.metric_type == metric_type,
        UsageMetric.date >= start_date,
        UsageMetric.date <= end_date
    ).group_by(UsageMetric.date).order_by(UsageMetric.date)
    
    results = query.all()
    
    trends = [
        {"date": result_date, "value": total}
        for result_date, total in results
    ]
    
    return {
        "metric_type": metric_type,
        "start_date": start_date,
        "end_date": end_date,
        "trends": trends
    }


@router.post("/usage/record")
async def record_usage_metric(
    record_request: RecordUsageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Manually record a usage metric (for testing or corrections).
    
    **Super Admin Only**
    """
    # Verify organization exists
    org = db.query(Organization).filter(
        Organization.id == record_request.organization_id
    ).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Default to today if no date provided
    metric_date = record_request.date or date.today()
    
    # Check if metric already exists for this date
    existing_metric = db.query(UsageMetric).filter(
        UsageMetric.organization_id == record_request.organization_id,
        UsageMetric.metric_type == record_request.metric_type,
        UsageMetric.date == metric_date
    ).first()
    
    if existing_metric:
        # Update existing metric
        existing_metric.value += record_request.value
        existing_metric.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_metric)
        return {
            "message": "Usage metric updated",
            "metric": {
                "id": existing_metric.id,
                "organization_id": str(existing_metric.organization_id),
                "metric_type": existing_metric.metric_type,
                "value": existing_metric.value,
                "date": existing_metric.date
            }
        }
    else:
        # Create new metric
        new_metric = UsageMetric(
            organization_id=record_request.organization_id,
            metric_type=record_request.metric_type,
            value=record_request.value,
            date=metric_date
        )
        db.add(new_metric)
        db.commit()
        db.refresh(new_metric)
        return {
            "message": "Usage metric recorded",
            "metric": {
                "id": new_metric.id,
                "organization_id": str(new_metric.organization_id),
                "metric_type": new_metric.metric_type,
                "value": new_metric.value,
                "date": new_metric.date
            }
        }

