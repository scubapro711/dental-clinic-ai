"""
Seed Demo Data for DentaFlow Load Testing
==========================================

Creates demo organizations, users, and data for load testing.

Usage:
    python seed_demo_data.py

Author: Manus AI
Date: October 15, 2025
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.models.user import User, UserRole
from app.models.organization import Organization, SubscriptionTier
from app.models.organization_membership import OrganizationMembership
from app.core.security import get_password_hash


def create_demo_organizations(db: Session) -> list[Organization]:
    """Create 10 demo organizations"""
    
    clinics = [
        {"name": "DentaFlow Clinic", "slug": "dentaflow", "email": "info@dentaflow.ai"},
        {"name": "Smile Dental", "slug": "smile", "email": "info@smile-dental.com"},
        {"name": "Bright Teeth Clinic", "slug": "bright", "email": "info@brightteeth.com"},
        {"name": "Perfect Smile", "slug": "perfect", "email": "info@perfectsmile.com"},
        {"name": "Dental Care Plus", "slug": "care", "email": "info@dentalcareplus.com"},
        {"name": "Advanced Dentistry", "slug": "advanced", "email": "info@advanceddental.com"},
        {"name": "Family Dental", "slug": "family", "email": "info@familydental.com"},
        {"name": "Elite Dental Clinic", "slug": "elite", "email": "info@elitedental.com"},
        {"name": "Modern Dentistry", "slug": "modern", "email": "info@moderndental.com"},
        {"name": "Healthy Smiles", "slug": "healthy", "email": "info@healthysmiles.com"},
    ]
    
    organizations = []
    
    for clinic_data in clinics:
        # Check if already exists
        existing = db.query(Organization).filter_by(slug=clinic_data["slug"]).first()
        if existing:
            print(f"✓ Organization '{clinic_data['name']}' already exists")
            organizations.append(existing)
            continue
        
        org = Organization(
            name=clinic_data["name"],
            slug=clinic_data["slug"],
            email=clinic_data["email"],
            phone="+972-50-123-4567",
            address="123 Main St, Tel Aviv, Israel",
            subscription_tier="professional",
            subscription_status="active",
            is_active=True,
            odoo_db_name=f"dentaflow_{clinic_data['slug']}"
        )
        
        db.add(org)
        db.flush()  # Get the ID
        organizations.append(org)
        print(f"✓ Created organization: {org.name} (ID: {org.id})")
    
    db.commit()
    return organizations


def create_demo_users(db: Session, organizations: list[Organization]) -> list[User]:
    """Create demo users for each organization"""
    
    users = []
    
    # Common password for all demo users
    demo_password = get_password_hash("demo123")
    
    # Create staff users for each organization
    for org in organizations:
        # Admin user
        admin_email = f"admin@{org.slug}.ai"
        existing_admin = db.query(User).filter_by(email=admin_email).first()
        
        if not existing_admin:
            admin = User(
                email=admin_email,
                hashed_password=demo_password,
                full_name=f"{org.name} Admin",
                role=UserRole.ORG_ADMIN,
                organization_id=org.id,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.flush()
            users.append(admin)
            print(f"✓ Created admin: {admin.email}")
        else:
            users.append(existing_admin)
            print(f"✓ Admin already exists: {admin_email}")
        
        # Staff user (dentist)
        staff_email = f"staff@{org.slug}.ai"
        existing_staff = db.query(User).filter_by(email=staff_email).first()
        
        if not existing_staff:
            staff = User(
                email=staff_email,
                hashed_password=demo_password,
                full_name=f"Dr. {org.name} Staff",
                role=UserRole.ORG_STAFF,
                organization_id=org.id,
                is_active=True,
                is_verified=True
            )
            db.add(staff)
            db.flush()
            users.append(staff)
            print(f"✓ Created staff: {staff.email}")
        else:
            users.append(existing_staff)
            print(f"✓ Staff already exists: {staff_email}")
    
    # Create common demo users (used in load testing)
    common_users = [
        {
            "email": "rachel@dentaflow.ai",
            "full_name": "Dr. Rachel Cohen",
            "role": UserRole.ORG_ADMIN
        },
        {
            "email": "david@dentaflow.ai",
            "full_name": "Dr. David Levi",
            "role": UserRole.ORG_STAFF
        },
        {
            "email": "sarah@example.com",
            "full_name": "Sarah Johnson",
            "role": UserRole.PATIENT
        },
        {
            "email": "john@example.com",
            "full_name": "John Smith",
            "role": UserRole.PATIENT
        },
    ]
    
    # Use first organization for common users
    first_org = organizations[0]
    
    for user_data in common_users:
        existing = db.query(User).filter_by(email=user_data["email"]).first()
        
        if not existing:
            user = User(
                email=user_data["email"],
                hashed_password=demo_password,
                full_name=user_data["full_name"],
                role=user_data["role"],
                organization_id=first_org.id if user_data["role"] != UserRole.PATIENT else None,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.flush()
            users.append(user)
            print(f"✓ Created common user: {user.email}")
        else:
            users.append(existing)
            print(f"✓ Common user already exists: {user_data['email']}")
    
    db.commit()
    return users


def main():
    """Main seed function"""
    
    print("\n" + "="*80)
    print("🌱 Seeding Demo Data for DentaFlow")
    print("="*80 + "\n")
    
    # Create database session
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Note: Tables are created by Alembic migrations, not here
        # We only seed data
        
        # Create organizations
        print("🏢 Creating demo organizations...")
        organizations = create_demo_organizations(db)
        print(f"✓ Total organizations: {len(organizations)}\n")
        
        # Create users
        print("👥 Creating demo users...")
        users = create_demo_users(db, organizations)
        print(f"✓ Total users created: {len(users)}\n")
        
        print("="*80)
        print("✅ Demo data seeded successfully!")
        print("="*80)
        print("\n📝 Demo Credentials:")
        print("-" * 80)
        print("Common Users (for load testing):")
        print("  - rachel@dentaflow.ai / demo123 (Admin)")
        print("  - david@dentaflow.ai / demo123 (Staff)")
        print("  - sarah@example.com / demo123 (Patient)")
        print("  - john@example.com / demo123 (Patient)")
        print("\nPer-Clinic Users:")
        print("  - admin@{slug}.ai / demo123 (Admin)")
        print("  - staff@{slug}.ai / demo123 (Staff)")
        print("\nClinics:")
        for org in organizations:
            print(f"  - {org.name} (slug: {org.slug})")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

