"""Check which methods exist in OdooClient."""
import sys
sys.path.insert(0, 'app')

from unittest.mock import patch

# Methods being called in agent tools
required_methods = [
    'add_patient_disease',
    'cancel_appointment',
    'create_appointment',
    'create_patient',
    'create_prescription',
    'create_treatment_plan',
    'create_treatment_record',
    'get_appointment',
    'get_available_slots',
    'get_dental_chart',
    'get_dentist_schedule',
    'get_doctors',
    'get_financial_summary',
    'get_invoices',
    'get_outstanding_balance',
    'get_patient',
    'get_patient_medical_history',
    'get_patient_prescriptions',
    'get_payments',
    'get_revenue_by_period',
    'get_treatment_history',
    'get_treatment_plans',
    'get_treatment_revenue',
    'search_appointments',
    'search_diseases',
    'search_medications',
    'search_patients',
    'update_patient',
    'update_tooth_status',
]

with patch('app.integrations.odoo_client.settings') as mock_settings:
    mock_settings.ODOO_URL = 'https://test.odoo.com'
    mock_settings.ODOO_DB = 'test_db'
    mock_settings.ODOO_USERNAME = 'test_user'
    mock_settings.ODOO_PASSWORD = 'test_pass'
    
    with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy'):
        from app.integrations.odoo_client import OdooClient
        client = OdooClient()
        
        print("🔍 Checking OdooClient methods:\n")
        missing = []
        existing = []
        
        for method in sorted(required_methods):
            if hasattr(client, method):
                existing.append(method)
                print(f"✅ {method}")
            else:
                missing.append(method)
                print(f"❌ {method} - MISSING!")
        
        print(f"\n📊 Summary:")
        print(f"✅ Existing: {len(existing)}/{len(required_methods)}")
        print(f"❌ Missing: {len(missing)}/{len(required_methods)}")
        
        if missing:
            print(f"\n⚠️  Missing methods:")
            for m in missing:
                print(f"   - {m}")
