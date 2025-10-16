# Track 5: Super Admin Dashboard & Agents - Architecture Document

**Version:** v1.0.0  
**Date:** October 16, 2025  
**Status:** 🔄 In Progress  
**Track:** Phase 3 - Track 5 (Super Admin Dashboard & Agents)

---

## 🎯 Executive Summary

Track 5 implements a comprehensive Super Admin Dashboard with advanced cost tracking, usage monitoring, revenue management, and specialized AI agents for platform operations. This is a critical component for investor presentation and platform management.

### Key Objectives

1. **Multi-Tenant Management** - Centralized view of all clinics
2. **Cost Tracking** - Real-time GCP cost monitoring and allocation
3. **Usage Tracking** - Comprehensive usage metrics per organization
4. **Revenue Management** - MRR, ARR, churn, and billing analytics
5. **AI Agents** - CSM, RevOps, and Platform Ops agents
6. **Admin Actions** - Organization management and support tools

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Super Admin Dashboard                     │
│                         (Frontend)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Super Admin API Layer                       │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │   Orgs   │  Costs   │  Usage   │ Revenue  │Analytics │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼───────┐
│   Database   │ │GCP Billing│ │ AI Agents    │
│  (Postgres)  │ │    API    │ │ (LangGraph)  │
└──────────────┘ └──────────┘ └──────────────┘
```

### Component Diagram

```
Super Admin Dashboard
├── Organizations Management
│   ├── Organizations List
│   ├── Organization Details
│   ├── User Management
│   └── Admin Actions
│
├── Cost Tracking
│   ├── Cost Dashboard
│   ├── Cost Breakdown by Service
│   ├── Cost Allocation per Org
│   └── Budget Alerts
│
├── Usage Tracking
│   ├── Usage Dashboard
│   ├── Usage by Organization
│   ├── Usage vs Limits
│   └── Usage Trends
│
├── Revenue & Billing
│   ├── Revenue Dashboard (MRR, ARR)
│   ├── Subscriptions Overview
│   ├── Payments Dashboard
│   └── Churn Analysis
│
├── Analytics & Insights
│   ├── Cohort Analysis
│   ├── Funnel Analysis
│   ├── Health Metrics
│   └── AI-Generated Insights
│
└── AI Agents
    ├── CSM Agent (Customer Success)
    ├── RevOps Agent (Revenue Operations)
    └── Platform Ops Agent (Operations)
```

---

## 📊 Data Models

### 1. UsageMetric Model

Tracks usage metrics for each organization.

```python
class UsageMetric(Base):
    __tablename__ = "usage_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    metric_type = Column(Enum(UsageMetricType), nullable=False)
    value = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_usage_metrics_org_date', 'organization_id', 'date'),
        Index('ix_usage_metrics_type_date', 'metric_type', 'date'),
    )

class UsageMetricType(str, Enum):
    AI_CONVERSATIONS = "ai_conversations"
    APPOINTMENTS_BOOKED = "appointments_booked"
    PATIENTS_ADDED = "patients_added"
    ACTIVE_USERS = "active_users"
    STORAGE_USED_MB = "storage_used_mb"
    API_CALLS = "api_calls"
    TELEGRAM_MESSAGES = "telegram_messages"
    SMS_SENT = "sms_sent"
    EMAILS_SENT = "emails_sent"
```

### 2. CostTracking Model

Tracks infrastructure costs allocated to organizations.

```python
class CostTracking(Base):
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    service_name = Column(String, nullable=False)  # Cloud Run, Cloud SQL, etc.
    cost_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)
    usage_details = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_cost_tracking_org_period', 'organization_id', 'billing_period_start'),
        Index('ix_cost_tracking_service_period', 'service_name', 'billing_period_start'),
    )
```

### 3. AnalyticsSnapshot Model

Stores pre-calculated analytics for performance.

```python
class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_type = Column(Enum(SnapshotType), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_analytics_snapshots_type_date', 'snapshot_type', 'snapshot_date'),
    )

class SnapshotType(str, Enum):
    DAILY_REVENUE = "daily_revenue"
    WEEKLY_COHORT = "weekly_cohort"
    MONTHLY_CHURN = "monthly_churn"
    USAGE_SUMMARY = "usage_summary"
    COST_SUMMARY = "cost_summary"
```

### 4. AdminAction Model

Audit log for admin actions.

```python
class AdminAction(Base):
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(Enum(AdminActionType), nullable=False)
    target_type = Column(String, nullable=False)  # organization, user, subscription
    target_id = Column(Integer, nullable=False)
    action_details = Column(JSONB, default={})
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_admin_actions_admin_user', 'admin_user_id'),
        Index('ix_admin_actions_target', 'target_type', 'target_id'),
    )

class AdminActionType(str, Enum):
    CREATE_ORGANIZATION = "create_organization"
    UPDATE_ORGANIZATION = "update_organization"
    SUSPEND_ORGANIZATION = "suspend_organization"
    DELETE_ORGANIZATION = "delete_organization"
    EXTEND_TRIAL = "extend_trial"
    CHANGE_PLAN = "change_plan"
    IMPERSONATE_USER = "impersonate_user"
    RESET_PASSWORD = "reset_password"
    CHANGE_USER_ROLE = "change_user_role"
```

---

## 🔌 API Endpoints

### Organizations Management

```python
# List all organizations
GET /api/v1/super-admin/organizations
  Query params: status, plan, search, page, limit
  Response: { organizations: [...], total: 100, page: 1 }

# Get organization details
GET /api/v1/super-admin/organizations/{org_id}
  Response: { organization: {...}, users: [...], subscription: {...}, usage: {...} }

# Update organization
PATCH /api/v1/super-admin/organizations/{org_id}
  Body: { name, status, settings }

# Suspend organization
POST /api/v1/super-admin/organizations/{org_id}/suspend
  Body: { reason }

# Delete organization
DELETE /api/v1/super-admin/organizations/{org_id}
  Query params: hard_delete (boolean)

# Extend trial
POST /api/v1/super-admin/organizations/{org_id}/extend-trial
  Body: { days }

# Change plan
POST /api/v1/super-admin/organizations/{org_id}/change-plan
  Body: { plan_id }
```

### Cost Tracking

```python
# Get cost summary
GET /api/v1/super-admin/costs/summary
  Query params: start_date, end_date
  Response: { total_cost, by_service: {...}, by_organization: {...} }

# Get costs by service
GET /api/v1/super-admin/costs/by-service
  Query params: start_date, end_date
  Response: { services: [{ name, cost, percentage }] }

# Get costs by organization
GET /api/v1/super-admin/costs/by-organization
  Query params: start_date, end_date, page, limit
  Response: { organizations: [{ id, name, cost }], total: 100 }

# Get organization cost details
GET /api/v1/super-admin/costs/organization/{org_id}
  Query params: start_date, end_date
  Response: { organization: {...}, costs: [...], trends: [...] }

# Get cost trends
GET /api/v1/super-admin/costs/trends
  Query params: start_date, end_date, granularity (daily, weekly, monthly)
  Response: { trends: [{ date, cost }] }
```

### Usage Tracking

```python
# Get usage summary
GET /api/v1/super-admin/usage/summary
  Response: { total_users, total_conversations, total_appointments, total_patients }

# Get usage by organization
GET /api/v1/super-admin/usage/by-organization
  Query params: metric_type, date, page, limit
  Response: { organizations: [{ id, name, value, limit, percentage }] }

# Get organization usage details
GET /api/v1/super-admin/usage/organization/{org_id}
  Query params: start_date, end_date
  Response: { organization: {...}, usage: {...}, trends: [...], limits: {...} }

# Get usage trends
GET /api/v1/super-admin/usage/trends
  Query params: metric_type, start_date, end_date
  Response: { trends: [{ date, value }] }

# Record usage metric (internal)
POST /api/v1/super-admin/usage/record
  Body: { organization_id, metric_type, value, date }
```

### Revenue & Billing

```python
# Get revenue summary
GET /api/v1/super-admin/revenue/summary
  Response: { mrr, arr, growth_rate, churn_rate }

# Get revenue trends
GET /api/v1/super-admin/revenue/trends
  Query params: start_date, end_date, granularity
  Response: { trends: [{ date, mrr, arr }] }

# Get subscriptions summary
GET /api/v1/super-admin/subscriptions/summary
  Response: { active, trial, canceled, past_due, total }

# Get subscriptions list
GET /api/v1/super-admin/subscriptions
  Query params: status, plan, page, limit
  Response: { subscriptions: [...], total: 100 }

# Get payments summary
GET /api/v1/super-admin/payments/summary
  Query params: start_date, end_date
  Response: { successful, failed, refunded, total_amount, stripe_fees }

# Get payments list
GET /api/v1/super-admin/payments
  Query params: status, start_date, end_date, page, limit
  Response: { payments: [...], total: 100 }
```

### Analytics & Insights

```python
# Get cohort analysis
GET /api/v1/super-admin/analytics/cohorts
  Query params: start_date, end_date
  Response: { cohorts: [{ month, signups, retained: [...] }] }

# Get funnel analysis
GET /api/v1/super-admin/analytics/funnel
  Response: { stages: [{ name, count, conversion_rate }] }

# Get churn prediction
GET /api/v1/super-admin/analytics/churn-prediction
  Response: { at_risk_organizations: [{ id, name, risk_score, reasons }] }

# Get upsell opportunities
GET /api/v1/super-admin/analytics/upsell-opportunities
  Response: { opportunities: [{ id, name, current_plan, recommended_plan, score }] }

# Get AI insights
GET /api/v1/super-admin/analytics/insights
  Response: { insights: [{ type, title, description, action, priority }] }
```

### Admin Actions

```python
# Impersonate user
POST /api/v1/super-admin/actions/impersonate
  Body: { user_id }
  Response: { token, expires_at }

# Reset user password
POST /api/v1/super-admin/actions/reset-password
  Body: { user_id }
  Response: { temp_password }

# Change user role
POST /api/v1/super-admin/actions/change-role
  Body: { user_id, new_role }

# Get admin action logs
GET /api/v1/super-admin/actions/logs
  Query params: admin_user_id, action_type, start_date, end_date, page, limit
  Response: { logs: [...], total: 100 }
```

---

## 🤖 AI Agents Architecture

### Separate LangGraph System

The Super Admin AI agents run in a **separate LangGraph system** from the clinic-facing agents (Alex, Sarah, Marcus, Sophia).

```
┌─────────────────────────────────────────────────────────────┐
│              Super Admin Agent System                        │
│                  (Separate LangGraph)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  CSM Agent   │  │ RevOps Agent │  │Platform Ops  │     │
│  │              │  │              │  │    Agent     │     │
│  │ Customer     │  │ Revenue      │  │ Operations   │     │
│  │ Success      │  │ Operations   │  │ Management   │     │
│  │ Management   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  Shared Tools:                                              │
│  - Organization Management                                  │
│  - Cost Analysis                                            │
│  - Usage Analysis                                           │
│  - Revenue Analysis                                         │
│  - Analytics & Insights                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Agent Specifications

#### 1. CSM Agent (Customer Success Manager)

**Purpose:** Proactive customer success management

**Capabilities:**
- Monitor organization health scores
- Identify at-risk customers
- Suggest interventions
- Track onboarding progress
- Analyze usage patterns
- Generate success reports

**Tools:**
- `get_organization_health_score`
- `get_at_risk_organizations`
- `get_onboarding_progress`
- `get_usage_trends`
- `suggest_intervention`
- `create_success_plan`

**Example Interactions:**
- "Which organizations are at risk of churning?"
- "Show me onboarding progress for new clinics"
- "Generate a health report for Organization #42"
- "What interventions should we do this week?"

#### 2. RevOps Agent (Revenue Operations)

**Purpose:** Revenue optimization and growth

**Capabilities:**
- Calculate and forecast MRR/ARR
- Analyze churn and retention
- Identify upsell opportunities
- Track conversion rates
- Optimize pricing
- Generate revenue reports

**Tools:**
- `calculate_mrr_arr`
- `analyze_churn`
- `identify_upsell_opportunities`
- `calculate_ltv`
- `forecast_revenue`
- `analyze_pricing_efficiency`

**Example Interactions:**
- "What's our MRR growth this month?"
- "Show me upsell opportunities"
- "Forecast revenue for next quarter"
- "Which plan has the best retention?"

#### 3. Platform Ops Agent (Platform Operations)

**Purpose:** Platform health and operations

**Capabilities:**
- Monitor infrastructure costs
- Analyze resource utilization
- Identify cost optimization opportunities
- Track system performance
- Manage capacity planning
- Generate ops reports

**Tools:**
- `get_infrastructure_costs`
- `analyze_resource_utilization`
- `identify_cost_savings`
- `get_system_performance`
- `plan_capacity`
- `generate_ops_report`

**Example Interactions:**
- "What are our infrastructure costs this month?"
- "Show me cost optimization opportunities"
- "Analyze resource utilization by organization"
- "Do we need to scale up Cloud SQL?"

---

## 🔐 Security & Permissions

### Role-Based Access Control

```python
# Only super_admin role can access Super Admin Dashboard
@router.get("/super-admin/organizations")
async def list_organizations(
    current_user: User = Depends(require_super_admin)
):
    ...

# Helper function
def require_super_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user
```

### Audit Logging

All admin actions are logged to `admin_actions` table for compliance and security.

```python
async def log_admin_action(
    admin_user_id: int,
    action_type: AdminActionType,
    target_type: str,
    target_id: int,
    action_details: dict,
    request: Request
):
    action = AdminAction(
        admin_user_id=admin_user_id,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        action_details=action_details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(action)
    await db.commit()
```

---

## 📈 Performance Optimization

### Caching Strategy

```python
# Cache expensive calculations
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_mrr_cached(date: str) -> float:
    """Cache MRR calculation for 1 hour."""
    return calculate_mrr(date)

# Use Redis for distributed caching
async def get_usage_summary_cached():
    cache_key = "super_admin:usage_summary"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    summary = await calculate_usage_summary()
    await redis.setex(cache_key, 300, json.dumps(summary))  # 5 min TTL
    return summary
```

### Background Jobs

```python
# Celery tasks for heavy calculations
@celery_app.task
def calculate_daily_analytics():
    """Run daily at midnight to pre-calculate analytics."""
    date = datetime.now().date()
    
    # Calculate and store snapshots
    revenue_snapshot = calculate_revenue_snapshot(date)
    usage_snapshot = calculate_usage_snapshot(date)
    cost_snapshot = calculate_cost_snapshot(date)
    
    # Store in analytics_snapshots table
    store_snapshots(date, revenue_snapshot, usage_snapshot, cost_snapshot)
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Test cost calculation
def test_calculate_organization_cost():
    org = create_test_organization()
    cost = calculate_organization_cost(org.id, start_date, end_date)
    assert cost > 0
    assert cost < 1000  # Sanity check

# Test MRR calculation
def test_calculate_mrr():
    create_test_subscriptions()
    mrr = calculate_mrr(datetime.now().date())
    assert mrr == 8165.0  # 10 clinics * ₪816.5
```

### Integration Tests

```python
# Test Super Admin API
def test_super_admin_organizations_list():
    response = client.get(
        "/api/v1/super-admin/organizations",
        headers=super_admin_headers
    )
    assert response.status_code == 200
    assert len(response.json()["organizations"]) > 0

# Test access control
def test_super_admin_access_denied():
    response = client.get(
        "/api/v1/super-admin/organizations",
        headers=regular_user_headers
    )
    assert response.status_code == 403
```

### E2E Tests

```python
# Test full Super Admin workflow
def test_super_admin_workflow():
    # 1. Login as super admin
    token = login_super_admin()
    
    # 2. View organizations
    orgs = get_organizations(token)
    assert len(orgs) > 0
    
    # 3. View organization details
    org_details = get_organization_details(token, orgs[0].id)
    assert org_details["subscription"] is not None
    
    # 4. Extend trial
    extend_trial(token, orgs[0].id, days=7)
    
    # 5. Verify trial extended
    updated_org = get_organization_details(token, orgs[0].id)
    assert updated_org["subscription"]["trial_end"] > org_details["subscription"]["trial_end"]
```

---

## 📦 Deployment Considerations

### Environment Variables

```bash
# GCP Billing
GCP_BILLING_ACCOUNT=billingAccounts/XXXXXX-XXXXXX-XXXXXX
GCP_BILLING_PROJECT_ID=dentaflow-production
GCP_BILLING_DATASET=billing_export

# Super Admin
SUPER_ADMIN_EMAIL=admin@dentaflow.ai
SUPER_ADMIN_DEFAULT_PASSWORD=<secure_password>

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300

# Background Jobs
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Database Migrations

```bash
# Create migration for new models
alembic revision --autogenerate -m "Add Super Admin Dashboard models"

# Apply migration
alembic upgrade head
```

### GCP Permissions

```bash
# Grant Billing Viewer role to service account
gcloud projects add-iam-policy-binding dentaflow-production \
  --member="serviceAccount:dentaflow-backend@dentaflow-production.iam.gserviceaccount.com" \
  --role="roles/billing.viewer"
```

---

## 📚 Documentation

### API Documentation

Auto-generated with FastAPI:
- Swagger UI: `https://api.dentaflow.ai/docs`
- ReDoc: `https://api.dentaflow.ai/redoc`

### User Guide

- Super Admin Dashboard User Guide
- Cost Tracking Guide
- Usage Monitoring Guide
- AI Agents Guide

---

## 🎯 Success Metrics

### Technical Metrics
- ✅ All API endpoints implemented and tested
- ✅ <500ms response time for dashboard pages
- ✅ 99.9% uptime for Super Admin Dashboard
- ✅ Real-time cost tracking (updated hourly)
- ✅ Usage tracking accuracy >99%

### Business Metrics
- ✅ Complete visibility into all organizations
- ✅ Real-time MRR/ARR tracking
- ✅ Churn prediction accuracy >80%
- ✅ Cost allocation per organization
- ✅ AI agents provide actionable insights

---

## 🚀 Next Steps

1. **Phase 1:** Implement data models and migrations
2. **Phase 2:** Build backend API endpoints
3. **Phase 3:** Create frontend UI components
4. **Phase 4:** Implement AI agents system
5. **Phase 5:** Integration testing and deployment
6. **Phase 6:** Documentation and training

---

**Architecture Team**: Manus AI Agent  
**Review Status**: Ready for Implementation  
**Estimated Time**: 2-3 weeks

