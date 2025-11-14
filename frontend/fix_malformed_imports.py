#!/usr/bin/env python3
"""
Fix malformed imports where API_CONFIG import was inserted inside another import block.
"""

import re
from pathlib import Path

def fix_malformed_import(file_path):
    """Fix malformed import in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: import {\nimport API_CONFIG from '@/config/api';\n
    # Should be: } from '...';\nimport API_CONFIG from '@/config/api';\nimport {
    
    # Find the malformed pattern
    pattern = r"(import\s+\{)\s*\nimport\s+API_CONFIG\s+from\s+'@/config/api';\s*\n"
    
    if re.search(pattern, content):
        # Find the previous import's closing
        # We need to move API_CONFIG import after the closing }
        
        # Strategy: Find "} from '...';\nimport {\nimport API_CONFIG"
        # Replace with: "} from '...';\nimport API_CONFIG from '@/config/api';\nimport {"
        
        fixed_pattern = r"(\}\s+from\s+['\"][^'\"]+['\"];)\s*\nimport\s+\{\s*\nimport\s+API_CONFIG\s+from\s+'@/config/api';\s*\n"
        replacement = r"\1\nimport API_CONFIG from '@/config/api';\nimport {\n"
        
        new_content = re.sub(fixed_pattern, replacement, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    
    return False

def main():
    """Main function."""
    files_to_check = [
        'src/pages/super-admin/CostDashboard.jsx',
        'src/pages/super-admin/HIPAACompliance.jsx',
        'src/pages/super-admin/OrganizationsPage.jsx',
        'src/pages/super-admin/RevenueDashboard.jsx',
    ]
    
    fixed_count = 0
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            if fix_malformed_import(path):
                print(f"✅ Fixed: {file_path}")
                fixed_count += 1
            else:
                print(f"⚠️  No malformed import found: {file_path}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
