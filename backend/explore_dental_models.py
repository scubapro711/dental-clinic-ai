"""
Explore Odoo dental models structure and fields.
"""
import xmlrpc.client
import json

# Configuration
ODOO_URL = "https://dentaflow.ai"
ODOO_DB = "dental_prod"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "DentaFlow2024"

def explore_models():
    """Explore dental models and their fields."""
    print("=" * 80)
    print("ODOO DENTAL MODELS EXPLORATION")
    print("=" * 80)
    
    # Connect
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    
    # Key models to explore
    key_models = [
        'res.partner',  # Patients
        'dental.insurance.claim.management',  # Claims
        'dental.health.fund',  # Health funds
        'medical.patient.disease',  # Patient diseases
        'patient.birthday.alert',  # Birthday alerts
    ]
    
    for model_name in key_models:
        print(f"\n{'='*80}")
        print(f"MODEL: {model_name}")
        print('='*80)
        
        try:
            # Get model fields
            fields_info = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                model_name, 'fields_get',
                [], {'attributes': ['string', 'type', 'required', 'readonly']}
            )
            
            print(f"\nTotal fields: {len(fields_info)}")
            print("\nKey fields:")
            
            # Sort and display important fields
            important_fields = {}
            for field_name, field_info in fields_info.items():
                if field_info.get('required') or field_name in ['name', 'id', 'state', 'date', 'patient_id', 'partner_id']:
                    important_fields[field_name] = field_info
            
            for field_name, field_info in sorted(important_fields.items()):
                req = " [REQUIRED]" if field_info.get('required') else ""
                ro = " [READONLY]" if field_info.get('readonly') else ""
                print(f"  - {field_name}: {field_info.get('string', 'N/A')} ({field_info.get('type', 'N/A')}){req}{ro}")
            
            # Try to get sample records
            print(f"\nSample records:")
            record_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                model_name, 'search',
                [[]], {'limit': 3}
            )
            
            if record_ids:
                print(f"  Found {len(record_ids)} sample records")
                # Get first record details
                sample_fields = ['id', 'name'] if 'name' in fields_info else ['id']
                if 'display_name' in fields_info:
                    sample_fields.append('display_name')
                
                records = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    model_name, 'read',
                    [record_ids[:1]], {'fields': sample_fields}
                )
                if records:
                    print(f"  Sample: {records[0]}")
            else:
                print("  No records found")
                
        except Exception as e:
            print(f"  Error exploring {model_name}: {e}")
    
    # Check for appointment-related models
    print(f"\n{'='*80}")
    print("SEARCHING FOR APPOINTMENT MODELS")
    print('='*80)
    
    all_models = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.model', 'search_read',
        [[]], {'fields': ['model', 'name'], 'limit': 1000}
    )
    
    appointment_models = [m for m in all_models if 'appointment' in m['model'].lower() or 'calendar' in m['model'].lower()]
    print(f"\nFound {len(appointment_models)} appointment/calendar models:")
    for model in appointment_models[:15]:
        print(f"  - {model['model']}: {model['name']}")
    
    print("\n" + "="*80)
    print("EXPLORATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    explore_models()
