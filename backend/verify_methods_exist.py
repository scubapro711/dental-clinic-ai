#!/usr/bin/env python3
"""
Verify which methods exist in OdooClient vs which are called
"""

import re

# Read OdooClient to get all methods
with open("app/integrations/odoo_client.py", 'r') as f:
    odoo_content = f.read()

# Extract method names from OdooClient
odoo_methods = set(re.findall(r'^\s+def (\w+)\(', odoo_content, re.MULTILINE))

# Methods called by agent tools (from previous analysis)
called_methods = {
    'add_patient_disease', 'cancel_appointment', 'create_appointment', 
    'create_patient', 'create_prescription', 'create_treatment_plan',
    'create_treatment_record', 'get_appointment', 'get_available_slots',
    'get_dental_chart', 'get_dentist_schedule', 'get_doctors',
    'get_financial_summary', 'get_invoices', 'get_outstanding_balance',
    'get_patient', 'get_patient_medical_history', 'get_patient_prescriptions',
    'get_payments', 'get_revenue_by_period', 'get_treatment_history',
    'get_treatment_plans', 'get_treatment_revenue', 'search_appointments',
    'search_diseases', 'search_medications', 'search_patients',
    'update_patient', 'update_tooth_status'
}

print("=" * 80)
print("ODOO CLIENT METHOD VERIFICATION")
print("=" * 80)
print()

# Check which methods exist
existing = called_methods & odoo_methods
missing = called_methods - odoo_methods

print(f"✅ EXISTING METHODS ({len(existing)}/{len(called_methods)}):")
print()
for method in sorted(existing):
    print(f"   ✓ {method}()")
print()

print("=" * 80)
print(f"❌ MISSING METHODS ({len(missing)}/{len(called_methods)}):")
print("=" * 80)
print()
for method in sorted(missing):
    print(f"   ✗ {method}()")
    # Find which files use this method
    import os
    for root, dirs, files in os.walk("app/agents/tools"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    if f"odoo_client.{method}(" in f.read():
                        print(f"      Used in: {filepath}")
print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total methods called: {len(called_methods)}")
print(f"Existing in OdooClient: {len(existing)} ({len(existing)/len(called_methods)*100:.1f}%)")
print(f"Missing from OdooClient: {len(missing)} ({len(missing)/len(called_methods)*100:.1f}%)")
print("=" * 80)
