"""
User API endpoints.

Handles user-centric operations:
- Get current user's organizations
- Get/update user profile
- User settings and preferences

All endpoints under /users/* are user-focused,
as opposed to organization-focused (/organizations/*)
or membership-focused (/memberships/*).
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

router = APIRouter(prefix="/users", tags=["Users"])


# ========== Schemas ==========

class UserOrganizationResponse(BaseModel):
    """
    Schema for user's organization response (enriched).
    
    This schema combines membership and organization data
    for a better user experience in organization selectors.
    
    **Design rationale:**
    - Frontend needs both membership (role) and organization (name) data
    - Single endpoint call instead of multiple requests
    - Optimized for UI components like organization switchers
    """
    # Membership info
    id: UUID  # Membership ID
    organization_role: str  # User's role in this organization (e.g., 'org_admin', 'org_staff')
    functional_role: str | None  # User's functional role (e.g., 'dentist', 'receptionist')
    is_active: bool  # Whether membership is active
    
    # Organization info (enriched from relationship)
    organization_id: UUID  # Organization UUID
    organization_name: str  # Organization display name
    organization_slug: str | None  # Organization URL slug
    
    class Config:
        from_attributes = True


# ========== Endpoints ==========

@router.get("/me/organizations", response_model=List[UserOrganizationResponse])
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
    
    **API Design Notes:**
    - Uses `/users/me/*` pattern (RESTful convention for "current user")
    - Returns enriched data (membership + organization) in single call
    - Separate from `/memberships/*` which is for admin operations
    - Separate from `/organizations/*` which is for org management
    
    **Related endpoints:**
    - `GET /memberships/users/{user_id}/memberships` - Admin viewing another user's memberships
    - `GET /organizations/{org_id}/memberships` - List all members of an organization
    """
    # Query active memberships for current user with organization data
    # Using SQLAlchemy relationship to eager load organization details
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.is_active == True
    ).all()
    
    # Enrich with organization details
    result = []
    for membership in memberships:
        org = membership.organization  # SQLAlchemy relationship (lazy load)
        
        # Build enriched response
        result.append(UserOrganizationResponse(
            # Membership fields
            id=membership.id,
            organization_role=membership.organization_role,
            functional_role=membership.functional_role,
            is_active=membership.is_active,
            # Organization fields (from relationship)
            organization_id=org.id,
            organization_name=org.name,
            organization_slug=org.slug
        ))
    
    return result


# ========== Future endpoints (placeholders) ==========
# 
# @router.get("/me/profile")
# async def get_my_profile(...):
#     """Get current user's profile."""
#     pass
# 
# @router.patch("/me/profile")
# async def update_my_profile(...):
#     """Update current user's profile."""
#     pass
# 
# @router.get("/me/settings")
# async def get_my_settings(...):
#     """Get current user's settings."""
#     pass
# 
# @router.patch("/me/settings")
# async def update_my_settings(...):
#     """Update current user's settings."""
#     pass
