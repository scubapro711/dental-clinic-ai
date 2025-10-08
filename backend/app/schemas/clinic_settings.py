"""
Pydantic schemas for Clinic Settings API.
"""
from datetime import time
from decimal import Decimal
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator


class OperatingHoursSchema(BaseModel):
    """Schema for daily operating hours."""
    open: Optional[time] = Field(None, description="Opening time")
    close: Optional[time] = Field(None, description="Closing time")
    
    @root_validator(skip_on_failure=True)
    def validate_hours(cls, values):
        """Validate that close time is after open time."""
        open_time = values.get('open')
        close_time = values.get('close')
        
        if open_time and close_time:
            if close_time <= open_time:
                raise ValueError("Closing time must be after opening time")
        elif (open_time and not close_time) or (close_time and not open_time):
            raise ValueError("Both open and close times must be provided")
        
        return values


class WeeklyHoursSchema(BaseModel):
    """Schema for weekly operating hours."""
    sunday: Optional[OperatingHoursSchema] = None
    monday: Optional[OperatingHoursSchema] = None
    tuesday: Optional[OperatingHoursSchema] = None
    wednesday: Optional[OperatingHoursSchema] = None
    thursday: Optional[OperatingHoursSchema] = None
    friday: Optional[OperatingHoursSchema] = None
    saturday: Optional[OperatingHoursSchema] = None


class AppointmentSettingsSchema(BaseModel):
    """Schema for appointment configuration."""
    default_duration: int = Field(
        30,
        ge=10,
        le=240,
        description="Default appointment duration in minutes"
    )
    buffer_time: int = Field(
        10,
        ge=0,
        le=60,
        description="Buffer time between appointments in minutes"
    )
    advance_booking_days: int = Field(
        60,
        ge=1,
        le=365,
        description="How many days in advance patients can book"
    )
    cancellation_notice_hours: int = Field(
        24,
        ge=0,
        le=168,
        description="Required notice for cancellation in hours"
    )
    no_show_fee: Decimal = Field(
        Decimal('100.00'),
        ge=0,
        le=1000,
        description="Fee for no-show appointments (ILS)"
    )
    allow_online_booking: bool = Field(
        True,
        description="Allow patients to book online"
    )
    require_deposit: bool = Field(
        False,
        description="Require deposit for appointments"
    )
    deposit_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Deposit amount if required (ILS)"
    )
    
    @root_validator(skip_on_failure=True)
    def validate_deposit(cls, values):
        """Validate deposit settings."""
        require_deposit = values.get('require_deposit')
        deposit_amount = values.get('deposit_amount')
        
        if require_deposit and not deposit_amount:
            raise ValueError("Deposit amount is required when require_deposit is True")
        
        return values


class CommunicationSettingsSchema(BaseModel):
    """Schema for communication preferences."""
    sms_enabled: bool = Field(True, description="Enable SMS notifications")
    email_enabled: bool = Field(True, description="Enable email notifications")
    whatsapp_enabled: bool = Field(False, description="Enable WhatsApp notifications")
    telegram_enabled: bool = Field(False, description="Enable Telegram notifications")
    reminder_hours_before: int = Field(
        24,
        ge=1,
        le=168,
        description="Send appointment reminder X hours before"
    )
    followup_after_hours: int = Field(
        24,
        ge=0,
        description="Send follow-up message X hours after appointment"
    )
    recall_after_months: int = Field(
        6,
        ge=1,
        le=24,
        description="Send recall reminder after X months"
    )
    
    @root_validator(skip_on_failure=True)
    def validate_at_least_one_channel(cls, values):
        """Ensure at least one communication channel is enabled."""
        if not any([
            values.get('sms_enabled'),
            values.get('email_enabled'),
            values.get('whatsapp_enabled'),
            values.get('telegram_enabled')
        ]):
            raise ValueError("At least one communication channel must be enabled")
        
        return values


class BillingSettingsSchema(BaseModel):
    """Schema for billing configuration."""
    currency: str = Field(
        'ILS',
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)"
    )
    tax_rate: Decimal = Field(
        Decimal('17.00'),
        ge=0,
        le=100,
        description="VAT/Tax rate percentage"
    )
    payment_methods: List[str] = Field(
        ['cash', 'credit_card', 'bank_transfer', 'bit'],
        description="Accepted payment methods"
    )
    invoice_prefix: Optional[str] = Field(
        None,
        max_length=10,
        description="Invoice number prefix"
    )
    invoice_starting_number: int = Field(
        1000,
        ge=1,
        description="Starting invoice number"
    )
    
    @validator('currency')
    def validate_currency_uppercase(cls, v):
        """Ensure currency code is uppercase."""
        return v.upper()
    
    @validator('payment_methods')
    def validate_payment_methods(cls, v):
        """Validate payment methods."""
        valid_methods = [
            'cash', 'credit_card', 'bank_transfer', 'bit',
            'paypal', 'check', 'insurance'
        ]
        for method in v:
            if method not in valid_methods:
                raise ValueError(f"Invalid payment method: {method}")
        
        if not v:
            raise ValueError("At least one payment method must be specified")
        
        return v


class ClinicInfoSchema(BaseModel):
    """Schema for clinic information."""
    name_hebrew: Optional[str] = Field(None, max_length=255)
    name_english: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    business_license: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, max_length=50)
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation."""
        if v and '@' not in v:
            raise ValueError("Invalid email address")
        return v
    
    @validator('website')
    def validate_website(cls, v):
        """Basic website URL validation."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("Website URL must start with http:// or https://")
        return v


class ClinicSettingsCreate(BaseModel):
    """Schema for creating clinic settings."""
    organization_id: UUID
    operating_hours: Optional[WeeklyHoursSchema] = None
    appointment_settings: Optional[AppointmentSettingsSchema] = None
    communication: Optional[CommunicationSettingsSchema] = None
    billing: Optional[BillingSettingsSchema] = None
    clinic_info: Optional[ClinicInfoSchema] = None


class ClinicSettingsUpdate(BaseModel):
    """Schema for updating clinic settings (all fields optional)."""
    operating_hours: Optional[WeeklyHoursSchema] = None
    appointment_settings: Optional[AppointmentSettingsSchema] = None
    communication: Optional[CommunicationSettingsSchema] = None
    billing: Optional[BillingSettingsSchema] = None
    clinic_info: Optional[ClinicInfoSchema] = None


class ClinicSettingsResponse(BaseModel):
    """Schema for clinic settings response."""
    id: UUID
    organization_id: UUID
    operating_hours: Dict
    appointment_settings: AppointmentSettingsSchema
    communication: CommunicationSettingsSchema
    billing: BillingSettingsSchema
    clinic_info: ClinicInfoSchema
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float,
            UUID: str
        }
