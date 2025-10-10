#!/usr/bin/env python3
"""
Test Data Creation Script

Creates test users, patients, and mappings for development and testing.
Usage: python scripts/create_test_data.py [--reset]
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import logging

from app.core.database import SessionLocal, engine
from app.models.user import User
from app.crud import user_patient_mapping as mapping_crud
from app.integrations.odoo_client_v2 import OdooClientV2

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Test data
TEST_USERS = [
    {
        "email": "admin@dentaflow.test",
        "password": "Admin123!",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "is_verified": True
    },
    {
        "email": "patient@dentaflow.test",
        "password": "Patient123!",
        "full_name": "Test Patient",
        "role": "patient",
        "is_active": True,
        "is_verified": True
    },
    {
        "email": "staff@dentaflow.test",
        "password": "Staff123!",
        "full_name": "Staff Member",
        "role": "staff",
        "is_active": True,
        "is_verified": True
    }
]


def print_header(text: str):
    """Print header."""
    print("\n" + "=" * 70)
    print(f"{text:^70}")
    print("=" * 70 + "\n")


def print_success(text: str):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text: str):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text: str):
    """Print info message."""
    print(f"ℹ {text}")


def create_test_users(db: Session, reset: bool = False):
    """Create test users."""
    print_header("Creating Test Users")
    
    created = 0
    skipped = 0
    errors = 0
    
    for user_data in TEST_USERS:
        try:
            # Check if user exists
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing:
                if reset:
                    print_info(f"Deleting existing user: {user_data['email']}")
                    db.delete(existing)
                    db.commit()
                else:
                    print_info(f"User already exists: {user_data['email']}")
                    skipped += 1
                    continue
            
            # Create user
            hashed_password = pwd_context.hash(user_data["password"])
            
            user = User(
                email=user_data["email"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"]
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print_success(f"Created user: {user.email} (ID: {user.id}, Role: {user.role})")
            print_info(f"  Password: {user_data['password']}")
            created += 1
            
        except Exception as e:
            print_error(f"Failed to create user {user_data['email']}: {e}")
            db.rollback()
            errors += 1
    
    print(f"\nSummary: {created} created, {skipped} skipped, {errors} errors")
    return created > 0


def create_test_mappings(db: Session):
    """Create test user-patient mappings."""
    print_header("Creating Test Mappings")
    
    try:
        odoo_client = OdooClientV2()
        
        # Get test patient user
        patient_user = db.query(User).filter(
            User.email == "patient@dentaflow.test"
        ).first()
        
        if not patient_user:
            print_error("Patient user not found")
            return False
        
        # Check if mapping exists
        existing = mapping_crud.get_mapping_by_user_id(db, patient_user.id)
        
        if existing:
            print_info(f"Mapping already exists for {patient_user.email}")
            print_info(f"  User ID: {existing.user_id}")
            print_info(f"  Odoo Patient ID: {existing.odoo_patient_id}")
            return True
        
        # Search for patient in Odoo
        print_info(f"Searching Odoo for patient: {patient_user.email}")
        patients = odoo_client.search_patients(email=patient_user.email)
        
        if not patients:
            print_info("Patient not found in Odoo, creating new patient...")
            
            # Create patient in Odoo
            patient_id = odoo_client.create_patient({
                "name": patient_user.full_name,
                "email": patient_user.email,
                "phone": "+972501234567"
            })
            
            if not patient_id:
                print_error("Failed to create patient in Odoo")
                return False
            
            print_success(f"Created patient in Odoo (ID: {patient_id})")
        else:
            patient_id = patients[0]['id']
            print_success(f"Found patient in Odoo (ID: {patient_id})")
        
        # Create mapping
        mapping = mapping_crud.create_mapping(
            db=db,
            user_id=str(patient_user.id),
            odoo_patient_id=patient_id,
            email=patient_user.email,
            full_name=patient_user.full_name
        )
        
        print_success(f"Created mapping:")
        print_info(f"  User ID: {mapping.user_id}")
        print_info(f"  Odoo Patient ID: {mapping.odoo_patient_id}")
        print_info(f"  Email: {mapping.email}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create mappings: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_credentials():
    """Print test credentials."""
    print_header("Test Credentials")
    
    print("Admin User:")
    print("  Email: admin@dentaflow.test")
    print("  Password: Admin123!")
    print("  Role: admin")
    print("")
    
    print("Patient User:")
    print("  Email: patient@dentaflow.test")
    print("  Password: Patient123!")
    print("  Role: patient")
    print("")
    
    print("Staff User:")
    print("  Email: staff@dentaflow.test")
    print("  Password: Staff123!")
    print("  Role: staff")
    print("")
    
    print("API Usage:")
    print("  1. Login: POST /api/v1/auth/login")
    print("  2. Use returned token in Authorization header")
    print("  3. Example: Authorization: Bearer <token>")


def main():
    """Main function."""
    print_header("DentaFlow Test Data Creation")
    
    # Check for reset flag
    reset = "--reset" in sys.argv
    
    if reset:
        print_info("RESET MODE: Existing test users will be deleted")
        print("")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create test users
        users_created = create_test_users(db, reset=reset)
        
        # Create test mappings
        if users_created or not reset:
            create_test_mappings(db)
        
        # Print credentials
        print_credentials()
        
        print_header("✓ Test Data Creation Complete")
        
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

