"""
Database models for DentalAI.

This module exports all SQLAlchemy models for easy import.
"""

# Core models
from app.models.user import User, UserRole
from app.models.organization import Organization, SubscriptionTier
from app.models.organization_membership import OrganizationMembership

# Billing and subscriptions
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier
from app.models.payment import Payment, PaymentStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.plan_configuration import PlanConfiguration

# Settings and configuration
from app.models.clinic_settings import ClinicSettings
from app.models.treatment_price import TreatmentPrice
from app.models.treatment_category import TreatmentCategory

# Communication
from app.models.conversation import Conversation, ConversationStatus, ConversationChannel
from app.models.message import Message, MessageRole
from app.models.telegram_conversation import TelegramConversation
from app.models.telegram_user import TelegramUser
from app.models.telegram_invite_code import TelegramInviteCode

# Verification and authentication
from app.models.email_verification import EmailVerificationToken
from app.models.sms_verification import SMSVerificationCode
from app.models.team_invitation import TeamInvitation

# Medical records
from app.models.medical_questionnaire import MedicalQuestionnaire
from app.models.tooth_record import ToothRecord
from app.models.xray import XRay

# Compliance and legal
from app.models.consent import (
    PatientConsent,
    DataSubjectRequest,
    PrivacyPolicyAcceptance,
    ConsentType,
    ConsentStatus,
)
from app.models.baa_signature import BAASignature
from app.models.audit_log import AuditLog

# Other
from app.models.proactive_suggestion import ProactiveSuggestion
from app.models.user_patient_mapping import UserPatientMapping

__all__ = [
    # Core
    "User",
    "UserRole",
    "Organization",
    "SubscriptionTier",
    "OrganizationMembership",
    # Billing
    "Subscription",
    "SubscriptionStatus",
    "PlanTier",
    "Payment",
    "PaymentStatus",
    "Invoice",
    "InvoiceStatus",
    "PlanConfiguration",
    # Settings
    "ClinicSettings",
    "TreatmentPrice",
    "TreatmentCategory",
    # Communication
    "Conversation",
    "ConversationStatus",
    "ConversationChannel",
    "Message",
    "MessageRole",
    "TelegramConversation",
    "TelegramUser",
    "TelegramInviteCode",
    # Verification
    "EmailVerificationToken",
    "SMSVerificationCode",
    "TeamInvitation",
    # Medical
    "MedicalQuestionnaire",
    "ToothRecord",
    "XRay",
    # Compliance
    "PatientConsent",
    "DataSubjectRequest",
    "PrivacyPolicyAcceptance",
    "ConsentType",
    "ConsentStatus",
    "BAASignature",
    "AuditLog",
    # Other
    "ProactiveSuggestion",
    "UserPatientMapping",
]

