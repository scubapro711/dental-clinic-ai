"""
Tests for Organization Membership functionality.
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.organization_membership import OrganizationMembership
from app.models.user import User
from app.models.organization import Organization


def test_create_membership(db: Session):
    """Test creating an organization membership."""
    # Create user
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    db.add(user)
    
    # Create organization
    org = Organization(
        name="Test Clinic",
        slug="test-clinic",
        email="clinic@example.com"
    )
    db.add(org)
    db.commit()
    
    # Create membership
    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=org.id,
        organization_role="staff",
        functional_role="dentist"
    )
    db.add(membership)
    db.commit()
    
    # Verify
    assert membership.id is not None
    assert membership.user_id == user.id
    assert membership.organization_id == org.id
    assert membership.is_active == True


def test_user_multiple_organizations(db: Session):
    """Test that a user can belong to multiple organizations."""
    # Create user
    user = User(
        email="multi@example.com",
        hashed_password="hashed",
        full_name="Multi User"
    )
    db.add(user)
    
    # Create two organizations
    org1 = Organization(name="Clinic 1", slug="clinic-1", email="c1@example.com")
    org2 = Organization(name="Clinic 2", slug="clinic-2", email="c2@example.com")
    db.add_all([org1, org2])
    db.commit()
    
    # Create memberships
    membership1 = OrganizationMembership(
        user_id=user.id,
        organization_id=org1.id,
        organization_role="owner"
    )
    membership2 = OrganizationMembership(
        user_id=user.id,
        organization_id=org2.id,
        organization_role="staff"
    )
    db.add_all([membership1, membership2])
    db.commit()
    
    # Verify
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id
    ).all()
    
    assert len(memberships) == 2
    assert memberships[0].organization_id != memberships[1].organization_id


def test_odoo_partner_link(db: Session):
    """Test linking membership to Odoo partner."""
    user = User(email="odoo@example.com", hashed_password="hashed", full_name="Odoo User")
    org = Organization(name="Odoo Clinic", slug="odoo-clinic", email="odoo@example.com")
    db.add_all([user, org])
    db.commit()
    
    # Create membership with Odoo link
    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=org.id,
        organization_role="patient",
        odoo_partner_id=123  # Odoo res.partner ID
    )
    db.add(membership)
    db.commit()
    
    # Verify
    assert membership.odoo_partner_id == 123
    
    # Query by Odoo ID
    found = db.query(OrganizationMembership).filter(
        OrganizationMembership.odoo_partner_id == 123
    ).first()
    
    assert found is not None
    assert found.user_id == user.id


def test_unique_constraint(db: Session):
    """Test that user can't have duplicate membership in same organization."""
    user = User(email="dup@example.com", hashed_password="hashed", full_name="Dup User")
    org = Organization(name="Dup Clinic", slug="dup-clinic", email="dup@example.com")
    db.add_all([user, org])
    db.commit()
    
    # First membership
    membership1 = OrganizationMembership(
        user_id=user.id,
        organization_id=org.id,
        organization_role="staff"
    )
    db.add(membership1)
    db.commit()
    
    # Try to create duplicate
    membership2 = OrganizationMembership(
        user_id=user.id,
        organization_id=org.id,
        organization_role="manager"
    )
    db.add(membership2)
    
    # Should raise IntegrityError
    with pytest.raises(Exception):  # IntegrityError
        db.commit()


def test_soft_delete(db: Session):
    """Test soft delete of membership."""
    user = User(email="soft@example.com", hashed_password="hashed", full_name="Soft User")
    org = Organization(name="Soft Clinic", slug="soft-clinic", email="soft@example.com")
    db.add_all([user, org])
    db.commit()
    
    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=org.id,
        organization_role="staff"
    )
    db.add(membership)
    db.commit()
    
    # Soft delete
    membership.is_active = False
    db.commit()
    
    # Verify still exists but inactive
    found = db.query(OrganizationMembership).filter(
        OrganizationMembership.id == membership.id
    ).first()
    
    assert found is not None
    assert found.is_active == False
    
    # Active memberships query should not include it
    active = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active == True
    ).all()
    
    assert len(active) == 0
