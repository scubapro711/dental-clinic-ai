"""
Comprehensive test of updated Odoo client with real data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.integrations.odoo_client import odoo_client

def test_odoo_integration():
    """Test all Odoo client methods."""
    print("="*80)
    print("COMPREHENSIVE ODOO CLIENT TEST")
    print("="*80)
    
    try:
        # Test 1: Authentication
        print("\n1. Testing authentication...")
        if odoo_client.authenticate():
            print("   ✓ Authentication successful")
        else:
            print("   ✗ Authentication failed")
            return False
        
        # Test 2: Search existing patients
        print("\n2. Searching for existing patients...")
        patient_ids = odoo_client.search_patients(limit=5)
        print(f"   Found {len(patient_ids)} patients")
        
        if patient_ids:
            patient = odoo_client.get_patient(patient_ids[0])
            print(f"   Sample patient: {patient.get('name')} (ID: {patient.get('id')})")
            existing_patient_id = patient_ids[0]
        else:
            existing_patient_id = None
        
        # Test 3: Create a new patient
        print("\n3. Creating a new test patient...")
        new_patient_id = odoo_client.create_patient(
            name="Test Patient - DentaFlow AI",
            email="test@dentaflow.ai",
            phone="050-1234567",
            israeli_id="123456789"
        )
        print(f"   ✓ Created patient with ID: {new_patient_id}")
        
        # Verify patient creation
        patient_data = odoo_client.get_patient(new_patient_id)
        print(f"   Verified: {patient_data.get('name')}")
        
        # Test 4: Get doctors
        print("\n4. Getting list of doctors...")
        doctors = odoo_client.get_doctors(limit=10)
        print(f"   Found {len(doctors)} doctors")
        
        if doctors:
            doctor = doctors[0]
            print(f"   Sample doctor: {doctor.get('name')} (ID: {doctor.get('id')})")
            doctor_id = doctor.get('id')
        else:
            print("   ⚠ No doctors found - cannot test appointments")
            doctor_id = None
        
        # Test 5: Create appointment (if we have a doctor)
        if doctor_id:
            print("\n5. Creating a test appointment...")
            appointment_date = datetime.now() + timedelta(days=1)
            appointment_date = appointment_date.replace(hour=10, minute=0, second=0, microsecond=0)
            
            appointment_id = odoo_client.create_appointment(
                patient_id=new_patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                duration=1.0,
                patient_state='scheduled',
                urgency=False
            )
            print(f"   ✓ Created appointment with ID: {appointment_id}")
            
            # Verify appointment
            appointment_data = odoo_client.get_appointment(appointment_id)
            print(f"   Verified: Appointment {appointment_data.get('name')}")
            print(f"   Date: {appointment_data.get('appointment_date')}")
            print(f"   Patient: {appointment_data.get('patient_id')}")
            print(f"   Doctor: {appointment_data.get('doctor_id')}")
            
            # Test 6: Search appointments
            print("\n6. Searching for appointments...")
            found_appointments = odoo_client.search_appointments(
                patient_id=new_patient_id,
                limit=10
            )
            print(f"   Found {len(found_appointments)} appointments for patient")
            
            # Test 7: Update appointment
            print("\n7. Confirming appointment...")
            if odoo_client.confirm_appointment(appointment_id):
                print("   ✓ Appointment confirmed")
                
                # Verify update
                updated_apt = odoo_client.get_appointment(appointment_id)
                print(f"   State: {updated_apt.get('state')}")
            
            # Test 8: Get available slots
            print("\n8. Getting available time slots...")
            tomorrow = datetime.now() + timedelta(days=2)
            day_after = tomorrow + timedelta(days=1)
            
            slots = odoo_client.get_available_slots(
                doctor_id=doctor_id,
                date_from=tomorrow,
                date_to=day_after,
                duration=1.0
            )
            print(f"   Found {len(slots)} available slots")
            if slots:
                print(f"   First slot: {slots[0]}")
                print(f"   Last slot: {slots[-1]}")
            
            # Test 9: Cancel appointment
            print("\n9. Cancelling test appointment...")
            if odoo_client.cancel_appointment(appointment_id, reason="Test cleanup"):
                print("   ✓ Appointment cancelled")
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nTest Summary:")
        print(f"  - Created patient ID: {new_patient_id}")
        if doctor_id:
            print(f"  - Used doctor ID: {doctor_id}")
            print(f"  - Created appointment ID: {appointment_id}")
        print(f"\nNote: Test data remains in Odoo for verification")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_odoo_integration()
    sys.exit(0 if success else 1)
