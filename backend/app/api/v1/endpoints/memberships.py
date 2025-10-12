"""
Organization Membership API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.models.organization import Organization

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


@router.get("/organizations/{org_id}/memberships", response_model=List[MembershipResponse])
async def list_memberships(
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
async def add_member(
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


@router.get("/users/{user_id}/memberships", response_model=List[MembershipResponse])
async def list_user_memberships(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    List all organizations a user is a member of.
    
    Returns active memberships only.
    """
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.is_active == True
    ).all()
    
    return memberships


@router.delete("/organizations/{org_id}/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
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
async def update_member_role(
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
