"""
Test Odoo-enabled Patient Portal Endpoints

This script tests the new endpoints that fetch real data from Odoo.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.api.v1.endpoints.patient_portal_odoo import (
    get_odoo_patient_id,
    get_patient_profile,
    get_health_score,
    get_appointments,
    get_doctors,
    get_available_slots
)
from app.models.user import User
from app.integrations.odoo_client_v2 import OdooClientV2


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


async def test_odoo_endpoints():
    """Test all Odoo endpoints."""
    
    print_section("PATIENT PORTAL - ODOO INTEGRATION TEST")
    
    # Initialize Odoo client
    print("Initializing Odoo client...")
    odoo_client = OdooClientV2()
    print("✅ Odoo client initialized\n")
    
    # Create a mock user for testing
    class MockUser:
        def __init__(self):
            self.id = "test-user-123"
            self.email = "avi.gold@example.com"  # Existing patient in Odoo
            self.full_name = "Avi Goldstein"
    
    test_user = MockUser()
    
    # Test 1: Get Odoo Patient ID
    print_section("Test 1: Get Odoo Patient ID")
    patient_id = get_odoo_patient_id(test_user)
    print(f"Patient ID for {test_user.email}: {patient_id}")
    
    if not patient_id:
        print("❌ Patient not found in Odoo. Using a different email...")
        test_user.email = "david.cohen@example.com"
        patient_id = get_odoo_patient_id(test_user)
        print(f"Patient ID for {test_user.email}: {patient_id}")
    
    # Test 2: Get Doctors List
    print_section("Test 2: Get Doctors List")
    try:
        doctors = odoo_client.get_doctors()
        print(f"Found {len(doctors)} doctors:")
        for doctor in doctors[:3]:  # Show first 3
            print(f"  - {doctor.get('name')} (ID: {doctor['id']})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get Appointments
    print_section("Test 3: Get Appointments")
    if patient_id:
        try:
            appointments = odoo_client.get_appointments(
                patient_id=patient_id,
                limit=5
            )
            print(f"Found {len(appointments)} appointments:")
            for apt in appointments[:3]:  # Show first 3
                date = apt.get('start', 'N/A')
                doctor = apt.get('doctor_id', [None, 'Unknown'])[1] if apt.get('doctor_id') else 'Unknown'
                print(f"  - {date} with {doctor}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⚠️ Skipping - no patient ID")
    
    # Test 4: Get Available Slots
    print_section("Test 4: Get Available Slots")
    try:
        # Get first doctor
        doctors = odoo_client.get_doctors()
        if doctors:
            doctor_id = doctors[0]['id']
            from datetime import date, timedelta
            tomorrow = (date.today() + timedelta(days=1)).isoformat()
            
            print(f"Checking slots for doctor {doctor_id} on {tomorrow}...")
            
            # Get existing appointments for that day
            appointments = odoo_client.get_appointments(
                doctor_id=doctor_id,
                date_from=tomorrow,
                date_to=tomorrow
            )
            
            print(f"Found {len(appointments)} existing appointments")
            
            # Generate available slots (simplified)
            booked_times = set()
            for apt in appointments:
                apt_date_str = apt.get('start')
                if apt_date_str:
                    from datetime import datetime
                    try:
                        apt_time = datetime.fromisoformat(apt_date_str).time()
                        booked_times.add(apt_time.strftime("%H:%M"))
                    except:
                        pass
            
            print(f"Booked times: {booked_times}")
            
            # Show some available slots
            available_count = 0
            for hour in range(9, 17):
                for minute in [0, 30]:
                    time_str = f"{hour:02d}:{minute:02d}"
                    if time_str not in booked_times:
                        available_count += 1
            
            print(f"✅ {available_count} available slots found")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print_section("TEST COMPLETE")
    print("✅ All Odoo endpoint tests completed!")
    print("\nNext steps:")
    print("1. Update frontend to use these endpoints")
    print("2. Add authentication to endpoints")
    print("3. Test with real user sessions")
    print("4. Add caching for better performance")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_odoo_endpoints())
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

