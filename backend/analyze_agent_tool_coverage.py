#!/usr/bin/env python3
"""
Comprehensive Agent Tool Coverage Analysis

Analyzes all 5 DentaFlow agents and their tool dependencies:
1. Alex - Patient Experience Agent
2. Sarah - Clinical AI Agent
3. Marcus - Financial Agent (CFO)
4. Sophia - Operations Agent
5. Harper - Compliance Agent (HIPAA)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import json

def extract_tool_calls_from_file(file_path: str) -> Set[str]:
    """Extract all OdooClient method calls from a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find all odoo_client method calls
        pattern = r'odoo_client\.(\w+)\('
        matches = re.findall(pattern, content)
        return set(matches)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return set()

def get_odoo_client_methods() -> Set[str]:
    """Get all methods defined in OdooClient."""
    odoo_client_path = "app/integrations/odoo_client.py"
    try:
        with open(odoo_client_path, 'r') as f:
            content = f.read()
        
        # Find all method definitions
        pattern = r'^\s+def (\w+)\('
        matches = re.findall(pattern, content, re.MULTILINE)
        # Filter out private methods
        return set(m for m in matches if not m.startswith('_'))
    except Exception as e:
        print(f"Error reading OdooClient: {e}")
        return set()

def analyze_agent_tools():
    """Analyze tool usage across all agents."""
    
    print("=" * 80)
    print("COMPREHENSIVE AGENT TOOL COVERAGE ANALYSIS")
    print("=" * 80)
    print()
    
    # Define agent tool files
    agent_files = {
        'Alex (Patient Experience)': [
            'app/agents/tools/alex_odoo_tools.py',
            'app/agents/tools/odoo_tools.py',
            'app/agents/tools/odoo_tools_v3.py'
        ],
        'Sarah (Clinical AI)': [
            'app/agents/tools/clinical_tools.py'
        ],
        'Marcus (Financial CFO)': [
            'app/agents/tools/marcus_financial_tools.py'
        ],
        'Sophia (Operations)': [
            'app/agents/tools/sophia_operations_tools.py'
        ],
        'Harper (HIPAA Compliance)': [
            'app/agents/tools/harper_compliance_tools.py'
        ]
    }
    
    # Get all OdooClient methods
    odoo_methods = get_odoo_client_methods()
    print(f"📊 Total OdooClient Methods: {len(odoo_methods)}")
    print()
    
    # Analyze each agent
    all_used_methods = set()
    agent_analysis = {}
    
    for agent_name, tool_files in agent_files.items():
        print("=" * 80)
        print(f"🤖 {agent_name}")
        print("=" * 80)
        
        agent_methods = set()
        existing_files = []
        missing_files = []
        
        for tool_file in tool_files:
            if os.path.exists(tool_file):
                existing_files.append(tool_file)
                methods = extract_tool_calls_from_file(tool_file)
                agent_methods.update(methods)
                
                if methods:
                    print(f"\n📄 {tool_file}")
                    for method in sorted(methods):
                        status = "✅" if method in odoo_methods else "❌"
                        print(f"   {status} {method}()")
            else:
                missing_files.append(tool_file)
        
        if missing_files:
            print(f"\n⚠️  Missing tool files:")
            for f in missing_files:
                print(f"   - {f}")
        
        all_used_methods.update(agent_methods)
        
        # Calculate coverage
        if agent_methods:
            existing_methods = agent_methods & odoo_methods
            missing_methods = agent_methods - odoo_methods
            coverage = len(existing_methods) / len(agent_methods) * 100
            
            print(f"\n📈 Coverage: {len(existing_methods)}/{len(agent_methods)} ({coverage:.1f}%)")
            
            if missing_methods:
                print(f"\n❌ Missing Methods ({len(missing_methods)}):")
                for method in sorted(missing_methods):
                    print(f"   - {method}()")
        else:
            print("\n⚠️  No OdooClient methods found for this agent")
        
        agent_analysis[agent_name] = {
            'tool_files': existing_files,
            'missing_files': missing_files,
            'methods_used': list(agent_methods),
            'methods_count': len(agent_methods)
        }
        
        print()
    
    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"\n📊 Total Unique Methods Used: {len(all_used_methods)}")
    print(f"📊 Total OdooClient Methods: {len(odoo_methods)}")
    
    existing_methods = all_used_methods & odoo_methods
    missing_methods = all_used_methods - odoo_methods
    unused_methods = odoo_methods - all_used_methods
    
    coverage = len(existing_methods) / len(all_used_methods) * 100 if all_used_methods else 0
    
    print(f"\n✅ Methods Implemented: {len(existing_methods)} ({coverage:.1f}%)")
    print(f"❌ Methods Missing: {len(missing_methods)}")
    print(f"⚠️  Methods Unused: {len(unused_methods)}")
    
    if missing_methods:
        print(f"\n❌ Missing Methods:")
        for method in sorted(missing_methods):
            print(f"   - {method}()")
    
    if unused_methods:
        print(f"\n⚠️  Unused Methods (Implemented but not called by any agent):")
        for method in sorted(unused_methods):
            print(f"   - {method}()")
    
    # Save results
    results = {
        'analysis_time': str(Path(__file__).stat().st_mtime),
        'summary': {
            'total_methods_used': len(all_used_methods),
            'total_odoo_methods': len(odoo_methods),
            'methods_implemented': len(existing_methods),
            'methods_missing': len(missing_methods),
            'methods_unused': len(unused_methods),
            'coverage_percentage': coverage
        },
        'agents': agent_analysis,
        'all_used_methods': sorted(list(all_used_methods)),
        'existing_methods': sorted(list(existing_methods)),
        'missing_methods': sorted(list(missing_methods)),
        'unused_methods': sorted(list(unused_methods))
    }
    
    output_file = '/home/ubuntu/agent_tool_coverage_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print("=" * 80)
    print(f"✅ Detailed results saved to: {output_file}")
    print("=" * 80)

if __name__ == "__main__":
    analyze_agent_tools()
