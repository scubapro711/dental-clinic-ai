"""
Super Admin Plan Management API endpoints.

Allows Super Admin to create, update, and manage subscription plans.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.plan_configuration import PlanConfiguration
from app.middleware.rate_limiter import limiter, get_rate_limit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/plans", tags=["Super Admin - Plans"])


# ==================== Schemas ====================

class PlanCreate(BaseModel):
    """Schema for creating a new plan"""
    plan_key: str = Field(..., min_length=1, max_length=50, description="Unique plan identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Display name")
    description: Optional[str] = Field(None, description="Plan description")
    amount: Decimal = Field(..., gt=0, description="Monthly price")
    currency: str = Field(default="ILS", min_length=3, max_length=3, description="Currency code")
    billing_interval: str = Field(default="month", description="Billing interval")
    trial_days: int = Field(default=30, ge=0, description="Trial period in days")
    max_users: Optional[int] = Field(None, ge=1, description="Maximum users (null = unlimited)")
    max_patients: Optional[int] = Field(None, ge=1, description="Maximum patients (null = unlimited)")
    features: List[str] = Field(default_factory=list, description="Feature keys")
    is_active: bool = Field(default=True, description="Is plan active")
    is_default: bool = Field(default=False, description="Is default plan")
    sort_order: int = Field(default=0, description="Display order")


class PlanUpdate(BaseModel):
    """Schema for updating an existing plan"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    billing_interval: Optional[str] = None
    trial_days: Optional[int] = Field(None, ge=0)
    max_users: Optional[int] = Field(None, ge=1)
    max_patients: Optional[int] = Field(None, ge=1)
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None


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

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("admin_plan_create"))
async def create_plan(
    request: Request,
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
):
    """
    Create a new subscription plan
    
    **Super Admin only**
    
    Body Parameters:
        - plan_key: Unique plan identifier (e.g., "starter")
        - name: Display name (e.g., "DentaFlow Starter")
        - description: Plan description
        - amount: Monthly price
        - currency: Currency code (default: "ILS")
        - billing_interval: Billing interval (default: "month")
        - trial_days: Trial period in days (default: 30)
        - max_users: Maximum users (null = unlimited)
        - max_patients: Maximum patients (null = unlimited)
        - features: List of feature keys
        - is_active: Is plan active (default: true)
        - is_default: Is default plan (default: false)
        - sort_order: Display order (default: 0)
    
    Returns:
        Created plan configuration
    """
    try:
        # Check if plan_key already exists
        existing = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_data.plan_key
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plan with key '{plan_data.plan_key}' already exists"
            )
        
        # If this is set as default, unset other defaults
        if plan_data.is_default:
            db.query(PlanConfiguration).update({"is_default": False})
        
        # Create plan
        plan = PlanConfiguration(
            plan_key=plan_data.plan_key,
            name=plan_data.name,
            description=plan_data.description,
            amount=plan_data.amount,
            currency=plan_data.currency,
            billing_interval=plan_data.billing_interval,
            trial_days=plan_data.trial_days,
            max_users=plan_data.max_users,
            max_patients=plan_data.max_patients,
            features=plan_data.features,
            is_active=plan_data.is_active,
            is_default=plan_data.is_default,
            sort_order=plan_data.sort_order
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Super Admin {admin_user.email} created plan: {plan.plan_key}")
        
        return plan.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create plan: {str(e)}")
        db.rollback()
        logger.error(f"Failed to create plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.get("/", response_model=List[dict])
async def list_all_plans(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user),
    include_inactive: bool = True
):
    """
    List all subscription plans
    
    **Super Admin only**
    
    Query Parameters:
        - include_inactive: Include inactive plans (default: true)
    
    Returns:
        List of all plan configurations
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


@router.get("/{plan_key}", response_model=dict)
async def get_plan_by_key(
    plan_key: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
):
    """
    Get a specific plan by key
    
    **Super Admin only**
    
    Path Parameters:
        - plan_key: Plan identifier
    
    Returns:
        Plan configuration
    """
    try:
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key
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


@router.patch("/{plan_key}", response_model=dict)
@limiter.limit(get_rate_limit("admin_plan_update"))
async def update_plan(
    request: Request,
    plan_key: str,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
):
    """
    Update an existing subscription plan
    
    **Super Admin only**
    
    Path Parameters:
        - plan_key: Plan identifier
    
    Body Parameters:
        - All fields are optional
        - Only provided fields will be updated
    
    Returns:
        Updated plan configuration
    """
    try:
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found: {plan_key}"
            )
        
        # Update fields
        update_data = plan_data.dict(exclude_unset=True)
        
        # If setting as default, unset other defaults
        if update_data.get("is_default"):
            db.query(PlanConfiguration).filter(
                PlanConfiguration.id != plan.id
            ).update({"is_default": False})
        
        for field, value in update_data.items():
            setattr(plan, field, value)
        
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Super Admin {admin_user.email} updated plan: {plan.plan_key}")
        
        return plan.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update plan: {str(e)}")
        db.rollback()
        logger.error(f"Failed to update plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.delete("/{plan_key}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(get_rate_limit("admin_plan_delete"))
async def delete_plan(
    request: Request,
    plan_key: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
):
    """
    Delete a subscription plan
    
    **Super Admin only**
    
    Path Parameters:
        - plan_key: Plan identifier
    
    Note: This is a hard delete. Consider deactivating instead.
    """
    try:
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found: {plan_key}"
            )
        
        # Check if any subscriptions use this plan
        from app.models.subscription import Subscription
        active_subs = db.query(Subscription).filter(
            Subscription.plan_tier == plan_key
        ).count()
        
        if active_subs > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete plan with {active_subs} active subscriptions. Deactivate instead."
            )
        
        db.delete(plan)
        db.commit()
        
        logger.info(f"Super Admin {admin_user.email} deleted plan: {plan.plan_key}")
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete plan: {str(e)}")
        db.rollback()
        logger.error(f"Failed to delete plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.post("/{plan_key}/activate", response_model=dict)
@limiter.limit(get_rate_limit("admin_plan_activate"))
async def activate_plan(
    request: Request,
    plan_key: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
):
    """
    Activate a subscription plan
    
    **Super Admin only**
    
    Path Parameters:
        - plan_key: Plan identifier
    
    Returns:
        Updated plan configuration
    """
    try:
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found: {plan_key}"
            )
        
        plan.is_active = True
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Super Admin {admin_user.email} activated plan: {plan.plan_key}")
        
        return plan.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate plan: {str(e)}")
        db.rollback()
        logger.error(f"Failed to activate plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.post("/{plan_key}/deactivate", response_model=dict)
@limiter.limit(get_rate_limit("admin_plan_deactivate"))
async def deactivate_plan(
    request: Request,
    plan_key: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_super_admin_user)
):
    """
    Deactivate a subscription plan
    
    **Super Admin only**
    
    Path Parameters:
        - plan_key: Plan identifier
    
    Returns:
        Updated plan configuration
    
    Note: Existing subscriptions will continue, but new subscriptions cannot be created.
    """
    try:
        plan = db.query(PlanConfiguration).filter(
            PlanConfiguration.plan_key == plan_key
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found: {plan_key}"
            )
        
        plan.is_active = False
        db.commit()
        db.refresh(plan)
        
        logger.info(f"Super Admin {admin_user.email} deactivated plan: {plan.plan_key}")
        
        return plan.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate plan: {str(e)}")
        db.rollback()
        logger.error(f"Failed to deactivate plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )

