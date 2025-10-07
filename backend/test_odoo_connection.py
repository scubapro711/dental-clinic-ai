"""
Test Odoo XML-RPC connection and API compatibility.
"""
import xmlrpc.client
import sys

# Configuration
ODOO_URL = "https://dentaflow.ai"
ODOO_DB = "dental_prod"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "DentaFlow2024"

def test_connection():
    """Test basic Odoo connection and authentication."""
    print("=" * 60)
    print("ODOO CONNECTION TEST")
    print("=" * 60)
    print(f"URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print(f"Username: {ODOO_USERNAME}")
    print()
    
    try:
        # Test 1: Version check
        print("Test 1: Checking Odoo version...")
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        version_info = common.version()
        print(f"✓ Connected to Odoo {version_info['server_version']}")
        print(f"  Server version series: {version_info.get('server_version_info', 'N/A')}")
        print()
        
        # Test 2: Authentication
        print("Test 2: Authenticating...")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if uid:
            print(f"✓ Authentication successful (UID: {uid})")
        else:
            print("✗ Authentication failed")
            return False
        print()
        
        # Test 3: Check access rights
        print("Test 3: Checking access rights...")
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        
        # Check if we can access res.partner model
        can_read = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'check_access_rights',
            ['read'], {'raise_exception': False}
        )
        print(f"  res.partner read access: {'✓ Yes' if can_read else '✗ No'}")
        
        can_create = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'check_access_rights',
            ['create'], {'raise_exception': False}
        )
        print(f"  res.partner create access: {'✓ Yes' if can_create else '✗ No'}")
        print()
        
        # Test 4: List available models
        print("Test 4: Searching for dental-related models...")
        all_models = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.model', 'search_read',
            [[]], {'fields': ['model', 'name'], 'limit': 1000}
        )
        
        dental_models = [m for m in all_models if 'dental' in m['model'].lower() or 'patient' in m['model'].lower()]
        if dental_models:
            print(f"  Found {len(dental_models)} dental-related models:")
            for model in dental_models[:10]:
                print(f"    - {model['model']}: {model['name']}")
        else:
            print("  ⚠ No dental-specific models found")
            print("  Note: Using standard res.partner for patient management")
        print()
        
        # Test 5: Test search with domain
        print("Test 5: Testing search with domain filters...")
        try:
            # Search for partners (patients)
            partner_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'search',
                [[['customer_rank', '>', 0]]], {'limit': 5}
            )
            print(f"✓ Domain search successful - found {len(partner_ids)} customers")
            
            if partner_ids:
                # Read one partner to test read operation
                partner = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'read',
                    [partner_ids[:1]], {'fields': ['name', 'email', 'phone']}
                )
                print(f"  Sample customer: {partner[0].get('name', 'N/A')}")
        except Exception as e:
            print(f"✗ Domain search failed: {e}")
        print()
        
        # Test 6: Check installed modules
        print("Test 6: Checking installed modules...")
        modules = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.module.module', 'search_read',
            [[['state', '=', 'installed']]], 
            {'fields': ['name', 'shortdesc'], 'limit': 1000}
        )
        
        dental_modules = [m for m in modules if 'dental' in m['name'].lower() or 'dental' in m.get('shortdesc', '').lower()]
        if dental_modules:
            print(f"  Found {len(dental_modules)} dental modules:")
            for module in dental_modules:
                print(f"    - {module['name']}: {module.get('shortdesc', 'N/A')}")
        else:
            print("  ⚠ No dental modules installed")
        print()
        
        print("=" * 60)
        print("CONNECTION TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
