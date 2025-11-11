"""
Organization Membership API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.middleware.rate_limiter import limiter, get_rate_limit
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.models.organization import Organization
from app.api.dependencies import get_current_user

router = APIRouter()


# Pydantic schemas
class MembershipCreate(BaseModel):
    """Schema for creating a membership."""
    user_id: UUID
    organization_id: UUID
    organization_role: str
    functional_role: str | None = None
    odoo_partner_id: int | None = None


class MembershipResponse(BaseModel):
    """Schema for membership response."""
    id: UUID
    user_id: UUID
    organization_id: UUID
    organization_role: str
    functional_role: str | None
    odoo_partner_id: int | None
    is_active: bool
    
    class Config:
        from_attributes = True


class UserOrganizationResponse(BaseModel):
    """
    Schema for user's organization response (enriched).
    
    This schema combines membership and organization data
    for a better user experience in organization selectors.
    """
    # Membership info
    id: UUID  # Membership ID
    organization_role: str  # User's role in this organization (e.g., 'org_admin', 'org_staff')
    functional_role: str | None  # User's functional role (e.g., 'dentist', 'receptionist')
    is_active: bool  # Whether membership is active
    
    # Organization info
    organization_id: UUID  # Organization UUID
    organization_name: str  # Organization display name
    organization_slug: str | None  # Organization URL slug
    
    class Config:
        from_attributes = True


@router.get("/organizations/{org_id}/memberships", response_model=List[MembershipResponse])
@limiter.limit(get_rate_limit("default"))
async def list_memberships(
    request: Request,
    org_id: UUID,
    db: Session = Depends(get_db)
):
    """
    List all members of an organization.
    
    Returns active memberships only.
    """
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org_id,
        OrganizationMembership.is_active == True
    ).all()
    
    return memberships


@router.post("/organizations/{org_id}/memberships", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("default"))
async def add_member(
    request: Request,
    org_id: UUID,
    membership_data: MembershipCreate,
    db: Session = Depends(get_db)
):
    """
    Add a user to an organization.
    
    Creates a new membership linking a user to an organization with specified roles.
    """
    # Verify organization exists
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == membership_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if membership already exists
    existing = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == membership_data.user_id,
        OrganizationMembership.organization_id == org_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this organization"
        )
    
    # Create membership
    membership = OrganizationMembership(
        user_id=membership_data.user_id,
        organization_id=org_id,
        organization_role=membership_data.organization_role,
        functional_role=membership_data.functional_role,
        odoo_partner_id=membership_data.odoo_partner_id
    )
    
    db.add(membership)
    db.commit()
    db.refresh(membership)
    
    return membership


@router.get("/users/me/organizations", response_model=List[UserOrganizationResponse])
@limiter.limit(get_rate_limit("default"))
async def get_my_organizations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's organizations (self-service endpoint).
    
    This endpoint returns enriched organization data combining:
    - Membership information (role, status)
    - Organization details (name, slug)
    
    **Use case:** Organization selector in UI, dashboard initialization
    
    **Security:** Automatically scoped to current authenticated user
    
    **Returns:** List of organizations with membership details
    
    **Example response:**
    ```json
    [
      {
        "id": "membership-uuid",
        "organization_role": "org_admin",
        "functional_role": "dentist",
        "is_active": true,
        "organization_id": "org-uuid",
        "organization_name": "Dr. Cohen Dental Clinic",
        "organization_slug": "cohen-dental"
      }
    ]
    ```
    
    **Note:** This is different from `/users/{user_id}/memberships` which:
    - Requires user_id parameter (admin use case)
    - Returns raw membership objects without enrichment
    - May require additional permissions
    """
    # Query active memberships for current user with organization data
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.is_active == True
    ).all()
    
    # Enrich with organization details
    result = []
    for membership in memberships:
        org = membership.organization  # SQLAlchemy relationship
        result.append(UserOrganizationResponse(
            # Membership fields
            id=membership.id,
            organization_role=membership.organization_role,
            functional_role=membership.functional_role,
            is_active=membership.is_active,
            # Organization fields
            organization_id=org.id,
            organization_name=org.name,
            organization_slug=org.slug
        ))
    
    return result


@router.get("/users/{user_id}/memberships", response_model=List[MembershipResponse])
@limiter.limit(get_rate_limit("default"))
async def list_user_memberships(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    List all organizations a user is a member of (admin endpoint).
    
    **Use case:** Admin viewing another user's organizations, debugging
    
    **Security:** May require admin permissions (add authorization check)
    
    **Returns:** Raw membership objects without enrichment
    
    **Note:** For self-service, use `/users/me/organizations` instead
    
    Returns active memberships only.
    """
    # TODO: Add authorization check - only allow if:
    # - Current user is super admin, OR
    # - Current user is org admin of the same organization, OR
    # - Current user is requesting their own memberships
    
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.is_active == True
    ).all()
    
    return memberships


@router.delete("/organizations/{org_id}/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(get_rate_limit("default"))
async def remove_member(
    request: Request,
    org_id: UUID,
    membership_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Remove a user from an organization.
    
    Soft deletes the membership by setting is_active to False.
    """
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.id == membership_id,
        OrganizationMembership.organization_id == org_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    # Soft delete
    membership.is_active = False
    db.commit()
    
    return None


@router.patch("/organizations/{org_id}/memberships/{membership_id}", response_model=MembershipResponse)
@limiter.limit(get_rate_limit("default"))
async def update_member_role(
    request: Request,
    org_id: UUID,
    membership_id: UUID,
    organization_role: str | None = None,
    functional_role: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Update a member's roles in an organization.
    """
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.id == membership_id,
        OrganizationMembership.organization_id == org_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    # Update roles
    if organization_role:
        membership.organization_role = organization_role
    if functional_role:
        membership.functional_role = functional_role
    
    db.commit()
    db.refresh(membership)
    
    return membership
