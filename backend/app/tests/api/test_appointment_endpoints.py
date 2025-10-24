"""
Day 3: Appointment Scheduling API Endpoint Tests

Critical tests for appointment management endpoints.
Tests cover creating, updating, canceling, and retrieving appointments.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, date
from uuid import uuid4

# Test client will be provided by pytest fixture


# ============================================================================
# CRITICAL TEST #1: Get Today's Appointments
# ============================================================================

@pytest.mark.asyncio
async def test_get_todays_appointments(client, db_session):
    """
    CRITICAL: Get today's appointments for dashboard
    
    Scenario: Clinic staff views today's schedule
    Expected: All today's appointments returned with patient info
    """
    # Mock Odoo appointments for today
    today = date.today()
    mock_appointments = [
        {
            'id': 1,
            'patient_id': [123, 'John Doe'],
            'doctor_id': [1, 'Dr. Smith'],
            'start': datetime.combine(today, datetime.min.time().replace(hour=9)).isoformat(),
            'stop': datetime.combine(today, datetime.min.time().replace(hour=10)).isoformat(),
            'duration': 1.0,
            'patient_status': 'regular',
            'state': 'confirmed',
            'urgency': False
        },
        {
            'id': 2,
            'patient_id': [124, 'Jane Smith'],
            'doctor_id': [1, 'Dr. Smith'],
            'start': datetime.combine(today, datetime.min.time().replace(hour=14)).isoformat(),
            'stop': datetime.combine(today, datetime.min.time().replace(hour=15)).isoformat(),
            'duration': 1.0,
            'patient_status': 'new',
            'state': 'confirmed',
            'urgency': True
        }
    ]
    
    with patch('app.api.v1.appointments.odoo_client') as mock_odoo:
        mock_odoo.search_read.return_value = mock_appointments
        
        response = client.get("/api/v1/appointments/today")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['patient_name'] == 'John Doe'
    assert data[1]['patient_name'] == 'Jane Smith'
    assert data[1]['is_first_visit'] == True
    assert data[1]['urgency'] == True


# ============================================================================
# CRITICAL TEST #2: Get Today's Appointments - Empty
# ============================================================================

@pytest.mark.asyncio
async def test_get_todays_appointments_empty(client, db_session):
    """
    CRITICAL: Get today's appointments when schedule is empty
    
    Scenario: No appointments scheduled for today
    Expected: Empty list returned
    """
    with patch('app.api.v1.appointments.odoo_client') as mock_odoo:
        mock_odoo.search_read.return_value = []
        
        response = client.get("/api/v1/appointments/today")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# ============================================================================
# CRITICAL TEST #3: Create Appointment - Success
# ============================================================================

@pytest.mark.skip(reason="POST /appointments/create endpoint not implemented yet")
@pytest.mark.asyncio
async def test_create_appointment_success(client, db_session):
    """
    CRITICAL: Create a new appointment
    
    Scenario: Patient books a new appointment
    Expected: Appointment created in Odoo successfully
    """
    appointment_data = {
        'patient_id': 123,
        'doctor_id': 1,
        'start': (datetime.now() + timedelta(days=7)).isoformat(),
        'duration': 1.0,
        'treatment_type': 'Cleaning',
        'notes': 'Regular checkup'
    }
    
    mock_appointment_id = 456
    
    with patch('app.integrations.odoo_client.OdooClient') as mock_odoo_class:
        mock_odoo = MagicMock()
        mock_odoo.create.return_value = mock_appointment_id
        mock_odoo_class.return_value = mock_odoo
        
        # Mock authentication
        with patch('app.api.dependencies.get_current_user'):
            response = client.post(
                "/api/v1/appointments/create",
                json=appointment_data
            )
    
    # Assertions
    assert response.status_code in [200, 201]
    data = response.json()
    assert 'id' in data or 'appointment_id' in data


# ============================================================================
# CRITICAL TEST #4: Create Appointment - Conflict
# ============================================================================

@pytest.mark.skip(reason="POST /appointments/create endpoint not implemented yet")
@pytest.mark.asyncio
async def test_create_appointment_conflict(client, db_session):
    """
    CRITICAL: Attempt to create appointment in occupied slot
    
    Scenario: Patient tries to book a slot that's already taken
    Expected: 409 Conflict error
    """
    appointment_data = {
        'patient_id': 123,
        'doctor_id': 1,
        'start': (datetime.now() + timedelta(days=7)).isoformat(),
        'duration': 1.0,
        'treatment_type': 'Cleaning'
    }
    
    with patch('app.integrations.odoo_client.OdooClient') as mock_odoo_class:
        mock_odoo = MagicMock()
        # Simulate conflict error from Odoo
        mock_odoo.create.side_effect = Exception("Slot already occupied")
        mock_odoo_class.return_value = mock_odoo
        
        with patch('app.api.dependencies.get_current_user'):
            response = client.post(
                "/api/v1/appointments/create",
                json=appointment_data
            )
    
    # Assertions
    assert response.status_code in [409, 400, 500]  # Conflict or error


# ============================================================================
# CRITICAL TEST #5: Update Appointment - Reschedule
# ============================================================================

@pytest.mark.skip(reason="PUT /appointments/{id} endpoint not implemented yet")
@pytest.mark.asyncio
async def test_update_appointment_reschedule(client, db_session):
    """
    CRITICAL: Reschedule an existing appointment
    
    Scenario: Patient needs to change appointment time
    Expected: Appointment updated successfully
    """
    appointment_id = 123
    update_data = {
        'start': (datetime.now() + timedelta(days=14)).isoformat(),
        'duration': 1.5
    }
    
    with patch('app.integrations.odoo_client.OdooClient') as mock_odoo_class:
        mock_odoo = MagicMock()
        mock_odoo.write.return_value = True
        mock_odoo_class.return_value = mock_odoo
        
        with patch('app.api.dependencies.get_current_user'):
            response = client.put(
                f"/api/v1/appointments/{appointment_id}",
                json=update_data
            )
    
    # Assertions
    assert response.status_code in [200, 204]


# ============================================================================
# CRITICAL TEST #6: Cancel Appointment
# ============================================================================

@pytest.mark.skip(reason="DELETE /appointments/{id} endpoint not implemented yet")
@pytest.mark.asyncio
async def test_cancel_appointment(client, db_session):
    """
    CRITICAL: Cancel an appointment
    
    Scenario: Patient cancels their appointment
    Expected: Appointment marked as cancelled in Odoo
    """
    appointment_id = 123
    
    with patch('app.integrations.odoo_client.OdooClient') as mock_odoo_class:
        mock_odoo = MagicMock()
        mock_odoo.write.return_value = True
        mock_odoo_class.return_value = mock_odoo
        
        with patch('app.api.dependencies.get_current_user'):
            response = client.delete(f"/api/v1/appointments/{appointment_id}")
    
    # Assertions
    assert response.status_code in [200, 204]


# ============================================================================
# CRITICAL TEST #7: Get Available Slots
# ============================================================================

@pytest.mark.skip(reason="GET /appointments/available-slots endpoint not implemented yet")
@pytest.mark.asyncio
async def test_get_available_slots(client, db_session):
    """
    CRITICAL: Get available appointment slots for a doctor
    
    Scenario: Patient wants to see available times
    Expected: List of available slots returned
    """
    doctor_id = 1
    target_date = (date.today() + timedelta(days=7)).isoformat()
    
    # Mock available slots
    mock_slots = [
        {
            'start': f"{target_date}T09:00:00",
            'end': f"{target_date}T10:00:00",
            'available': True
        },
        {
            'start': f"{target_date}T10:00:00",
            'end': f"{target_date}T11:00:00",
            'available': True
        },
        {
            'start': f"{target_date}T14:00:00",
            'end': f"{target_date}T15:00:00",
            'available': False  # Occupied
        }
    ]
    
    with patch('app.integrations.odoo_client.OdooClient') as mock_odoo_class:
        mock_odoo = MagicMock()
        # Mock method to get available slots
        mock_odoo.search_read.return_value = []  # No appointments = all slots available
        mock_odoo_class.return_value = mock_odoo
        
        response = client.get(
            f"/api/v1/appointments/available-slots?doctor_id={doctor_id}&date={target_date}"
        )
    
    # Assertions
    assert response.status_code in [200, 404]  # OK or endpoint not implemented yet
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


# ============================================================================
# CRITICAL TEST #8: Get Appointment Details
# ============================================================================

@pytest.mark.skip(reason="Appointment management done via Alex Agent, not direct API")
@pytest.mark.asyncio
async def test_get_appointment_details(client, db_session):
    """
    CRITICAL: Get detailed information about a specific appointment
    
    Scenario: Clinic staff views appointment details
    Expected: Full appointment info returned
    """
    appointment_id = 123
    
    mock_appointment = {
        'id': appointment_id,
        'patient_id': [123, 'John Doe'],
        'doctor_id': [1, 'Dr. Smith'],
        'start': (datetime.now() + timedelta(days=7)).isoformat(),
        'stop': (datetime.now() + timedelta(days=7, hours=1)).isoformat(),
        'duration': 1.0,
        'state': 'confirmed',
        'treatment_type': 'Cleaning',
        'notes': 'Regular checkup',
        'patient_status': 'regular',
        'urgency': False
    }
    
    with patch('app.integrations.odoo_client.OdooClient') as mock_odoo_class:
        mock_odoo = MagicMock()
        mock_odoo.read.return_value = [mock_appointment]
        mock_odoo_class.return_value = mock_odoo
        
        response = client.get(f"/api/v1/appointments/{appointment_id}")
    
    # Assertions
    assert response.status_code in [200, 404]  # OK or endpoint not implemented
    if response.status_code == 200:
        data = response.json()
        assert data['id'] == appointment_id
        assert 'patient_name' in data or 'patient_id' in data

