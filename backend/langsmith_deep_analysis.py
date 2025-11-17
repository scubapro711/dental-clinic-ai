#!/usr/bin/env python3
"""
LangSmith Deep Analysis - Find ALL Missing Methods

This script uses LangSmith API to analyze all traces and identify
exactly which methods are missing from OdooClient.
"""

import os
from datetime import datetime, timedelta
from collections import defaultdict
import re

# LANGSMITH_API_KEY should be set in environment variables

from langsmith import Client

print("=" * 80)
print("  LANGSMITH DEEP ANALYSIS - MISSING METHODS DETECTOR")
print("=" * 80)

client = Client()
project_name = "dentaflow-agent-eval"

print(f"\n🔍 Fetching traces from project: {project_name}")
print("-" * 80)

# Get all runs from the last 24 hours
runs = list(client.list_runs(
    project_name=project_name,
    start_time=datetime.now() - timedelta(hours=24),
    limit=100
))

print(f"✅ Found {len(runs)} total runs\n")

# Analyze errors
errors_by_type = defaultdict(list)
missing_methods = defaultdict(list)
all_errors = []

for run in runs:
    if run.error:
        error_msg = str(run.error)
        all_errors.append({
            'name': run.name,
            'error': error_msg,
            'run_id': run.id
        })
        
        # Extract AttributeError for missing methods
        if 'AttributeError' in error_msg:
            # Pattern: 'OdooClient' object has no attribute 'method_name'
            match = re.search(r"has no attribute '([^']+)'", error_msg)
            if match:
                method_name = match.group(1)
                missing_methods[method_name].append(run.name)
        
        # Extract other error types
        if 'TypeError' in error_msg:
            match = re.search(r"got an unexpected keyword argument '([^']+)'", error_msg)
            if match:
                param_name = match.group(1)
                errors_by_type['unexpected_param'].append({
                    'param': param_name,
                    'test': run.name
                })
        
        # SSL errors
        if 'SSL' in error_msg or 'CERTIFICATE' in error_msg:
            errors_by_type['ssl'].append(run.name)

# Report
print("=" * 80)
print("  ANALYSIS RESULTS")
print("=" * 80)

if missing_methods:
    print(f"\n❌ MISSING METHODS ({len(missing_methods)} unique):")
    print("-" * 80)
    for method, tests in sorted(missing_methods.items()):
        print(f"\n  Method: {method}")
        print(f"  Failed in {len(tests)} test(s):")
        for test in sorted(set(tests)):
            print(f"    - {test}")

if errors_by_type.get('unexpected_param'):
    print(f"\n⚠️  UNEXPECTED PARAMETERS:")
    print("-" * 80)
    for error in errors_by_type['unexpected_param']:
        print(f"  Parameter '{error['param']}' in test: {error['test']}")

if errors_by_type.get('ssl'):
    print(f"\n🔒 SSL ERRORS ({len(errors_by_type['ssl'])} tests):")
    print("-" * 80)
    for test in sorted(set(errors_by_type['ssl'])):
        print(f"  - {test}")

# Summary
print("\n" + "=" * 80)
print("  SUMMARY")
print("=" * 80)
print(f"\n  Total runs analyzed: {len(runs)}")
print(f"  Runs with errors: {len(all_errors)}")
print(f"  Missing methods: {len(missing_methods)}")
print(f"  SSL errors: {len(errors_by_type.get('ssl', []))}")
print(f"  Parameter errors: {len(errors_by_type.get('unexpected_param', []))}")

# Action items
print("\n" + "=" * 80)
print("  ACTION ITEMS")
print("=" * 80)

if missing_methods:
    print(f"\n✅ Add these {len(missing_methods)} methods to OdooClient:")
    for method in sorted(missing_methods.keys()):
        print(f"   - {method}()")

if errors_by_type.get('unexpected_param'):
    print(f"\n✅ Fix these parameter mismatches:")
    seen = set()
    for error in errors_by_type['unexpected_param']:
        key = error['param']
        if key not in seen:
            print(f"   - Add '{key}' parameter support")
            seen.add(key)

if errors_by_type.get('ssl'):
    print(f"\n⚠️  SSL certificate issue - not related to methods")

print("\n" + "=" * 80)
print("  DETAILED ERROR LOG")
print("=" * 80)

for i, error in enumerate(all_errors[:10], 1):  # Show first 10
    print(f"\n{i}. Test: {error['name']}")
    print(f"   Error: {error['error'][:200]}...")

print("\n" + "=" * 80)
