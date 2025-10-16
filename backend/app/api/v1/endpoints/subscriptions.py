"""
Subscription API endpoints.

Handles subscription management, billing, and plan selection.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_membership
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier
from app.models.plan_configuration import PlanConfiguration
from app.services.stripe_service import StripeService
from app.middleware.rate_limiter import limiter, get_rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ==================== Public Endpoints ====================

@router.get("/plans", response_model=List[dict])
async def list_plans(
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """
    List available subscription plans
    
    Returns all active plans by default.
    Super Admin can include inactive plans.
    
    Query Parameters:
        - include_inactive: Include inactive plans (default: false)
    
    Returns:
        List of plan configurations
    """
    try:
        query = db.query(PlanConfiguration)
        
        if not include_inactive:
            query = query.filter(PlanConfiguration.is_active == True)
        
        plans = query.order_by(PlanConfiguration.sort_order).all()
        
        return [plan.to_dict() for plan in plans]
    
    except Exception as e:
        logger.error(f"Failed to list plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plans"
        )


@router.get("/plans/{plan_key}", response_model=dict)
async def get_plan(
    plan_key: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific plan by key
    
    Path Parameters:
        - plan_key: Plan identifier (e.g., "starter", "professional", "enterprise")
    
    Returns:
        Plan configuration
    """
    try:
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key,
            PlanConfiguration.is_active == True
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found: {plan_key}"
            )
        
        return plan.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan"
        )


# ==================== Authenticated Endpoints ====================

@router.post("/subscribe", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("subscription_create"))
async def create_subscription(
    request: Request,
    plan_key: str,
    apply_early_adopter: bool = False,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Create a new subscription
    
    Creates a subscription with a 30-day free trial.
    Requires payment method (will be charged after trial).
    
    Body Parameters:
        - plan_key: Plan identifier (e.g., "starter", "professional", "enterprise")
        - apply_early_adopter: Apply 20% early adopter discount (default: false)
    
    Returns:
        Subscription details
    
    Raises:
        400: If organization already has an active subscription
        404: If plan not found
        500: If subscription creation fails
    """
    try:
        organization = membership.organization
        
        # Check if organization already has an active subscription
        existing_sub = db.query(Subscription).filter(
            Subscription.organization_id == organization.id,
            Subscription.status.in_([
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.ACTIVE
            ])
        ).first()
        
        if existing_sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization already has an active subscription"
            )
        
        # Get plan configuration
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key,
            PlanConfiguration.is_active == True
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found: {plan_key}"
            )
        
        # Convert plan_key to PlanTier enum
        # This is a temporary mapping until we fully migrate to PlanConfiguration
        plan_tier_map = {
            "starter": PlanTier.STARTER,
            "professional": PlanTier.PROFESSIONAL,
            "enterprise": PlanTier.ENTERPRISE
        }
        plan_tier = plan_tier_map.get(plan_key)
        if not plan_tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan key: {plan_key}"
            )
        
        # Create subscription via Stripe
        stripe_service = StripeService(db)
        subscription = await stripe_service.create_subscription(
            organization=organization,
            plan_tier=plan_tier,
            trial_days=plan.trial_days,
            apply_early_adopter_discount=apply_early_adopter
        )
        
        logger.info(f"Created subscription {subscription.id} for org {organization.id}")
        
        return {
            "id": str(subscription.id),
            "organization_id": str(subscription.organization_id),
            "plan_tier": subscription.plan_tier.value,
            "status": subscription.status.value,
            "amount": float(subscription.amount),
            "currency": subscription.currency,
            "trial_start": subscription.trial_start.isoformat() if subscription.trial_start else None,
            "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
            "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            "stripe_subscription_id": subscription.stripe_subscription_id,
            "is_in_trial": subscription.is_in_trial,
            "created_at": subscription.created_at.isoformat() if subscription.created_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.get("/my-subscription", response_model=dict)
async def get_my_subscription(
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Get current user's organization subscription
    
    Returns:
        Subscription details or null if no subscription
    """
    try:
        organization = membership.organization
        
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization.id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            return {"subscription": None}
        
        return {
            "id": str(subscription.id),
            "organization_id": str(subscription.organization_id),
            "plan_tier": subscription.plan_tier.value,
            "status": subscription.status.value,
            "amount": float(subscription.amount),
            "currency": subscription.currency,
            "trial_start": subscription.trial_start.isoformat() if subscription.trial_start else None,
            "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
            "current_period_start": subscription.current_period_start.isoformat() if subscription.current_period_start else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
            "is_active": subscription.is_active,
            "is_in_trial": subscription.is_in_trial,
            "plan_limits": subscription.plan_limits,
            "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
            "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None
        }
    
    except Exception as e:
        logger.error(f"Failed to get subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription"
        )


@router.post("/my-subscription/cancel", response_model=dict)
@limiter.limit(get_rate_limit("subscription_cancel"))
async def cancel_my_subscription(
    request: Request,
    cancel_immediately: bool = False,
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    """
    Cancel current user's organization subscription
    
    Body Parameters:
        - cancel_immediately: Cancel immediately (default: false, cancels at period end)
    
    Returns:
        Updated subscription details
    """
    try:
        organization = membership.organization
        
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization.id,
            Subscription.status.in_([
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.ACTIVE
            ])
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Cancel subscription via Stripe
        stripe_service = StripeService(db)
        subscription = await stripe_service.cancel_subscription(
            subscription=subscription,
            cancel_immediately=cancel_immediately
        )
        
        logger.info(f"Canceled subscription {subscription.id} for org {organization.id}")
        
        return {
            "id": str(subscription.id),
            "status": subscription.status.value,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/my-subscription/invoices", response_model=List[dict])
async def get_my_invoices(
    db: Session = Depends(get_db),
    membership: OrganizationMembership = Depends(get_current_membership),
    limit: int = 10
):
    """
    Get invoices for current user's organization subscription
    
    Query Parameters:
        - limit: Maximum number of invoices to return (default: 10)
    
    Returns:
        List of invoices
    """
    try:
        organization = membership.organization
        
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization.id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            return []
        
        # Get invoices from Stripe
        stripe_service = StripeService(db)
        invoices = await stripe_service.list_invoices(
            subscription=subscription,
            limit=limit
        )
        
        return [
            {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "amount_due": float(invoice.amount_due),
                "amount_paid": float(invoice.amount_paid),
                "amount_remaining": float(invoice.amount_remaining),
                "currency": invoice.currency,
                "status": invoice.status.value,
                "invoice_pdf": invoice.invoice_pdf,
                "hosted_invoice_url": invoice.hosted_invoice_url,
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None
            }
            for invoice in invoices
        ]
    
    except Exception as e:
        logger.error(f"Failed to get invoices: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )

