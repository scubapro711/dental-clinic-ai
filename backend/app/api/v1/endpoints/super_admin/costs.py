"""
Super Admin - Cost Tracking Endpoints

Endpoints for managing and viewing infrastructure costs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta, date
from decimal import Decimal

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models import CostTracking, Organization, User
from app.services.bigquery_billing_service import get_bigquery_billing_service
from app.services.cost_sync_service import CostSyncService, sync_yesterday_costs, backfill_costs

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary")
def get_cost_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get cost summary for the specified period.
    
    Returns:
    - Total cost
    - Cost by service
    - Cost trends
    - Unit economics
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get total cost from database
    total_cost = db.query(func.sum(CostTracking.cost_amount)).filter(
        CostTracking.date >= start_date,
        CostTracking.date <= end_date
    ).scalar() or Decimal("0.0")
    
    # Get cost by service
    cost_by_service = db.query(
        CostTracking.service_name,
        func.sum(CostTracking.cost_amount).label("total_cost")
    ).filter(
        CostTracking.date >= start_date,
        CostTracking.date <= end_date
    ).group_by(
        CostTracking.service_name
    ).order_by(
        func.sum(CostTracking.cost_amount).desc()
    ).limit(20).all()
    
    # Calculate percentages
    by_service = []
    for service_name, service_cost in cost_by_service:
        percentage = (float(service_cost) / float(total_cost) * 100) if total_cost > 0 else 0
        by_service.append({
            "service": service_name,
            "cost": float(service_cost),
            "percentage": round(percentage, 2)
        })
    
    # Get daily costs for trends
    daily_costs = db.query(
        CostTracking.date,
        func.sum(CostTracking.cost_amount).label("total_cost")
    ).filter(
        CostTracking.date >= start_date,
        CostTracking.date <= end_date
    ).group_by(
        CostTracking.date
    ).order_by(
        CostTracking.date
    ).all()
    
    trends = [
        {
            "date": cost_date.isoformat(),
            "cost": float(cost_amount)
        }
        for cost_date, cost_amount in daily_costs
    ]
    
    # Calculate unit economics
    active_orgs = db.query(func.count(Organization.id)).filter(
        Organization.is_active == True
    ).scalar() or 0
    
    # TODO: Get total users count
    total_users = 0  # Placeholder
    
    cost_per_org = float(total_cost) / active_orgs if active_orgs > 0 else 0
    cost_per_user = float(total_cost) / total_users if total_users > 0 else 0
    
    return {
        "total_cost": float(total_cost),
        "currency": "USD",
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "by_service": by_service,
        "trends": trends,
        "unit_economics": {
            "cost_per_organization": round(cost_per_org, 2),
            "cost_per_user": round(cost_per_user, 2),
            "active_organizations": active_orgs,
            "total_users": total_users
        }
    }


@router.get("/by-service")
def get_cost_by_service(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get cost breakdown by GCP service."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    results = db.query(
        CostTracking.service_name,
        func.sum(CostTracking.cost_amount).label("total_cost")
    ).filter(
        CostTracking.date >= start_date,
        CostTracking.date <= end_date
    ).group_by(
        CostTracking.service_name
    ).order_by(
        func.sum(CostTracking.cost_amount).desc()
    ).limit(limit).all()
    
    # Calculate total for percentages
    total_cost = sum(cost for _, cost in results)
    
    return [
        {
            "service": service_name,
            "cost": float(cost),
            "percentage": round((float(cost) / float(total_cost) * 100), 2) if total_cost > 0 else 0
        }
        for service_name, cost in results
    ]


@router.get("/trends")
def get_cost_trends(
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get cost trends over time.
    
    Args:
        days: Number of days to include
        granularity: daily, weekly, or monthly
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    if granularity == "daily":
        results = db.query(
            CostTracking.date,
            func.sum(CostTracking.cost_amount).label("total_cost")
        ).filter(
            CostTracking.date >= start_date,
            CostTracking.date <= end_date
        ).group_by(
            CostTracking.date
        ).order_by(
            CostTracking.date
        ).all()
        
        return [
            {
                "date": cost_date.isoformat(),
                "cost": float(cost)
            }
            for cost_date, cost in results
        ]
    
    # TODO: Implement weekly and monthly aggregation
    return []


@router.post("/sync")
def sync_costs(
    days: int = Query(1, ge=1, le=90, description="Number of days to sync"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger cost sync from GCP BigQuery.
    
    Args:
        days: Number of days to sync (default: 1 = yesterday only)
    """
    bigquery_service = get_bigquery_billing_service()
    
    if not bigquery_service.is_configured():
        raise HTTPException(
            status_code=400,
            detail="GCP Billing export not configured. Please set up billing export to BigQuery first."
        )
    
    try:
        if days == 1:
            # Sync yesterday only
            result = sync_yesterday_costs(db)
        else:
            # Backfill multiple days
            result = backfill_costs(db, days)
        
        return result
        
    except Exception as e:
        logger.error(f"Error syncing costs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.get("/setup-status")
def get_setup_status(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Check if GCP Billing integration is properly configured.
    
    Returns setup status and instructions if not configured.
    """
    bigquery_service = get_bigquery_billing_service()
    is_configured = bigquery_service.is_configured()
    
    # Check if we have any cost data
    has_data = db.query(CostTracking).first() is not None
    
    # Get latest sync date
    latest_sync = db.query(func.max(CostTracking.date)).scalar()
    
    return {
        "is_configured": is_configured,
        "has_data": has_data,
        "latest_sync_date": latest_sync.isoformat() if latest_sync else None,
        "setup_instructions": {
            "step_1": "Enable Billing Export in GCP Console",
            "step_2": "Create BigQuery dataset for billing data",
            "step_3": "Set environment variables: GCP_PROJECT_ID, GCP_BILLING_DATASET, GCP_BILLING_TABLE",
            "step_4": "Grant BigQuery Data Viewer role to service account",
            "step_5": "Wait 24-48 hours for data to populate",
            "step_6": "Run manual sync to verify",
            "documentation": "https://cloud.google.com/billing/docs/how-to/export-data-bigquery"
        } if not is_configured else None
    }


@router.get("/by-organization")
def get_cost_by_organization(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get cost allocation by organization.
    
    Note: This requires proper tagging/labeling of GCP resources by organization.
    Currently returns estimated allocation based on usage metrics.
    """
    # TODO: Implement actual cost allocation based on GCP resource labels
    # For now, return placeholder data
    
    return {
        "status": "not_implemented",
        "message": "Cost allocation by organization requires GCP resource labeling",
        "instructions": [
            "1. Tag all GCP resources with organization_id label",
            "2. Update BigQuery queries to group by labels",
            "3. Implement cost allocation logic"
        ]
    }

