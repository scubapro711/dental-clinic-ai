#!/usr/bin/env python3
"""
Odoo Dental Models Discovery Script

This script connects to Odoo and discovers all dental-related models,
their fields, relationships, and constraints.

Usage:
    python discover_odoo_models.py
"""

import json
from app.integrations.odoo_client_v2 import OdooClientV2


def discover_model(odoo: OdooClientV2, model_name: str) -> dict:
    """
    Discover a single Odoo model.
    
    Args:
        odoo: OdooClientV2 instance
        model_name: Name of the model to discover
    
    Returns:
        Dictionary with model information
    """
    print(f"\n{'='*80}")
    print(f"Discovering: {model_name}")
    print(f"{'='*80}\n")
    
    try:
        # Get fields
        fields = odoo._execute(model_name, 'fields_get', [], {
            'attributes': ['string', 'type', 'required', 'readonly', 'help', 'relation']
        })
        
        print(f"✅ Found {len(fields)} fields\n")
        
        # Get sample records
        try:
            records = odoo._execute(model_name, 'search_read', [[]], {
                'limit': 3,
                'fields': list(fields.keys())[:10]  # First 10 fields only
            })
            print(f"✅ Found {len(records)} sample records\n")
        except Exception as e:
            print(f"⚠️ Could not fetch sample records: {e}\n")
            records = []
        
        return {
            "model": model_name,
            "fields": fields,
            "sample_records": records,
            "field_count": len(fields),
            "record_count": len(records)
        }
    
    except Exception as e:
        print(f"❌ Error discovering {model_name}: {e}\n")
        return {
            "model": model_name,
            "error": str(e)
        }


def main():
    """Main discovery function"""
    
    print("\n" + "="*80)
    print("ODOO DENTAL MODELS DISCOVERY")
    print("="*80 + "\n")
    
    # Initialize Odoo client
    odoo = OdooClientV2()
    
    # Test connection
    print("Testing Odoo connection...")
    try:
        version = odoo._execute('ir.module.module', 'search_read', 
                                     [[('name', '=', 'base')]], 
                                     {'fields': ['name'], 'limit': 1})
        print(f"✅ Connected to Odoo successfully!\n")
    except Exception as e:
        print(f"❌ Failed to connect to Odoo: {e}\n")
        return
    
    # Models to discover
    models_to_discover = [
        # Clinical Models
        'patient.patient',
        'patient.patient.disease',
        'patient.patient.medication',
        'patient.appointment',
        
        # Dental-specific Models
        'dental.treatment.plan',
        'dental.chart',
        'dental.tooth',
        'dental.treatment',
        'dental.procedure',
        
        # Insurance Models
        'dental.insurance.claim',
        'dental.insurance.provider',
        'dental.insurance.claim.management',
        
        # Financial Models
        'account.move',  # Invoices
        'account.payment',
        'product.product',  # Treatments as products
        
        # Patient Management
        'res.partner',  # Patients
        'calendar.event',  # Appointments
    ]
    
    # Discover all models
    results = {}
    for model_name in models_to_discover:
        result = discover_model(odoo, model_name)
        results[model_name] = result
        
        # Print summary
        if 'error' not in result:
            print(f"Summary for {model_name}:")
            print(f"  - Fields: {result['field_count']}")
            print(f"  - Sample records: {result['record_count']}")
            
            # Print key fields
            print(f"\n  Key fields:")
            for field_name, field_info in list(result['fields'].items())[:10]:
                field_type = field_info.get('type', 'unknown')
                field_label = field_info.get('string', field_name)
                required = '(required)' if field_info.get('required') else ''
                print(f"    - {field_name}: {field_label} [{field_type}] {required}")
            
            if result['field_count'] > 10:
                print(f"    ... and {result['field_count'] - 10} more fields")
    
    # Save results to file
    output_file = '/home/ubuntu/ODOO_MODELS_DISCOVERY.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Discovery complete! Results saved to: {output_file}")
    print(f"{'='*80}\n")
    
    # Print summary
    print("\n📊 SUMMARY\n")
    print(f"{'Model':<50} {'Status':<15} {'Fields':<10} {'Records':<10}")
    print("-" * 85)
    
    for model_name, result in results.items():
        if 'error' in result:
            status = "❌ Error"
            fields = "-"
            records = "-"
        else:
            status = "✅ Success"
            fields = str(result['field_count'])
            records = str(result['record_count'])
        
        print(f"{model_name:<50} {status:<15} {fields:<10} {records:<10}")
    
    print("\n" + "="*80)
    print("Next steps:")
    print("1. Review ODOO_MODELS_DISCOVERY.json")
    print("2. Identify which models exist and which don't")
    print("3. Update MASTER_PLAN_FINAL_V2.md with accurate model info")
    print("4. Create Clinical Tools based on actual models")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

