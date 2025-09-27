#!/usr/bin/env python3
"""
Debug script for DemoDataAdapter
"""

import sys
import os
import pymysql

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_agents.tools.demo_data_adapter import DemoDataAdapter

def test_adapter_directly():
    """Test the adapter directly"""
    print("🔍 Testing DemoDataAdapter Directly")
    print("=" * 40)
    
    db_config = {
        'host': 'localhost',
        'user': 'dental_user',
        'password': 'dental_pass_2025',
        'database': 'dental_clinic_demo',
        'port': 3306,
        'charset': 'utf8mb4',
    }
    
    adapter = DemoDataAdapter(db_config)
    
    try:
        print("1. Connecting to database...")
        adapter.connect()
        print("✅ Connected successfully")
        
        print("\n2. Testing get_providers...")
        try:
            providers = adapter.get_providers()
            print(f"✅ Found {len(providers)} providers:")
            for provider in providers:
                print(f"   - {provider}")
        except Exception as e:
            print(f"❌ Error in get_providers: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n3. Testing search_patients...")
        try:
            patients = adapter.search_patients("Yossi")
            print(f"✅ Found {len(patients)} patients:")
            for patient in patients:
                print(f"   - {patient}")
        except Exception as e:
            print(f"❌ Error in search_patients: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n4. Testing direct SQL query...")
        try:
            with adapter.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM doctors LIMIT 2")
                doctors = cursor.fetchall()
                print(f"✅ Direct query found {len(doctors)} doctors:")
                for doctor in doctors:
                    print(f"   - {doctor}")
        except Exception as e:
            print(f"❌ Error in direct query: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        adapter.disconnect()
        print("✅ Disconnected")

if __name__ == "__main__":
    test_adapter_directly()
