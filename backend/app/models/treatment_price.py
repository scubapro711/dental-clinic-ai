"""
Treatment Price model for organization-specific pricing.

Based on Israeli dental treatment catalog and pricing research.
"""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, Numeric,
    String, Text, ForeignKey, UniqueConstraint
)
from app.core.database_types import UUID
from sqlalchemy.orm import relationship, validates

from app.core.database import Base


class TreatmentPrice(Base):
    """
    Treatment pricing for dental clinic.
    
    Each organization can define custom prices for dental treatments.
    Supports:
    - Multiple price tiers (base, member, insurance)
    - Odoo product integration
    - Hebrew and English names
    - Treatment categories
    - Duration and specialist requirements
    """
    __tablename__ = "treatment_prices"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign key
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ========== Treatment Identification ==========
    
    treatment_code = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Unique treatment code (e.g., 'CLEAN-001', 'FILL-002')"
    )
    
    treatment_name_hebrew = Column(
        String(255),
        nullable=False,
        comment="Treatment name in Hebrew"
    )
    
    treatment_name_english = Column(
        String(255),
        nullable=True,
        comment="Treatment name in English"
    )
    
    category = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Treatment category (e.g., 'preventive', 'restorative', 'cosmetic')"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed treatment description"
    )
    
    # ========== Pricing ==========
    
    base_price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Base price for treatment (ILS)"
    )
    
    member_price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Discounted price for members (ILS)"
    )
    
    insurance_price = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Price covered by insurance (ILS)"
    )
    
    currency = Column(
        String(3),
        nullable=False,
        default='ILS',
        comment="Currency code (ISO 4217)"
    )
    
    # ========== Duration and Scheduling ==========
    
    duration_minutes = Column(
        Integer,
        nullable=False,
        default=30,
        comment="Estimated treatment duration in minutes"
    )
    
    requires_specialist = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether treatment requires a specialist"
    )
    
    specialist_type = Column(
        String(100),
        nullable=True,
        comment="Type of specialist required (e.g., 'orthodontist', 'endodontist')"
    )
    
    # ========== Odoo Integration ==========
    
    odoo_product_id = Column(
        Integer,
        nullable=True,
        index=True,
        comment="Odoo product.product ID"
    )
    
    odoo_product_template_id = Column(
        Integer,
        nullable=True,
        comment="Odoo product.template ID"
    )
    
    # ========== Status and Visibility ==========
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether treatment is currently offered"
    )
    
    is_visible_online = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether treatment is visible in online booking"
    )
    
    requires_approval = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether treatment requires manager approval"
    )
    
    # ========== Metadata ==========
    
    notes = Column(
        Text,
        nullable=True,
        comment="Internal notes about treatment"
    )
    
    display_order = Column(
        Integer,
        nullable=True,
        comment="Order for displaying in lists"
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
    
    organization = relationship("Organization", back_populates="treatment_prices")
    
    # ========== Constraints ==========
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'treatment_code', name='uq_org_treatment_code'),
    )
    
    # ========== Validators ==========
    
    @validates('base_price')
    def validate_base_price(self, key: str, value: Decimal) -> Decimal:
        """Validate base price is positive."""
        if value < 0:
            raise ValueError("Base price cannot be negative")
        if value > 100000:
            raise ValueError("Base price seems unreasonably high (max 100,000 ILS)")
        return value
    
    @validates('member_price')
    def validate_member_price(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Validate member price is less than base price."""
        if value is not None:
            if value < 0:
                raise ValueError("Member price cannot be negative")
            if self.base_price and value > self.base_price:
                raise ValueError("Member price cannot exceed base price")
        return value
    
    @validates('insurance_price')
    def validate_insurance_price(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Validate insurance price."""
        if value is not None:
            if value < 0:
                raise ValueError("Insurance price cannot be negative")
            if self.base_price and value > self.base_price:
                raise ValueError("Insurance price cannot exceed base price")
        return value
    
    @validates('duration_minutes')
    def validate_duration(self, key: str, value: int) -> int:
        """Validate treatment duration."""
        if value < 5:
            raise ValueError("Duration must be at least 5 minutes")
        if value > 480:  # 8 hours
            raise ValueError("Duration cannot exceed 480 minutes (8 hours)")
        return value
    
    @validates('currency')
    def validate_currency(self, key: str, value: str) -> str:
        """Validate currency code."""
        if len(value) != 3:
            raise ValueError("Currency code must be 3 characters (ISO 4217)")
        return value.upper()
    
    @validates('category')
    def validate_category(self, key: str, value: str) -> str:
        """Validate treatment category."""
        valid_categories = [
            'preventive',      # ניקוי, פלואור
            'restorative',     # סתימות, כתרים
            'endodontic',      # טיפולי שורש
            'periodontic',     # טיפולי חניכיים
            'prosthodontic',   # גשרים, תותבות
            'orthodontic',     # יישור שיניים
            'cosmetic',        # הלבנה, ציפויים
            'surgical',        # עקירות, השתלות
            'pediatric',       # טיפולי ילדים
            'emergency',       # טיפולי חירום
            'diagnostic',      # צילומים, בדיקות
            'other'
        ]
        
        if value not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        return value
    
    @validates('specialist_type')
    def validate_specialist_type(self, key: str, value: Optional[str]) -> Optional[str]:
        """Validate specialist type."""
        if value:
            valid_specialists = [
                'general_dentist',
                'orthodontist',
                'endodontist',
                'periodontist',
                'prosthodontist',
                'oral_surgeon',
                'pediatric_dentist',
                'cosmetic_dentist'
            ]
            
            if value not in valid_specialists:
                raise ValueError(f"Invalid specialist type. Must be one of: {', '.join(valid_specialists)}")
        
        return value
    
    # ========== Helper Methods ==========
    
    def get_price_for_tier(self, tier: str = 'base') -> Decimal:
        """Get price for specific tier."""
        if tier == 'member' and self.member_price:
            return self.member_price
        elif tier == 'insurance' and self.insurance_price:
            return self.insurance_price
        return self.base_price
    
    def calculate_patient_cost(self, tier: str = 'base', insurance_coverage: Optional[Decimal] = None) -> Decimal:
        """Calculate final cost to patient after insurance."""
        price = self.get_price_for_tier(tier)
        
        if insurance_coverage:
            patient_cost = price - insurance_coverage
            return max(Decimal('0.00'), patient_cost)  # Never negative
        
        return price
    
    def is_available_for_booking(self) -> bool:
        """Check if treatment is available for online booking."""
        return self.is_active and self.is_visible_online and not self.requires_approval
    
    def to_dict(self) -> Dict:
        """Convert treatment to dictionary for API responses."""
        return {
            'id': str(self.id),
            'organization_id': str(self.organization_id),
            'treatment_code': self.treatment_code,
            'name': {
                'hebrew': self.treatment_name_hebrew,
                'english': self.treatment_name_english
            },
            'category': self.category,
            'description': self.description,
            'pricing': {
                'base': float(self.base_price),
                'member': float(self.member_price) if self.member_price else None,
                'insurance': float(self.insurance_price) if self.insurance_price else None,
                'currency': self.currency
            },
            'duration_minutes': self.duration_minutes,
            'specialist': {
                'required': self.requires_specialist,
                'type': self.specialist_type
            },
            'odoo': {
                'product_id': self.odoo_product_id,
                'template_id': self.odoo_product_template_id
            },
            'status': {
                'active': self.is_active,
                'visible_online': self.is_visible_online,
                'requires_approval': self.requires_approval
            },
            'notes': self.notes,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<TreatmentPrice(code={self.treatment_code}, price={self.base_price})>"


# Default Israeli dental treatments catalog
# Based on common treatments in Israeli dental clinics
DEFAULT_ISRAELI_TREATMENTS = [
    {
        'treatment_code': 'EXAM-001',
        'treatment_name_hebrew': 'בדיקה כללית',
        'treatment_name_english': 'General Examination',
        'category': 'diagnostic',
        'base_price': Decimal('150.00'),
        'duration_minutes': 20,
        'description': 'בדיקת שיניים כללית וייעוץ'
    },
    {
        'treatment_code': 'CLEAN-001',
        'treatment_name_hebrew': 'ניקוי אבנית',
        'treatment_name_english': 'Teeth Cleaning (Scaling)',
        'category': 'preventive',
        'base_price': Decimal('300.00'),
        'member_price': Decimal('250.00'),
        'duration_minutes': 45,
        'description': 'הסרת אבנית וליטוש שיניים'
    },
    {
        'treatment_code': 'FILL-001',
        'treatment_name_hebrew': 'סתימה קומפוזיט',
        'treatment_name_english': 'Composite Filling',
        'category': 'restorative',
        'base_price': Decimal('400.00'),
        'member_price': Decimal('350.00'),
        'duration_minutes': 30,
        'description': 'סתימה לבנה בחומר קומפוזיט'
    },
    {
        'treatment_code': 'ROOT-001',
        'treatment_name_hebrew': 'טיפול שורש',
        'treatment_name_english': 'Root Canal Treatment',
        'category': 'endodontic',
        'base_price': Decimal('1500.00'),
        'member_price': Decimal('1300.00'),
        'duration_minutes': 90,
        'requires_specialist': True,
        'specialist_type': 'endodontist',
        'description': 'טיפול שורש מלא'
    },
    {
        'treatment_code': 'CROWN-001',
        'treatment_name_hebrew': 'כתר חרסינה',
        'treatment_name_english': 'Porcelain Crown',
        'category': 'prosthodontic',
        'base_price': Decimal('3000.00'),
        'member_price': Decimal('2700.00'),
        'duration_minutes': 60,
        'description': 'כתר חרסינה מלא'
    },
    {
        'treatment_code': 'EXTRACT-001',
        'treatment_name_hebrew': 'עקירת שן',
        'treatment_name_english': 'Tooth Extraction',
        'category': 'surgical',
        'base_price': Decimal('500.00'),
        'duration_minutes': 30,
        'description': 'עקירת שן פשוטה'
    },
    {
        'treatment_code': 'WHITENING-001',
        'treatment_name_hebrew': 'הלבנת שיניים',
        'treatment_name_english': 'Teeth Whitening',
        'category': 'cosmetic',
        'base_price': Decimal('1500.00'),
        'duration_minutes': 60,
        'description': 'הלבנת שיניים במרפאה'
    },
    {
        'treatment_code': 'IMPLANT-001',
        'treatment_name_hebrew': 'שתל דנטלי',
        'treatment_name_english': 'Dental Implant',
        'category': 'surgical',
        'base_price': Decimal('5000.00'),
        'duration_minutes': 120,
        'requires_specialist': True,
        'specialist_type': 'oral_surgeon',
        'requires_approval': True,
        'description': 'שתל דנטלי כולל כתר'
    },
    {
        'treatment_code': 'XRAY-001',
        'treatment_name_hebrew': 'צילום פנורמי',
        'treatment_name_english': 'Panoramic X-Ray',
        'category': 'diagnostic',
        'base_price': Decimal('200.00'),
        'duration_minutes': 10,
        'description': 'צילום רנטגן פנורמי'
    },
    {
        'treatment_code': 'ORTHO-001',
        'treatment_name_hebrew': 'יישור שיניים (חודשי)',
        'treatment_name_english': 'Orthodontic Treatment (Monthly)',
        'category': 'orthodontic',
        'base_price': Decimal('800.00'),
        'duration_minutes': 30,
        'requires_specialist': True,
        'specialist_type': 'orthodontist',
        'description': 'תשלום חודשי ליישור שיניים'
    }
]
