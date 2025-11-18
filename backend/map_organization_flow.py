"""
Map how organization_id flows from API to agents to OdooClient.
"""
import os
import re
import ast
from collections import defaultdict

print("="*80)
print("ORGANIZATION_ID FLOW MAPPING")
print("="*80)

# Step 1: Find all functions that accept organization_id parameter
functions_with_org_id = []

for root, dirs, files in os.walk("app"):
    if "test" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check if function has organization_id parameter
                            for arg in node.args.args:
                                if 'organization' in arg.arg.lower():
                                    functions_with_org_id.append({
                                        'file': filepath,
                                        'function': node.name,
                                        'param': arg.arg,
                                        'line': node.lineno
                                    })
                                    break
            except Exception as e:
                pass

print(f"\n✅ Found {len(functions_with_org_id)} functions with organization_id parameter\n")

# Group by file
by_file = defaultdict(list)
for func in functions_with_org_id:
    by_file[func['file']].append(func)

# Print by category
categories = {
    'API Endpoints': 'app/api',
    'Agent Tools': 'app/agents/tools',
    'Agent Core': 'app/agents',
    'Services': 'app/services',
    'Models': 'app/models',
    'Other': ''
}

for category, path_prefix in categories.items():
    matching = [f for f in functions_with_org_id if path_prefix in f['file']]
    if matching:
        print(f"\n{'='*60}")
        print(f"{category} ({len(matching)} functions)")
        print(f"{'='*60}")
        for func in matching[:10]:  # Show first 10
            print(f"  {func['function']}() in {func['file'].replace('app/', '')}:{func['line']}")
        if len(matching) > 10:
            print(f"  ... and {len(matching) - 10} more")

# Step 2: Check AgentState
print(f"\n{'='*80}")
print("AGENT STATE ANALYSIS")
print(f"{'='*80}")

try:
    with open('app/agents/graph_state.py', 'r') as f:
        content = f.read()
        if 'organization_id' in content:
            print("✅ AgentState includes organization_id")
        else:
            print("❌ AgentState does NOT include organization_id")
except:
    print("⚠️  Could not read graph_state.py")

# Step 3: Check how agent tools are called
print(f"\n{'='*80}")
print("AGENT TOOL INVOCATION ANALYSIS")
print(f"{'='*80}")

# Check if tools receive state
tool_files = [
    'app/agents/tools/alex_odoo_tools.py',
    'app/agents/tools/sarah_advanced_clinical_tools.py',
    'app/agents/tools/marcus_financial_tools.py',
    'app/agents/tools/sophia_staff_tools.py'
]

for tool_file in tool_files:
    if os.path.exists(tool_file):
        with open(tool_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Find function definitions
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and '(' in line:
                    func_name = line.split('def ')[1].split('(')[0]
                    # Check if function signature includes organization or state
                    func_def = line
                    if 'organization' in func_def.lower() or 'state' in func_def.lower():
                        print(f"  ✅ {tool_file.split('/')[-1]}: {func_name}() has org context")
                        break
            else:
                print(f"  ❌ {tool_file.split('/')[-1]}: No functions with org context found")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"Total functions with organization_id: {len(functions_with_org_id)}")
print(f"API endpoints: {len([f for f in functions_with_org_id if 'app/api' in f['file']])}")
print(f"Agent tools: {len([f for f in functions_with_org_id if 'app/agents/tools' in f['file']])}")
print(f"Services: {len([f for f in functions_with_org_id if 'app/services' in f['file']])}")
print(f"\n⚠️  Functions WITHOUT organization_id that use OdooClient: ~74")
print(f"📋 Gap: Need to add organization_id to these functions")

