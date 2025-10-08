"""
Clinic Settings model for organization-specific configuration.

Based on DENTAL_CLINIC_OPERATIONS_RESEARCH.md - comprehensive Israeli clinic settings.
"""
from datetime import datetime, time
from typing import Optional, List, Dict
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, Numeric, 
    String, Text, Time, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.database import Base


class ClinicSettings(Base):
    """
    Clinic-specific settings and configuration.
    
    Each organization (dental clinic) has one settings record that controls:
    - Operating hours (Israeli work week: Sunday-Friday)
    - Appointment scheduling rules
    - Communication preferences
    - Billing and payment settings
    - Clinic information
    
    Based on research of Israeli dental clinic operations.
    """
    __tablename__ = "clinic_settings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign key
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # ========== Operating Hours ==========
    # Israeli work week: Sunday-Friday (Saturday is Shabbat)
    
    sunday_open = Column(Time, nullable=True)
    sunday_close = Column(Time, nullable=True)
    
    monday_open = Column(Time, nullable=True)
    monday_close = Column(Time, nullable=True)
    
    tuesday_open = Column(Time, nullable=True)
    tuesday_close = Column(Time, nullable=True)
    
    wednesday_open = Column(Time, nullable=True)
    wednesday_close = Column(Time, nullable=True)
    
    thursday_open = Column(Time, nullable=True)
    thursday_close = Column(Time, nullable=True)
    
    friday_open = Column(Time, nullable=True)
    friday_close = Column(Time, nullable=True)
    
    saturday_open = Column(Time, nullable=True)
    saturday_close = Column(Time, nullable=True)
    
    # ========== Appointment Settings ==========
    # Based on industry best practices from research
    
    default_appointment_duration = Column(
        Integer,
        nullable=False,
        default=30,
        comment="Default appointment duration in minutes"
    )
    
    buffer_between_appointments = Column(
        Integer,
        nullable=False,
        default=10,
        comment="Buffer time between appointments in minutes"
    )
    
    advance_booking_days = Column(
        Integer,
        nullable=False,
        default=60,
        comment="How many days in advance patients can book"
    )
    
    cancellation_notice_hours = Column(
        Integer,
        nullable=False,
        default=24,
        comment="Required notice for cancellation (hours)"
    )
    
    no_show_fee = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('100.00'),
        comment="Fee for no-show appointments (ILS)"
    )
    
    allow_online_booking = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Allow patients to book online"
    )
    
    require_deposit = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Require deposit for appointments"
    )
    
    deposit_amount = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Deposit amount if required (ILS)"
    )
    
    # ========== Communication Settings ==========
    
    sms_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Enable SMS notifications"
    )
    
    email_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Enable email notifications"
    )
    
    whatsapp_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Enable WhatsApp notifications"
    )
    
    telegram_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Enable Telegram notifications"
    )
    
    reminder_hours_before = Column(
        Integer,
        nullable=False,
        default=24,
        comment="Send appointment reminder X hours before"
    )
    
    send_followup_after_hours = Column(
        Integer,
        nullable=False,
        default=24,
        comment="Send follow-up message X hours after appointment"
    )
    
    send_recall_after_months = Column(
        Integer,
        nullable=False,
        default=6,
        comment="Send recall reminder after X months"
    )
    
    # ========== Billing Settings ==========
    # Israeli market specific
    
    currency = Column(
        String(3),
        nullable=False,
        default='ILS',
        comment="Currency code (ISO 4217)"
    )
    
    tax_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal('17.00'),
        comment="VAT/Tax rate percentage (Israel: 17%)"
    )
    
    payment_methods = Column(
        JSON,
        nullable=False,
        default=["cash", "credit_card", "bank_transfer", "bit"],
        comment="Accepted payment methods"
    )
    
    invoice_prefix = Column(
        String(10),
        nullable=True,
        comment="Invoice number prefix (e.g., 'INV-')"
    )
    
    invoice_starting_number = Column(
        Integer,
        nullable=False,
        default=1000,
        comment="Starting invoice number"
    )
    
    # ========== Clinic Information ==========
    
    clinic_name_hebrew = Column(
        String(255),
        nullable=True,
        comment="Clinic name in Hebrew"
    )
    
    clinic_name_english = Column(
        String(255),
        nullable=True,
        comment="Clinic name in English"
    )
    
    clinic_logo_url = Column(
        String(500),
        nullable=True,
        comment="URL to clinic logo image"
    )
    
    clinic_address = Column(
        Text,
        nullable=True,
        comment="Full clinic address"
    )
    
    clinic_phone = Column(
        String(20),
        nullable=True,
        comment="Clinic phone number"
    )
    
    clinic_email = Column(
        String(255),
        nullable=True,
        comment="Clinic email address"
    )
    
    clinic_website = Column(
        String(255),
        nullable=True,
        comment="Clinic website URL"
    )
    
    # ========== Business Settings ==========
    
    business_license_number = Column(
        String(50),
        nullable=True,
        comment="Israeli business license number"
    )
    
    tax_id = Column(
        String(50),
        nullable=True,
        comment="Israeli tax ID (מס' עוסק מורשה)"
    )
    
    # ========== Timestamps ==========
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # ========== Relationships ==========
    
    organization = relationship("Organization", back_populates="settings")
    
    # ========== Constraints ==========
    
    __table_args__ = (
        UniqueConstraint('organization_id', name='uq_clinic_settings_org'),
    )
    
    # ========== Validators ==========
    
    @validates('default_appointment_duration')
    def validate_appointment_duration(self, key: str, value: int) -> int:
        """Validate appointment duration is reasonable."""
        if value < 10:
            raise ValueError("Appointment duration must be at least 10 minutes")
        if value > 240:
            raise ValueError("Appointment duration cannot exceed 240 minutes (4 hours)")
        return value
    
    @validates('buffer_between_appointments')
    def validate_buffer_time(self, key: str, value: int) -> int:
        """Validate buffer time is reasonable."""
        if value < 0:
            raise ValueError("Buffer time cannot be negative")
        if value > 60:
            raise ValueError("Buffer time cannot exceed 60 minutes")
        return value
    
    @validates('advance_booking_days')
    def validate_advance_booking(self, key: str, value: int) -> int:
        """Validate advance booking days."""
        if value < 1:
            raise ValueError("Advance booking must be at least 1 day")
        if value > 365:
            raise ValueError("Advance booking cannot exceed 365 days")
        return value
    
    @validates('cancellation_notice_hours')
    def validate_cancellation_notice(self, key: str, value: int) -> int:
        """Validate cancellation notice hours."""
        if value < 0:
            raise ValueError("Cancellation notice cannot be negative")
        if value > 168:  # 1 week
            raise ValueError("Cancellation notice cannot exceed 168 hours (1 week)")
        return value
    
    @validates('no_show_fee')
    def validate_no_show_fee(self, key: str, value: Decimal) -> Decimal:
        """Validate no-show fee."""
        if value < 0:
            raise ValueError("No-show fee cannot be negative")
        if value > 1000:
            raise ValueError("No-show fee seems too high (max 1000 ILS)")
        return value
    
    @validates('tax_rate')
    def validate_tax_rate(self, key: str, value: Decimal) -> Decimal:
        """Validate tax rate percentage."""
        if value < 0:
            raise ValueError("Tax rate cannot be negative")
        if value > 100:
            raise ValueError("Tax rate cannot exceed 100%")
        return value
    
    @validates('currency')
    def validate_currency(self, key: str, value: str) -> str:
        """Validate currency code."""
        if len(value) != 3:
            raise ValueError("Currency code must be 3 characters (ISO 4217)")
        return value.upper()
    
    @validates('reminder_hours_before')
    def validate_reminder_hours(self, key: str, value: int) -> int:
        """Validate reminder hours."""
        if value < 1:
            raise ValueError("Reminder must be at least 1 hour before")
        if value > 168:  # 1 week
            raise ValueError("Reminder cannot be more than 168 hours (1 week) before")
        return value
    
    @validates('send_recall_after_months')
    def validate_recall_months(self, key: str, value: int) -> int:
        """Validate recall months."""
        if value < 1:
            raise ValueError("Recall period must be at least 1 month")
        if value > 24:
            raise ValueError("Recall period cannot exceed 24 months")
        return value
    
    # ========== Helper Methods ==========
    
    def is_open_on_day(self, day_name: str) -> bool:
        """Check if clinic is open on a specific day."""
        open_time = getattr(self, f"{day_name}_open")
        close_time = getattr(self, f"{day_name}_close")
        return open_time is not None and close_time is not None
    
    def get_working_hours(self, day_name: str) -> Optional[tuple[time, time]]:
        """Get working hours for a specific day."""
        open_time = getattr(self, f"{day_name}_open")
        close_time = getattr(self, f"{day_name}_close")
        if open_time and close_time:
            return (open_time, close_time)
        return None
    
    def get_all_working_hours(self) -> Dict[str, Optional[tuple[time, time]]]:
        """Get working hours for all days."""
        days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        return {day: self.get_working_hours(day) for day in days}
    
    @hybrid_property
    def has_any_communication_enabled(self) -> bool:
        """Check if any communication channel is enabled."""
        return (
            self.sms_enabled or 
            self.email_enabled or 
            self.whatsapp_enabled or 
            self.telegram_enabled
        )
    
    @hybrid_property
    def accepts_online_payments(self) -> bool:
        """Check if clinic accepts online payments."""
        if not self.payment_methods:
            return False
        online_methods = ['credit_card', 'bit', 'paypal']
        return any(method in self.payment_methods for method in online_methods)
    
    def to_dict(self) -> Dict:
        """Convert settings to dictionary for API responses."""
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'operating_hours': self.get_all_working_hours(),
            'appointment_settings': {
                'default_duration': self.default_appointment_duration,
                'buffer_time': self.buffer_between_appointments,
                'advance_booking_days': self.advance_booking_days,
                'cancellation_notice_hours': self.cancellation_notice_hours,
                'no_show_fee': float(self.no_show_fee),
                'allow_online_booking': self.allow_online_booking,
                'require_deposit': self.require_deposit,
                'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            },
            'communication': {
                'sms_enabled': self.sms_enabled,
                'email_enabled': self.email_enabled,
                'whatsapp_enabled': self.whatsapp_enabled,
                'telegram_enabled': self.telegram_enabled,
                'reminder_hours_before': self.reminder_hours_before,
                'followup_after_hours': self.send_followup_after_hours,
                'recall_after_months': self.send_recall_after_months,
            },
            'billing': {
                'currency': self.currency,
                'tax_rate': float(self.tax_rate),
                'payment_methods': self.payment_methods,
                'invoice_prefix': self.invoice_prefix,
                'invoice_starting_number': self.invoice_starting_number,
            },
            'clinic_info': {
                'name_hebrew': self.clinic_name_hebrew,
                'name_english': self.clinic_name_english,
                'logo_url': self.clinic_logo_url,
                'address': self.clinic_address,
                'phone': self.clinic_phone,
                'email': self.clinic_email,
                'website': self.clinic_website,
                'business_license': self.business_license_number,
                'tax_id': self.tax_id,
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<ClinicSettings(organization_id={self.organization_id})>"


# Default settings for Israeli dental clinics
DEFAULT_ISRAELI_CLINIC_SETTINGS = {
    # Typical Israeli clinic hours (Sunday-Thursday full day, Friday half day)
    'sunday_open': time(8, 0),
    'sunday_close': time(18, 0),
    'monday_open': time(8, 0),
    'monday_close': time(18, 0),
    'tuesday_open': time(8, 0),
    'tuesday_close': time(18, 0),
    'wednesday_open': time(8, 0),
    'wednesday_close': time(18, 0),
    'thursday_open': time(8, 0),
    'thursday_close': time(18, 0),
    'friday_open': time(8, 0),
    'friday_close': time(13, 0),  # Half day for Shabbat
    'saturday_open': None,  # Closed for Shabbat
    'saturday_close': None,
    
    # Standard appointment settings
    'default_appointment_duration': 30,
    'buffer_between_appointments': 10,
    'advance_booking_days': 60,
    'cancellation_notice_hours': 24,
    'no_show_fee': Decimal('100.00'),
    'allow_online_booking': True,
    'require_deposit': False,
    
    # Communication defaults
    'sms_enabled': True,
    'email_enabled': True,
    'whatsapp_enabled': False,
    'telegram_enabled': False,
    'reminder_hours_before': 24,
    'send_followup_after_hours': 24,
    'send_recall_after_months': 6,
    
    # Israeli billing defaults
    'currency': 'ILS',
    'tax_rate': Decimal('17.00'),  # Israeli VAT
    'payment_methods': ['cash', 'credit_card', 'bank_transfer', 'bit'],
    'invoice_starting_number': 1000,
}
