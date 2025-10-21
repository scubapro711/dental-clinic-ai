"""
Unit Tests for User Model
==========================

Tests for the User model including:
- Model creation and validation
- Field constraints
- Relationships
- Enums (UserRole)
- Timestamps
- Soft delete functionality
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.user import User, UserRole
from app.models.organization import Organization


@pytest.mark.unit
@pytest.mark.models
@pytest.mark.critical
class TestUserModel:
    """Test suite for User model."""
    
    def test_create_user_with_required_fields(self, db_session):
        """Test creating a user with only required fields."""
        # Arrange
        user_data = {
            "email": "test@dentaflow.com",
            "hashed_password": "$2b$12$test_hashed_password",
            "full_name": "Test User",
            "role": UserRole.ORG_ADMIN
        }
        
        # Act
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.id is not None
        assert user.email == "test@dentaflow.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.ORG_ADMIN
        assert user.is_active is True  # Default value
        assert user.is_verified is False  # Default value
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_create_user_with_all_fields(self, db_session, test_organization):
        """Test creating a user with all optional fields."""
        # Arrange
        user_data = {
            "email": "full@dentaflow.com",
            "hashed_password": "$2b$12$test_hashed_password",
            "full_name": "Full Test User",
            "phone": "+1234567890",
            "phone_verified": True,
            "google_id": "google_123456",
            "picture_url": "https://example.com/pic.jpg",
            "role": UserRole.ORG_STAFF,
            "organization_id": test_organization.id,
            "mfa_enabled": True,
            "mfa_secret": "SECRET123",
            "is_active": True,
            "is_verified": True
        }
        
        # Act
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.phone == "+1234567890"
        assert user.phone_verified is True
        assert user.google_id == "google_123456"
        assert user.picture_url == "https://example.com/pic.jpg"
        assert user.mfa_enabled is True
        assert user.mfa_secret == "SECRET123"
        assert user.organization_id == test_organization.id
    
    def test_user_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        # Arrange
        user1 = User(
            email="duplicate@dentaflow.com",
            hashed_password="hash1",
            full_name="User 1",
            role=UserRole.ORG_ADMIN
        )
        db_session.add(user1)
        db_session.commit()
        
        # Act & Assert
        user2 = User(
            email="duplicate@dentaflow.com",  # Same email
            hashed_password="hash2",
            full_name="User 2",
            role=UserRole.ORG_STAFF
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()
    
    def test_user_google_id_unique_constraint(self, db_session):
        """Test that google_id must be unique."""
        # Arrange
        user1 = User(
            email="user1@dentaflow.com",
            hashed_password="hash1",
            full_name="User 1",
            role=UserRole.ORG_ADMIN,
            google_id="google_123"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Act & Assert
        user2 = User(
            email="user2@dentaflow.com",
            hashed_password="hash2",
            full_name="User 2",
            role=UserRole.ORG_STAFF,
            google_id="google_123"  # Same Google ID
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()
    
    def test_user_role_enum_values(self, db_session):
        """Test all UserRole enum values."""
        roles = [
            UserRole.SUPER_ADMIN,
            UserRole.ORG_ADMIN,
            UserRole.ORG_STAFF,
            UserRole.ORG_VIEWER,
            UserRole.PATIENT
        ]
        
        for role in roles:
            user = User(
                email=f"user_{role.value}@dentaflow.com",
                hashed_password="hash",
                full_name=f"User {role.value}",
                role=role
            )
            db_session.add(user)
        
        db_session.commit()
        
        # Assert all users were created
        assert db_session.query(User).count() == 5
    
    def test_user_timestamps_auto_set(self, db_session):
        """Test that timestamps are automatically set."""
        # Arrange
        before_create = datetime.utcnow()
        
        # Act
        user = User(
            email="timestamp@dentaflow.com",
            hashed_password="hash",
            full_name="Timestamp User",
            role=UserRole.ORG_ADMIN
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        after_create = datetime.utcnow()
        
        # Assert
        assert user.created_at is not None
        assert user.updated_at is not None
        assert before_create <= user.created_at <= after_create
        assert before_create <= user.updated_at <= after_create
    
    def test_user_updated_at_changes_on_update(self, db_session):
        """Test that updated_at changes when user is updated."""
        # Arrange
        user = User(
            email="update@dentaflow.com",
            hashed_password="hash",
            full_name="Update User",
            role=UserRole.ORG_ADMIN
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        original_updated_at = user.updated_at
        
        # Act - Update user
        import time
        time.sleep(0.1)  # Ensure time difference
        user.full_name = "Updated Name"
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.updated_at > original_updated_at
        assert user.full_name == "Updated Name"
    
    def test_user_organization_relationship(self, db_session, test_organization):
        """Test relationship between User and Organization."""
        # Arrange & Act
        user = User(
            email="org@dentaflow.com",
            hashed_password="hash",
            full_name="Org User",
            role=UserRole.ORG_ADMIN,
            organization_id=test_organization.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.organization is not None
        assert user.organization.id == test_organization.id
        assert user.organization.name == test_organization.name
    
    def test_user_default_values(self, db_session):
        """Test default values for User model."""
        # Act
        user = User(
            email="defaults@dentaflow.com",
            hashed_password="hash",
            full_name="Defaults User",
            role=UserRole.ORG_ADMIN
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assert
        assert user.is_active is True
        assert user.is_verified is False
        assert user.phone_verified is False
        assert user.mfa_enabled is False
        assert user.mfa_secret is None
        assert user.google_id is None
        assert user.picture_url is None
        assert user.last_login_at is None
    
    def test_user_required_fields_validation(self, db_session):
        """Test that required fields cannot be None."""
        # Test missing email
        with pytest.raises(Exception):
            user = User(
                hashed_password="hash",
                full_name="No Email",
                role=UserRole.ORG_ADMIN
            )
            db_session.add(user)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing password
        with pytest.raises(Exception):
            user = User(
                email="nopassword@dentaflow.com",
                full_name="No Password",
                role=UserRole.ORG_ADMIN
            )
            db_session.add(user)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing full_name
        with pytest.raises(Exception):
            user = User(
                email="noname@dentaflow.com",
                hashed_password="hash",
                role=UserRole.ORG_ADMIN
            )
            db_session.add(user)
            db_session.commit()


@pytest.mark.unit
@pytest.mark.models
class TestUserRoleEnum:
    """Test suite for UserRole enum."""
    
    def test_user_role_enum_values(self):
        """Test all UserRole enum values."""
        assert UserRole.SUPER_ADMIN.value == "super_admin"
        assert UserRole.ORG_ADMIN.value == "org_admin"
        assert UserRole.ORG_STAFF.value == "org_staff"
        assert UserRole.ORG_VIEWER.value == "org_viewer"
        assert UserRole.PATIENT.value == "patient"
    
    def test_user_role_enum_count(self):
        """Test that UserRole has exactly 5 values."""
        assert len(UserRole) == 5
