"""
Integration Tests for Super Admin Dashboard

Tests all Super Admin endpoints to ensure proper functionality.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.main import app
from app.core.database import get_db
from app.models import (
    User, Organization, Subscription, Payment, UsageMetric,
    CostTracking, AnalyticsSnapshot, AdminAction,
    UserRole, SubscriptionStatus, SubscriptionTier, PaymentStatus,
    UsageMetricType, SnapshotType, AdminActionType
)


client = TestClient(app)


@pytest.fixture
def super_admin_token(db_session):
    """Create a super admin user and return auth token."""
    # Create super admin user
    super_admin = User(
        email="superadmin@dentaflow.ai",
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        hashed_password="$2b$12$test_hash"  # Mock password hash
    )
    db_session.add(super_admin)
    db_session.commit()
    db_session.refresh(super_admin)
    
    # Generate token (simplified for testing)
    # In production, use proper JWT token generation
    return "test_super_admin_token"


@pytest.fixture
def test_organizations(db_session):
    """Create test organizations with subscriptions."""
    orgs = []
    
    for i in range(5):
        org = Organization(
            name=f"Test Clinic {i+1}",
            slug=f"test-clinic-{i+1}",
            email=f"clinic{i+1}@test.com",
            subscription_tier=SubscriptionTier.PROFESSIONAL if i % 2 == 0 else SubscriptionTier.BASIC,
            subscription_status=SubscriptionStatus.ACTIVE if i < 3 else SubscriptionStatus.TRIALING,
            is_active=True
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        # Create subscription
        subscription = Subscription(
            organization_id=org.id,
            plan_tier=org.subscription_tier,
            status=org.subscription_status,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            trial_end=datetime.utcnow() + timedelta(days=30) if org.subscription_status == SubscriptionStatus.TRIALING else None
        )
        db_session.add(subscription)
        
        # Create usage metrics
        for day in range(7):
            metric_date = date.today() - timedelta(days=day)
            
            usage_metrics = [
                UsageMetric(
                    organization_id=org.id,
                    metric_type=UsageMetricType.AI_CONVERSATIONS,
                    value=10 + (i * 5) + day,
                    date=metric_date
                ),
                UsageMetric(
                    organization_id=org.id,
                    metric_type=UsageMetricType.APPOINTMENTS_BOOKED,
                    value=5 + (i * 2) + day,
                    date=metric_date
                ),
                UsageMetric(
                    organization_id=org.id,
                    metric_type=UsageMetricType.PATIENTS_ADDED,
                    value=3 + i + day,
                    date=metric_date
                ),
            ]
            
            for metric in usage_metrics:
                db_session.add(metric)
        
        orgs.append(org)
    
    db_session.commit()
    return orgs


class TestOrganizationsEndpoints:
    """Test Organizations Management endpoints."""
    
    def test_list_organizations(self, super_admin_token, test_organizations):
        """Test listing all organizations."""
        response = client.get(
            "/api/v1/super-admin/organizations",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "organizations" in data
        assert "total" in data
        assert len(data["organizations"]) > 0
    
    def test_list_organizations_with_filters(self, super_admin_token, test_organizations):
        """Test filtering organizations."""
        # Filter by status
        response = client.get(
            "/api/v1/super-admin/organizations?status=active",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        for org in data["organizations"]:
            assert org["subscription_status"] == "active"
    
    def test_get_organization_details(self, super_admin_token, test_organizations):
        """Test getting organization details."""
        org_id = test_organizations[0].id
        
        response = client.get(
            f"/api/v1/super-admin/organizations/{org_id}",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "organization" in data
        assert "users" in data
        assert "subscription" in data
        assert "usage_summary" in data
    
    def test_update_organization(self, super_admin_token, test_organizations):
        """Test updating organization."""
        org_id = test_organizations[0].id
        
        response = client.patch(
            f"/api/v1/super-admin/organizations/{org_id}",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            json={"name": "Updated Clinic Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Clinic Name"
    
    def test_extend_trial(self, super_admin_token, test_organizations):
        """Test extending trial period."""
        # Find an organization in trial
        trial_org = next(org for org in test_organizations if org.subscription_status == SubscriptionStatus.TRIALING)
        
        response = client.post(
            f"/api/v1/super-admin/organizations/{trial_org.id}/extend-trial",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            json={"days": 7}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "new_trial_end" in data
    
    def test_change_plan(self, super_admin_token, test_organizations):
        """Test changing subscription plan."""
        org_id = test_organizations[0].id
        
        response = client.post(
            f"/api/v1/super-admin/organizations/{org_id}/change-plan",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            json={"plan_tier": "enterprise"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["new_plan"] == "enterprise"


class TestUsageEndpoints:
    """Test Usage Tracking endpoints."""
    
    def test_usage_summary(self, super_admin_token, test_organizations):
        """Test getting usage summary."""
        response = client.get(
            "/api/v1/super-admin/usage/summary",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_conversations" in data
        assert "total_appointments" in data
        assert "total_patients" in data
    
    def test_usage_by_organization(self, super_admin_token, test_organizations):
        """Test getting usage by organization."""
        response = client.get(
            "/api/v1/super-admin/usage/by-organization",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            params={"metric_type": "ai_conversations"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "organization_id" in data[0]
            assert "metric_type" in data[0]
            assert "value" in data[0]
    
    def test_usage_trends(self, super_admin_token, test_organizations):
        """Test getting usage trends."""
        response = client.get(
            "/api/v1/super-admin/usage/trends",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            params={"metric_type": "ai_conversations"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "metric_type" in data
        assert "trends" in data
        assert isinstance(data["trends"], list)
    
    def test_record_usage_metric(self, super_admin_token, test_organizations):
        """Test recording a usage metric."""
        org_id = test_organizations[0].id
        
        response = client.post(
            "/api/v1/super-admin/usage/record",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            json={
                "organization_id": str(org_id),
                "metric_type": "ai_conversations",
                "value": 50
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "metric" in data


class TestRevenueEndpoints:
    """Test Revenue & Billing endpoints."""
    
    def test_revenue_summary(self, super_admin_token, test_organizations):
        """Test getting revenue summary."""
        response = client.get(
            "/api/v1/super-admin/revenue/summary",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mrr" in data
        assert "arr" in data
        assert "growth_rate" in data
        assert "churn_rate" in data
        assert "active_subscriptions" in data
    
    def test_revenue_trends(self, super_admin_token, test_organizations):
        """Test getting revenue trends."""
        response = client.get(
            "/api/v1/super-admin/revenue/trends",
            headers={"Authorization": f"Bearer {super_admin_token}"},
            params={"granularity": "monthly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_subscriptions_summary(self, super_admin_token, test_organizations):
        """Test getting subscriptions summary."""
        response = client.get(
            "/api/v1/super-admin/subscriptions/summary",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "active" in data
        assert "trial" in data
        assert "canceled" in data
        assert "past_due" in data
        assert "total" in data
    
    def test_list_subscriptions(self, super_admin_token, test_organizations):
        """Test listing subscriptions."""
        response = client.get(
            "/api/v1/super-admin/subscriptions",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
        assert "total" in data
    
    def test_payments_summary(self, super_admin_token, test_organizations):
        """Test getting payments summary."""
        response = client.get(
            "/api/v1/super-admin/payments/summary",
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "successful_count" in data
        assert "failed_count" in data
        assert "total_amount" in data


class TestAccessControl:
    """Test access control for Super Admin endpoints."""
    
    def test_non_super_admin_access_denied(self, db_session):
        """Test that non-super-admin users cannot access endpoints."""
        # Create regular user
        regular_user = User(
            email="regular@test.com",
            full_name="Regular User",
            role=UserRole.ORG_ADMIN,
            is_active=True,
            hashed_password="$2b$12$test_hash"
        )
        db_session.add(regular_user)
        db_session.commit()
        
        # Try to access super admin endpoint
        response = client.get(
            "/api/v1/super-admin/organizations",
            headers={"Authorization": "Bearer regular_user_token"}
        )
        
        assert response.status_code == 403
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        response = client.get("/api/v1/super-admin/organizations")
        
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

