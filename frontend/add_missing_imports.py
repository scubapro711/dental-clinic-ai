#!/usr/bin/env python3
"""
Professional script to add missing API_CONFIG imports.

This script:
1. Finds all files that use API_CONFIG
2. Checks if they have the import statement
3. Adds the import in the correct location
4. Validates the changes
"""

import os
import re
from pathlib import Path

# Import statement to add
IMPORT_STATEMENT = "import API_CONFIG from '@/config/api';"

def has_api_config_import(content):
    """Check if file already has API_CONFIG import."""
    patterns = [
        r"import\s+API_CONFIG\s+from\s+['\"]@/config/api['\"]",
        r"import\s+\{[^}]*API_CONFIG[^}]*\}\s+from\s+['\"]@/config/api['\"]",
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False

def uses_api_config(content):
    """Check if file uses API_CONFIG."""
    # Look for API_CONFIG usage (but not in import statements)
    pattern = r'(?<!import\s)(?<!from\s[\'"])API_CONFIG'
    return bool(re.search(pattern, content))

def find_import_insert_position(content):
    """Find the best position to insert the import statement."""
    lines = content.split('\n')
    
    # Strategy 1: After the last import statement
    last_import_line = -1
    for i, line in enumerate(lines):
        # Match various import patterns
        if re.match(r'^\s*import\s+', line):
            last_import_line = i
    
    if last_import_line >= 0:
        # Insert after the last import
        return last_import_line + 1
    
    # Strategy 2: After any leading comments/docstrings
    insert_line = 0
    in_multiline_comment = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines at the start
        if not stripped and insert_line == i:
            insert_line = i + 1
            continue
        
        # Skip single-line comments
        if stripped.startswith('//'):
            insert_line = i + 1
            continue
        
        # Handle multi-line comments
        if '/*' in stripped:
            in_multiline_comment = True
        if '*/' in stripped:
            in_multiline_comment = False
            insert_line = i + 1
            continue
        
        if in_multiline_comment:
            continue
        
        # Found first non-comment line
        break
    
    return insert_line

def add_import_to_file(file_path):
    """Add API_CONFIG import to a file if needed."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if import is needed
    if not uses_api_config(content):
        return False, "Does not use API_CONFIG"
    
    if has_api_config_import(content):
        return False, "Already has import"
    
    # Find insert position
    lines = content.split('\n')
    insert_pos = find_import_insert_position(content)
    
    # Insert the import
    lines.insert(insert_pos, IMPORT_STATEMENT)
    
    # Write back
    new_content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"Added import at line {insert_pos + 1}"

def main():
    """Main function."""
    src_dir = Path('src')
    
    # Find all JS/JSX/TS/TSX files
    files_to_check = []
    for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
        files_to_check.extend(src_dir.rglob(ext))
    
    # Exclude the config file itself
    files_to_check = [f for f in files_to_check if 'config/api' not in str(f)]
    
    print(f"Checking {len(files_to_check)} files...")
    print()
    
    fixed_files = []
    skipped_files = []
    
    for file_path in sorted(files_to_check):
        modified, reason = add_import_to_file(file_path)
        
        if modified:
            fixed_files.append(file_path)
            print(f"✅ Fixed: {file_path}")
        elif "Does not use" not in reason:
            skipped_files.append((file_path, reason))
    
    print()
    print(f"{'='*70}")
    print(f"Fixed {len(fixed_files)} files")
    print(f"Skipped {len(skipped_files)} files (already have import)")
    print(f"{'='*70}")
    
    if skipped_files:
        print()
        print("Skipped files:")
        for file_path, reason in skipped_files:
            print(f"  - {file_path}: {reason}")
    
    # Verify no files are missing imports
    print()
    print("Verifying...")
    missing_imports = []
    
    for file_path in files_to_check:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if uses_api_config(content) and not has_api_config_import(content):
            missing_imports.append(file_path)
    
    if missing_imports:
        print(f"⚠️  Still missing imports in {len(missing_imports)} files:")
        for file_path in missing_imports:
            print(f"  - {file_path}")
    else:
        print("✅ All files have correct imports!")

if __name__ == '__main__':
    main()
