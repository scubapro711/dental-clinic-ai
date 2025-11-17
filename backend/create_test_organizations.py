"""
Create test organizations for multi-tenancy security validation.
"""

import os
import sys
from uuid import uuid4
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.organization import Organization, SubscriptionTier

def create_test_organizations():
    """Create 2 test organizations for security validation."""
    db = SessionLocal()
    
    try:
        # Organization 1: Test Clinic Alpha
        org1_id = uuid4()
        org1 = Organization(
            id=org1_id,
            name="Test Clinic Alpha",
            slug="test-clinic-alpha",
            description="Test organization for multi-tenancy validation",
            email="alpha@test-clinic.com",
            phone="+972-50-1234567",
            address="123 Test Street, Tel Aviv",
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            subscription_status="active",
            subscription_start_date=datetime.utcnow(),
            odoo_db_name="test_clinic_alpha_db",
            odoo_api_key="test_alpha_api_key_12345",
            is_active=True
        )
        
        # Organization 2: Test Clinic Beta
        org2_id = uuid4()
        org2 = Organization(
            id=org2_id,
            name="Test Clinic Beta",
            slug="test-clinic-beta",
            description="Test organization for multi-tenancy validation",
            email="beta@test-clinic.com",
            phone="+972-50-7654321",
            address="456 Test Avenue, Jerusalem",
            subscription_tier=SubscriptionTier.ENTERPRISE,
            subscription_status="active",
            subscription_start_date=datetime.utcnow(),
            odoo_db_name="test_clinic_beta_db",
            odoo_api_key="test_beta_api_key_67890",
            is_active=True
        )
        
        # Check if they already exist
        existing_alpha = db.query(Organization).filter(Organization.slug == "test-clinic-alpha").first()
        existing_beta = db.query(Organization).filter(Organization.slug == "test-clinic-beta").first()
        
        if existing_alpha:
            print(f"✅ Test Clinic Alpha already exists: {existing_alpha.id}")
            org1_id = existing_alpha.id
        else:
            db.add(org1)
            db.commit()
            print(f"✅ Created Test Clinic Alpha: {org1_id}")
        
        if existing_beta:
            print(f"✅ Test Clinic Beta already exists: {existing_beta.id}")
            org2_id = existing_beta.id
        else:
            db.add(org2)
            db.commit()
            print(f"✅ Created Test Clinic Beta: {org2_id}")
        
        print(f"\n📋 Test Organization IDs:")
        print(f"   Alpha: {org1_id}")
        print(f"   Beta:  {org2_id}")
        
        return str(org1_id), str(org2_id)
        
    except Exception as e:
        print(f"❌ Error creating test organizations: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_organizations()
