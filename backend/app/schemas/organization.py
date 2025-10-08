"""
Organization schemas for API requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OrganizationRegisterRequest(BaseModel):
    """Organization registration request."""
    # Clinic info
    clinic_name: str = Field(..., min_length=2, max_length=200)
    clinic_email: EmailStr
    clinic_phone: Optional[str] = Field(None, max_length=20)
    clinic_address: Optional[str] = Field(None, max_length=500)
    
    # Owner info
    owner_full_name: str = Field(..., min_length=2, max_length=200)
    owner_email: EmailStr
    owner_password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    owner_phone: Optional[str] = Field(None, max_length=20)


class OrganizationResponse(BaseModel):
    """Organization response."""
    id: str
    name: str
    slug: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    subscription_tier: str
    subscription_status: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Organization list response."""
    organizations: list[OrganizationResponse]
    total: int
