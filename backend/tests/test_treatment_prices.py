"""
Tests for Treatment Price functionality.
"""
import pytest
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.treatment_price import TreatmentPrice, DEFAULT_ISRAELI_TREATMENTS
from app.models.organization import Organization


def test_create_treatment_price(db: Session):
    """Test creating a treatment price."""
    org = Organization(name="Test Clinic", slug="test-clinic", email="test@example.com")
    db.add(org)
    db.commit()
    
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="TEST-001",
        treatment_name_hebrew="טיפול בדיקה",
        treatment_name_english="Test Treatment",
        category="diagnostic",
        base_price=Decimal('100.00'),
        duration_minutes=30
    )
    db.add(treatment)
    db.commit()
    
    assert treatment.id is not None
    assert treatment.treatment_code == "TEST-001"
    assert treatment.base_price == Decimal('100.00')


def test_unique_treatment_code_per_org(db: Session):
    """Test that treatment code must be unique per organization."""
    org = Organization(name="Unique Test", slug="unique-test", email="unique@example.com")
    db.add(org)
    db.commit()
    
    # First treatment
    treatment1 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="UNIQUE-001",
        treatment_name_hebrew="טיפול 1",
        category="preventive",
        base_price=Decimal('100.00')
    )
    db.add(treatment1)
    db.commit()
    
    # Try duplicate code
    treatment2 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="UNIQUE-001",  # Same code!
        treatment_name_hebrew="טיפול 2",
        category="preventive",
        base_price=Decimal('200.00')
    )
    db.add(treatment2)
    
    with pytest.raises(Exception):  # IntegrityError
        db.commit()


def test_different_orgs_can_have_same_code(db: Session):
    """Test that different organizations can use the same treatment code."""
    org1 = Organization(name="Clinic 1", slug="clinic-1", email="c1@example.com")
    org2 = Organization(name="Clinic 2", slug="clinic-2", email="c2@example.com")
    db.add_all([org1, org2])
    db.commit()
    
    treatment1 = TreatmentPrice(
        organization_id=org1.id,
        treatment_code="SHARED-001",
        treatment_name_hebrew="טיפול 1",
        category="preventive",
        base_price=Decimal('100.00')
    )
    
    treatment2 = TreatmentPrice(
        organization_id=org2.id,
        treatment_code="SHARED-001",  # Same code, different org
        treatment_name_hebrew="טיפול 2",
        category="preventive",
        base_price=Decimal('200.00')
    )
    
    db.add_all([treatment1, treatment2])
    db.commit()
    
    # Should succeed
    assert treatment1.id != treatment2.id


def test_validate_base_price(db: Session):
    """Test base price validation."""
    org = Organization(name="Price Test", slug="price-test", email="price@example.com")
    db.add(org)
    db.commit()
    
    # Negative price
    with pytest.raises(ValueError, match="cannot be negative"):
        treatment = TreatmentPrice(
            organization_id=org.id,
            treatment_code="NEG-001",
            treatment_name_hebrew="שלילי",
            category="preventive",
            base_price=Decimal('-100.00')
        )
        db.add(treatment)
        db.flush()
    
    db.rollback()
    
    # Too high
    with pytest.raises(ValueError, match="unreasonably high"):
        treatment = TreatmentPrice(
            organization_id=org.id,
            treatment_code="HIGH-001",
            treatment_name_hebrew="יקר מדי",
            category="preventive",
            base_price=Decimal('150000.00')
        )
        db.add(treatment)
        db.flush()


def test_validate_duration(db: Session):
    """Test duration validation."""
    org = Organization(name="Duration Test", slug="duration-test", email="duration@example.com")
    db.add(org)
    db.commit()
    
    # Too short
    with pytest.raises(ValueError, match="at least 5 minutes"):
        treatment = TreatmentPrice(
            organization_id=org.id,
            treatment_code="SHORT-001",
            treatment_name_hebrew="קצר מדי",
            category="preventive",
            base_price=Decimal('100.00'),
            duration_minutes=2
        )
        db.add(treatment)
        db.flush()
    
    db.rollback()
    
    # Too long
    with pytest.raises(ValueError, match="cannot exceed 480 minutes"):
        treatment = TreatmentPrice(
            organization_id=org.id,
            treatment_code="LONG-001",
            treatment_name_hebrew="ארוך מדי",
            category="preventive",
            base_price=Decimal('100.00'),
            duration_minutes=500
        )
        db.add(treatment)
        db.flush()


def test_validate_category(db: Session):
    """Test category validation."""
    org = Organization(name="Cat Test", slug="cat-test", email="cat@example.com")
    db.add(org)
    db.commit()
    
    # Invalid category
    with pytest.raises(ValueError, match="Invalid category"):
        treatment = TreatmentPrice(
            organization_id=org.id,
            treatment_code="INVALID-001",
            treatment_name_hebrew="קטגוריה לא תקינה",
            category="invalid_category",
            base_price=Decimal('100.00')
        )
        db.add(treatment)
        db.flush()


def test_get_price_for_tier(db: Session):
    """Test getting price for different tiers."""
    org = Organization(name="Tier Test", slug="tier-test", email="tier@example.com")
    db.add(org)
    db.commit()
    
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="TIER-001",
        treatment_name_hebrew="טיפול עם רמות",
        category="preventive",
        base_price=Decimal('300.00'),
        member_price=Decimal('250.00'),
        insurance_price=Decimal('200.00')
    )
    db.add(treatment)
    db.commit()
    
    # Base tier
    assert treatment.get_price_for_tier('base') == Decimal('300.00')
    
    # Member tier
    assert treatment.get_price_for_tier('member') == Decimal('250.00')
    
    # Insurance tier
    assert treatment.get_price_for_tier('insurance') == Decimal('200.00')
    
    # Unknown tier defaults to base
    assert treatment.get_price_for_tier('unknown') == Decimal('300.00')


def test_calculate_patient_cost(db: Session):
    """Test calculating patient cost after insurance."""
    org = Organization(name="Cost Test", slug="cost-test", email="cost@example.com")
    db.add(org)
    db.commit()
    
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="COST-001",
        treatment_name_hebrew="חישוב עלות",
        category="preventive",
        base_price=Decimal('500.00')
    )
    db.add(treatment)
    db.commit()
    
    # No insurance
    assert treatment.calculate_patient_cost() == Decimal('500.00')
    
    # With insurance coverage
    assert treatment.calculate_patient_cost(insurance_coverage=Decimal('200.00')) == Decimal('300.00')
    
    # Insurance covers everything
    assert treatment.calculate_patient_cost(insurance_coverage=Decimal('500.00')) == Decimal('0.00')
    
    # Insurance covers more than price (shouldn't be negative)
    assert treatment.calculate_patient_cost(insurance_coverage=Decimal('600.00')) == Decimal('0.00')


def test_is_available_for_booking(db: Session):
    """Test checking if treatment is available for booking."""
    org = Organization(name="Booking Test", slug="booking-test", email="booking@example.com")
    db.add(org)
    db.commit()
    
    # Available treatment
    treatment1 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="AVAIL-001",
        treatment_name_hebrew="זמין",
        category="preventive",
        base_price=Decimal('100.00'),
        is_active=True,
        is_visible_online=True,
        requires_approval=False
    )
    db.add(treatment1)
    db.commit()
    
    assert treatment1.is_available_for_booking() == True
    
    # Not active
    treatment2 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="INACTIVE-001",
        treatment_name_hebrew="לא פעיל",
        category="preventive",
        base_price=Decimal('100.00'),
        is_active=False
    )
    db.add(treatment2)
    db.commit()
    
    assert treatment2.is_available_for_booking() == False
    
    # Requires approval
    treatment3 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="APPROVAL-001",
        treatment_name_hebrew="דורש אישור",
        category="surgical",
        base_price=Decimal('5000.00'),
        requires_approval=True
    )
    db.add(treatment3)
    db.commit()
    
    assert treatment3.is_available_for_booking() == False


def test_odoo_integration_fields(db: Session):
    """Test Odoo integration fields."""
    org = Organization(name="Odoo Test", slug="odoo-test", email="odoo@example.com")
    db.add(org)
    db.commit()
    
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="ODOO-001",
        treatment_name_hebrew="אינטגרציה עם Odoo",
        category="preventive",
        base_price=Decimal('100.00'),
        odoo_product_id=12345,
        odoo_product_template_id=67890
    )
    db.add(treatment)
    db.commit()
    
    assert treatment.odoo_product_id == 12345
    assert treatment.odoo_product_template_id == 67890


def test_to_dict(db: Session):
    """Test converting treatment to dictionary."""
    org = Organization(name="Dict Test", slug="dict-test", email="dict@example.com")
    db.add(org)
    db.commit()
    
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="DICT-001",
        treatment_name_hebrew="מילון",
        treatment_name_english="Dictionary",
        category="preventive",
        base_price=Decimal('100.00'),
        member_price=Decimal('80.00'),
        duration_minutes=30
    )
    db.add(treatment)
    db.commit()
    
    data = treatment.to_dict()
    
    # Check structure
    assert 'id' in data
    assert 'treatment_code' in data
    assert 'name' in data
    assert 'pricing' in data
    assert 'specialist' in data
    assert 'odoo' in data
    assert 'status' in data
    
    # Check nested data
    assert data['name']['hebrew'] == "מילון"
    assert data['name']['english'] == "Dictionary"
    assert data['pricing']['base'] == 100.00
    assert data['pricing']['member'] == 80.00


def test_default_israeli_treatments(db: Session):
    """Test creating default Israeli treatments."""
    org = Organization(name="Defaults Test", slug="defaults-test", email="defaults@example.com")
    db.add(org)
    db.commit()
    
    # Create all defaults
    for default in DEFAULT_ISRAELI_TREATMENTS:
        treatment = TreatmentPrice(
            organization_id=org.id,
            **default
        )
        db.add(treatment)
    
    db.commit()
    
    # Verify all created
    count = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org.id
    ).count()
    
    assert count == len(DEFAULT_ISRAELI_TREATMENTS)
    
    # Verify specific treatments
    cleaning = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org.id,
        TreatmentPrice.treatment_code == 'CLEAN-001'
    ).first()
    
    assert cleaning is not None
    assert cleaning.treatment_name_hebrew == 'ניקוי אבנית'
    assert cleaning.category == 'preventive'


def test_cascade_delete(db: Session):
    """Test that treatments are deleted when organization is deleted."""
    org = Organization(name="Cascade Test", slug="cascade-test", email="cascade@example.com")
    db.add(org)
    db.commit()
    
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="CASCADE-001",
        treatment_name_hebrew="מחיקה מדורגת",
        category="preventive",
        base_price=Decimal('100.00')
    )
    db.add(treatment)
    db.commit()
    
    treatment_id = treatment.id
    
    # Delete organization
    db.delete(org)
    db.commit()
    
    # Treatment should be deleted too
    found = db.query(TreatmentPrice).filter(TreatmentPrice.id == treatment_id).first()
    assert found is None


def test_specialist_requirements(db: Session):
    """Test specialist requirement fields."""
    org = Organization(name="Specialist Test", slug="specialist-test", email="specialist@example.com")
    db.add(org)
    db.commit()
    
    # Treatment requiring specialist
    treatment = TreatmentPrice(
        organization_id=org.id,
        treatment_code="SPEC-001",
        treatment_name_hebrew="טיפול מומחה",
        category="endodontic",
        base_price=Decimal('1500.00'),
        requires_specialist=True,
        specialist_type="endodontist"
    )
    db.add(treatment)
    db.commit()
    
    assert treatment.requires_specialist == True
    assert treatment.specialist_type == "endodontist"


def test_display_order(db: Session):
    """Test display order functionality."""
    org = Organization(name="Order Test", slug="order-test", email="order@example.com")
    db.add(org)
    db.commit()
    
    # Create treatments with different orders
    t1 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="ORDER-001",
        treatment_name_hebrew="שלישי",
        category="preventive",
        base_price=Decimal('100.00'),
        display_order=3
    )
    
    t2 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="ORDER-002",
        treatment_name_hebrew="ראשון",
        category="preventive",
        base_price=Decimal('100.00'),
        display_order=1
    )
    
    t3 = TreatmentPrice(
        organization_id=org.id,
        treatment_code="ORDER-003",
        treatment_name_hebrew="שני",
        category="preventive",
        base_price=Decimal('100.00'),
        display_order=2
    )
    
    db.add_all([t1, t2, t3])
    db.commit()
    
    # Query ordered
    treatments = db.query(TreatmentPrice).filter(
        TreatmentPrice.organization_id == org.id
    ).order_by(TreatmentPrice.display_order).all()
    
    assert treatments[0].treatment_code == "ORDER-002"  # display_order=1
    assert treatments[1].treatment_code == "ORDER-003"  # display_order=2
    assert treatments[2].treatment_code == "ORDER-001"  # display_order=3
