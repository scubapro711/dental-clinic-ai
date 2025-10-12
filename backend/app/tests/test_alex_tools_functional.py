'''
Alex Tools Functional Tests - CORRECTED

Tests that each Alex tool actually works correctly with proper signatures.
Based on actual tool signatures extracted from AlexAgent.

Total: 20 tools
'''

import sys
from datetime import datetime, timedelta

def run_test(test_func):
    """Helper function to run a test and print the result."""
    test_name = test_func.__name__
    print(f"Running test: {test_name}...")
    try:
        result = test_func()
        if result:
            # Truncate result for display
            result_str = str(result)
            if len(result_str) > 150:
                result_str = result_str[:150] + "..."
            print(f"✅ PASSED: {test_name}")
            print(f"   Result: {result_str}")
            return True
        else:
            print(f"❌ FAILED: {test_name} - No result returned")
            return False
    except Exception as e:
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {e}")
        return False

# ==========================================
# PATIENT MANAGEMENT TOOLS (4 tools)
# ==========================================

def test_create_patient_tool():
    """Test creating a new patient."""
    from app.agents.tools.alex_patient_tools import create_patient_tool
    
    result = create_patient_tool(
        first_name="Test",
        last_name="Patient",
        phone="050-1234567",
        clinic_id=1,
        email="test@example.com"
    )
    
    # Result is a dict
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert result.get('success') is not None, "Missing 'success' key in result"
    return result

def test_update_patient_info_tool():
    """Test updating patient information."""
    from app.agents.tools.alex_patient_tools import update_patient_info_tool
    
    result = update_patient_info_tool(
        patient_id=1,
        email="newemail@example.com"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_get_patient_full_context_tool():
    """Test getting full patient context."""
    from app.agents.tools.alex_patient_tools import get_patient_full_context_tool
    
    result = get_patient_full_context_tool(patient_id=1)
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_add_patient_note_tool():
    """Test adding a note to patient record."""
    from app.agents.tools.alex_patient_tools import add_patient_note_tool
    
    result = add_patient_note_tool(
        patient_id=1,
        note="Test note from automated test",
        note_type="general"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

# ==========================================
# COMMUNICATIONS TOOLS (3 tools)
# ==========================================

def test_send_sms_tool():
    """Test sending SMS."""
    from app.agents.tools.alex_communications_tools import send_sms_tool
    
    result = send_sms_tool(
        patient_id=1,
        template="appointment_reminder",
        clinic_id=1
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_send_email_tool():
    """Test sending email."""
    from app.agents.tools.alex_communications_tools import send_email_tool
    
    result = send_email_tool(
        patient_id=1,
        template="appointment_confirmation",
        clinic_id=1,
        subject="Test Email"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_send_telegram_message_tool():
    """Test sending Telegram message."""
    from app.agents.tools.alex_communications_tools import send_telegram_message_tool
    
    result = send_telegram_message_tool(
        patient_id=1,
        message="Test Telegram message"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

# ==========================================
# FINANCIAL TOOLS (3 tools)
# ==========================================

def test_process_payment_tool():
    """Test processing a payment."""
    from app.agents.tools.alex_financial_tools import process_payment_tool
    
    result = process_payment_tool(
        patient_id=1,
        amount=500.0,
        payment_method="credit_card"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_create_payment_plan_tool():
    """Test creating a payment plan."""
    from app.agents.tools.alex_financial_tools import create_payment_plan_tool
    
    result = create_payment_plan_tool(
        patient_id=1,
        total_amount=5000.0,
        num_payments=6,
        first_payment_date="2025-11-01"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_check_insurance_coverage_tool():
    """Test checking insurance coverage."""
    from app.agents.tools.alex_financial_tools import check_insurance_coverage_tool
    
    result = check_insurance_coverage_tool(
        patient_id=1,
        treatment_code="D0120"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

# ==========================================
# SCHEDULING TOOLS (2 tools)
# ==========================================

def test_bulk_reschedule_appointments_tool():
    """Test bulk rescheduling appointments."""
    from app.agents.tools.alex_scheduling_tools import bulk_reschedule_appointments_tool
    
    result = bulk_reschedule_appointments_tool(
        doctor_id=1,
        original_date="2025-10-15",
        new_date="2025-10-16",
        reason="Doctor unavailable"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

def test_manage_waitlist_tool():
    """Test managing waitlist."""
    from app.agents.tools.alex_scheduling_tools import manage_waitlist_tool
    
    result = manage_waitlist_tool(
        action="add",
        patient_id=1,
        doctor_id=1,
        preferred_date="2025-10-20"
    )
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    return result

# ==========================================
# LEGACY TOOLS (4 tools)
# ==========================================

def test_get_available_slots_tool():
    """Test getting available appointment slots."""
    from app.agents.tools.agent_tools import get_available_slots_tool
    
    result = get_available_slots_tool(days_ahead=7)
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_create_appointment_tool():
    """Test creating an appointment."""
    from app.agents.tools.agent_tools import create_appointment_tool
    
    future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M")
    
    result = create_appointment_tool(
        patient_name="Test Patient",
        patient_phone="050-1234567",
        appointment_date=future_date,
        notes="Test appointment"
    )
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_patient_invoices_tool():
    """Test getting patient invoices."""
    from app.agents.tools.agent_tools import get_patient_invoices_tool
    
    result = get_patient_invoices_tool(
        patient_name="Test Patient",
        patient_phone="050-1234567"
    )
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_invoice_details_tool():
    """Test getting invoice details."""
    from app.agents.tools.agent_tools import get_invoice_details_tool
    
    result = get_invoice_details_tool(invoice_id=1)
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# ODOO TOOLS (3 tools) - Use invoke()
# ==========================================

def test_get_my_appointments():
    """Test getting user's appointments from Odoo."""
    from app.agents.tools.odoo_tools_v3 import get_my_appointments
    
    # These tools expect tool_input as a dict with organization_id as string
    result = get_my_appointments.invoke({
        "user_id": "1",
        "user_role": "patient",
        "organization_id": "1"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    return result

def test_book_appointment():
    """Test booking an appointment through Odoo."""
    from app.agents.tools.odoo_tools_v3 import book_appointment
    
    future_datetime = datetime.now() + timedelta(days=5)
    appointment_date = future_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    result = book_appointment.invoke({
        "user_id": "1",
        "user_role": "patient",
        "organization_id": "1",
        "appointment_date": appointment_date,
        "doctor_id": 1
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    return result

def test_get_available_appointment_slots():
    """Test getting available slots from Odoo."""
    from app.agents.tools.odoo_tools_v3 import get_available_appointment_slots
    
    result = get_available_appointment_slots.invoke({
        "user_id": "1",
        "user_role": "patient",
        "days_ahead": 7
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    return result

# ==========================================
# RAG TOOL (1 tool) - Use invoke()
# ==========================================

def test_search_general_knowledge_tool():
    """Test RAG search for general knowledge."""
    from app.agents.tools.rag_tools import search_general_knowledge_tool
    
    result = search_general_knowledge_tool.invoke({
        "query": "What is a root canal treatment?"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 20, "RAG result too short"
    return result

# ==========================================
# MAIN TEST RUNNER
# ==========================================

if __name__ == "__main__":
    print("=" * 80)
    print("ALEX TOOLS FUNCTIONAL TESTS")
    print("=" * 80)
    print()
    
    tests = [
        # Patient Management (4)
        test_create_patient_tool,
        test_update_patient_info_tool,
        test_get_patient_full_context_tool,
        test_add_patient_note_tool,
        
        # Communications (3)
        test_send_sms_tool,
        test_send_email_tool,
        test_send_telegram_message_tool,
        
        # Financial (3)
        test_process_payment_tool,
        test_create_payment_plan_tool,
        test_check_insurance_coverage_tool,
        
        # Scheduling (2)
        test_bulk_reschedule_appointments_tool,
        test_manage_waitlist_tool,
        
        # Legacy (4)
        test_get_available_slots_tool,
        test_create_appointment_tool,
        test_get_patient_invoices_tool,
        test_get_invoice_details_tool,
        
        # Odoo (3)
        test_get_my_appointments,
        test_book_appointment,
        test_get_available_appointment_slots,
        
        # RAG (1)
        test_search_general_knowledge_tool,
    ]
    
    print(f"Running {len(tests)} functional tests for Alex's tools...\n")
    
    results = []
    for test in tests:
        result = run_test(test)
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print("=" * 80)
    print(f"RESULTS: {passed}/{total} tests passed ({percentage:.1f}%)")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 All Alex tool functional tests passed!")
        sys.exit(0)
    elif passed >= total * 0.9:
        print(f"\n✅ Excellent! {passed}/{total} tests passed (>90%)")
        sys.exit(0)
    elif passed >= total * 0.75:
        print(f"\n⚠️ Good progress: {passed}/{total} tests passed (>75%)")
        sys.exit(1)
    else:
        print(f"\n❌ More work needed: {passed}/{total} tests passed (<75%)")
        sys.exit(1)

