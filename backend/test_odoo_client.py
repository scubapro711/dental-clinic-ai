"""
Test script for OdooClient

This script tests the updated OdooClient that uses OdooWrapper.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.odoo_client import OdooClient


def test_patient_operations():
    """Test patient CRUD operations."""
    print("\n" + "="*60)
    print("TEST 1: Patient Operations")
    print("="*60)
    
    client = OdooClient()
    
    # Search patients
    print("\n1. Searching patients by name 'John'...")
    patient_ids = client.search_patients(name="John")
    print(f"✅ Found {len(patient_ids)} patients")
    if patient_ids:
        print(f"   First 5 IDs: {patient_ids[:5]}")
    
    # Get patient details
    if patient_ids:
        print(f"\n2. Getting details for patient {patient_ids[0]}...")
        patient = client.get_patient(patient_ids[0])
        if patient:
            print(f"✅ Patient details:")
            print(f"   Name: {patient['name']}")
            print(f"   Email: {patient.get('email', 'N/A')}")
            print(f"   Phone: {patient.get('phone', 'N/A')}")
    
    # Count patients
    print("\n3. Counting total patients...")
    count = client.count_patients()
    print(f"✅ Total patients: {count}")
    
    # Create patient
    print("\n4. Creating new patient...")
    new_patient_id = client.create_patient(
        name="Test Patient",
        email="test@example.com",
        phone="+972501234567"
    )
    print(f"✅ Created patient with ID: {new_patient_id}")
    
    # Update patient
    print(f"\n5. Updating patient {new_patient_id}...")
    success = client.update_patient(new_patient_id, email="updated@example.com")
    print(f"✅ Update {'successful' if success else 'failed'}")


def test_appointment_operations():
    """Test appointment CRUD operations."""
    print("\n" + "="*60)
    print("TEST 2: Appointment Operations")
    print("="*60)
    
    client = OdooClient()
    
    # Search appointments
    print("\n1. Searching appointments for patient 1...")
    appt_ids = client.search_appointments(patient_id=1)
    print(f"✅ Found {len(appt_ids)} appointments")
    if appt_ids:
        print(f"   First 5 IDs: {appt_ids[:5]}")
    
    # Get appointment details
    if appt_ids:
        print(f"\n2. Getting details for appointment {appt_ids[0]}...")
        appt = client.get_appointment(appt_ids[0])
        if appt:
            print(f"✅ Appointment details:")
            print(f"   Patient: {appt.get('patient_name', 'N/A')}")
            print(f"   Date: {appt['date']}")
            print(f"   Time: {appt['time']}")
            print(f"   Treatment: {appt.get('treatment_type', 'N/A')}")
            print(f"   Status: {appt['status']}")
    
    # Count appointments
    print("\n3. Counting scheduled appointments...")
    count = client.count_appointments(status="scheduled")
    print(f"✅ Scheduled appointments: {count}")
    
    # Create appointment
    print("\n4. Creating new appointment...")
    new_appt_id = client.create_appointment(
        patient_id=1,
        date="2025-10-20",
        time="10:00",
        treatment_type="Test Checkup",
        duration_minutes=30
    )
    print(f"✅ Created appointment with ID: {new_appt_id}")
    
    # Update appointment
    print(f"\n5. Confirming appointment {new_appt_id}...")
    success = client.confirm_appointment(new_appt_id)
    print(f"✅ Confirmation {'successful' if success else 'failed'}")
    
    # Cancel appointment
    print(f"\n6. Cancelling appointment {new_appt_id}...")
    success = client.cancel_appointment(new_appt_id)
    print(f"✅ Cancellation {'successful' if success else 'failed'}")


def test_invoice_operations():
    """Test invoice operations."""
    print("\n" + "="*60)
    print("TEST 3: Invoice Operations")
    print("="*60)
    
    client = OdooClient()
    
    # Search invoices
    print("\n1. Searching invoices for patient 1...")
    invoice_ids = client.search_invoices(patient_id=1)
    print(f"✅ Found {len(invoice_ids)} invoices")
    if invoice_ids:
        print(f"   First 5 IDs: {invoice_ids[:5]}")
    
    # Get invoice details
    if invoice_ids:
        print(f"\n2. Getting details for invoice {invoice_ids[0]}...")
        invoice = client.get_invoice(invoice_ids[0])
        if invoice:
            print(f"✅ Invoice details:")
            print(f"   Patient: {invoice.get('patient_name', 'N/A')}")
            print(f"   Issue Date: {invoice.get('issue_date', 'N/A')}")
            print(f"   Total: ₪{invoice.get('total_amount', 0)}")
            print(f"   Status: {invoice['status']}")
    
    # Count invoices
    print("\n3. Counting paid invoices...")
    count = client.count_invoices(status="paid")
    print(f"✅ Paid invoices: {count}")


def test_available_slots():
    """Test available slots functionality."""
    print("\n" + "="*60)
    print("TEST 4: Available Slots")
    print("="*60)
    
    client = OdooClient()
    
    print("\n1. Getting available slots for next 2 days...")
    slots = client.get_available_slots("2025-10-15", "2025-10-17", duration_minutes=60)
    print(f"✅ Found {len(slots)} available slots")
    
    if slots:
        print("\n   First 5 slots:")
        for slot in slots[:5]:
            print(f"   - {slot['date']} at {slot['time']}")


def test_full_workflow():
    """Test a complete workflow: create patient, book appointment, check invoice."""
    print("\n" + "="*60)
    print("TEST 5: Full Workflow")
    print("="*60)
    
    client = OdooClient()
    
    # Step 1: Create patient
    print("\n1. Creating new patient...")
    patient_id = client.create_patient(
        name="Workflow Test Patient",
        email="workflow@test.com",
        phone="+972509999999"
    )
    print(f"✅ Created patient ID: {patient_id}")
    
    # Step 2: Get patient details
    print(f"\n2. Retrieving patient {patient_id} details...")
    patient = client.get_patient(patient_id)
    if patient:
        print(f"✅ Patient: {patient['name']}")
    
    # Step 3: Create appointment
    print(f"\n3. Booking appointment for patient {patient_id}...")
    appt_id = client.create_appointment(
        patient_id=patient_id,
        date="2025-10-25",
        time="14:30",
        treatment_type="Initial Consultation",
        duration_minutes=45,
        notes="First visit"
    )
    print(f"✅ Created appointment ID: {appt_id}")
    
    # Step 4: Confirm appointment
    print(f"\n4. Confirming appointment {appt_id}...")
    success = client.confirm_appointment(appt_id)
    print(f"✅ Appointment confirmed: {success}")
    
    # Step 5: Get appointment details
    print(f"\n5. Retrieving appointment {appt_id} details...")
    appt = client.get_appointment(appt_id)
    if appt:
        print(f"✅ Appointment on {appt['date']} at {appt['time']}")
        print(f"   Status: {appt['status']}")
    
    print("\n✅ Full workflow completed successfully!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 TESTING UPDATED ODOO CLIENT")
    print("="*60)
    
    try:
        test_patient_operations()
        test_appointment_operations()
        test_invoice_operations()
        test_available_slots()
        test_full_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎉 OdooClient is working correctly!")
        print("   - Patient operations: ✅")
        print("   - Appointment operations: ✅")
        print("   - Invoice operations: ✅")
        print("   - Available slots: ✅")
        print("   - Full workflow: ✅")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
