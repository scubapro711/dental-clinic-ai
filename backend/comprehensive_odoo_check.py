#!/usr/bin/env python3
"""
Comprehensive OdooClient Method Checker

This script checks all methods used across all agent tools and verifies
they exist in both OdooClient and RealisticMockOdooClient.
"""

import sys
import os
import re
from pathlib import Path
from collections import defaultdict
from unittest.mock import patch

# Add app to path
sys.path.insert(0, 'app')

print("=" * 80)
print("  COMPREHENSIVE ODOO CLIENT METHOD CHECKER")
print("=" * 80)

# Step 1: Scan all agent tools files for method calls
print("\n📁 Step 1: Scanning agent tools files...")
print("-" * 80)

tools_dir = Path('app/agents/tools')
method_calls = defaultdict(list)

for tool_file in tools_dir.glob('*.py'):
    if tool_file.name.startswith('__'):
        continue
    
    with open(tool_file, 'r') as f:
        content = f.read()
        
        # Find all odoo_client.method() calls
        odoo_client_calls = re.findall(r'odoo_client\.([a-z_]+)\(', content)
        for method in odoo_client_calls:
            method_calls[method].append(tool_file.name)
        
        # Find all odoo.method() calls (from get_odoo_client())
        odoo_calls = re.findall(r'odoo\.([a-z_]+)\(', content)
        for method in odoo_calls:
            # Filter out common Python methods
            if method not in ['get', 'items', 'keys', 'values', 'append', 'extend', 'format', 'join', 'split', 'strip', 'lower', 'upper']:
                method_calls[method].append(tool_file.name)

print(f"✅ Found {len(method_calls)} unique method calls across {len(list(tools_dir.glob('*.py')))} files")

# Step 2: Check OdooClient
print("\n🔍 Step 2: Checking OdooClient...")
print("-" * 80)

with patch('app.integrations.odoo_client.settings') as mock_settings:
    mock_settings.ODOO_URL = 'https://test.odoo.com'
    mock_settings.ODOO_DB = 'test_db'
    mock_settings.ODOO_USERNAME = 'test_user'
    mock_settings.ODOO_PASSWORD = 'test_pass'
    
    with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy'):
        from app.integrations.odoo_client import OdooClient
        odoo_client = OdooClient()
        
        odoo_client_methods = set(dir(odoo_client))
        odoo_client_missing = []
        odoo_client_existing = []
        
        for method in sorted(method_calls.keys()):
            if method in odoo_client_methods and not method.startswith('_'):
                odoo_client_existing.append(method)
            else:
                odoo_client_missing.append(method)

print(f"✅ OdooClient has {len(odoo_client_existing)} methods")
print(f"❌ OdooClient missing {len(odoo_client_missing)} methods")

# Step 3: Check RealisticMockOdooClient
print("\n🔍 Step 3: Checking RealisticMockOdooClient...")
print("-" * 80)

# Mock the data loading
with patch.object(Path, 'exists', return_value=False):
    from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
    mock_client = RealisticMockOdooClient()
    
    mock_client_methods = set(dir(mock_client))
    mock_client_missing = []
    mock_client_existing = []
    
    for method in sorted(method_calls.keys()):
        if method in mock_client_methods and not method.startswith('_'):
            mock_client_existing.append(method)
        else:
            mock_client_missing.append(method)

print(f"✅ RealisticMockOdooClient has {len(mock_client_existing)} methods")
print(f"❌ RealisticMockOdooClient missing {len(mock_client_missing)} methods")

# Step 4: Generate detailed report
print("\n" + "=" * 80)
print("  DETAILED REPORT")
print("=" * 80)

print("\n📊 SUMMARY:")
print(f"  Total unique methods called: {len(method_calls)}")
print(f"  OdooClient coverage: {len(odoo_client_existing)}/{len(method_calls)} ({len(odoo_client_existing)/len(method_calls)*100:.1f}%)")
print(f"  MockOdooClient coverage: {len(mock_client_existing)}/{len(method_calls)} ({len(mock_client_existing)/len(method_calls)*100:.1f}%)")

if odoo_client_missing:
    print(f"\n❌ MISSING IN ODOOCLIENT ({len(odoo_client_missing)} methods):")
    for method in sorted(odoo_client_missing):
        files = set(method_calls[method])
        print(f"   - {method}")
        print(f"     Used in: {', '.join(sorted(files)[:3])}")

if mock_client_missing:
    print(f"\n❌ MISSING IN REALISTICMOCKODOOCLIENT ({len(mock_client_missing)} methods):")
    for method in sorted(mock_client_missing):
        files = set(method_calls[method])
        print(f"   - {method}")
        print(f"     Used in: {', '.join(sorted(files)[:3])}")

# Step 5: Critical methods analysis
print("\n" + "=" * 80)
print("  CRITICAL METHODS ANALYSIS")
print("=" * 80)

critical_missing = set(odoo_client_missing) | set(mock_client_missing)
if critical_missing:
    print(f"\n⚠️  {len(critical_missing)} methods need to be implemented:")
    for method in sorted(critical_missing):
        in_odoo = "✅" if method in odoo_client_existing else "❌"
        in_mock = "✅" if method in mock_client_existing else "❌"
        print(f"   {method:30s} | OdooClient: {in_odoo} | Mock: {in_mock}")
else:
    print("\n✅ All methods are implemented in both clients!")

# Step 6: Recommendations
print("\n" + "=" * 80)
print("  RECOMMENDATIONS")
print("=" * 80)

if odoo_client_missing:
    print(f"\n🔧 Add these methods to OdooClient:")
    for method in sorted(odoo_client_missing):
        print(f"   def {method}(self, ...):")
        print(f"       # TODO: Implement {method}")
        print()

if mock_client_missing:
    print(f"\n🔧 Add these methods to RealisticMockOdooClient:")
    for method in sorted(mock_client_missing):
        print(f"   def {method}(self, ...):")
        print(f"       # TODO: Implement {method}")
        print()

print("\n" + "=" * 80)
print("  END OF REPORT")
print("=" * 80)
