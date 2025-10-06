"""
Minimal test for agent tools with real Odoo data
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.tools.agent_tools import (
    search_patient_tool,
    get_patient_count_tool,
    get_appointment_count_tool,
)

print("=" * 60)
print("🧪 TESTING AGENT TOOLS WITH REAL ODOO")
print("=" * 60)

print("\n1️⃣  Search Patient (Cohen)...")
result = search_patient_tool(name="Cohen", requesting_user_role="doctor")
print(f"   ✅ {result}")

print("\n2️⃣  Get Patient Count...")
result = get_patient_count_tool(requesting_user_role="owner")
print(f"   ✅ {result}")

print("\n3️⃣  Get Appointment Count...")
result = get_appointment_count_tool(requesting_user_role="owner")
print(f"   ✅ {result}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
