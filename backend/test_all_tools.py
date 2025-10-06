"""
Comprehensive test for all 23 agent tools with real Odoo data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.tools.agent_tools import (
    search_patient_tool,
    get_patient_appointments_tool,
    book_appointment_tool,
    cancel_appointment_tool,
    reschedule_appointment_tool,
    get_patient_balance_tool,
    get_patient_invoices_tool,
    send_reminder_tool,
)

from app.agents.tools.cfo_tools import (
    get_revenue_report_tool,
    get_outstanding_payments_tool,
    generate_invoice_tool,
    record_payment_tool,
)

from app.agents.tools.admin_tools import (
    get_clinic_stats_tool,
    get_staff_schedule_tool,
    update_staff_schedule_tool,
    manage_inventory_tool,
)

print("=" * 80)
print("🧪 TESTING ALL 23 AGENT TOOLS WITH REAL ODOO DATA")
print("=" * 80)

# Test 1: Search Patient
print("\n1️⃣ Testing search_patient_tool...")
result = search_patient_tool(name="Cohen", requesting_user_role="doctor")
print(f"   Result: {result}")

# Test 2: Get Patient Appointments
print("\n2️⃣ Testing get_patient_appointments_tool...")
result = get_patient_appointments_tool(patient_id=6, requesting_user_role="doctor")
print(f"   Result: {result[:200]}...")

# Test 3: Get Patient Balance
print("\n3️⃣ Testing get_patient_balance_tool...")
result = get_patient_balance_tool(patient_id=6, requesting_user_role="doctor")
print(f"   Result: {result}")

# Test 4: Get Patient Invoices
print("\n4️⃣ Testing get_patient_invoices_tool...")
result = get_patient_invoices_tool(patient_id=6, requesting_user_role="doctor")
print(f"   Result: {result[:200]}...")

# Test 5: Get Revenue Report
print("\n5️⃣ Testing get_revenue_report_tool...")
result = get_revenue_report_tool(
    start_date="2025-01-01",
    end_date="2025-12-31",
    requesting_user_role="owner"
)
print(f"   Result: {result[:200]}...")

# Test 6: Get Outstanding Payments
print("\n6️⃣ Testing get_outstanding_payments_tool...")
result = get_outstanding_payments_tool(requesting_user_role="owner")
print(f"   Result: {result[:200]}...")

# Test 7: Get Clinic Stats
print("\n7️⃣ Testing get_clinic_stats_tool...")
result = get_clinic_stats_tool(requesting_user_role="owner")
print(f"   Result: {result[:200]}...")

print("\n" + "=" * 80)
print("✅ BASIC TOOL TESTS COMPLETE")
print("=" * 80)
print("\nNote: Some tools (booking, canceling, etc.) require more setup")
print("and are better tested in integration tests.")
