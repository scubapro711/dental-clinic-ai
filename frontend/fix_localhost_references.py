#!/usr/bin/env python3
"""
Script to replace all hardcoded localhost:8000 references with API_CONFIG usage.

This script:
1. Finds all files with localhost:8000 references
2. Adds import statement for API_CONFIG if not present
3. Replaces hardcoded URLs with API_CONFIG.endpoint() or API_CONFIG.ws()
"""

import os
import re
from pathlib import Path

# Patterns to find and replace
PATTERNS = [
    # HTTP URLs
    (r"'http://localhost:8000/api/v1/([^']*)'", r"API_CONFIG.endpoint('\1')"),
    (r'"http://localhost:8000/api/v1/([^"]*)"', r'API_CONFIG.endpoint("\1")'),
    (r"'http://localhost:8000'", r"API_CONFIG.BASE_URL"),
    (r'"http://localhost:8000"', r'API_CONFIG.BASE_URL'),
    
    # WebSocket URLs
    (r"'ws://localhost:8000/([^']*)'", r"API_CONFIG.ws('\1')"),
    (r'"ws://localhost:8000/([^"]*)"', r'API_CONFIG.ws("\1")'),
    (r"'ws://localhost:8000'", r"API_CONFIG.WS_URL"),
    (r'"ws://localhost:8000"', r'API_CONFIG.WS_URL'),
]

# Import statement to add
IMPORT_STATEMENT = "import API_CONFIG from '@/config/api';\n"

def needs_api_config_import(content):
    """Check if file needs API_CONFIG import."""
    return 'API_CONFIG' in content and 'from' not in content and '@/config/api' not in content

def add_import_statement(content):
    """Add API_CONFIG import at the top of the file."""
    # Find the last import statement
    import_pattern = r'^import\s+.*?;?\s*$'
    matches = list(re.finditer(import_pattern, content, re.MULTILINE))
    
    if matches:
        # Insert after the last import
        last_import = matches[-1]
        insert_pos = last_import.end()
        return content[:insert_pos] + '\n' + IMPORT_STATEMENT + content[insert_pos:]
    else:
        # No imports found, add at the beginning
        return IMPORT_STATEMENT + '\n' + content

def fix_file(file_path):
    """Fix localhost references in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply all replacements
    for pattern, replacement in PATTERNS:
        content = re.sub(pattern, replacement, content)
    
    # If content changed, add import if needed
    if content != original_content:
        if needs_api_config_import(content):
            content = add_import_statement(content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def main():
    """Main function."""
    src_dir = Path('src')
    
    # Find all JS/JSX/TS/TSX files
    files_to_check = []
    for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
        files_to_check.extend(src_dir.rglob(ext))
    
    print(f"Checking {len(files_to_check)} files...")
    
    fixed_files = []
    for file_path in files_to_check:
        # Skip if file contains 'localhost:8000'
        with open(file_path, 'r', encoding='utf-8') as f:
            if 'localhost:8000' in f.read():
                if fix_file(file_path):
                    fixed_files.append(file_path)
                    print(f"✅ Fixed: {file_path}")
    
    print(f"\n{'='*60}")
    print(f"Fixed {len(fixed_files)} files")
    print(f"{'='*60}")
    
    # Verify no localhost:8000 left
    remaining = []
    for file_path in files_to_check:
        with open(file_path, 'r', encoding='utf-8') as f:
            if 'localhost:8000' in f.read():
                remaining.append(file_path)
    
    if remaining:
        print(f"\n⚠️  Still found localhost:8000 in {len(remaining)} files:")
        for file_path in remaining:
            print(f"  - {file_path}")
    else:
        print("\n✅ No more localhost:8000 references found!")

if __name__ == '__main__':
    main()
