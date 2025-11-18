#!/usr/bin/env python3
"""
Comprehensive OdooClient Method Analysis
Analyzes all agent tools to find OdooClient method calls
"""

import os
import re
from collections import defaultdict

# Find all tool files
tool_files = []
for root, dirs, files in os.walk("app/agents/tools"):
    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            tool_files.append(os.path.join(root, file))

# Also check agent files
for root, dirs, files in os.walk("app/agents"):
    for file in files:
        if file.endswith(".py") and file not in ["__init__.py", "graph_state.py", "error_handler.py"]:
            if "tools" not in root:  # Skip tools dir (already added)
                tool_files.append(os.path.join(root, file))

# Pattern to match odoo_client method calls
pattern = r'odoo_client\.(\w+)\('

# Store results
method_calls = defaultdict(list)
all_methods = set()

print("=" * 80)
print("COMPREHENSIVE ODOO CLIENT METHOD ANALYSIS")
print("=" * 80)
print()

for file_path in sorted(tool_files):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = re.findall(pattern, content)
        
        if matches:
            unique_methods = set(matches)
            all_methods.update(unique_methods)
            
            for method in unique_methods:
                method_calls[method].append(file_path)
            
            print(f"📄 {file_path}")
            for method in sorted(unique_methods):
                print(f"   ├─ {method}()")
            print()
    
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

print("=" * 80)
print("SUMMARY: ALL UNIQUE ODOO CLIENT METHODS")
print("=" * 80)
print()

for method in sorted(all_methods):
    files = method_calls[method]
    print(f"🔧 {method}()")
    print(f"   Used in {len(files)} file(s):")
    for file_path in files:
        print(f"   ├─ {file_path}")
    print()

print("=" * 80)
print(f"TOTAL: {len(all_methods)} unique methods found")
print("=" * 80)
