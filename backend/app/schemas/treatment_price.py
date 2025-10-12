"""
Pydantic schemas for Treatment Price API.
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class TreatmentPriceCreate(BaseModel):
    """Schema for creating a treatment price."""
    organization_id: UUID
    treatment_code: str = Field(..., min_length=1, max_length=50)
    treatment_name_hebrew: str = Field(..., min_length=1, max_length=255)
    treatment_name_english: Optional[str] = Field(None, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    
    base_price: Decimal = Field(..., ge=0, le=100000)
    member_price: Optional[Decimal] = Field(None, ge=0)
    insurance_price: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field('ILS', min_length=3, max_length=3)
    
    duration_minutes: int = Field(30, ge=5, le=480)
    requires_specialist: bool = False
    specialist_type: Optional[str] = None
    
    odoo_product_id: Optional[int] = None
    odoo_product_template_id: Optional[int] = None
    
    is_active: bool = True
    is_visible_online: bool = True
    requires_approval: bool = False
    
    notes: Optional[str] = None
    display_order: Optional[int] = None
    
    @validator('currency')
    def validate_currency_uppercase(cls, v):
        """Ensure currency is uppercase."""
        return v.upper()
    
    @validator('category')
    def validate_category(cls, v):
        """Validate treatment category."""
        valid_categories = [
            'preventive', 'restorative', 'endodontic', 'periodontic',
            'prosthodontic', 'orthodontic', 'cosmetic', 'surgical',
            'pediatric', 'emergency', 'diagnostic', 'other'
        ]
        if v not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return v
    
    @validator('specialist_type')
    def validate_specialist_type(cls, v, values):
        """Validate specialist type if specialist is required."""
        if values.get('requires_specialist') and not v:
            raise ValueError("specialist_type is required when requires_specialist is True")
        
        if v:
            valid_specialists = [
                'general_dentist', 'orthodontist', 'endodontist',
                'periodontist', 'prosthodontist', 'oral_surgeon',
                'pediatric_dentist', 'cosmetic_dentist'
            ]
            if v not in valid_specialists:
                raise ValueError(f"Invalid specialist type. Must be one of: {', '.join(valid_specialists)}")
        
        return v
    
    @validator('member_price')
    def validate_member_price(cls, v, values):
        """Validate member price is less than base price."""
        if v and 'base_price' in values and v > values['base_price']:
            raise ValueError("member_price cannot exceed base_price")
        return v
    
    @validator('insurance_price')
    def validate_insurance_price(cls, v, values):
        """Validate insurance price is less than base price."""
        if v and 'base_price' in values and v > values['base_price']:
            raise ValueError("insurance_price cannot exceed base_price")
        return v


class TreatmentPriceUpdate(BaseModel):
    """Schema for updating a treatment price (all fields optional)."""
    treatment_code: Optional[str] = Field(None, min_length=1, max_length=50)
    treatment_name_hebrew: Optional[str] = Field(None, min_length=1, max_length=255)
    treatment_name_english: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    
    base_price: Optional[Decimal] = Field(None, ge=0, le=100000)
    member_price: Optional[Decimal] = Field(None, ge=0)
    insurance_price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    requires_specialist: Optional[bool] = None
    specialist_type: Optional[str] = None
    
    odoo_product_id: Optional[int] = None
    odoo_product_template_id: Optional[int] = None
    
    is_active: Optional[bool] = None
    is_visible_online: Optional[bool] = None
    requires_approval: Optional[bool] = None
    
    notes: Optional[str] = None
    display_order: Optional[int] = None
    
    @validator('currency')
    def validate_currency_uppercase(cls, v):
        """Ensure currency is uppercase."""
        if v:
            return v.upper()
        return v
    
    @validator('category')
    def validate_category(cls, v):
        """Validate treatment category."""
        if v:
            valid_categories = [
                'preventive', 'restorative', 'endodontic', 'periodontic',
                'prosthodontic', 'orthodontic', 'cosmetic', 'surgical',
                'pediatric', 'emergency', 'diagnostic', 'other'
            ]
            if v not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        return v


class TreatmentPriceResponse(BaseModel):
    """Schema for treatment price response."""
    id: UUID
    organization_id: UUID
    treatment_code: str
    name: dict
    category: str
    description: Optional[str]
    pricing: dict
    duration_minutes: int
    specialist: dict
    odoo: dict
    status: dict
    notes: Optional[str]
    display_order: Optional[int]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class TreatmentPriceBulkCreate(BaseModel):
    """Schema for bulk creating treatment prices."""
    organization_id: UUID
    treatments: list[TreatmentPriceCreate]
    
    @validator('treatments')
    def validate_treatments_not_empty(cls, v):
        """Ensure treatments list is not empty."""
        if not v:
            raise ValueError("treatments list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot create more than 100 treatments at once")
        return v
