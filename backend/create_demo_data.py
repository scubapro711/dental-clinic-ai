"""
Demo Data Generation Script for DentaFlow

Creates a complete demo environment with:
- Demo organization
- Demo users (admin, dentist, receptionist)
- Demo conversations
- Odoo credentials (for testing)
"""

import os
import sys

# Load environment FIRST before any imports
with open(os.path.join(os.path.dirname(__file__), '.env.test')) as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.organization import Organization, SubscriptionTier
from app.models.user import User, UserRole
from app.models.organization_membership import OrganizationMembership
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message
from app.core.security import get_password_hash


def create_demo_data(db_url: str):
    """Create demo data in the database."""
    
    engine = create_engine(db_url)
    session = Session(engine)
    
    try:
        print("=== Creating Demo Data ===\n")
        
        # 1. Create Demo Organization
        print("1. Creating demo organization...")
        org = Organization(
            id=uuid4(),
            name="Demo Dental Clinic",
            slug="demo-clinic",
            description="Demo dental clinic for testing",
            email="demo@dentaflow.ai",
            phone="+972-50-123-4567",
            address="123 Demo Street, Tel Aviv, Israel",
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            subscription_status="active",
            subscription_start_date=datetime.utcnow(),
            odoo_db_name="demo_clinic",
            odoo_api_key="demo_api_key_12345",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(org)
        session.flush()
        print(f"   ✅ Organization created: {org.id}")
        
        # 2. Create Demo Users
        print("\n2. Creating demo users...")
        
        # Admin user
        admin = User(
            id=uuid4(),
            email="admin@demo.dentaflow.ai",
            hashed_password=get_password_hash("demo123"),
            full_name="Admin User",
            role=UserRole.ORG_ADMIN,
            organization_id=org.id,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(admin)
        print(f"   ✅ Admin user: {admin.email}")
        
        # Dentist user
        dentist = User(
            id=uuid4(),
            email="dentist@demo.dentaflow.ai",
            hashed_password=get_password_hash("demo123"),
            full_name="Dr. Sarah Cohen",
            role=UserRole.ORG_STAFF,
            organization_id=org.id,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(dentist)
        print(f"   ✅ Dentist user: {dentist.email}")
        
        # Receptionist user
        receptionist = User(
            id=uuid4(),
            email="receptionist@demo.dentaflow.ai",
            hashed_password=get_password_hash("demo123"),
            full_name="Alex Receptionist",
            role=UserRole.ORG_STAFF,
            organization_id=org.id,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(receptionist)
        print(f"   ✅ Receptionist user: {receptionist.email}")
        
        session.flush()
        
        # 3. Create Organization Memberships
        print("\n3. Creating organization memberships...")
        
        # Admin membership
        admin_membership = OrganizationMembership(
            id=uuid4(),
            user_id=admin.id,
            organization_id=org.id,
            organization_role="owner",
            functional_role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(admin_membership)
        print(f"   ✅ Admin membership created")
        
        # Dentist membership
        dentist_membership = OrganizationMembership(
            id=uuid4(),
            user_id=dentist.id,
            organization_id=org.id,
            organization_role="staff",
            functional_role="dentist",
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(dentist_membership)
        print(f"   ✅ Dentist membership created")
        
        # Receptionist membership
        receptionist_membership = OrganizationMembership(
            id=uuid4(),
            user_id=receptionist.id,
            organization_id=org.id,
            organization_role="staff",
            functional_role="receptionist",
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(receptionist_membership)
        print(f"   ✅ Receptionist membership created")
        
        # Note: Conversations and messages require more complex setup
        # They can be created through the API after login
        
        # Commit all changes
        session.commit()
        
        print("\n" + "="*50)
        print("✅ Demo data created successfully!")
        print("="*50)
        print("\n📋 Login Credentials:")
        print(f"   Admin:        admin@demo.dentaflow.ai / demo123")
        print(f"   Dentist:      dentist@demo.dentaflow.ai / demo123")
        print(f"   Receptionist: receptionist@demo.dentaflow.ai / demo123")
        print(f"\n🏢 Organization ID: {org.id}")
        print(f"🔑 Odoo DB: {org.odoo_db_name}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in .env.test")
        sys.exit(1)
    
    create_demo_data(db_url)
