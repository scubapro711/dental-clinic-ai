import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.plan_configuration import PlanConfiguration
from app.core.security import get_password_hash
import uuid

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Apply migrations
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def super_admin_user():
    db = TestingSessionLocal()
    email = f"superadmin_{uuid.uuid4()}@test.com"
    user = User(
        email=email,
        hashed_password=get_password_hash("testpassword"),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()
    db.close()


@pytest.fixture(scope="module")
def regular_user():
    db = TestingSessionLocal()
    email = f"user_{uuid.uuid4()}@test.com"
    user = User(
        email=email,
        hashed_password=get_password_hash("testpassword"),
        role=UserRole.ORG_ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()
    db.close()


def test_full_subscription_flow(super_admin_user, regular_user):
    # 1. Super Admin Login
    response = client.post("/api/v1/auth/token", data={"username": super_admin_user.email, "password": "testpassword"})
    assert response.status_code == 200
    super_admin_token = response.json()["access_token"]
    super_admin_headers = {"Authorization": f"Bearer {super_admin_token}"}

    # 2. Super Admin creates a plan
    plan_key = f"test-plan-{uuid.uuid4()}"
    plan_data = {
        "plan_key": plan_key,
        "name": "Test Plan",
        "amount": 99.99,
        "max_users": 10,
        "max_patients": 100,
    }
    response = client.post("/api/v1/admin/plans/", json=plan_data, headers=super_admin_headers)
    assert response.status_code == 201
    plan_id = response.json()["id"]

    # 3. Regular User Login
    response = client.post("/api/v1/auth/token", data={"username": regular_user.email, "password": "testpassword"})
    assert response.status_code == 200
    regular_user_token = response.json()["access_token"]
    regular_user_headers = {"Authorization": f"Bearer {regular_user_token}"}

    # 4. Regular user creates an organization
    org_name = f"Test Clinic {uuid.uuid4()}"
    response = client.post("/api/v1/organizations/", json={"name": org_name, "email": regular_user.email}, headers=regular_user_headers)
    assert response.status_code == 200
    org_id = response.json()["id"]

    # 5. Regular user subscribes to the plan (trial)
    response = client.post("/api/v1/subscriptions/create", json={"plan_id": plan_id}, headers=regular_user_headers)
    assert response.status_code == 200
    subscription_data = response.json()
    assert subscription_data["status"] == "trialing"
    assert subscription_data["plan"]["id"] == plan_id

    # 6. Verify subscription in the database
    db = TestingSessionLocal()
    from app.models.subscription import Subscription, SubscriptionStatus
    subscription = db.query(Subscription).filter_by(organization_id=org_id).first()
    assert subscription is not None
    assert subscription.status == SubscriptionStatus.TRIALING
    db.close()

    # 7. Simulate webhook for trial end and payment success
    # In a real scenario, this would be a POST to /webhooks/stripe from Stripe
    # Here we will manually update the subscription status to active
    db = TestingSessionLocal()
    subscription = db.query(Subscription).filter_by(organization_id=org_id).first()
    subscription.status = SubscriptionStatus.ACTIVE
    db.commit()
    db.close()

    # 8. Verify subscription is active
    response = client.get("/api/v1/subscriptions/current", headers=regular_user_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    # 9. User cancels subscription
    response = client.post("/api/v1/subscriptions/cancel", headers=regular_user_headers)
    assert response.status_code == 200

    # 10. Verify subscription is canceled
    response = client.get("/api/v1/subscriptions/current", headers=regular_user_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "canceled"

