"""
Secure Error Handler Middleware

Prevents information leakage by sanitizing error messages before sending to clients.
Logs detailed errors server-side for debugging while showing generic messages to users.

FIXED: Bug #35 - Information Leakage in Error Messages
Date: 2025-01-25
"""

import logging
import uuid
from typing import Dict, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

logger = logging.getLogger(__name__)


class SecureErrorHandler(BaseHTTPMiddleware):
    """
    Middleware to handle errors securely without exposing internal details.
    
    Features:
    - Generates unique error IDs for tracking
    - Logs detailed errors server-side
    - Returns generic user-friendly messages
    - Environment-specific error detail levels
    - HIPAA-compliant error handling
    """
    
    def __init__(self, app, debug: bool = None):
        super().__init__(app)
        # Use environment variable or parameter
        self.debug = debug if debug is not None else os.getenv("DEBUG", "false").lower() == "true"
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and handle any errors securely.
        """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return self.handle_error(e, request)
    
    def handle_error(self, error: Exception, request: Request) -> JSONResponse:
        """
        Handle error securely with proper logging and sanitized response.
        
        Args:
            error: The exception that occurred
            request: The FastAPI request object
            
        Returns:
            JSONResponse with sanitized error message
        """
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())
        
        # Log detailed error server-side (with full stack trace)
        logger.error(
            f"Error ID {error_id}: {type(error).__name__}: {str(error)}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method,
                "client_host": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Determine appropriate status code and message
        status_code, error_code, user_message = self._categorize_error(error)
        
        # Build response
        response_data = {
            "error": error_code,
            "message": user_message,
            "error_id": error_id
        }
        
        # In debug mode, include more details (development only!)
        if self.debug:
            response_data["debug"] = {
                "exception_type": type(error).__name__,
                "exception_message": str(error),
                "path": request.url.path
            }
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    def _categorize_error(self, error: Exception) -> tuple[int, str, str]:
        """
        Categorize error and return appropriate status code, error code, and message.
        
        Args:
            error: The exception to categorize
            
        Returns:
            Tuple of (status_code, error_code, user_message)
        """
        error_type = type(error).__name__
        
        # Database errors
        if "psycopg2" in error_type or "sqlalchemy" in error_type.lower():
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "DATABASE_ERROR",
                "A database error occurred. Please try again later."
            )
        
        # File operation errors
        if error_type in ["FileNotFoundError", "PermissionError", "IOError"]:
            return (
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "FILE_OPERATION_ERROR",
                "A file operation error occurred. Please try again later."
            )
        
        # Validation errors
        if error_type in ["ValidationError", "ValueError"]:
            return (
                status.HTTP_400_BAD_REQUEST,
                "VALIDATION_ERROR",
                "Invalid input data. Please check your request and try again."
            )
        
        # Authentication/Authorization errors
        if error_type in ["AuthenticationError", "PermissionError", "Unauthorized"]:
            return (
                status.HTTP_401_UNAUTHORIZED,
                "AUTHENTICATION_ERROR",
                "Authentication failed. Please log in and try again."
            )
        
        # Not found errors
        if error_type in ["NotFoundError", "DoesNotExist"]:
            return (
                status.HTTP_404_NOT_FOUND,
                "NOT_FOUND",
                "The requested resource was not found."
            )
        
        # Default: Internal server error
        return (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred. Please try again later."
        )


def sanitize_error_message(error: Exception, debug: bool = False) -> Dict[str, Any]:
    """
    Sanitize error message for safe exposure to API consumers.
    
    This function can be used directly in exception handlers to sanitize
    error messages before including them in HTTPException detail.
    
    Args:
        error: The exception to sanitize
        debug: Whether to include debug information (development only!)
        
    Returns:
        Dictionary with sanitized error information
        
    Example:
        try:
            risky_operation()
        except Exception as e:
            error_data = sanitize_error_message(e)
            raise HTTPException(status_code=500, detail=error_data)
    """
    # Generate unique error ID
    error_id = str(uuid.uuid4())
    
    # Log detailed error server-side
    logger.error(
        f"Error ID {error_id}: {type(error).__name__}: {str(error)}",
        exc_info=True,
        extra={"error_id": error_id}
    )
    
    # Determine error category
    error_type = type(error).__name__
    
    # Build sanitized response
    response = {
        "error": "INTERNAL_ERROR",
        "message": "An unexpected error occurred. Please try again later.",
        "error_id": error_id
    }
    
    # Categorize error
    if "psycopg2" in error_type or "sqlalchemy" in error_type.lower():
        response["error"] = "DATABASE_ERROR"
        response["message"] = "A database error occurred. Please try again later."
    elif error_type in ["FileNotFoundError", "PermissionError", "IOError"]:
        response["error"] = "FILE_OPERATION_ERROR"
        response["message"] = "A file operation error occurred. Please try again later."
    elif error_type in ["ValidationError", "ValueError"]:
        response["error"] = "VALIDATION_ERROR"
        response["message"] = "Invalid input data. Please check your request and try again."
    
    # In debug mode, include more details (development only!)
    if debug:
        response["debug"] = {
            "exception_type": error_type,
            "exception_message": str(error)
        }
    
    return response


def get_generic_error_message(status_code: int) -> str:
    """
    Get a generic, user-friendly error message for a given status code.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        User-friendly error message
    """
    messages = {
        400: "Invalid request. Please check your input and try again.",
        401: "Authentication required. Please log in and try again.",
        403: "Access denied. You don't have permission to perform this action.",
        404: "The requested resource was not found.",
        409: "Conflict. The resource already exists or is in use.",
        422: "Invalid input data. Please check your request and try again.",
        429: "Too many requests. Please slow down and try again later.",
        500: "An unexpected error occurred. Please try again later.",
        502: "Service temporarily unavailable. Please try again later.",
        503: "Service temporarily unavailable. Please try again later.",
        504: "Request timeout. Please try again later."
    }
    
    return messages.get(status_code, "An error occurred. Please try again later.")


# Error codes for consistent error handling across the application
class ErrorCodes:
    """Standard error codes for the application."""
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_CONSTRAINT_VIOLATION = "DATABASE_CONSTRAINT_VIOLATION"
    
    # File operation errors
    FILE_OPERATION_ERROR = "FILE_OPERATION_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_PERMISSION_ERROR = "FILE_PERMISSION_ERROR"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Authentication/Authorization errors
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # External service errors
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    API_ERROR = "API_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"


# HIPAA-compliant error messages (no PHI exposure)
class HIPAAErrorMessages:
    """HIPAA-compliant error messages that don't expose PHI."""
    
    PATIENT_NOT_FOUND = "Patient record not found."
    PATIENT_ACCESS_DENIED = "Access to patient record denied."
    APPOINTMENT_NOT_FOUND = "Appointment not found."
    APPOINTMENT_CONFLICT = "Appointment scheduling conflict."
    MEDICAL_RECORD_ERROR = "Error accessing medical record."
    INSURANCE_VERIFICATION_ERROR = "Insurance verification failed."
    PRESCRIPTION_ERROR = "Error processing prescription."
    BILLING_ERROR = "Billing error occurred."
    
    @staticmethod
    def get_generic_message() -> str:
        """Get a generic HIPAA-compliant error message."""
        return "An error occurred while processing your healthcare request. Please contact support for assistance."

