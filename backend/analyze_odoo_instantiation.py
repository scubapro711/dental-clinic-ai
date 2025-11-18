import os
import re

# Find all Python files that instantiate OdooClient
files_to_check = []
for root, dirs, files in os.walk("app"):
    # Skip test directories for now
    if "test" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
                if "OdooClient()" in content:
                    files_to_check.append(filepath)

print(f"Found {len(files_to_check)} production files using OdooClient\n")

# Analyze each file
patterns = {
    "global_singleton": 0,
    "function_local": 0,
    "class_attribute": 0,
    "other": 0
}

for filepath in files_to_check:
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if "OdooClient()" in line:
                # Check context
                if i > 0:
                    prev_lines = '\n'.join(lines[max(0, i-5):i])
                    
                    # Global singleton pattern
                    if re.search(r'^(odoo_client|client)\s*=\s*OdooClient\(\)', line.strip()):
                        if not any(keyword in prev_lines for keyword in ['def ', 'class ']):
                            patterns["global_singleton"] += 1
                            print(f"✅ Global Singleton: {filepath}:{i+1}")
                        else:
                            patterns["function_local"] += 1
                            print(f"⚠️  Function Local: {filepath}:{i+1}")
                    elif 'self.' in line:
                        patterns["class_attribute"] += 1
                        print(f"📦 Class Attribute: {filepath}:{i+1}")
                    else:
                        patterns["other"] += 1
                        print(f"❓ Other: {filepath}:{i+1}")

print(f"\n{'='*60}")
print("SUMMARY:")
print(f"{'='*60}")
for pattern, count in patterns.items():
    print(f"{pattern}: {count}")
