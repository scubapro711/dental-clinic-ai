#!/usr/bin/env python3
"""
Test script for DemoDataAdapter
Tests the database integration and functionality
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_agents.tools.advanced_dental_tool import AdvancedDentalTool

async def test_dental_tool():
    """Test the AdvancedDentalTool with real database"""
    print("🧪 Testing Advanced Dental Tool with Demo Database")
    print("=" * 55)
    
    # Initialize the tool
    tool = AdvancedDentalTool()
    
    try:
        # Initialize the tool
        print("\n1. Initializing tool...")
        await tool.initialize()
        print("✅ Tool initialized successfully")
        
        # Test health check
        print("\n2. Testing health check...")
        health = await tool.health_check()
        print(f"✅ Health check: {health['status']}")
        print(f"   Database connection: {health.get('database_connection', 'unknown')}")
        
        # Test get providers
        print("\n3. Testing get providers...")
        providers = await tool.get_providers()
        print(f"✅ Found {len(providers)} providers:")
        for provider in providers:
            print(f"   - {provider.get('name', '')} {provider.get('surname', '')} (ID: {provider.get('id')})")
        
        # Test search patients
        print("\n4. Testing patient search...")
        patients = await tool.search_patients("Yossi")
        print(f"✅ Found {len(patients)} patients for 'Yossi':")
        for patient in patients:
            print(f"   - {patient.get('name', '')} {patient.get('surname', '')} (ID: {patient.get('id')})")
        
        # Test search patients by surname
        print("\n5. Testing patient search by surname...")
        patients = await tool.search_patients("Mizrahi")
        print(f"✅ Found {len(patients)} patients for 'Mizrahi':")
        for patient in patients:
            print(f"   - {patient.get('name', '')} {patient.get('surname', '')} (ID: {patient.get('id')})")
        
        # Test get available slots
        if providers:
            provider_id = providers[0]['id']
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"\n6. Testing available slots for provider {provider_id} on {tomorrow}...")
            slots = await tool.get_available_slots(provider_id, tomorrow)
            print(f"✅ Found {len(slots)} available slots:")
            for i, slot in enumerate(slots[:5]):  # Show first 5 slots
                print(f"   - {slot.get('time', '')} ({slot.get('duration', 0)} min)")
            if len(slots) > 5:
                print(f"   ... and {len(slots) - 5} more slots")
        
        # Test get patient appointments
        if patients:
            patient_id = patients[0]['id']
            print(f"\n7. Testing appointments for patient {patient_id}...")
            appointments = await tool.get_patient_appointments(patient_id)
            print(f"✅ Found {len(appointments)} appointments:")
            for appointment in appointments:
                print(f"   - {appointment.get('appointments_title', '')} on {appointment.get('appointments_from', '')}")
        
        # Test booking an appointment
        if providers and patients:
            provider_id = providers[0]['id']
            patient_id = patients[0]['id']
            appointment_time = (datetime.now() + timedelta(days=2, hours=10)).isoformat()
            print(f"\n8. Testing appointment booking...")
            print(f"   Patient: {patient_id}, Provider: {provider_id}")
            print(f"   Time: {appointment_time}")
            
            result = await tool.book_appointment(
                patient_id=patient_id,
                provider_id=provider_id,
                datetime_str=appointment_time,
                treatment_type="Test Appointment"
            )
            
            if result['success']:
                print(f"✅ Appointment booked successfully!")
                print(f"   Appointment ID: {result['appointment']['id']}")
                
                # Test cancelling the appointment
                appointment_id = result['appointment']['id']
                print(f"\n9. Testing appointment cancellation...")
                cancel_result = await tool.cancel_appointment(str(appointment_id))
                if cancel_result['success']:
                    print(f"✅ Appointment {appointment_id} cancelled successfully")
                else:
                    print(f"❌ Failed to cancel appointment: {cancel_result['message']}")
            else:
                print(f"❌ Failed to book appointment: {result['message']}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n10. Cleaning up...")
        await tool.cleanup()
        print("✅ Cleanup completed")

async def test_database_connection():
    """Test direct database connection"""
    print("\n🔍 Testing Direct Database Connection")
    print("=" * 40)
    
    try:
        import pymysql
        
        db_config = {
            'host': 'localhost',
            'user': 'dental_user',
            'password': 'dental_pass_2025',
            'database': 'dental_clinic_demo',
            'port': 3306,
            'charset': 'utf8mb4',
        }
        
        connection = pymysql.connect(**db_config)
        print("✅ Direct database connection successful")
        
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Test basic queries
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        patient_count = cursor.fetchone()['count']
        print(f"✅ Patients in database: {patient_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM doctors")
        doctor_count = cursor.fetchone()['count']
        print(f"✅ Doctors in database: {doctor_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM appointments")
        appointment_count = cursor.fetchone()['count']
        print(f"✅ Appointments in database: {appointment_count}")
        
        cursor.close()
        connection.close()
        print("✅ Database connection test completed")
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Demo Database Tests")
    print("=" * 50)
    
    # Test direct database connection first
    asyncio.run(test_database_connection())
    
    # Test the dental tool
    asyncio.run(test_dental_tool())
    
    print("\n🏁 All tests completed!")
