"""
Unit Tests for Odoo Error Handler

Tests for app.services.odoo_error_handler module including:
- Custom exceptions
- Validation models (Pydantic)
- Error handling decorator
- Retry decorator
- Validation functions
- Data sanitization
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta
from pydantic import ValidationError

from app.services.odoo_error_handler import (
    # Exceptions
    OdooServiceError,
    OdooConnectionError,
    OdooValidationError,
    OdooAuthenticationError,
    OdooNotFoundError,
    OdooPermissionError,
    # Validation Models
    PatientProfileValidation,
    AppointmentValidation,
    AvailableSlotsValidation,
    # Decorators
    handle_odoo_errors,
    retry_on_failure,
    # Validation Functions
    validate_patient_id,
    validate_doctor_id,
    validate_date_range,
    validate_pagination,
    # Sanitization Functions
    sanitize_patient_data,
    sanitize_appointment_data,
)


@pytest.mark.unit
@pytest.mark.service
class TestExceptions:
    """Test custom exception classes."""
    
    def test_odoo_service_error(self):
        """Test base OdooServiceError."""
        error = OdooServiceError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_odoo_connection_error(self):
        """Test OdooConnectionError inherits from OdooServiceError."""
        error = OdooConnectionError("Connection failed")
        assert isinstance(error, OdooServiceError)
        assert isinstance(error, Exception)
    
    def test_odoo_validation_error(self):
        """Test OdooValidationError."""
        error = OdooValidationError("Validation failed")
        assert isinstance(error, OdooServiceError)
    
    def test_odoo_authentication_error(self):
        """Test OdooAuthenticationError."""
        error = OdooAuthenticationError("Auth failed")
        assert isinstance(error, OdooServiceError)
    
    def test_odoo_not_found_error(self):
        """Test OdooNotFoundError."""
        error = OdooNotFoundError("Not found")
        assert isinstance(error, OdooServiceError)
    
    def test_odoo_permission_error(self):
        """Test OdooPermissionError."""
        error = OdooPermissionError("Permission denied")
        assert isinstance(error, OdooServiceError)


@pytest.mark.unit
@pytest.mark.service
class TestPatientProfileValidation:
    """Test PatientProfileValidation model."""
    
    def test_valid_patient_profile(self):
        """Test valid patient profile."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "date_of_birth": date(1990, 1, 1)
        }
        profile = PatientProfileValidation(**data)
        assert profile.name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.phone == "+1-555-123-4567"
        assert profile.date_of_birth == date(1990, 1, 1)
    
    def test_patient_profile_minimal(self):
        """Test patient profile with minimal data."""
        profile = PatientProfileValidation(name="Jane Doe")
        assert profile.name == "Jane Doe"
        assert profile.email is None
        assert profile.phone is None
        assert profile.date_of_birth is None
    
    def test_patient_profile_name_too_short(self):
        """Test that name must be at least 2 characters."""
        with pytest.raises(ValidationError) as exc_info:
            PatientProfileValidation(name="A")
        assert "at least 2 characters" in str(exc_info.value)
    
    def test_patient_profile_name_too_long(self):
        """Test that name cannot exceed 100 characters."""
        with pytest.raises(ValidationError) as exc_info:
            PatientProfileValidation(name="A" * 101)
        assert "at most 100 characters" in str(exc_info.value)
    
    def test_patient_profile_invalid_email(self):
        """Test that invalid email is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PatientProfileValidation(name="John Doe", email="invalid-email")
        assert "email" in str(exc_info.value).lower()
    
    def test_patient_profile_invalid_phone(self):
        """Test that invalid phone is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PatientProfileValidation(name="John Doe", phone="abc")
        assert "phone" in str(exc_info.value).lower()
    
    def test_patient_profile_future_dob(self):
        """Test that future date of birth is rejected."""
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            PatientProfileValidation(name="John Doe", date_of_birth=future_date)
        assert "future" in str(exc_info.value).lower()
    
    def test_patient_profile_old_dob(self):
        """Test that date of birth before 1900 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PatientProfileValidation(name="John Doe", date_of_birth=date(1899, 12, 31))
        assert "1900" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.service
class TestAppointmentValidation:
    """Test AppointmentValidation model."""
    
    def test_valid_appointment(self):
        """Test valid appointment."""
        future_date = datetime.now() + timedelta(days=1)
        data = {
            "patient_id": 123,
            "doctor_id": 456,
            "appointment_date": future_date,
            "duration_minutes": 30,
            "appointment_type": "Checkup",
            "notes": "Regular checkup"
        }
        appointment = AppointmentValidation(**data)
        assert appointment.patient_id == 123
        assert appointment.doctor_id == 456
        assert appointment.duration_minutes == 30
    
    def test_appointment_minimal(self):
        """Test appointment with minimal data."""
        future_date = datetime.now() + timedelta(days=1)
        appointment = AppointmentValidation(
            patient_id=123,
            doctor_id=456,
            appointment_date=future_date
        )
        assert appointment.duration_minutes == 30  # Default
        assert appointment.appointment_type is None
        assert appointment.notes is None
    
    def test_appointment_invalid_patient_id(self):
        """Test that patient_id must be positive."""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            AppointmentValidation(
                patient_id=0,
                doctor_id=456,
                appointment_date=future_date
            )
        assert "greater than 0" in str(exc_info.value)
    
    def test_appointment_invalid_doctor_id(self):
        """Test that doctor_id must be positive."""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            AppointmentValidation(
                patient_id=123,
                doctor_id=-1,
                appointment_date=future_date
            )
        assert "greater than 0" in str(exc_info.value)
    
    def test_appointment_past_date(self):
        """Test that appointment date cannot be in the past."""
        past_date = datetime.now() - timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            AppointmentValidation(
                patient_id=123,
                doctor_id=456,
                appointment_date=past_date
            )
        assert "past" in str(exc_info.value).lower()
    
    def test_appointment_duration_too_short(self):
        """Test that duration must be at least 15 minutes."""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            AppointmentValidation(
                patient_id=123,
                doctor_id=456,
                appointment_date=future_date,
                duration_minutes=10
            )
        assert "greater than or equal to 15" in str(exc_info.value)
    
    def test_appointment_duration_too_long(self):
        """Test that duration cannot exceed 240 minutes."""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            AppointmentValidation(
                patient_id=123,
                doctor_id=456,
                appointment_date=future_date,
                duration_minutes=300
            )
        assert "less than or equal to 240" in str(exc_info.value)
    
    def test_appointment_notes_too_long(self):
        """Test that notes cannot exceed 500 characters."""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            AppointmentValidation(
                patient_id=123,
                doctor_id=456,
                appointment_date=future_date,
                notes="A" * 501
            )
        assert "at most 500 characters" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.service
class TestAvailableSlotsValidation:
    """Test AvailableSlotsValidation model."""
    
    def test_valid_slots_request(self):
        """Test valid available slots request."""
        data = {
            "doctor_id": 456,
            "date": date.today() + timedelta(days=1),
            "duration_minutes": 30
        }
        slots = AvailableSlotsValidation(**data)
        assert slots.doctor_id == 456
        assert slots.duration_minutes == 30
    
    def test_slots_request_minimal(self):
        """Test slots request with minimal data."""
        slots = AvailableSlotsValidation(
            doctor_id=456,
            date=date.today() + timedelta(days=1)
        )
        assert slots.duration_minutes == 30  # Default
    
    def test_slots_request_invalid_doctor_id(self):
        """Test that doctor_id must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            AvailableSlotsValidation(
                doctor_id=0,
                date=date.today() + timedelta(days=1)
            )
        assert "greater than 0" in str(exc_info.value)
    
    def test_slots_request_past_date(self):
        """Test that date cannot be in the past."""
        with pytest.raises(ValidationError) as exc_info:
            AvailableSlotsValidation(
                doctor_id=456,
                date=date.today() - timedelta(days=1)
            )
        assert "past" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.service
class TestHandleOdooErrorsDecorator:
    """Test handle_odoo_errors decorator."""
    
    def test_decorator_success(self):
        """Test decorator with successful function."""
        @handle_odoo_errors("test_operation")
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_decorator_handles_exception(self):
        """Test decorator handles exceptions by raising HTTPException."""
        from fastapi import HTTPException
        
        @handle_odoo_errors("test_operation")
        def failing_func():
            raise Exception("Test error")
        
        with pytest.raises(HTTPException) as exc_info:
            failing_func()
        assert exc_info.value.status_code == 500
        assert "unexpected error" in exc_info.value.detail.lower()
    
    def test_decorator_preserves_odoo_errors(self):
        """Test decorator converts OdooServiceError to HTTPException."""
        from fastapi import HTTPException
        
        @handle_odoo_errors("test_operation")
        def odoo_error_func():
            raise OdooConnectionError("Connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            odoo_error_func()
        assert exc_info.value.status_code == 503
        assert "unavailable" in exc_info.value.detail.lower()


@pytest.mark.unit
@pytest.mark.service
class TestRetryOnFailureDecorator:
    """Test retry_on_failure decorator."""
    
    def test_retry_success_first_try(self):
        """Test retry decorator with successful first attempt."""
        mock_func = Mock(return_value="success")
        decorated = retry_on_failure(max_retries=3, delay=0.1)(mock_func)
        
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test retry decorator succeeds after failures."""
        mock_func = Mock(side_effect=[OdooConnectionError("Fail"), OdooConnectionError("Fail"), "success"])
        decorated = retry_on_failure(max_retries=3, delay=0.01, exceptions=(OdooConnectionError,))(mock_func)
        
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausted(self):
        """Test retry decorator exhausts retries."""
        mock_func = Mock(side_effect=OdooConnectionError("Always fails"))
        decorated = retry_on_failure(max_retries=2, delay=0.01, exceptions=(OdooConnectionError,))(mock_func)
        
        with pytest.raises(OdooConnectionError) as exc_info:
            decorated()
        assert "Always fails" in str(exc_info.value)
        assert mock_func.call_count == 3  # max_retries + 1 (initial attempt)


@pytest.mark.unit
@pytest.mark.service
class TestValidationFunctions:
    """Test validation functions."""
    
    def test_validate_patient_id_valid(self):
        """Test validate_patient_id with valid ID."""
        result = validate_patient_id(123)
        assert result == 123
    
    def test_validate_patient_id_invalid(self):
        """Test validate_patient_id with invalid ID."""
        with pytest.raises(OdooValidationError) as exc_info:
            validate_patient_id(0)
        assert "patient" in str(exc_info.value).lower() and "id" in str(exc_info.value).lower()
        
        with pytest.raises(OdooValidationError):
            validate_patient_id(-1)
    
    def test_validate_doctor_id_valid(self):
        """Test validate_doctor_id with valid ID."""
        result = validate_doctor_id(456)
        assert result == 456
    
    def test_validate_doctor_id_invalid(self):
        """Test validate_doctor_id with invalid ID."""
        with pytest.raises(OdooValidationError) as exc_info:
            validate_doctor_id(0)
        assert "doctor" in str(exc_info.value).lower() and "id" in str(exc_info.value).lower()
    
    def test_validate_date_range_valid(self):
        """Test validate_date_range with valid range."""
        date_from, date_to = validate_date_range("2025-01-01", "2025-12-31")
        assert date_from == "2025-01-01"
        assert date_to == "2025-12-31"
    
    def test_validate_date_range_none(self):
        """Test validate_date_range with None values."""
        date_from, date_to = validate_date_range(None, None)
        assert date_from is None
        assert date_to is None
    
    def test_validate_date_range_invalid_format(self):
        """Test validate_date_range with invalid format."""
        with pytest.raises(OdooValidationError) as exc_info:
            validate_date_range("invalid-date", "2025-12-31")
        assert "date" in str(exc_info.value).lower()
    
    def test_validate_date_range_from_after_to(self):
        """Test validate_date_range with from_date after to_date."""
        with pytest.raises(OdooValidationError) as exc_info:
            validate_date_range("2025-12-31", "2025-01-01")
        assert "after" in str(exc_info.value).lower() or "before" in str(exc_info.value).lower()
    
    def test_validate_pagination_valid(self):
        """Test validate_pagination with valid values."""
        limit, offset = validate_pagination(10, 0)
        assert limit == 10
        assert offset == 0
    
    def test_validate_pagination_invalid_limit(self):
        """Test validate_pagination with invalid limit."""
        with pytest.raises(OdooValidationError) as exc_info:
            validate_pagination(0, 0)
        assert "limit" in str(exc_info.value).lower()
        
        with pytest.raises(OdooValidationError):
            validate_pagination(1001, 0)
    
    def test_validate_pagination_invalid_offset(self):
        """Test validate_pagination with invalid offset."""
        with pytest.raises(OdooValidationError) as exc_info:
            validate_pagination(10, -1)
        assert "offset" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.service
class TestSanitizationFunctions:
    """Test data sanitization functions."""
    
    def test_sanitize_patient_data_valid(self):
        """Test sanitize_patient_data with valid data."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "date_of_birth": "1990-01-01"
        }
        result = sanitize_patient_data(data)
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
    
    def test_sanitize_patient_data_strips_whitespace(self):
        """Test sanitize_patient_data strips whitespace."""
        data = {
            "name": "  John Doe  ",
            "email": "  john@example.com  "
        }
        result = sanitize_patient_data(data)
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
    
    def test_sanitize_patient_data_removes_empty_strings(self):
        """Test sanitize_patient_data handles empty strings."""
        data = {
            "name": "John Doe",
            "email": "",
            "phone": "   "
        }
        result = sanitize_patient_data(data)
        assert "name" in result
        # Empty strings are not added to result for email (checked with 'if data[field]')
        assert "email" not in result
        # Phone with only spaces gets processed and becomes empty string
        assert "phone" in result
        assert result["phone"] == ""
    
    def test_sanitize_appointment_data_valid(self):
        """Test sanitize_appointment_data with valid data."""
        data = {
            "patient_id": 123,
            "doctor_id": 456,
            "appointment_date": "2025-12-01T10:00:00",
            "notes": "Regular checkup"
        }
        result = sanitize_appointment_data(data)
        assert result["patient_id"] == 123
        assert result["doctor_id"] == 456
    
    def test_sanitize_appointment_data_strips_whitespace(self):
        """Test sanitize_appointment_data strips whitespace."""
        data = {
            "patient_id": 123,
            "doctor_id": 456,
            "appointment_date": "2025-12-01T10:00:00",
            "notes": "  Regular checkup  "
        }
        result = sanitize_appointment_data(data)
        assert result["notes"] == "Regular checkup"
    
    def test_sanitize_appointment_data_removes_empty_strings(self):
        """Test sanitize_appointment_data removes empty strings."""
        data = {
            "patient_id": 123,
            "doctor_id": 456,
            "appointment_date": "2025-12-01T10:00:00",
            "notes": ""
        }
        result = sanitize_appointment_data(data)
        assert "notes" not in result or result["notes"] is None

