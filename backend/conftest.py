"""
Pytest configuration and fixtures for testing.

This file provides test fixtures including an in-memory SQLite database
for fast unit testing without requiring PostgreSQL installation.
"""

import os
import sys
from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Set test environment before importing app modules
os.environ["APP_ENV"] = "test"
# Use PostgreSQL test database instead of SQLite
os.environ["DATABASE_URL"] = "postgresql://dentalai_user:dentalai_password@localhost:5432/dentalai_test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["ODOO_URL"] = "http://localhost:8069"
os.environ["ODOO_DB"] = "dentalai_odoo"
os.environ["ODOO_USERNAME"] = "admin"
os.environ["ODOO_PASSWORD"] = "admin"
os.environ["TELEGRAM_BOT_TOKEN"] = "test-token"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")

from app.core.database import Base
from app.models import *  # Import all models


# Create PostgreSQL engine for testing (supports JSONB!)
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://dentalai_user:dentalai_password@localhost:5432/dentalai_test"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL debugging
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.
    
    This fixture:
    1. Creates all tables
    2. Provides a database session
    3. Rolls back all changes after the test
    4. Drops all tables
    
    Usage:
        def test_something(db):
            user = User(email="test@example.com")
            db.add(user)
            db.commit()
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client for API testing.
    
    This fixture provides a FastAPI TestClient with the test database.
    
    Usage:
        def test_api(client):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_db
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db):
    """Create a sample user for testing."""
    from app.models.user import User, UserRole
    from datetime import datetime
    from uuid import uuid4
    
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        phone="+972501234567",
        password_hash="hashed_password",
        role=UserRole.CLINIC_OWNER,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_organization(db):
    """Create a sample organization for testing."""
    from app.models.organization import Organization
    from datetime import datetime
    from uuid import uuid4
    
    org = Organization(
        id=uuid4(),
        name="Test Clinic",
        email="clinic@example.com",
        phone="+972501234567",
        address="123 Test St, Tel Aviv",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def sample_membership(db, sample_user, sample_organization):
    """Create a sample membership for testing."""
    from app.models.organization_membership import OrganizationMembership
    from datetime import datetime
    from uuid import uuid4
    
    membership = OrganizationMembership(
        id=uuid4(),
        user_id=sample_user.id,
        organization_id=sample_organization.id,
        organization_role="owner",
        is_active=True,
        joined_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
