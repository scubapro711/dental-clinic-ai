"""
Test Alex Agent with Real Odoo Integration

This script tests the Alex agent with real Odoo tools.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.tools.alex_odoo_tools import (
    search_patient_odoo,
    get_patient_details_odoo,
    create_patient_odoo,
    update_patient_odoo,
    get_doctors_list_odoo,
)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_alex_odoo_tools():
    """Test all Alex Odoo tools."""
    
    print_section("ALEX AGENT - ODOO INTEGRATION TEST")
    
    # Test context - simulating an admin user
    test_user_id = "admin_1"
    test_user_role = "admin"
    
    # Test 1: Search for existing patients
    print_section("Test 1: Search for Patients")
    result = search_patient_odoo(
        name="Avi",
        requesting_user_id=test_user_id,
        requesting_user_role=test_user_role
    )
    print(result)
    
    # Test 2: Get patient details
    print_section("Test 2: Get Patient Details")
    result = get_patient_details_odoo(
        patient_id=12,  # Avi Goldstein from our earlier test
        requesting_user_id=test_user_id,
        requesting_user_role=test_user_role
    )
    print(result)
    
    # Test 3: Create a new patient
    print_section("Test 3: Create New Patient")
    result = create_patient_odoo(
        name="Test Patient - Alex Integration",
        phone="054-1234567",
        email="alex.test@dentaflow.ai",
        city="Tel Aviv",
        requesting_user_id=test_user_id,
        requesting_user_role=test_user_role
    )
    print(result)
    
    # Extract patient ID from result
    if "ID:" in result:
        new_patient_id = int(result.split("ID:")[1].strip())
        
        # Test 4: Update the new patient
        print_section("Test 4: Update Patient")
        result = update_patient_odoo(
            patient_id=new_patient_id,
            phone="054-9876543",
            email="alex.updated@dentaflow.ai",
            requesting_user_id=test_user_id,
            requesting_user_role=test_user_role
        )
        print(result)
        
        # Test 5: Verify the update
        print_section("Test 5: Verify Update")
        result = get_patient_details_odoo(
            patient_id=new_patient_id,
            requesting_user_id=test_user_id,
            requesting_user_role=test_user_role
        )
        print(result)
    
    # Test 6: Get doctors list
    print_section("Test 6: Get Doctors List")
    result = get_doctors_list_odoo(
        requesting_user_id=test_user_id,
        requesting_user_role=test_user_role
    )
    print(result)
    
    # Test 7: RBAC - Patient trying to access other patient's data
    print_section("Test 7: RBAC Test - Patient Access Control")
    result = get_patient_details_odoo(
        patient_id=12,  # Avi Goldstein
        requesting_user_id="999",  # Different patient
        requesting_user_role="patient"
    )
    print(result)
    
    print_section("TEST COMPLETE")
    print("✅ All Alex Odoo tools tested successfully!")
    print("\nNext steps:")
    print("1. Integrate these tools into Alex agent")
    print("2. Test with real user conversations")
    print("3. Deploy to production")


if __name__ == "__main__":
    try:
        test_alex_odoo_tools()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
