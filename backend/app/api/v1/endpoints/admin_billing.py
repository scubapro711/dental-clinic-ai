"""
Super Admin Billing Dashboard API endpoints.

Provides comprehensive billing and subscription analytics for Super Admin.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus
from app.models.plan_configuration import PlanConfiguration
from app.models.organization import Organization
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/billing", tags=["Super Admin - Billing"])


# ==================== Dependencies ====================

def get_super_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify current user is Super Admin
    
    Raises:
        403: If user is not Super Admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return current_user


# ==================== Endpoints ====================

@router.get("/stats")
async def get_billing_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
) -> Dict[str, Any]:
    """
    Get comprehensive billing statistics
    
    **Super Admin only**
    
    Returns:
        - monthly_revenue: Total MRR
        - revenue_growth: % growth from last month
        - active_subscriptions: Count of active subscriptions
        - trial_subscriptions: Count of trial subscriptions
        - conversion_rate: Trial to paid conversion rate
        - churn_rate: Monthly churn rate
        - canceled_this_month: Subscriptions canceled this month
        - plans: List of all plans with subscriber counts
    """
    try:
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        
        # Active subscriptions
        active_subs = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).count()
        
        # Trial subscriptions
        trial_subs = db.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.TRIALING
        ).count()
        
        # Monthly revenue (sum of all active subscriptions)
        monthly_revenue = db.query(
            func.sum(PlanConfiguration.amount)
        ).join(
            Subscription, Subscription.plan_id == PlanConfiguration.id
        ).filter(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
        ).scalar() or Decimal(0)
        
        # Revenue from last month (for growth calculation)
        last_month_revenue = db.query(
            func.sum(PlanConfiguration.amount)
        ).join(
            Subscription, Subscription.plan_id == PlanConfiguration.id
        ).filter(
            and_(
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]),
                Subscription.start_date < last_month
            )
        ).scalar() or Decimal(0)
        
        # Calculate revenue growth
        revenue_growth = 0
        if last_month_revenue > 0:
            revenue_growth = round(
                ((monthly_revenue - last_month_revenue) / last_month_revenue) * 100, 
                2
            )
        
        # Conversion rate (trials that converted to paid)
        total_trials = db.query(Subscription).filter(
            or_(
                Subscription.status == SubscriptionStatus.TRIALING,
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.trial_end.isnot(None),
                    Subscription.trial_end < now
                )
            )
        ).count()
        
        converted_trials = db.query(Subscription).filter(
            and_(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.trial_end.isnot(None),
                Subscription.trial_end < now
            )
        ).count()
        
        conversion_rate = 0
        if total_trials > 0:
            conversion_rate = round((converted_trials / total_trials) * 100, 2)
        
        # Churn rate (canceled this month / active at start of month)
        canceled_this_month = db.query(Subscription).filter(
            and_(
                Subscription.status == SubscriptionStatus.CANCELED,
                Subscription.canceled_at >= last_month
            )
        ).count()
        
        active_start_of_month = active_subs + canceled_this_month
        churn_rate = 0
        if active_start_of_month > 0:
            churn_rate = round((canceled_this_month / active_start_of_month) * 100, 2)
        
        # Plans with subscriber counts
        plans = db.query(PlanConfiguration).order_by(PlanConfiguration.sort_order).all()
        plans_data = []
        for plan in plans:
            sub_count = db.query(Subscription).filter(
                and_(
                    Subscription.plan_id == plan.id,
                    Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
                )
            ).count()
            plans_data.append({
                "id": plan.id,
                "name": plan.name,
                "subscribers": sub_count
            })
        
        return {
            "monthly_revenue": float(monthly_revenue),
            "revenue_growth": revenue_growth,
            "active_subscriptions": active_subs,
            "trial_subscriptions": trial_subs,
            "conversion_rate": conversion_rate,
            "churn_rate": churn_rate,
            "canceled_this_month": canceled_this_month,
            "plans": plans_data
        }
    
    except Exception as e:
        logger.error(f"Failed to get billing stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing statistics"
        )


@router.get("/subscriptions")
async def get_all_subscriptions(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user),
    status_filter: Optional[str] = None,
    plan_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get all subscriptions with filters
    
    **Super Admin only**
    
    Query Parameters:
        - status_filter: Filter by status (active, trialing, canceled, etc.)
        - plan_id: Filter by plan ID
        - limit: Maximum results (default: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        - subscriptions: List of subscriptions with organization and plan details
        - total: Total count
    """
    try:
        query = db.query(Subscription).join(
            Organization, Subscription.organization_id == Organization.id
        ).join(
            PlanConfiguration, Subscription.plan_id == PlanConfiguration.id
        )
        
        # Apply filters
        if status_filter:
            try:
                status_enum = SubscriptionStatus[status_filter.upper()]
                query = query.filter(Subscription.status == status_enum)
            except KeyError:
                pass
        
        if plan_id:
            query = query.filter(Subscription.plan_id == plan_id)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        subscriptions = query.order_by(
            Subscription.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Format results
        results = []
        for sub in subscriptions:
            org = db.query(Organization).filter(Organization.id == sub.organization_id).first()
            plan = db.query(PlanConfiguration).filter(PlanConfiguration.id == sub.plan_id).first()
            
            results.append({
                "id": sub.id,
                "organization_id": sub.organization_id,
                "organization_name": org.name if org else "Unknown",
                "plan_id": sub.plan_id,
                "plan_name": plan.name if plan else "Unknown",
                "status": sub.status.value,
                "monthly_price": float(plan.amount) if plan else 0,
                "discount_percentage": sub.discount_percentage or 0,
                "start_date": sub.start_date.isoformat() if sub.start_date else None,
                "trial_end": sub.trial_end.isoformat() if sub.trial_end else None,
                "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
                "canceled_at": sub.canceled_at.isoformat() if sub.canceled_at else None,
                "created_at": sub.created_at.isoformat() if sub.created_at else None
            })
        
        return {
            "subscriptions": results,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"Failed to get subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscriptions"
        )


@router.get("/subscription/{subscription_id}")
async def get_subscription_details(
    subscription_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific subscription
    
    **Super Admin only**
    
    Path Parameters:
        - subscription_id: Subscription ID
    
    Returns:
        Detailed subscription information including:
        - Subscription details
        - Organization details
        - Plan details
        - Invoice history
        - Payment history
    """
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Get organization
        org = db.query(Organization).filter(
            Organization.id == subscription.organization_id
        ).first()
        
        # Get plan
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.id == subscription.plan_id
        ).first()
        
        # Get invoices
        invoices = db.query(Invoice).filter(
            Invoice.subscription_id == subscription_id
        ).order_by(Invoice.created_at.desc()).all()
        
        # Get payments
        payments = db.query(Payment).filter(
            Payment.subscription_id == subscription_id
        ).order_by(Payment.created_at.desc()).all()
        
        return {
            "subscription": {
                "id": subscription.id,
                "status": subscription.status.value,
                "stripe_subscription_id": subscription.stripe_subscription_id,
                "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
                "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
                "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
                "discount_percentage": subscription.discount_percentage,
                "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
                "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None
            },
            "organization": {
                "id": org.id if org else None,
                "name": org.name if org else "Unknown",
                "email": org.email if org else None
            },
            "plan": {
                "id": plan.id if plan else None,
                "name": plan.name if plan else "Unknown",
                "amount": float(plan.amount) if plan else 0,
                "currency": plan.currency if plan else "ILS",
                "max_users": plan.max_users if plan else None,
                "max_patients": plan.max_patients if plan else None
            },
            "invoices": [
                {
                    "id": inv.id,
                    "number": inv.invoice_number,
                    "amount": float(inv.amount),
                    "status": inv.status.value,
                    "created_at": inv.created_at.isoformat() if inv.created_at else None,
                    "pdf_url": inv.pdf_url
                }
                for inv in invoices
            ],
            "payments": [
                {
                    "id": pay.id,
                    "amount": float(pay.amount),
                    "status": pay.status.value,
                    "payment_method": pay.payment_method,
                    "created_at": pay.created_at.isoformat() if pay.created_at else None
                }
                for pay in payments
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscription details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription details"
        )


@router.get("/revenue-chart")
async def get_revenue_chart_data(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user),
    months: int = 6
) -> Dict[str, Any]:
    """
    Get revenue data for chart visualization
    
    **Super Admin only**
    
    Query Parameters:
        - months: Number of months to retrieve (default: 6)
    
    Returns:
        Monthly revenue data for the specified period
    """
    try:
        now = datetime.utcnow()
        data = []
        
        for i in range(months):
            month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            # Get revenue for this month
            revenue = db.query(
                func.sum(Payment.amount)
            ).filter(
                and_(
                    Payment.status == PaymentStatus.SUCCEEDED,
                    Payment.created_at >= month_start,
                    Payment.created_at <= month_end
                )
            ).scalar() or Decimal(0)
            
            data.insert(0, {
                "month": month_start.strftime("%Y-%m"),
                "revenue": float(revenue)
            })
        
        return {
            "data": data
        }
    
    except Exception as e:
        logger.error(f"Failed to get revenue chart data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue data"
        )

