"""
API v1 router configuration.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, 
    chat, 
    telegram, 
    statistics,
    memberships,
    clinic_settings,
    treatment_prices,
    auth_cognito,
    auth_google,
    audit_logs,
    proactive_suggestions,
    organizations,
    email_verification,
    sms_verification,
    baa_signature,
    team_invitations,
    patient_portal,
    invoices
)
from app.api.v1 import appointments, dashboard

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
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])

# Organization management
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(memberships.router, prefix="/memberships", tags=["memberships"])
api_router.include_router(team_invitations.router, tags=["invitations"])
api_router.include_router(clinic_settings.router, prefix="/clinic-settings", tags=["clinic-settings"])
api_router.include_router(treatment_prices.router, prefix="/treatment-prices", tags=["treatment-prices"])

# AI features
api_router.include_router(proactive_suggestions.router, prefix="/suggestions", tags=["suggestions"])

# Dashboard & Appointments
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
from app.api.v1 import agent_actions
api_router.include_router(agent_actions.router, prefix="/agent-actions", tags=["agent-actions"])

# Monitoring & Compliance
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit"])
api_router.include_router(baa_signature.router, tags=["compliance"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])

# Patient Portal
api_router.include_router(patient_portal.router, tags=["patient-portal"])
# Patient Portal with Odoo Integration
from app.api.v1.endpoints import patient_portal_odoo
api_router.include_router(patient_portal_odoo.router, tags=["patient-portal-odoo"])
api_router.include_router(invoices.router, tags=["invoices"])

__all__ = ["api_router"]
