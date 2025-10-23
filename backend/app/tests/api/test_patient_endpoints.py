"""
Day 3: Patient Management API Endpoint Tests

Critical tests for patient-facing API endpoints that interact with Odoo.
Tests cover profile management, health scores, and patient data retrieval.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.user import User
from app.models.user_patient_mapping import UserPatientMapping


# ============================================================================
# CRITICAL TEST #1: Get Patient Profile - Linked to Odoo
# ============================================================================

@pytest.mark.asyncio
async def test_get_patient_profile_linked(authenticated_client, db_session, test_user):
    """
    CRITICAL: Get patient profile when user is linked to Odoo patient
    
    Scenario: Patient logs in and views their profile
    Expected: Profile data fetched from Odoo successfully
    """
    # Setup: Create user-patient mapping
    mapping = UserPatientMapping(
        user_id=test_user.id,
        odoo_patient_id=123,
        email=test_user.email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Mock Odoo response
    mock_odoo_data = [{
        'id': 123,
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+972501234567',
        'mobile': None,
        'birthdate_date': '1990-01-01',
        'street': '123 Main St',
        'city': 'Tel Aviv',
        'zip': '12345',
        'country_id': [1, 'Israel']
    }]
    
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient') as mock_odoo:
        mock_instance = MagicMock()
        mock_instance.read.return_value = mock_odoo_data
        mock_odoo.return_value = mock_instance
        
        response = authenticated_client.get("/api/v1/patient/profile")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['odoo_linked'] == True
    assert data['odoo_id'] == 123
    assert data['name'] == 'John Doe'
    assert data['email'] == 'john@example.com'
    assert data['phone'] == '+972501234567'
    assert data['date_of_birth'] == '1990-01-01'
    assert data['address']['city'] == 'Tel Aviv'


# ============================================================================
# CRITICAL TEST #2: Get Patient Profile - Not Linked
# ============================================================================

@pytest.mark.asyncio
async def test_get_patient_profile_not_linked(authenticated_client, db_session, test_user):
    """
    CRITICAL: Get patient profile when user is NOT linked to Odoo
    
    Scenario: New user logs in before completing onboarding
    Expected: Returns basic user info with odoo_linked=False
    """
    # No mapping created - user not linked to Odoo
    
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient'):
        response = authenticated_client.get("/api/v1/patient/profile")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['odoo_linked'] == False
    assert data['email'] == test_user.email
    assert 'odoo_id' not in data or data.get('odoo_id') is None


# ============================================================================
# CRITICAL TEST #3: Get Health Score - With Appointments
# ============================================================================

@pytest.mark.asyncio
async def test_get_health_score_with_appointments(authenticated_client, db_session, test_user):
    """
    CRITICAL: Calculate health score for patient with appointment history
    
    Scenario: Patient has recent appointments
    Expected: High health score with positive factors
    """
    # Setup: Create user-patient mapping
    mapping = UserPatientMapping(
        user_id=test_user.id,
        odoo_patient_id=123,
        email=test_user.email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Mock Odoo appointments - recent checkup
    mock_appointments = [
        {
            'id': 1,
            'start': (datetime.now() - timedelta(days=30)).isoformat(),
            'state': 'done'
        },
        {
            'id': 2,
            'start': (datetime.now() + timedelta(days=30)).isoformat(),
            'state': 'confirmed'
        }
    ]
    
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient') as mock_odoo:
        mock_instance = MagicMock()
        mock_instance.search_read.return_value = mock_appointments
        mock_odoo.return_value = mock_instance
        
        response = authenticated_client.get("/api/v1/patient/health-score")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['score'] >= 80  # High score for recent appointments
    assert len(data['factors']) > 0
    assert any(f['status'] == 'good' for f in data['factors'])
    assert len(data['recommendations']) > 0


# ============================================================================
# CRITICAL TEST #4: Get Health Score - No Appointments
# ============================================================================

@pytest.mark.asyncio
async def test_get_health_score_no_appointments(authenticated_client, db_session, test_user):
    """
    CRITICAL: Calculate health score for patient without appointments
    
    Scenario: New patient with no appointment history
    Expected: Lower score with recommendations to schedule
    """
    # Setup: Create user-patient mapping
    mapping = UserPatientMapping(
        user_id=test_user.id,
        odoo_patient_id=123,
        email=test_user.email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Mock Odoo appointments - empty
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient') as mock_odoo:
        mock_instance = MagicMock()
        mock_instance.search_read.return_value = []
        mock_odoo.return_value = mock_instance
        
        response = authenticated_client.get("/api/v1/patient/health-score")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['score'] < 80  # Lower score for no appointments
    assert 'Schedule a dental checkup' in str(data['recommendations'])


# ============================================================================
# CRITICAL TEST #5: Get Appointments - Upcoming Filter
# ============================================================================

@pytest.mark.asyncio
async def test_get_appointments_upcoming(authenticated_client, db_session, test_user):
    """
    CRITICAL: Get patient's upcoming appointments
    
    Scenario: Patient wants to see future appointments
    Expected: Only upcoming appointments returned
    """
    # Setup: Create user-patient mapping
    mapping = UserPatientMapping(
        user_id=test_user.id,
        odoo_patient_id=123,
        email=test_user.email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Mock Odoo appointments - mix of past and future
    mock_appointments = [
        {
            'id': 1,
            'patient_id': [123, 'John Doe'],
            'doctor_id': [1, 'Dr. Smith'],
            'start': (datetime.now() + timedelta(days=7)).isoformat(),
            'stop': (datetime.now() + timedelta(days=7, hours=1)).isoformat(),
            'state': 'confirmed',
            'treatment_type': 'Cleaning'
        },
        {
            'id': 2,
            'patient_id': [123, 'John Doe'],
            'doctor_id': [1, 'Dr. Smith'],
            'start': (datetime.now() + timedelta(days=30)).isoformat(),
            'stop': (datetime.now() + timedelta(days=30, hours=1)).isoformat(),
            'state': 'confirmed',
            'treatment_type': 'Checkup'
        }
    ]
    
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient') as mock_odoo:
        mock_instance = MagicMock()
        mock_instance.search_read.return_value = mock_appointments
        mock_odoo.return_value = mock_instance
        
        response = authenticated_client.get("/api/v1/appointments?status=upcoming")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert 'appointments' in data
    assert len(data['appointments']) == 2
    assert all(datetime.fromisoformat(apt['start']) > datetime.now() 
               for apt in data['appointments'])


# ============================================================================
# CRITICAL TEST #6: Get Appointments - Past Filter
# ============================================================================

@pytest.mark.asyncio
async def test_get_appointments_past(authenticated_client, db_session, test_user):
    """
    CRITICAL: Get patient's past appointments
    
    Scenario: Patient wants to review appointment history
    Expected: Only past appointments returned
    """
    # Setup: Create user-patient mapping
    mapping = UserPatientMapping(
        user_id=test_user.id,
        odoo_patient_id=123,
        email=test_user.email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Mock Odoo appointments - past only
    mock_appointments = [
        {
            'id': 1,
            'patient_id': [123, 'John Doe'],
            'doctor_id': [1, 'Dr. Smith'],
            'start': (datetime.now() - timedelta(days=30)).isoformat(),
            'stop': (datetime.now() - timedelta(days=30, hours=-1)).isoformat(),
            'state': 'done',
            'treatment_type': 'Cleaning'
        }
    ]
    
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient') as mock_odoo:
        mock_instance = MagicMock()
        mock_instance.search_read.return_value = mock_appointments
        mock_odoo.return_value = mock_instance
        
        response = authenticated_client.get("/api/v1/appointments?status=past")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert 'appointments' in data
    assert len(data['appointments']) == 1
    assert data['appointments'][0]['state'] == 'done'


# ============================================================================
# CRITICAL TEST #7: Get Appointments - Pagination
# ============================================================================

@pytest.mark.asyncio
async def test_get_appointments_pagination(authenticated_client, db_session, test_user):
    """
    CRITICAL: Test appointment pagination
    
    Scenario: Patient has many appointments, requests paginated results
    Expected: Correct limit and offset applied
    """
    # Setup: Create user-patient mapping
    mapping = UserPatientMapping(
        user_id=test_user.id,
        odoo_patient_id=123,
        email=test_user.email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(mapping)
    db_session.commit()
    
    # Mock Odoo appointments - 5 appointments
    mock_appointments = [
        {
            'id': i,
            'patient_id': [123, 'John Doe'],
            'doctor_id': [1, 'Dr. Smith'],
            'start': (datetime.now() + timedelta(days=i)).isoformat(),
            'stop': (datetime.now() + timedelta(days=i, hours=1)).isoformat(),
            'state': 'confirmed',
            'treatment_type': 'Checkup'
        }
        for i in range(1, 6)
    ]
    
    with patch('app.api.v1.endpoints.patient_portal_odoo.OdooClient') as mock_odoo:
        mock_instance = MagicMock()
        mock_instance.search_read.return_value = mock_appointments[:3]  # First 3
        mock_odoo.return_value = mock_instance
        
        response = authenticated_client.get("/api/v1/appointments?limit=3&offset=0")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['limit'] == 3
    assert data['offset'] == 0
    assert len(data['appointments']) <= 3


# ============================================================================
# CRITICAL TEST #8: Unauthorized Access
# ============================================================================

@pytest.mark.asyncio
async def test_patient_endpoints_unauthorized(client):
    """
    CRITICAL: Test unauthorized access to patient endpoints
    
    Scenario: Unauthenticated user tries to access patient data
    Expected: 401 Unauthorized error
    """
    # No authentication mock - should fail
    response = client.get("/api/v1/patient/profile")
    
    # Assertions
    assert response.status_code in [401, 403]  # Unauthorized or Forbidden


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password_here",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user

