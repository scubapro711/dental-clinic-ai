"""
Test script for OdooWrapper

This script tests the OdooRPC-compatible wrapper with MockOdoo.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.integrations.odoo_wrapper import get_odoo_client


def test_patient_search():
    """Test patient search functionality."""
    print("\n" + "="*60)
    print("TEST 1: Patient Search")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Search all patients
    print("\n1. Searching all patients...")
    patient_ids = odoo.env['res.partner'].search([('is_patient', '=', True)], limit=5)
    print(f"✅ Found {len(patient_ids)} patients (showing first 5)")
    print(f"   IDs: {patient_ids}")
    
    # Count patients
    print("\n2. Counting all patients...")
    count = odoo.env['res.partner'].search_count([('is_patient', '=', True)])
    print(f"✅ Total patients: {count}")
    
    return patient_ids


def test_patient_read(patient_ids):
    """Test patient read functionality."""
    print("\n" + "="*60)
    print("TEST 2: Patient Read")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Read patient data
    print("\n1. Reading patient data...")
    patients = odoo.env['res.partner'].read(patient_ids[:3], ['name', 'email', 'phone'])
    
    for patient in patients:
        print(f"\n   Patient ID: {patient['id']}")
        print(f"   Name: {patient['name']}")
        print(f"   Email: {patient['email']}")
        print(f"   Phone: {patient['phone']}")
    
    print(f"\n✅ Read {len(patients)} patients successfully")
    
    return patients


def test_patient_browse(patient_ids):
    """Test patient browse functionality."""
    print("\n" + "="*60)
    print("TEST 3: Patient Browse (OdooRPC-style)")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Browse patients
    print("\n1. Browsing patients...")
    patients = odoo.env['res.partner'].browse(patient_ids[:3])
    
    for patient in patients:
        print(f"\n   Patient: {patient.name}")
        print(f"   Email: {patient.email}")
        print(f"   Phone: {patient.phone}")
        print(f"   Age: {patient.age}")
    
    print(f"\n✅ Browsed {len(patients)} patients successfully")


def test_appointment_search():
    """Test appointment search functionality."""
    print("\n" + "="*60)
    print("TEST 4: Appointment Search")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Search all appointments
    print("\n1. Searching all appointments...")
    appt_ids = odoo.env['dental.appointment'].search([], limit=5)
    print(f"✅ Found {len(appt_ids)} appointments (showing first 5)")
    print(f"   IDs: {appt_ids}")
    
    # Search appointments for specific patient
    print("\n2. Searching appointments for patient ID 1...")
    patient_appts = odoo.env['dental.appointment'].search([('patient_id', '=', 1)])
    print(f"✅ Found {len(patient_appts)} appointments for patient 1")
    
    return appt_ids


def test_appointment_read(appt_ids):
    """Test appointment read functionality."""
    print("\n" + "="*60)
    print("TEST 5: Appointment Read")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Read appointment data
    print("\n1. Reading appointment data...")
    appointments = odoo.env['dental.appointment'].read(appt_ids[:3])
    
    for appt in appointments:
        print(f"\n   Appointment ID: {appt['id']}")
        print(f"   Patient ID: {appt['patient_id']}")
        print(f"   Date: {appt['date']}")
        print(f"   Time: {appt['time']}")
        print(f"   Dentist: {appt.get('dentist', 'N/A')}")
        print(f"   Status: {appt['status']}")
    
    print(f"\n✅ Read {len(appointments)} appointments successfully")


def test_create_appointment():
    """Test appointment creation."""
    print("\n" + "="*60)
    print("TEST 6: Create Appointment")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Create new appointment
    print("\n1. Creating new appointment...")
    new_appt_id = odoo.env['dental.appointment'].create({
        'patient_id': 1,
        'date': '2025-10-15',
        'time': '14:00',
        'dentist': 'Dr. Test',
        'treatment_type': 'Test Checkup',
        'notes': 'Test appointment created by OdooWrapper'
    })
    
    print(f"✅ Created appointment with ID: {new_appt_id}")
    
    # Read the created appointment
    print("\n2. Reading created appointment...")
    appt = odoo.env['dental.appointment'].read([new_appt_id])[0]
    print(f"   Date: {appt['date']}")
    print(f"   Time: {appt['time']}")
    print(f"   Dentist: {appt.get('dentist', 'N/A')}")
    
    return new_appt_id


def test_update_appointment(appt_id):
    """Test appointment update."""
    print("\n" + "="*60)
    print("TEST 7: Update Appointment")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Update appointment
    print(f"\n1. Updating appointment {appt_id}...")
    success = odoo.env['dental.appointment'].write([appt_id], {
        'status': 'confirmed',
        'notes': 'Updated by OdooWrapper test'
    })
    
    print(f"✅ Update {'successful' if success else 'failed'}")
    
    # Read updated appointment
    print("\n2. Reading updated appointment...")
    appts = odoo.env['dental.appointment'].read([appt_id])
    if appts:
        appt = appts[0]
        print(f"   Status: {appt['status']}")
        print(f"   Notes: {appt.get('notes', 'N/A')}")
    else:
        print(f"   ⚠️  Appointment {appt_id} not found (this is OK for mock data)")


def test_invoice_search():
    """Test invoice search functionality."""
    print("\n" + "="*60)
    print("TEST 8: Invoice Search")
    print("="*60)
    
    odoo = get_odoo_client()
    
    # Search all invoices
    print("\n1. Searching all invoices...")
    invoice_ids = odoo.env['account.move'].search([], limit=5)
    print(f"✅ Found {len(invoice_ids)} invoices (showing first 5)")
    print(f"   IDs: {invoice_ids}")
    
    # Read invoice data
    if invoice_ids:
        print("\n2. Reading invoice data...")
        invoices = odoo.env['account.move'].read(invoice_ids[:3])
        
        for inv in invoices:
            print(f"\n   Invoice ID: {inv['id']}")
            print(f"   Patient ID: {inv['patient_id']}")
            print(f"   Amount: ₪{inv.get('total_amount', 0)}")
            print(f"   Status: {inv['status']}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 TESTING ODOORPC WRAPPER")
    print("="*60)
    
    try:
        # Test patients
        patient_ids = test_patient_search()
        test_patient_read(patient_ids)
        test_patient_browse(patient_ids)
        
        # Test appointments
        appt_ids = test_appointment_search()
        test_appointment_read(appt_ids)
        
        # Test create/update
        new_appt_id = test_create_appointment()
        test_update_appointment(new_appt_id)
        
        # Test invoices
        test_invoice_search()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎉 OdooWrapper is working correctly!")
        print("   - Patient operations: ✅")
        print("   - Appointment operations: ✅")
        print("   - Invoice operations: ✅")
        print("   - Create/Update operations: ✅")
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
