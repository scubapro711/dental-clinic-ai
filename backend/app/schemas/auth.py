"""
Authentication schemas for request/response validation.
"""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request."""

    # Account Information
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    # Personal Information
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[str] = Field(None, description="Date of birth in YYYY-MM-DD format")
    gender: Optional[str] = Field(None, description="Gender: male, female, or other")
    blood_type: Optional[str] = Field(None, description="Blood type: A+, A-, B+, B-, AB+, AB-, O+, O-")
    
    # Address
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Medical Information (Optional)
    has_allergies: Optional[bool] = Field(None, description="Does the patient have any allergies?")
    allergy_notes: Optional[str] = Field(None, max_length=500)
    has_medications: Optional[bool] = Field(None, description="Is the patient currently taking any medications?")
    medication_notes: Optional[str] = Field(None, max_length=500)
    
    # System
    invitation_token: Optional[str] = Field(None, max_length=100, description="Invitation token if joining via team invitation")


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
