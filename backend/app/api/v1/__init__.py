"""
API v1 router configuration.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, 
    chat,
    ai_chat,
    telegram,
    telegram_admin,
    statistics,
    memberships,
    clinic_settings,
    treatment_prices,
    auth_cognito,
    auth_google,
    audit_logs,
    proactive_suggestions,
    decision_queue,
    tooth_chart,
    medical_questionnaire,
    xray,
    treatment_categories,
    organizations,
    email_verification,
    sms_verification,
    baa_signature,
    team_invitations,
    patient_portal,
    invoices,
    financial,
    dashboard,
    dashboard_metrics,
    migrate,
    verify_schema,
    subscriptions,
    admin_plans,
    admin_billing,
    webhooks,
    legal,
    demo,
)
from app.api.v1.endpoints.super_admin import organizations as super_admin_organizations
from app.api.v1.endpoints.super_admin import usage as super_admin_usage
from app.api.v1.endpoints.super_admin import revenue as super_admin_revenue
from app.api.v1.endpoints.super_admin import costs as super_admin_costs
from app.api.v1.endpoints.super_admin import exports as super_admin_exports
from app.api.v1.endpoints.super_admin import analytics as super_admin_analytics
from app.api.v1 import appointments

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Authentication
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(auth_cognito.router, prefix="/auth", tags=["auth"])
api_router.include_router(auth_google.router, tags=["auth"])
api_router.include_router(email_verification.router, tags=["auth"])
api_router.include_router(sms_verification.router, tags=["auth"])

# Core features
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(ai_chat.router, prefix="/ai", tags=["ai-chat"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(telegram_admin.router, tags=["telegram-admin"])

# Organization management
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(memberships.router, prefix="/memberships", tags=["memberships"])
api_router.include_router(team_invitations.router, tags=["invitations"])
api_router.include_router(clinic_settings.router, prefix="/clinic-settings", tags=["clinic-settings"])
api_router.include_router(treatment_prices.router, prefix="/treatment-prices", tags=["treatment-prices"])

# AI features
api_router.include_router(proactive_suggestions.router, prefix="/suggestions", tags=["suggestions"])
api_router.include_router(decision_queue.router, prefix="/decision-queue", tags=["decision-queue"])

# Dental features
api_router.include_router(tooth_chart.router, prefix="/tooth-chart", tags=["tooth-chart"])
api_router.include_router(medical_questionnaire.router, prefix="/medical-questionnaire", tags=["medical-questionnaire"])
api_router.include_router(xray.router, prefix="/xray", tags=["xray"])
api_router.include_router(treatment_categories.router, prefix="/treatment-categories", tags=["treatment-categories"])

# Dashboard & Appointments
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(dashboard_metrics.router, prefix="/dashboard/metrics", tags=["dashboard-metrics"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
from app.api.v1 import agent_actions
api_router.include_router(agent_actions.router, prefix="/agent-actions", tags=["agent-actions"])

# Monitoring & Compliance
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit"])
api_router.include_router(baa_signature.router, tags=["compliance"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])

# Financial
api_router.include_router(financial.router, tags=["financial"])

# Subscriptions & Billing
api_router.include_router(subscriptions.router, tags=["subscriptions"])
api_router.include_router(admin_plans.router, tags=["super-admin"])
api_router.include_router(admin_billing.router, tags=["super-admin"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Super Admin Dashboard
api_router.include_router(super_admin_organizations.router, prefix="/super-admin", tags=["super-admin"])
api_router.include_router(super_admin_usage.router, prefix="/super-admin", tags=["super-admin"])
api_router.include_router(super_admin_revenue.router, prefix="/super-admin", tags=["super-admin"])
api_router.include_router(super_admin_costs.router, prefix="/super-admin/costs", tags=["super-admin"])
api_router.include_router(super_admin_exports.router, prefix="/super-admin/export", tags=["super-admin"])
api_router.include_router(super_admin_analytics.router, prefix="/super-admin/analytics", tags=["super-admin"])

# Patient Portal
api_router.include_router(patient_portal.router, tags=["patient-portal"])

# Legal Documents
api_router.include_router(legal.router, tags=["legal"])

# Interactive Demo
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
# Patient Portal with Odoo Integration
from app.api.v1.endpoints import patient_portal_odoo, user_patient_mapping
api_router.include_router(patient_portal_odoo.router, tags=["patient-portal-odoo"])
api_router.include_router(user_patient_mapping.router, tags=["user-patient-mapping"])
api_router.include_router(invoices.router, tags=["invoices"])

# Temporary migration endpoint
api_router.include_router(migrate.router, prefix="/migrate", tags=["migration"])
api_router.include_router(verify_schema.router, prefix="/verify", tags=["verification"])

__all__ = ["api_router"]
