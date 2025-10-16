"""
Super Admin - Analytics Endpoints

Advanced analytics endpoints for cohort analysis, LTV, retention, and funnels.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models import User
from app.services.analytics_service import get_analytics_service

router = APIRouter()


@router.get("/cohorts")
def get_cohort_analysis(
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get cohort analysis showing retention by signup month.
    
    Returns retention percentages for each cohort at different time intervals.
    """
    analytics = get_analytics_service(db)
    return analytics.cohort_analysis(months=months)


@router.get("/ltv")
def get_ltv_metrics(
    organization_id: Optional[int] = Query(None, description="Specific organization ID"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get Lifetime Value (LTV) metrics.
    
    If organization_id is provided, returns LTV for that specific organization.
    Otherwise, returns average LTV across all organizations.
    """
    analytics = get_analytics_service(db)
    return analytics.calculate_ltv(organization_id=organization_id)


@router.get("/ltv/predict/{organization_id}")
def predict_organization_ltv(
    organization_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Predict LTV for a specific organization based on current behavior.
    
    Uses MRR, average lifetime, and usage patterns to estimate future value.
    """
    analytics = get_analytics_service(db)
    return analytics.predict_ltv(organization_id=organization_id)


@router.get("/retention")
def get_retention_curve(
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get retention curve showing % of organizations still active over time.
    
    Returns monthly retention data points.
    """
    analytics = get_analytics_service(db)
    return analytics.retention_curve(months=months)


@router.get("/funnel")
def get_funnel_analysis(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get conversion funnel analysis from trial to paid.
    
    Shows:
    - Total signups
    - Trial conversions
    - Paid conversions
    - Conversion rates at each stage
    """
    analytics = get_analytics_service(db)
    return analytics.funnel_analysis()


@router.get("/churn")
def get_churn_analysis(
    months: int = Query(6, ge=1, le=12, description="Number of months to analyze"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get churn analysis and patterns.
    
    Returns:
    - Churn rate
    - Churned organizations count
    - Churn reasons breakdown
    """
    analytics = get_analytics_service(db)
    return analytics.churn_analysis(months=months)


@router.get("/summary")
def get_analytics_summary(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics summary with all key metrics.
    
    Combines cohort, LTV, retention, funnel, and churn data.
    """
    analytics = get_analytics_service(db)
    
    return {
        "ltv_metrics": analytics.calculate_ltv(),
        "funnel": analytics.funnel_analysis(),
        "churn": analytics.churn_analysis(months=6),
        "retention_3_months": analytics.retention_curve(months=3),
        "recent_cohorts": analytics.cohort_analysis(months=6)
    }

