"""
DentaFlow SaaS - Global Test Fixtures
=====================================

This module provides global pytest fixtures for all tests.
Fixtures are organized by category and can be used across all test files.

Categories:
- Database fixtures (PostgreSQL, Redis, Neo4j)
- API fixtures (FastAPI TestClient, authentication)
- Agent fixtures (LangGraph agents, mock LLMs)
- Mock service fixtures (Stripe, Odoo, Pinecone, Telegram)
- Test data fixtures (users, organizations, patients)

Usage:
    from fixtures.conftest import client, db_session, mock_stripe
    
    def test_example(client, db_session):
        # Test code here
        pass
"""

import os

# ============================================
# Environment Setup (MUST be before any app imports)
# ============================================
# Set required environment variables for tests BEFORE importing any app modules
os.environ["APP_ENV"] = "test"
os.environ["TESTING"] = "1"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
os.environ["JWT_SECRET"] = "test-jwt-secret-for-testing-only-not-for-production"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-32-bytes-long!!"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["DISABLE_EXTERNAL_APIS"] = "1"

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from datetime import datetime, timedelta
from uuid import uuid4

# FastAPI
from fastapi.testclient import TestClient
from fastapi import FastAPI

# SQLAlchemy
from sqlalchemy import create_engine, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import uuid as uuid_lib

# ============================================
# UUID and JSONB Support
# ============================================
# NOTE: UUID and JSONB compatibility is handled by app.core.database_types
# No additional TypeDecorators or monkey-patching needed in tests!

# Faker for test data (safe to import early)
from faker import Faker

# NOTE: All app.* imports are done lazily inside fixtures to ensure
# environment variables are set BEFORE any app code is loaded

# ============================================
# Pytest Configuration
# ============================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Set test environment
    os.environ["APP_ENV"] = "test"
    os.environ["TESTING"] = "1"
    
    # Set required secrets for tests
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
    os.environ["JWT_SECRET"] = "test-jwt-secret-for-testing-only-not-for-production"
    
    # Disable external API calls by default
    os.environ["DISABLE_EXTERNAL_APIS"] = "1"
    
    # Use in-memory databases for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Use DB 15 for tests


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark tests based on path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
            item.add_marker(pytest.mark.critical)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)


# ============================================
# Event Loop Fixtures
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================
# Database Fixtures
# ============================================

@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine (SQLite in-memory)."""
    from app.core.database import Base
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Use checkfirst=True to avoid "index already exists" errors
    Base.metadata.create_all(bind=engine, checkfirst=True)
    yield engine
    Base.metadata.drop_all(bind=engine, checkfirst=True)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
async def async_db_session(db_engine) -> AsyncGenerator[Session, None]:
    """Create an async test database session."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker as async_sessionmaker
    
    # Note: For real async tests, use aiosqlite or asyncpg
    # This is a simplified version
    TestingSessionLocal = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


# ============================================
# FastAPI App Fixtures
# ============================================

@pytest.fixture(scope="function")
def app(db_session) -> FastAPI:
    """Create a test FastAPI application."""
    from app.main import app as main_app
    from app.core.database import get_db
    
    # Override database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    main_app.dependency_overrides[get_db] = override_get_db
    
    yield main_app
    
    # Clean up
    main_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app) -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(scope="function")
def authenticated_client(app, test_user, db_session) -> TestClient:
    """Create a test client with real JWT authentication."""
    from app.core.security import create_access_token
    
    # Ensure test_user is committed to DB
    db_session.commit()
    
    # Create real JWT token with all required fields
    token_data = {
        "sub": str(test_user.id),  # user_id as string
        "email": test_user.email,
        "role": test_user.role,
    }
    token = create_access_token(data=token_data)
    
    # Create client with authorization header
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {token}"}
    
    return client


# ============================================
# Authentication Fixtures
# ============================================

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    from app.models.user import User, UserRole
    
    user = User(
        id=uuid4(),
        email="test@dentaflow.com",
        full_name="Test User",
        role=UserRole.ORG_ADMIN,
        is_active=True,
        is_verified=True,
        hashed_password="$2b$12$test_hashed_password",  # bcrypt hash
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_organization(db_session):
    """Create a test organization."""
    from app.models.organization import Organization
    
    org = Organization(
        id=uuid4(),
        name="Test Dental Clinic",
        slug="test-clinic",
        email="clinic@test.com",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture(scope="function")
def test_subscription(db_session, test_organization):
    """Create a test subscription."""
    from app.models.subscription import Subscription, PlanTier, SubscriptionStatus
    
    subscription = Subscription(
        id=uuid4(),
        organization_id=test_organization.id,
        tier=PlanTier.professional,
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow()
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


@pytest.fixture(scope="function")
def auth_headers(test_user) -> dict:
    """Create authentication headers for API requests."""
    # Generate a test JWT token
    from app.services.auth_service import AuthService
    
    token = AuthService.create_access_token(
        data={"sub": str(test_user.id), "role": test_user.role.value}
    )
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }



# ============================================
# Mock Service Fixtures
# ============================================

@pytest.fixture(scope="function")
def mock_stripe(monkeypatch):
    """Mock Stripe API calls."""
    class MockStripe:
        class Customer:
            @staticmethod
            def create(**kwargs):
                return {"id": "cus_test123", **kwargs}
            
            @staticmethod
            def retrieve(customer_id):
                return {"id": customer_id, "email": "test@example.com"}
        
        class Subscription:
            @staticmethod
            def create(**kwargs):
                return {"id": "sub_test123", "status": "active", **kwargs}
            
            @staticmethod
            def retrieve(subscription_id):
                return {"id": subscription_id, "status": "active"}
    
    return MockStripe()


@pytest.fixture(scope="function")
def mock_odoo(monkeypatch):
    """Mock Odoo API calls."""
    class MockOdoo:
        def __init__(self):
            self.appointments = []
            self.patients = []
        
        def create_appointment(self, **kwargs):
            appointment = {"id": len(self.appointments) + 1, **kwargs}
            self.appointments.append(appointment)
            return appointment
        
        def get_appointments(self, **filters):
            return self.appointments
        
        def create_patient(self, **kwargs):
            patient = {"id": len(self.patients) + 1, **kwargs}
            self.patients.append(patient)
            return patient
    
    return MockOdoo()


@pytest.fixture(scope="function")
def mock_pinecone(monkeypatch):
    """Mock Pinecone vector database."""
    class MockPinecone:
        def __init__(self):
            self.vectors = {}
        
        def upsert(self, vectors, namespace=""):
            for vector in vectors:
                key = f"{namespace}:{vector['id']}"
                self.vectors[key] = vector
        
        def query(self, vector, top_k=5, namespace=""):
            # Return mock results
            return {
                "matches": [
                    {
                        "id": "hipaa_1",
                        "score": 0.95,
                        "metadata": {"text": "HIPAA compliance requirement..."}
                    }
                ]
            }
    
    return MockPinecone()


@pytest.fixture(scope="function")
def mock_openai(monkeypatch):
    """Mock OpenAI API calls."""
    class MockOpenAI:
        class ChatCompletion:
            @staticmethod
            def create(**kwargs):
                return {
                    "id": "chatcmpl-test123",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "This is a test response from the AI."
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 20,
                        "total_tokens": 30
                    }
                }
    
    return MockOpenAI()


@pytest.fixture(scope="function")
def mock_telegram(monkeypatch):
    """Mock Telegram Bot API."""
    class MockTelegram:
        def __init__(self):
            self.messages = []
        
        def send_message(self, chat_id, text, **kwargs):
            message = {
                "message_id": len(self.messages) + 1,
                "chat": {"id": chat_id},
                "text": text,
                **kwargs
            }
            self.messages.append(message)
            return message
    
    return MockTelegram()


# ============================================
# Test Data Fixtures
# ============================================

@pytest.fixture(scope="session")
def faker_instance():
    """Create a Faker instance for generating test data."""
    return Faker()


@pytest.fixture(scope="function")
def sample_patient_data(faker_instance):
    """Generate sample patient data."""
    return {
        "first_name": faker_instance.first_name(),
        "last_name": faker_instance.last_name(),
        "email": faker_instance.email(),
        "phone": faker_instance.phone_number(),
        "date_of_birth": faker_instance.date_of_birth(minimum_age=18, maximum_age=90),
        "address": faker_instance.address()
    }


@pytest.fixture(scope="function")
def sample_appointment_data(faker_instance):
    """Generate sample appointment data."""
    return {
        "patient_id": uuid4(),
        "doctor_id": uuid4(),
        "start_time": datetime.utcnow() + timedelta(days=1),
        "end_time": datetime.utcnow() + timedelta(days=1, hours=1),
        "type": "checkup",
        "notes": faker_instance.text(max_nb_chars=200)
    }


# ============================================
# Agent Fixtures
# ============================================

@pytest.fixture(scope="function")
def mock_agent_graph():
    """Mock LangGraph agent graph."""
    class MockAgentGraph:
        def invoke(self, state, config=None):
            # Return a mock response
            from langchain_core.messages import AIMessage
            return {
                "messages": state.get("messages", []) + [
                    AIMessage(content="Mock agent response")
                ],
                "current_agent": "alex",
                "organization_id": state.get("organization_id"),
                "user_role": state.get("user_role")
            }
    
    return MockAgentGraph()


# ============================================
# Cleanup Fixtures
# ============================================

@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data(db_session):
    """Automatically clean up test data after each test."""
    yield
    # Cleanup happens here after test execution
    db_session.rollback()


# ============================================
# Utility Fixtures
# ============================================

@pytest.fixture(scope="function")
def freeze_time():
    """Freeze time for testing time-dependent code."""
    from freezegun import freeze_time as _freeze_time
    return _freeze_time


@pytest.fixture(scope="function")
def capture_logs():
    """Capture log output for testing."""
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    yield log_capture
    
    logger.removeHandler(handler)



# Set TESTING environment variable for all tests
import os
os.environ["TESTING"] = "1"
os.environ["APP_ENV"] = "test"
