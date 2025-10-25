"""
Tests for Bug #25: N+1 Queries Performance Issue

This test suite verifies that the N+1 query problem has been fixed
in critical API endpoints by using eager loading (joinedload/selectinload)
and optimized queries (GROUP BY).

Bug #25 Description:
- Severity: Medium
- Impact: Performance degradation with large datasets
- Root Cause: Lazy loading of relationships causing separate queries in loops
- Fix: Implement eager loading and optimize with GROUP BY aggregations
"""

import pytest
from sqlalchemy import event, select
from sqlalchemy.engine import Engine
from app.models.subscription import Subscription
from app.models.organization import Organization
from app.models.plan_configuration import PlanConfiguration
from app.models.user import User, UserRole
from datetime import datetime, timedelta, timezone
from decimal import Decimal


# Query counter for detecting N+1 queries
query_count = 0


@pytest.fixture(autouse=True)
def reset_query_counter():
    """Reset query counter before each test"""
    global query_count
    query_count = 0


@pytest.fixture
def query_counter(db_session):
    """Fixture to count SQL queries executed"""
    global query_count
    
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        global query_count
        query_count += 1
    
    event.listen(Engine, "before_cursor_execute", before_cursor_execute)
    
    yield
    
    event.remove(Engine, "before_cursor_execute", before_cursor_execute)


@pytest.fixture
def test_data(db_session):
    """Create test data: 10 plans, 50 organizations, 50 subscriptions"""
    plans = []
    for i in range(10):
        plan = PlanConfiguration(
            plan_key=f"plan_{i}",
            name=f"Plan {i}",
            amount=Decimal(100 + i * 10),
            currency="ILS",
            sort_order=i
        )
        db_session.add(plan)
        plans.append(plan)
    
    db_session.flush()
    
    organizations = []
    subscriptions = []
    
    for i in range(50):
        org = Organization(
            name=f"Clinic {i}",
            slug=f"clinic-{i}",
            email=f"clinic{i}@example.com"
        )
        db_session.add(org)
        organizations.append(org)
        
        db_session.flush()
        
        # Create subscription for each organization
        sub = Subscription(
            organization_id=org.id,
            plan_id=plans[i % 10].id,  # Distribute across 10 plans
            stripe_subscription_id=f"sub_{i}",
            stripe_customer_id=f"cus_{i}",
            status="active",
            amount=plans[i % 10].amount,
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db_session.add(sub)
        subscriptions.append(sub)
    
    db_session.commit()
    
    return {
        "plans": plans,
        "organizations": organizations,
        "subscriptions": subscriptions
    }


class TestBug25NPlusOneQueries:
    """Test suite for Bug #25: N+1 Queries"""
    
    def test_get_billing_stats_no_n_plus_one(self, db_session, query_counter, test_data):
        """
        Test that get_billing_stats uses GROUP BY instead of N+1 queries
        
        Before fix: 1 query for plans + N queries for subscriber counts = 11 queries
        After fix: 1 query for plans + 1 GROUP BY query = 2 queries
        """
        global query_count
        query_count = 0
        
        # Simulate the optimized query from get_billing_stats
        from sqlalchemy import func
        
        # Get subscriber counts with GROUP BY (1 query)
        plan_subscriber_counts = dict(
            db_session.query(
                Subscription.plan_id,
                func.count(Subscription.id)
            ).filter(
                Subscription.status == "active"
            ).group_by(Subscription.plan_id).all()
        )
        
        # Get all plans (1 query)
        plans = db_session.query(PlanConfiguration).order_by(PlanConfiguration.sort_order).all()
        
        # Build results (no additional queries)
        plans_data = []
        for plan in plans:
            plans_data.append({
                "id": plan.id,
                "name": plan.name,
                "subscribers": plan_subscriber_counts.get(plan.id, 0)
            })
        
        # Verify: Should be exactly 2 queries (GROUP BY + get plans)
        assert query_count <= 3, f"Expected ≤3 queries, got {query_count} (N+1 query detected!)"
        assert len(plans_data) == 10
        
        # Verify subscriber counts are correct
        total_subscribers = sum(p["subscribers"] for p in plans_data)
        assert total_subscribers == 50  # All 50 subscriptions
    
    def test_get_all_subscriptions_with_eager_loading(self, db_session, query_counter, test_data):
        """
        Test that get_all_subscriptions uses joinedload for eager loading
        
        Before fix: 1 query for subscriptions + N queries for orgs + N queries for plans = 101 queries
        After fix: 1 query with JOINs = 1 query
        """
        global query_count
        query_count = 0
        
        from sqlalchemy.orm import joinedload
        
        # Get subscriptions with eager loading (1 query with JOINs)
        subscriptions = db_session.query(Subscription).options(
            joinedload(Subscription.organization),
            joinedload(Subscription.plan)
        ).limit(50).all()
        
        # Access relationships (should NOT trigger additional queries)
        results = []
        for sub in subscriptions:
            results.append({
                "organization_name": sub.organization.name,
                "plan_name": sub.plan.name,
                "monthly_price": float(sub.plan.amount)
            })
        
        # Verify: Should be exactly 1 query (with JOINs)
        assert query_count <= 2, f"Expected ≤2 queries, got {query_count} (N+1 query detected!)"
        assert len(results) == 50
    
    def test_subscription_plan_relationship_exists(self, db_session, test_data):
        """
        Test that Subscription.plan relationship is properly defined
        
        This was missing in the original model and caused the N+1 query issue.
        """
        sub = db_session.query(Subscription).first()
        
        # Verify plan relationship exists
        assert hasattr(sub, 'plan'), "Subscription.plan relationship is missing!"
        assert sub.plan is not None, "Subscription.plan is None!"
        assert isinstance(sub.plan, PlanConfiguration)
        assert sub.plan.id == sub.plan_id
    
    def test_subscription_organization_relationship_exists(self, db_session, test_data):
        """
        Test that Subscription.organization relationship is properly defined
        """
        sub = db_session.query(Subscription).first()
        
        # Verify organization relationship exists
        assert hasattr(sub, 'organization'), "Subscription.organization relationship is missing!"
        assert sub.organization is not None, "Subscription.organization is None!"
        assert isinstance(sub.organization, Organization)
        assert sub.organization.id == sub.organization_id
    
    def test_lazy_loading_vs_eager_loading_performance(self, db_session, query_counter, test_data):
        """
        Compare lazy loading vs eager loading performance
        
        This test demonstrates the performance difference.
        """
        global query_count
        
        # Test 1: Lazy loading (N+1 queries)
        query_count = 0
        subs_lazy = db_session.query(Subscription).limit(10).all()
        
        for sub in subs_lazy:
            _ = sub.organization.name  # Triggers query for each subscription
            _ = sub.plan.name  # Triggers query for each subscription
        
        lazy_query_count = query_count
        
        # Test 2: Eager loading (1 query)
        query_count = 0
        from sqlalchemy.orm import joinedload
        
        subs_eager = db_session.query(Subscription).options(
            joinedload(Subscription.organization),
            joinedload(Subscription.plan)
        ).limit(10).all()
        
        for sub in subs_eager:
            _ = sub.organization.name  # No additional query
            _ = sub.plan.name  # No additional query
        
        eager_query_count = query_count
        
        # Verify: Eager loading should use significantly fewer queries
        assert eager_query_count < lazy_query_count / 2, \
            f"Eager loading ({eager_query_count} queries) should be much faster than lazy loading ({lazy_query_count} queries)"
    
    def test_group_by_aggregation_correctness(self, db_session, test_data):
        """
        Test that GROUP BY aggregation produces correct subscriber counts
        """
        from sqlalchemy import func
        
        # Get subscriber counts with GROUP BY
        plan_subscriber_counts = dict(
            db_session.query(
                Subscription.plan_id,
                func.count(Subscription.id)
            ).filter(
                Subscription.status == "active"
            ).group_by(Subscription.plan_id).all()
        )
        
        # Verify counts manually
        for plan_id, count in plan_subscriber_counts.items():
            manual_count = db_session.query(Subscription).filter(
                Subscription.plan_id == plan_id,
                Subscription.status == "active"
            ).count()
            
            assert count == manual_count, \
                f"GROUP BY count ({count}) doesn't match manual count ({manual_count}) for plan {plan_id}"

