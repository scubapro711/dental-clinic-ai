"""
Super Admin - Export Endpoints

Endpoints for exporting dashboard data to CSV.
"""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta, date

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models import (
    Organization, User, Subscription, Payment, UsageMetric, CostTracking
)
from app.utils.csv_export import (
    export_organizations_csv,
    export_revenue_csv,
    export_usage_csv,
    export_costs_csv,
    export_subscriptions_csv,
    export_payments_csv
)

router = APIRouter()


@router.get("/organizations")
def export_organizations(
    status: str = Query(None, regex="^(active|trialing|canceled|all)$"),
    plan: str = Query(None, regex="^(basic|professional|enterprise|all)$"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Export organizations to CSV.
    
    Query parameters:
    - status: Filter by subscription status
    - plan: Filter by subscription plan
    """
    query = db.query(Organization)
    
    # Apply filters
    if status and status != "all":
        query = query.filter(Organization.subscription_status == status)
    
    if plan and plan != "all":
        query = query.filter(Organization.subscription_tier == plan)
    
    organizations = query.all()
    
    # Convert to dict format
    org_data = [
        {
            "id": org.id,
            "name": org.name,
            "email": org.email,
            "subscription_tier": org.subscription_tier.value if org.subscription_tier else "",
            "subscription_status": org.subscription_status.value if org.subscription_status else "",
            "created_at": org.created_at.isoformat() if org.created_at else "",
            "trial_end": org.trial_end.isoformat() if org.trial_end else "",
            "is_active": org.is_active
        }
        for org in organizations
    ]
    
    # Generate CSV
    csv_content = export_organizations_csv(org_data)
    
    # Return as downloadable file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=organizations_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/subscriptions")
def export_subscriptions(
    status: str = Query(None),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Export subscriptions to CSV."""
    query = db.query(Subscription).join(Organization)
    
    if status:
        query = query.filter(Subscription.status == status)
    
    subscriptions = query.all()
    
    # Convert to dict format
    sub_data = [
        {
            "id": sub.id,
            "organization_name": sub.organization.name if sub.organization else "",
            "plan_tier": sub.plan_tier.value if sub.plan_tier else "",
            "status": sub.status.value if sub.status else "",
            "plan_price": float(sub.plan_price) if sub.plan_price else 0,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else "",
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else "",
            "trial_end": sub.trial_end.isoformat() if sub.trial_end else "",
            "created_at": sub.created_at.isoformat() if sub.created_at else ""
        }
        for sub in subscriptions
    ]
    
    csv_content = export_subscriptions_csv(sub_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=subscriptions_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/payments")
def export_payments(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Export payments to CSV."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    payments = db.query(Payment).join(Organization).filter(
        Payment.created_at >= start_date
    ).all()
    
    # Convert to dict format
    payment_data = [
        {
            "id": payment.id,
            "organization_name": payment.organization.name if payment.organization else "",
            "amount": float(payment.amount) if payment.amount else 0,
            "currency": payment.currency or "USD",
            "status": payment.status.value if payment.status else "",
            "payment_method": payment.payment_method or "",
            "created_at": payment.created_at.isoformat() if payment.created_at else "",
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else ""
        }
        for payment in payments
    ]
    
    csv_content = export_payments_csv(payment_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=payments_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/usage")
def export_usage(
    days: int = Query(30, ge=1, le=365),
    metric_type: str = Query(None),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Export usage metrics to CSV."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(UsageMetric).join(Organization).filter(
        UsageMetric.date >= start_date,
        UsageMetric.date <= end_date
    )
    
    if metric_type:
        query = query.filter(UsageMetric.metric_type == metric_type)
    
    usage_metrics = query.all()
    
    # Convert to dict format
    usage_data = [
        {
            "organization_id": metric.organization_id,
            "organization_name": metric.organization.name if metric.organization else "",
            "metric_type": metric.metric_type.value if metric.metric_type else "",
            "value": metric.value,
            "date": metric.date.isoformat() if metric.date else ""
        }
        for metric in usage_metrics
    ]
    
    csv_content = export_usage_csv(usage_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=usage_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/costs")
def export_costs(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Export cost data to CSV."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    costs = db.query(CostTracking).filter(
        CostTracking.date >= start_date,
        CostTracking.date <= end_date
    ).all()
    
    # Convert to dict format
    cost_data = [
        {
            "date": cost.date.isoformat() if cost.date else "",
            "service_name": cost.service_name or "",
            "cost_amount": float(cost.cost_amount) if cost.cost_amount else 0,
            "currency": cost.currency or "USD"
        }
        for cost in costs
    ]
    
    csv_content = export_costs_csv(cost_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=costs_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/revenue")
def export_revenue(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Export revenue data to CSV.
    
    Note: This calculates daily MRR/ARR from subscription data.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Calculate daily revenue metrics
    revenue_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Get active subscriptions on this date
        active_subs = db.query(Subscription).filter(
            Subscription.current_period_start <= current_date,
            Subscription.current_period_end >= current_date,
            Subscription.status.in_(["active", "trialing"])
        ).all()
        
        mrr = sum(float(sub.plan_price or 0) for sub in active_subs)
        arr = mrr * 12
        
        revenue_data.append({
            "date": current_date.isoformat(),
            "mrr": mrr,
            "arr": arr,
            "new_mrr": 0,  # TODO: Calculate new MRR
            "churned_mrr": 0,  # TODO: Calculate churned MRR
            "expansion_mrr": 0,  # TODO: Calculate expansion MRR
            "contraction_mrr": 0  # TODO: Calculate contraction MRR
        })
        
        current_date += timedelta(days=1)
    
    csv_content = export_revenue_csv(revenue_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=revenue_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )

