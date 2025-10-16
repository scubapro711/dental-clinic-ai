"""
Super Admin - Organizations Management Endpoints

Endpoints for managing all organizations in the system.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.api.dependencies import require_super_admin
from app.models import (
    Organization, User, OrganizationMembership,
    Subscription, UsageMetric, AdminAction, AdminActionType
)
from pydantic import BaseModel


router = APIRouter()


# Pydantic Schemas
class OrganizationListItem(BaseModel):
    id: str
    name: str
    email: str
    subscription_tier: str
    subscription_status: str
    is_active: bool
    created_at: datetime
    user_count: int
    subscription_id: Optional[str] = None
    trial_end: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrganizationDetail(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    email: str
    phone: Optional[str]
    address: Optional[str]
    subscription_tier: str
    subscription_status: str
    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    odoo_db_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class ExtendTrialRequest(BaseModel):
    days: int


class ChangePlanRequest(BaseModel):
    plan_tier: str


class SuspendOrganizationRequest(BaseModel):
    reason: str


# Helper Functions
async def log_admin_action(
    db: Session,
    admin_user_id: int,
    action_type: AdminActionType,
    target_type: str,
    target_id: int,
    action_details: dict,
    request: Request
):
    """Log admin action for audit trail."""
    action = AdminAction(
        admin_user_id=admin_user_id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        action_details=action_details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(action)
    db.commit()


# Endpoints
@router.get("/organizations", response_model=dict)
async def list_organizations(
    status: Optional[str] = Query(None, description="Filter by subscription status"),
    plan: Optional[str] = Query(None, description="Filter by subscription tier"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    List all organizations with filtering and pagination.
    
    **Super Admin Only**
    
    Query Parameters:
    - status: Filter by subscription status (active, trial, canceled, past_due)
    - plan: Filter by subscription tier (basic, professional, enterprise)
    - search: Search by organization name or email
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    """
    query = db.query(Organization)
    
    # Apply filters
    if status:
        query = query.filter(Organization.subscription_status == status)
    
    if plan:
        query = query.filter(Organization.subscription_tier == plan)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Organization.name.ilike(search_filter),
                Organization.email.ilike(search_filter)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    organizations = query.offset(offset).limit(limit).all()
    
    # Enrich with user count and subscription info
    result = []
    for org in organizations:
        user_count = db.query(OrganizationMembership).filter(
            OrganizationMembership.organization_id == org.id
        ).count()
        
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == org.id
        ).first()
        
        result.append({
            "id": str(org.id),
            "name": org.name,
            "email": org.email,
            "subscription_tier": org.subscription_tier,
            "subscription_status": org.subscription_status,
            "is_active": org.is_active,
            "created_at": org.created_at,
            "user_count": user_count,
            "subscription_id": str(subscription.id) if subscription else None,
            "trial_end": subscription.trial_end if subscription else None
        })
    
    return {
        "organizations": result,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/organizations/{org_id}", response_model=dict)
async def get_organization_details(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Get detailed information about a specific organization.
    
    **Super Admin Only**
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get users
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org_id
    ).all()
    
    users = []
    for membership in memberships:
        user = db.query(User).filter(User.id == membership.user_id).first()
        if user:
            users.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": membership.role,
                "is_active": user.is_active,
                "created_at": user.created_at
            })
    
    # Get subscription
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == org_id
    ).first()
    
    subscription_data = None
    if subscription:
        subscription_data = {
            "id": str(subscription.id),
            "status": subscription.status,
            "plan_tier": subscription.plan_tier,
            "trial_end": subscription.trial_end,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "stripe_subscription_id": subscription.stripe_subscription_id
        }
    
    # Get recent usage metrics (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    usage_metrics = db.query(UsageMetric).filter(
        UsageMetric.organization_id == org_id,
        UsageMetric.date >= thirty_days_ago
    ).all()
    
    usage_summary = {}
    for metric in usage_metrics:
        metric_type = metric.metric_type
        if metric_type not in usage_summary:
            usage_summary[metric_type] = 0
        usage_summary[metric_type] += metric.value
    
    return {
        "organization": OrganizationDetail.from_orm(org).dict(),
        "users": users,
        "subscription": subscription_data,
        "usage_summary": usage_summary
    }


@router.patch("/organizations/{org_id}", response_model=OrganizationDetail)
async def update_organization(
    org_id: str,
    update_data: OrganizationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Update organization details.
    
    **Super Admin Only**
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Track changes for audit log
    changes = {}
    
    # Update fields
    if update_data.name is not None:
        changes["name"] = {"old": org.name, "new": update_data.name}
        org.name = update_data.name
    
    if update_data.description is not None:
        changes["description"] = {"old": org.description, "new": update_data.description}
        org.description = update_data.description
    
    if update_data.email is not None:
        changes["email"] = {"old": org.email, "new": update_data.email}
        org.email = update_data.email
    
    if update_data.phone is not None:
        changes["phone"] = {"old": org.phone, "new": update_data.phone}
        org.phone = update_data.phone
    
    if update_data.address is not None:
        changes["address"] = {"old": org.address, "new": update_data.address}
        org.address = update_data.address
    
    if update_data.is_active is not None:
        changes["is_active"] = {"old": org.is_active, "new": update_data.is_active}
        org.is_active = update_data.is_active
    
    org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(org)
    
    # Log admin action
    await log_admin_action(
        db=db,
        admin_user_id=current_user.id,
        action_type=AdminActionType.UPDATE_ORGANIZATION,
        target_type="organization",
        target_id=org_id,
        action_details={"changes": changes},
        request=request
    )
    
    return OrganizationDetail.from_orm(org)


@router.post("/organizations/{org_id}/suspend")
async def suspend_organization(
    org_id: str,
    suspend_request: SuspendOrganizationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Suspend an organization.
    
    **Super Admin Only**
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    previous_status = org.subscription_status
    org.subscription_status = "suspended"
    org.is_active = False
    org.updated_at = datetime.utcnow()
    db.commit()
    
    # Log admin action
    await log_admin_action(
        db=db,
        admin_user_id=current_user.id,
        action_type=AdminActionType.SUSPEND_ORGANIZATION,
        target_type="organization",
        target_id=org_id,
        action_details={
            "reason": suspend_request.reason,
            "previous_status": previous_status,
            "new_status": "suspended"
        },
        request=request
    )
    
    return {"message": "Organization suspended successfully"}


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: str,
    request: Request,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Delete an organization (soft delete by default).
    
    **Super Admin Only**
    
    Query Parameters:
    - hard_delete: If true, permanently delete. If false (default), soft delete.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if hard_delete:
        # Permanent deletion
        db.delete(org)
        action_type = AdminActionType.DELETE_ORGANIZATION
        action_details = {"type": "hard_delete"}
    else:
        # Soft deletion
        org.deleted_at = datetime.utcnow()
        org.is_active = False
        action_type = AdminActionType.DELETE_ORGANIZATION
        action_details = {"type": "soft_delete"}
    
    db.commit()
    
    # Log admin action
    await log_admin_action(
        db=db,
        admin_user_id=current_user.id,
        action_type=action_type,
        target_type="organization",
        target_id=org_id,
        action_details=action_details,
        request=request
    )
    
    return {"message": "Organization deleted successfully"}


@router.post("/organizations/{org_id}/extend-trial")
async def extend_trial(
    org_id: str,
    extend_request: ExtendTrialRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Extend the trial period for an organization.
    
    **Super Admin Only**
    """
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == org_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    if not subscription.trial_end:
        raise HTTPException(status_code=400, detail="Organization is not in trial period")
    
    from datetime import timedelta
    old_trial_end = subscription.trial_end
    subscription.trial_end = subscription.trial_end + timedelta(days=extend_request.days)
    db.commit()
    
    # Log admin action
    await log_admin_action(
        db=db,
        admin_user_id=current_user.id,
        action_type=AdminActionType.EXTEND_TRIAL,
        target_type="subscription",
        target_id=subscription.id,
        action_details={
            "organization_id": org_id,
            "days_extended": extend_request.days,
            "old_trial_end": old_trial_end.isoformat(),
            "new_trial_end": subscription.trial_end.isoformat()
        },
        request=request
    )
    
    return {
        "message": f"Trial extended by {extend_request.days} days",
        "new_trial_end": subscription.trial_end
    }


@router.post("/organizations/{org_id}/change-plan")
async def change_plan(
    org_id: str,
    change_request: ChangePlanRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """
    Change the subscription plan for an organization.
    
    **Super Admin Only**
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == org_id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    old_plan = subscription.plan_tier
    subscription.plan_tier = change_request.plan_tier
    org.subscription_tier = change_request.plan_tier
    db.commit()
    
    # Log admin action
    await log_admin_action(
        db=db,
        admin_user_id=current_user.id,
        action_type=AdminActionType.CHANGE_PLAN,
        target_type="subscription",
        target_id=subscription.id,
        action_details={
            "organization_id": org_id,
            "old_plan": old_plan,
            "new_plan": change_request.plan_tier
        },
        request=request
    )
    
    return {
        "message": f"Plan changed from {old_plan} to {change_request.plan_tier}",
        "new_plan": change_request.plan_tier
    }

