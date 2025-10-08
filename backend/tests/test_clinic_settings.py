"""
Tests for Clinic Settings functionality.
"""
import pytest
from datetime import time
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.clinic_settings import ClinicSettings, DEFAULT_ISRAELI_CLINIC_SETTINGS
from app.models.organization import Organization


def test_create_settings_with_defaults(db: Session):
    """Test creating settings with Israeli defaults."""
    # Create organization
    org = Organization(
        name="Test Clinic",
        slug="test-clinic",
        email="test@example.com"
    )
    db.add(org)
    db.commit()
    
    # Create settings with defaults
    settings = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings)
    db.commit()
    
    # Verify defaults
    assert settings.id is not None
    assert settings.sunday_open == time(8, 0)
    assert settings.sunday_close == time(18, 0)
    assert settings.friday_close == time(13, 0)  # Half day
    assert settings.saturday_open is None  # Shabbat
    assert settings.currency == 'ILS'
    assert settings.tax_rate == Decimal('17.00')
    assert 'bit' in settings.payment_methods


def test_create_custom_settings(db: Session):
    """Test creating settings with custom values."""
    org = Organization(
        name="Custom Clinic",
        slug="custom-clinic",
        email="custom@example.com"
    )
    db.add(org)
    db.commit()
    
    # Create custom settings
    settings = ClinicSettings(
        organization_id=org.id,
        sunday_open=time(9, 0),
        sunday_close=time(17, 0),
        default_appointment_duration=45,
        buffer_between_appointments=15,
        currency='USD',
        tax_rate=Decimal('10.00')
    )
    db.add(settings)
    db.commit()
    
    # Verify custom values
    assert settings.sunday_open == time(9, 0)
    assert settings.default_appointment_duration == 45
    assert settings.currency == 'USD'


def test_unique_constraint(db: Session):
    """Test that organization can only have one settings record."""
    org = Organization(
        name="Unique Test",
        slug="unique-test",
        email="unique@example.com"
    )
    db.add(org)
    db.commit()
    
    # First settings
    settings1 = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings1)
    db.commit()
    
    # Try to create duplicate
    settings2 = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings2)
    
    # Should raise IntegrityError
    with pytest.raises(Exception):  # IntegrityError
        db.commit()


def test_validate_appointment_duration(db: Session):
    """Test appointment duration validation."""
    org = Organization(name="Val Test", slug="val-test", email="val@example.com")
    db.add(org)
    db.commit()
    
    # Too short
    with pytest.raises(ValueError, match="at least 10 minutes"):
        settings = ClinicSettings(
            organization_id=org.id,
            default_appointment_duration=5
        )
        db.add(settings)
        db.flush()
    
    db.rollback()
    
    # Too long
    with pytest.raises(ValueError, match="cannot exceed 240 minutes"):
        settings = ClinicSettings(
            organization_id=org.id,
            default_appointment_duration=300
        )
        db.add(settings)
        db.flush()


def test_validate_buffer_time(db: Session):
    """Test buffer time validation."""
    org = Organization(name="Buffer Test", slug="buffer-test", email="buffer@example.com")
    db.add(org)
    db.commit()
    
    # Negative
    with pytest.raises(ValueError, match="cannot be negative"):
        settings = ClinicSettings(
            organization_id=org.id,
            buffer_between_appointments=-5
        )
        db.add(settings)
        db.flush()
    
    db.rollback()
    
    # Too long
    with pytest.raises(ValueError, match="cannot exceed 60 minutes"):
        settings = ClinicSettings(
            organization_id=org.id,
            buffer_between_appointments=90
        )
        db.add(settings)
        db.flush()


def test_validate_tax_rate(db: Session):
    """Test tax rate validation."""
    org = Organization(name="Tax Test", slug="tax-test", email="tax@example.com")
    db.add(org)
    db.commit()
    
    # Negative
    with pytest.raises(ValueError, match="cannot be negative"):
        settings = ClinicSettings(
            organization_id=org.id,
            tax_rate=Decimal('-5.00')
        )
        db.add(settings)
        db.flush()
    
    db.rollback()
    
    # Over 100%
    with pytest.raises(ValueError, match="cannot exceed 100%"):
        settings = ClinicSettings(
            organization_id=org.id,
            tax_rate=Decimal('150.00')
        )
        db.add(settings)
        db.flush()


def test_validate_currency(db: Session):
    """Test currency code validation."""
    org = Organization(name="Curr Test", slug="curr-test", email="curr@example.com")
    db.add(org)
    db.commit()
    
    # Wrong length
    with pytest.raises(ValueError, match="must be 3 characters"):
        settings = ClinicSettings(
            organization_id=org.id,
            currency='US'
        )
        db.add(settings)
        db.flush()


def test_is_open_on_day(db: Session):
    """Test checking if clinic is open on specific day."""
    org = Organization(name="Hours Test", slug="hours-test", email="hours@example.com")
    db.add(org)
    db.commit()
    
    settings = ClinicSettings(
        organization_id=org.id,
        sunday_open=time(8, 0),
        sunday_close=time(18, 0),
        saturday_open=None,
        saturday_close=None
    )
    db.add(settings)
    db.commit()
    
    # Sunday is open
    assert settings.is_open_on_day('sunday') == True
    
    # Saturday is closed
    assert settings.is_open_on_day('saturday') == False


def test_get_working_hours(db: Session):
    """Test getting working hours for a day."""
    org = Organization(name="Work Test", slug="work-test", email="work@example.com")
    db.add(org)
    db.commit()
    
    settings = ClinicSettings(
        organization_id=org.id,
        monday_open=time(9, 0),
        monday_close=time(17, 0)
    )
    db.add(settings)
    db.commit()
    
    hours = settings.get_working_hours('monday')
    assert hours == (time(9, 0), time(17, 0))
    
    # Closed day
    hours = settings.get_working_hours('saturday')
    assert hours is None


def test_get_all_working_hours(db: Session):
    """Test getting all weekly working hours."""
    org = Organization(name="Week Test", slug="week-test", email="week@example.com")
    db.add(org)
    db.commit()
    
    settings = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings)
    db.commit()
    
    all_hours = settings.get_all_working_hours()
    
    # Check structure
    assert 'sunday' in all_hours
    assert 'saturday' in all_hours
    
    # Sunday should be open
    assert all_hours['sunday'] is not None
    
    # Saturday should be closed (Shabbat)
    assert all_hours['saturday'] is None


def test_has_any_communication_enabled(db: Session):
    """Test checking if any communication channel is enabled."""
    org = Organization(name="Comm Test", slug="comm-test", email="comm@example.com")
    db.add(org)
    db.commit()
    
    # All disabled
    settings = ClinicSettings(
        organization_id=org.id,
        sms_enabled=False,
        email_enabled=False,
        whatsapp_enabled=False,
        telegram_enabled=False
    )
    db.add(settings)
    db.commit()
    
    assert settings.has_any_communication_enabled == False
    
    # Enable one
    settings.sms_enabled = True
    db.commit()
    
    assert settings.has_any_communication_enabled == True


def test_accepts_online_payments(db: Session):
    """Test checking if clinic accepts online payments."""
    org = Organization(name="Pay Test", slug="pay-test", email="pay@example.com")
    db.add(org)
    db.commit()
    
    # Only cash
    settings = ClinicSettings(
        organization_id=org.id,
        payment_methods=['cash']
    )
    db.add(settings)
    db.commit()
    
    assert settings.accepts_online_payments == False
    
    # Add credit card
    settings.payment_methods = ['cash', 'credit_card']
    db.commit()
    
    assert settings.accepts_online_payments == True


def test_to_dict(db: Session):
    """Test converting settings to dictionary."""
    org = Organization(name="Dict Test", slug="dict-test", email="dict@example.com")
    db.add(org)
    db.commit()
    
    settings = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings)
    db.commit()
    
    data = settings.to_dict()
    
    # Check structure
    assert 'id' in data
    assert 'organization_id' in data
    assert 'operating_hours' in data
    assert 'appointment_settings' in data
    assert 'communication' in data
    assert 'billing' in data
    assert 'clinic_info' in data
    
    # Check nested data
    assert 'default_duration' in data['appointment_settings']
    assert 'currency' in data['billing']
    assert 'sms_enabled' in data['communication']


def test_cascade_delete(db: Session):
    """Test that settings are deleted when organization is deleted."""
    org = Organization(name="Cascade Test", slug="cascade-test", email="cascade@example.com")
    db.add(org)
    db.commit()
    
    settings = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings)
    db.commit()
    
    settings_id = settings.id
    
    # Delete organization
    db.delete(org)
    db.commit()
    
    # Settings should be deleted too
    found = db.query(ClinicSettings).filter(ClinicSettings.id == settings_id).first()
    assert found is None


def test_israeli_defaults_complete(db: Session):
    """Test that Israeli defaults include all required fields."""
    org = Organization(name="Defaults Test", slug="defaults-test", email="defaults@example.com")
    db.add(org)
    db.commit()
    
    settings = ClinicSettings(
        organization_id=org.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings)
    db.commit()
    
    # Verify all critical defaults are set
    assert settings.default_appointment_duration > 0
    assert settings.currency is not None
    assert settings.tax_rate is not None
    assert settings.payment_methods is not None
    assert len(settings.payment_methods) > 0
    assert settings.reminder_hours_before > 0
    
    # Verify Israeli-specific defaults
    assert settings.currency == 'ILS'
    assert settings.tax_rate == Decimal('17.00')
    assert 'bit' in settings.payment_methods  # Israeli payment method
