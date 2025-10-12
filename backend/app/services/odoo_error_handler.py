"""
Odoo Error Handling and Validation

Provides comprehensive error handling, validation, and retry logic for Odoo operations.
"""

import logging
from typing import Any, Callable, Optional, TypeVar, Dict
from functools import wraps
from datetime import datetime, date
import time

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

logger = logging.getLogger(__name__)

T = TypeVar('T')


# Custom Exceptions
class OdooServiceError(Exception):
    """Base exception for Odoo service errors."""
    pass


class OdooConnectionError(OdooServiceError):
    """Raised when connection to Odoo fails."""
    pass


class OdooValidationError(OdooServiceError):
    """Raised when data validation fails."""
    pass


class OdooAuthenticationError(OdooServiceError):
    """Raised when authentication fails."""
    pass


class OdooNotFoundError(OdooServiceError):
    """Raised when resource is not found."""
    pass


class OdooPermissionError(OdooServiceError):
    """Raised when user lacks permission."""
    pass


# Validation Models
class PatientProfileValidation(BaseModel):
    """Validation model for patient profile data."""
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    date_of_birth: Optional[date] = None
    
    @validator('date_of_birth')
    def validate_dob(cls, v):
        if v and v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        if v and v.year < 1900:
            raise ValueError('Date of birth must be after 1900')
        return v


class AppointmentValidation(BaseModel):
    """Validation model for appointment data."""
    patient_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    appointment_date: datetime
    duration_minutes: int = Field(default=30, ge=15, le=240)
    appointment_type: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        if v < datetime.now():
            raise ValueError('Appointment date cannot be in the past')
        return v


class AvailableSlotsValidation(BaseModel):
    """Validation model for available slots request."""
    doctor_id: int = Field(..., gt=0)
    date: date
    duration_minutes: int = Field(default=30, ge=15, le=240)
    
    @validator('date')
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError('Date cannot be in the past')
        return v


# Error Handler Decorator
def handle_odoo_errors(
    operation_name: str,
    fallback_value: Any = None,
    raise_http_exception: bool = True
):
    """
    Decorator for handling Odoo operation errors.
    
    Args:
        operation_name: Name of the operation for logging
        fallback_value: Value to return on error (if not raising exception)
        raise_http_exception: Whether to raise HTTPException or return fallback
    
    Usage:
        @handle_odoo_errors('get_patient_profile')
        def get_patient(patient_id: int):
            return odoo_client.get_patient(patient_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except OdooConnectionError as e:
                logger.error(f"{operation_name} - Connection error: {e}")
                if raise_http_exception:
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable. Please try again later."
                    )
                return fallback_value
            
            except OdooAuthenticationError as e:
                logger.error(f"{operation_name} - Authentication error: {e}")
                if raise_http_exception:
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication failed. Please log in again."
                    )
                return fallback_value
            
            except OdooPermissionError as e:
                logger.error(f"{operation_name} - Permission error: {e}")
                if raise_http_exception:
                    raise HTTPException(
                        status_code=403,
                        detail="You don't have permission to access this resource."
                    )
                return fallback_value
            
            except OdooNotFoundError as e:
                logger.error(f"{operation_name} - Not found: {e}")
                if raise_http_exception:
                    raise HTTPException(
                        status_code=404,
                        detail="Resource not found."
                    )
                return fallback_value
            
            except OdooValidationError as e:
                logger.error(f"{operation_name} - Validation error: {e}")
                if raise_http_exception:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid data: {str(e)}"
                    )
                return fallback_value
            
            except Exception as e:
                logger.error(f"{operation_name} - Unexpected error: {e}", exc_info=True)
                if raise_http_exception:
                    raise HTTPException(
                        status_code=500,
                        detail="An unexpected error occurred. Please try again."
                    )
                return fallback_value
        
        return wrapper
    return decorator


# Retry Logic
def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (OdooConnectionError,)
):
    """
    Decorator for retrying failed operations.
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to retry on
    
    Usage:
        @retry_on_failure(max_retries=3, delay=1.0)
        def fetch_from_odoo():
            return odoo_client.get_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries} retries failed")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


# Validation Functions
def validate_patient_id(patient_id: int) -> int:
    """
    Validate patient ID.
    
    Args:
        patient_id: Patient ID to validate
    
    Returns:
        Validated patient ID
    
    Raises:
        OdooValidationError: If validation fails
    """
    if not isinstance(patient_id, int) or patient_id <= 0:
        raise OdooValidationError(f"Invalid patient ID: {patient_id}")
    return patient_id


def validate_doctor_id(doctor_id: int) -> int:
    """
    Validate doctor ID.
    
    Args:
        doctor_id: Doctor ID to validate
    
    Returns:
        Validated doctor ID
    
    Raises:
        OdooValidationError: If validation fails
    """
    if not isinstance(doctor_id, int) or doctor_id <= 0:
        raise OdooValidationError(f"Invalid doctor ID: {doctor_id}")
    return doctor_id


def validate_date_range(date_from: Optional[str], date_to: Optional[str]) -> tuple:
    """
    Validate date range.
    
    Args:
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
    
    Returns:
        Tuple of (date_from, date_to)
    
    Raises:
        OdooValidationError: If validation fails
    """
    if date_from:
        try:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        except ValueError:
            raise OdooValidationError(f"Invalid date format for date_from: {date_from}")
    else:
        from_date = None
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            raise OdooValidationError(f"Invalid date format for date_to: {date_to}")
    else:
        to_date = None
    
    if from_date and to_date and from_date > to_date:
        raise OdooValidationError("date_from cannot be after date_to")
    
    return (date_from, date_to)


def validate_pagination(limit: int, offset: int) -> tuple:
    """
    Validate pagination parameters.
    
    Args:
        limit: Maximum results
        offset: Offset for pagination
    
    Returns:
        Tuple of (limit, offset)
    
    Raises:
        OdooValidationError: If validation fails
    """
    if limit <= 0 or limit > 1000:
        raise OdooValidationError(f"Invalid limit: {limit}. Must be between 1 and 1000")
    
    if offset < 0:
        raise OdooValidationError(f"Invalid offset: {offset}. Must be >= 0")
    
    return (limit, offset)


# Data Sanitization
def sanitize_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize patient data before sending to Odoo.
    
    Args:
        data: Patient data dictionary
    
    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    
    # Required fields
    if 'name' in data and data['name']:
        sanitized['name'] = str(data['name']).strip()[:100]
    
    # Optional fields
    if 'email' in data and data['email']:
        sanitized['email'] = str(data['email']).strip().lower()
    
    if 'phone' in data and data['phone']:
        # Remove non-numeric characters except + and spaces
        phone = ''.join(c for c in str(data['phone']) if c.isdigit() or c in ['+', ' ', '-', '(', ')'])
        sanitized['phone'] = phone.strip()
    
    if 'street' in data and data['street']:
        sanitized['street'] = str(data['street']).strip()[:200]
    
    if 'city' in data and data['city']:
        sanitized['city'] = str(data['city']).strip()[:100]
    
    if 'zip' in data and data['zip']:
        sanitized['zip'] = str(data['zip']).strip()[:20]
    
    if 'notes' in data and data['notes']:
        sanitized['comment'] = str(data['notes']).strip()[:500]
    
    return sanitized


def sanitize_appointment_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize appointment data before sending to Odoo.
    
    Args:
        data: Appointment data dictionary
    
    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    
    # Required fields
    if 'patient_id' in data:
        sanitized['patient_id'] = validate_patient_id(data['patient_id'])
    
    if 'doctor_id' in data:
        sanitized['doctor_id'] = validate_doctor_id(data['doctor_id'])
    
    if 'appointment_date' in data:
        if isinstance(data['appointment_date'], str):
            sanitized['appointment_sdate'] = data['appointment_date']
        elif isinstance(data['appointment_date'], datetime):
            sanitized['appointment_sdate'] = data['appointment_date'].isoformat()
    
    # Optional fields
    if 'appointment_type' in data and data['appointment_type']:
        sanitized['appointment_type'] = str(data['appointment_type']).strip()[:100]
    
    if 'notes' in data and data['notes']:
        sanitized['notes'] = str(data['notes']).strip()[:500]
    
    return sanitized

