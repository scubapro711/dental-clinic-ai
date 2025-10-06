"""
Simple test for available agent tools with real Odoo data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.tools.agent_tools import (
    search_patient_tool,
    get_patient_appointments_tool,
    get_patient_invoices_tool,
    get_patient_count_tool,
    get_appointment_count_tool,
)

from app.agents.tools.cfo_tools import (
    get_revenue_report_tool,
    get_outstanding_payments_tool,
)

from app.agents.tools.admin_tools import (
    get_clinic_stats_tool,
)

print("=" * 80)
print("🧪 TESTING AGENT TOOLS WITH REAL ODOO DATA")
print("=" * 80)

# Test 1: Search Patient
print("\n1️⃣  Testing search_patient_tool...")
try:
    result = search_patient_tool(name="Cohen", requesting_user_role="doctor")
    print(f"   ✅ Result: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Get Patient Count
print("\n2️⃣  Testing get_patient_count_tool...")
try:
    result = get_patient_count_tool(requesting_user_role="owner")
    print(f"   ✅ Result: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get Appointment Count
print("\n3️⃣  Testing get_appointment_count_tool...")
try:
    result = get_appointment_count_tool(requesting_user_role="owner")
    print(f"   ✅ Result: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Get Patient Appointments
print("\n4️⃣  Testing get_patient_appointments_tool...")
try:
    result = get_patient_appointments_tool(patient_id=6, requesting_user_role="doctor")
    print(f"   ✅ Result: {result[:150]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Get Patient Invoices
print("\n5️⃣  Testing get_patient_invoices_tool...")
try:
    result = get_patient_invoices_tool(patient_id=6, requesting_user_role="doctor")
    print(f"   ✅ Result: {result[:150]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Get Revenue Report
print("\n6️⃣  Testing get_revenue_report_tool...")
try:
    result = get_revenue_report_tool(
        start_date="2025-01-01",
        end_date="2025-12-31",
        requesting_user_role="owner"
    )
    print(f"   ✅ Result: {result[:150]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 7: Get Outstanding Payments
print("\n7️⃣  Testing get_outstanding_payments_tool...")
try:
    result = get_outstanding_payments_tool(requesting_user_role="owner")
    print(f"   ✅ Result: {result[:150]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 8: Get Clinic Stats
print("\n8️⃣  Testing get_clinic_stats_tool...")
try:
    result = get_clinic_stats_tool(requesting_user_role="owner")
    print(f"   ✅ Result: {result[:150]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ TOOL TESTS COMPLETE")
print("=" * 80)
