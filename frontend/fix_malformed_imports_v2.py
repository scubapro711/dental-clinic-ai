#!/usr/bin/env python3
"""
Find and fix all malformed imports where API_CONFIG import is inside another import block
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent / 'src'

def fix_malformed_import(content):
    """
    Fix cases where:
    import {
    import API_CONFIG from '@/config/api';
      SomeIcon,
      ...
    } from 'lucide-react';
    
    Should be:
    import API_CONFIG from '@/config/api';
    import {
      SomeIcon,
      ...
    } from 'lucide-react';
    """
    # Pattern: import {\nimport API_CONFIG...
    pattern = r"(import\s+\{)\s*\n\s*(import\s+API_CONFIG\s+from\s+['\"]@/config/api['\"];?)\s*\n"
    replacement = r"\2\n\1\n"
    
    new_content = re.sub(pattern, replacement, content)
    
    return new_content

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix malformed imports
        content = fix_malformed_import(content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Searching for files with malformed imports...")
    
    # Find all JS/JSX/TS/TSX files
    files_to_check = []
    for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
        files_to_check.extend(BASE_DIR.rglob(ext))
    
    # Filter files that have the malformed pattern
    files_with_malformed_imports = []
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Check for the malformed pattern
            if re.search(r"import\s+\{\s*\n\s*import\s+API_CONFIG", content):
                files_with_malformed_imports.append(file_path)
        except:
            pass
    
    print(f"📁 Found {len(files_with_malformed_imports)} files with malformed imports")
    
    if len(files_with_malformed_imports) == 0:
        print("✅ No malformed imports found!")
        return
    
    # Process each file
    fixed_count = 0
    for file_path in files_with_malformed_imports:
        if process_file(file_path):
            print(f"✅ Fixed: {file_path.relative_to(BASE_DIR.parent)}")
            fixed_count += 1
        else:
            print(f"⏭️  Skipped: {file_path.relative_to(BASE_DIR.parent)}")
    
    print(f"\n🎉 Fixed {fixed_count} files!")
    
    # Verify no malformed imports remain
    print("\n🔍 Verifying no malformed imports remain...")
    remaining = 0
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if re.search(r"import\s+\{\s*\n\s*import\s+API_CONFIG", content):
                print(f"⚠️  Still has malformed import: {file_path.relative_to(BASE_DIR.parent)}")
                remaining += 1
        except:
            pass
    
    if remaining == 0:
        print("✅ All malformed imports fixed!")
    else:
        print(f"⚠️  {remaining} files still have malformed imports")

if __name__ == '__main__':
    main()
