"""
Authentication schemas for request/response validation.
"""

import re
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    invitation_token: Optional[str] = Field(None, max_length=100, description="Invitation token if joining via team invitation")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength for HIPAA compliance.
        
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        
        This ensures strong passwords to protect sensitive healthcare data.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'/`~]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\;\'`~)')
        
        return v


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    user_id: UUID
    email: str
    role: str
    organization_id: Optional[UUID] = None


class UserResponse(BaseModel):
    """User response model."""

    id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    organization_id: Optional[UUID]

    class Config:
        from_attributes = True
