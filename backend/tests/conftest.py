"""
Pytest configuration and fixtures for DentalAI Backend tests.

This module provides:
- Test database setup/teardown
- Mock external services (Odoo, Neo4j, Redis, OpenAI)
- Test fixtures for common objects
- Environment configuration for tests
"""

import os
import pytest
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "test"
os.environ["ODOO_URL"] = "http://localhost:8069"
os.environ["ODOO_DB"] = "test"
os.environ["ODOO_USERNAME"] = "admin"
os.environ["ODOO_PASSWORD"] = "admin"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-test-mock")
os.environ["TELEGRAM_BOT_TOKEN"] = "123456:test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret"

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.organization import Organization


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a test database session using SQLite in-memory.
    
    Each test gets a fresh database that's automatically cleaned up.
    """
    # Create in-memory SQLite engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# Mock External Services
# ============================================================================

@pytest.fixture(scope="function")
def mock_openai():
    """Mock OpenAI API calls."""
    with patch("app.agents.alex.ChatOpenAI") as mock:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(
            content="This is a mocked AI response for testing purposes."
        )
        mock.return_value = mock_instance
        yield mock


@pytest.fixture(scope="function")
def mock_odoo():
    """Mock Odoo client."""
    with patch("app.integrations.mock_odoo_realistic.MockOdooRealisticClient") as mock:
        mock_instance = MagicMock()
        
        # Mock search_patients
        mock_instance.search_patients.return_value = [
            {
                "id": "patient_001",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+972501234567"
            }
        ]
        
        # Mock get_available_slots
        mock_instance.get_available_slots.return_value = [
            {
                "date": "2025-10-07",
                "time": "10:00",
                "doctor_id": "doctor_001",
                "doctor_name": "Dr. Smith"
            }
        ]
        
        # Mock create_appointment
        mock_instance.create_appointment.return_value = {
            "id": "appt_001",
            "patient_id": "patient_001",
            "date": "2025-10-07",
            "time": "10:00",
            "status": "confirmed"
        }
        
        # Mock get_patient_invoices
        mock_instance.get_patient_invoices.return_value = [
            {
                "id": "inv_001",
                "amount": 500.00,
                "status": "paid",
                "date": "2025-09-15"
            }
        ]
        
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture(scope="function")
def mock_causal_memory_fixture():
    """Mock causal memory for tests."""
    with patch("app.agents.agent_graph.causal_memory") as mock:
        mock.store_interaction.return_value = "test-interaction-id"
        mock.get_similar_interactions.return_value = []
        yield mock


@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis client."""
    with patch("app.core.config.settings.REDIS_URL", "redis://localhost:6379/1"):
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = True
        mock_client.exists.return_value = False
        yield mock_client


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_organization(test_db: Session) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Dental Clinic",
        slug="test-clinic",
        subscription_tier="PRO",
        subscription_status="active",
        settings={}
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org


@pytest.fixture(scope="function")
def test_user(test_db: Session, test_organization: Organization) -> User:
    """Create a test user."""
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Test123!@#"),
        full_name="Test User",
        phone="+972501234567",
        role="ORG_ADMIN",
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        data={"sub": str(test_user.id)}
    )
    
    return {
        "Authorization": f"Bearer {access_token}"
    }


# ============================================================================
# Agent Test Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def mock_agent_graph():
    """Mock AgentGraphV2 for testing."""
    with patch("app.agents.agent_graph.AgentGraphV2") as mock:
        mock_instance = MagicMock()
        
        # Mock process_message
        async def mock_process_message(*args, **kwargs):
            return {
                "agent": "alex",
                "response": "This is a mocked agent response.",
                "requires_human": False,
                "escalation_level": None
            }
        
        mock_instance.process_message = mock_process_message
        mock.return_value = mock_instance
        
        yield mock_instance


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may require external services)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (may take more than 1 second)"
    )
    config.addinivalue_line(
        "markers", "skip_ci: Skip in CI environment"
    )
