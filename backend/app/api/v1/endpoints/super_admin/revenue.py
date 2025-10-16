"""
Super Admin - Revenue & Billing Endpoints

Endpoints for tracking revenue, subscriptions, and payments.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models import (
    User, Organization, Subscription, SubscriptionStatus,
    Payment, PaymentStatus, PlanConfiguration
)
from pydantic import BaseModel


router = APIRouter()


# Pydantic Schemas
class RevenueSummary(BaseModel):
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    growth_rate: float  # MRR growth rate (%)
    churn_rate: float  # Monthly churn rate (%)
    active_subscriptions: int
    trial_subscriptions: int
    canceled_subscriptions: int


class RevenueTrend(BaseModel):
    date: date
    mrr: float
    arr: float


class SubscriptionsSummary(BaseModel):
    active: int
    trial: int
    canceled: int
    past_due: int
    total: int


class PaymentsSummary(BaseModel):
    successful_count: int
    failed_count: int
    refunded_count: int
    total_amount: float
    stripe_fees: float
    net_revenue: float


# Helper Functions
def calculate_mrr(db: Session, target_date: date = None) -> float:
    """Calculate Monthly Recurring Revenue for a specific date."""
    if not target_date:
        target_date = date.today()
    
    # Get all active subscriptions
    active_subs = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.current_period_start <= target_date,
        or_(
            Subscription.current_period_end >= target_date,
            Subscription.current_period_end.is_(None)
        )
    ).all()
    
    total_mrr = 0.0
    for sub in active_subs:
        # Get plan configuration
        plan_config = db.query(PlanConfiguration).filter(
            PlanConfiguration.tier == sub.plan_tier,
            PlanConfiguration.is_active == True
        ).first()
        
        if plan_config:
            total_mrr += float(plan_config.price_monthly)
    
    return total_mrr


def calculate_churn_rate(db: Session, target_month: date = None) -> float:
    """Calculate monthly churn rate."""
    if not target_month:
        target_month = date.today().replace(day=1)
    
    # Get subscriptions at start of month
    start_of_month = target_month
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Count active at start
    active_start = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Subscription.created_at < start_of_month
    ).count()
    
    if active_start == 0:
        return 0.0
    
    # Count canceled during month
    canceled_during_month = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.CANCELED,
        Subscription.canceled_at >= start_of_month,
        Subscription.canceled_at <= end_of_month
    ).count()
    
    churn_rate = (canceled_during_month / active_start) * 100
    return round(churn_rate, 2)


# Endpoints
@router.get("/revenue/summary", response_model=RevenueSummary)
async def get_revenue_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get overall revenue summary.
    
    **Super Admin Only**
    
    Returns:
    - MRR (Monthly Recurring Revenue)
    - ARR (Annual Recurring Revenue)
    - Growth rate (vs last month)
    - Churn rate
    - Subscription counts by status
    """
    # Calculate current MRR
    current_mrr = calculate_mrr(db)
    
    # Calculate last month's MRR for growth rate
    last_month = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_mrr = calculate_mrr(db, last_month)
    
    # Calculate growth rate
    if last_month_mrr > 0:
        growth_rate = ((current_mrr - last_month_mrr) / last_month_mrr) * 100
    else:
        growth_rate = 0.0
    
    # Calculate ARR
    current_arr = current_mrr * 12
    
    # Calculate churn rate
    churn_rate = calculate_churn_rate(db)
    
    # Count subscriptions by status
    active_count = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).count()
    
    trial_count = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.TRIALING
    ).count()
    
    canceled_count = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.CANCELED
    ).count()
    
    return RevenueSummary(
        mrr=round(current_mrr, 2),
        arr=round(current_arr, 2),
        growth_rate=round(growth_rate, 2),
        churn_rate=churn_rate,
        active_subscriptions=active_count,
        trial_subscriptions=trial_count,
        canceled_subscriptions=canceled_count
    )


@router.get("/revenue/trends", response_model=List[RevenueTrend])
async def get_revenue_trends(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    granularity: str = Query("monthly", description="Granularity: daily, weekly, monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get revenue trends over time.
    
    **Super Admin Only**
    """
    # Default to last 12 months
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = (end_date - timedelta(days=365)).replace(day=1)
    
    trends = []
    current_date = start_date
    
    while current_date <= end_date:
        mrr = calculate_mrr(db, current_date)
        arr = mrr * 12
        
        trends.append(RevenueTrend(
            date=current_date,
            mrr=round(mrr, 2),
            arr=round(arr, 2)
        ))
        
        # Move to next period
        if granularity == "daily":
            current_date += timedelta(days=1)
        elif granularity == "weekly":
            current_date += timedelta(weeks=1)
        else:  # monthly
            # Move to first day of next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    return trends


@router.get("/subscriptions/summary", response_model=SubscriptionsSummary)
async def get_subscriptions_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get subscriptions summary by status.
    
    **Super Admin Only**
    """
    active = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE
    ).count()
    
    trial = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.TRIALING
    ).count()
    
    canceled = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.CANCELED
    ).count()
    
    past_due = db.query(Subscription).filter(
        Subscription.status == SubscriptionStatus.PAST_DUE
    ).count()
    
    total = active + trial + canceled + past_due
    
    return SubscriptionsSummary(
        active=active,
        trial=trial,
        canceled=canceled,
        past_due=past_due,
        total=total
    )


@router.get("/subscriptions", response_model=dict)
async def list_subscriptions(
    status: Optional[SubscriptionStatus] = Query(None, description="Filter by status"),
    plan: Optional[str] = Query(None, description="Filter by plan tier"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    List all subscriptions with filtering and pagination.
    
    **Super Admin Only**
    """
    query = db.query(Subscription)
    
    # Apply filters
    if status:
        query = query.filter(Subscription.status == status)
    
    if plan:
        query = query.filter(Subscription.plan_tier == plan)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    subscriptions = query.offset(offset).limit(limit).all()
    
    # Enrich with organization info
    result = []
    for sub in subscriptions:
        org = db.query(Organization).filter(
            Organization.id == sub.organization_id
        ).first()
        
        result.append({
            "id": str(sub.id),
            "organization_id": str(sub.organization_id),
            "organization_name": org.name if org else "Unknown",
            "status": sub.status,
            "plan_tier": sub.plan_tier,
            "trial_end": sub.trial_end,
            "current_period_start": sub.current_period_start,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
            "created_at": sub.created_at
        })
    
    return {
        "subscriptions": result,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/payments/summary", response_model=PaymentsSummary)
async def get_payments_summary(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get payments summary for a date range.
    
    **Super Admin Only**
    """
    # Default to current month
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date.replace(day=1)
    
    # Convert to datetime for comparison
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Count successful payments
    successful = db.query(Payment).filter(
        Payment.status == PaymentStatus.SUCCEEDED,
        Payment.created_at >= start_datetime,
        Payment.created_at <= end_datetime
    ).all()
    
    successful_count = len(successful)
    total_amount = sum(float(p.amount) for p in successful)
    
    # Count failed payments
    failed_count = db.query(Payment).filter(
        Payment.status == PaymentStatus.FAILED,
        Payment.created_at >= start_datetime,
        Payment.created_at <= end_datetime
    ).count()
    
    # Count refunded payments
    refunded = db.query(Payment).filter(
        Payment.status == PaymentStatus.REFUNDED,
        Payment.created_at >= start_datetime,
        Payment.created_at <= end_datetime
    ).all()
    
    refunded_count = len(refunded)
    
    # Estimate Stripe fees (2.9% + $0.30 per transaction)
    stripe_fees = sum(
        (float(p.amount) * 0.029) + 0.30
        for p in successful
    )
    
    net_revenue = total_amount - stripe_fees
    
    return PaymentsSummary(
        successful_count=successful_count,
        failed_count=failed_count,
        refunded_count=refunded_count,
        total_amount=round(total_amount, 2),
        stripe_fees=round(stripe_fees, 2),
        net_revenue=round(net_revenue, 2)
    )


@router.get("/payments", response_model=dict)
async def list_payments(
    status: Optional[PaymentStatus] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    List all payments with filtering and pagination.
    
    **Super Admin Only**
    """
    query = db.query(Payment)
    
    # Apply filters
    if status:
        query = query.filter(Payment.status == status)
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(Payment.created_at >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Payment.created_at <= end_datetime)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
    
    # Enrich with subscription and organization info
    result = []
    for payment in payments:
        subscription = db.query(Subscription).filter(
            Subscription.id == payment.subscription_id
        ).first()
        
        org = None
        if subscription:
            org = db.query(Organization).filter(
                Organization.id == subscription.organization_id
            ).first()
        
        result.append({
            "id": str(payment.id),
            "subscription_id": str(payment.subscription_id),
            "organization_name": org.name if org else "Unknown",
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "stripe_payment_intent_id": payment.stripe_payment_intent_id,
            "created_at": payment.created_at
        })
    
    return {
        "payments": result,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

