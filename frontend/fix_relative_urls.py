#!/usr/bin/env python3
"""
Fix all relative API URLs to use API_CONFIG.endpoint()

This script:
1. Finds all files with fetch('/api/v1/...') or fetch("/api/v1/...")
2. Replaces them with API_CONFIG.endpoint('...')
3. Adds import statement if missing
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent / 'src'

def has_api_config_import(content):
    """Check if file already imports API_CONFIG"""
    import_pattern = r"import\s+API_CONFIG\s+from\s+['\"]@/config/api['\"]";
    return re.search(import_pattern, content) is not None

def add_api_config_import(content):
    """Add API_CONFIG import to the file"""
    lines = content.split('\n')
    
    # Find the last import statement
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            last_import_idx = i
    
    # Add import after last import
    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, "import API_CONFIG from '@/config/api';")
    else:
        # No imports found, add at the beginning
        lines.insert(0, "import API_CONFIG from '@/config/api';")
    
    return '\n'.join(lines)

def fix_relative_urls(content):
    """Replace all relative API URLs with API_CONFIG.endpoint()"""
    
    # Pattern 1: fetch('/api/v1/...' with single quotes
    pattern1 = r"fetch\('[^']*?/api/v1/([^']+)'\s*,"
    replacement1 = r"fetch(API_CONFIG.endpoint('\1'),"
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: fetch("/api/v1/..." with double quotes
    pattern2 = r'fetch\("[^"]*?/api/v1/([^"]+)"\s*,'
    replacement2 = r"fetch(API_CONFIG.endpoint('\1'),"
    content = re.sub(pattern2, replacement2, content)
    
    # Pattern 3: fetch(`/api/v1/...` with backticks
    pattern3 = r"fetch\(`[^`]*?/api/v1/([^`]+)`\s*,"
    replacement3 = r"fetch(API_CONFIG.endpoint('\1'),"
    content = re.sub(pattern3, replacement3, content)
    
    # Pattern 4: fetch('/api/v1/...') without trailing comma
    pattern4 = r"fetch\('[^']*?/api/v1/([^']+)'\)"
    replacement4 = r"fetch(API_CONFIG.endpoint('\1'))"
    content = re.sub(pattern4, replacement4, content)
    
    # Pattern 5: fetch("/api/v1/...") without trailing comma
    pattern5 = r'fetch\("[^"]*?/api/v1/([^"]+)"\)'
    replacement5 = r"fetch(API_CONFIG.endpoint('\1'))"
    content = re.sub(pattern5, replacement5, content)
    
    return content

def process_file(file_path):
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix relative URLs
        content = fix_relative_urls(content)
        
        # Add import if needed
        if content != original_content and not has_api_config_import(content):
            content = add_api_config_import(content)
        
        # Check if content changed
        if content == original_content:
            return False
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Searching for files with relative API URLs...")
    
    # Find all JS/JSX/TS/TSX files
    files_to_check = []
    for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
        files_to_check.extend(BASE_DIR.rglob(ext))
    
    # Filter files that have relative URLs
    files_with_relative_urls = []
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if "fetch('/api/v1" in content or 'fetch("/api/v1' in content or "fetch(`/api/v1" in content:
                files_with_relative_urls.append(file_path)
        except:
            pass
    
    print(f"📁 Found {len(files_with_relative_urls)} files with relative URLs")
    
    # Process each file
    fixed_count = 0
    for file_path in files_with_relative_urls:
        if process_file(file_path):
            print(f"✅ Fixed: {file_path.relative_to(BASE_DIR.parent)}")
            fixed_count += 1
        else:
            print(f"⏭️  Skipped: {file_path.relative_to(BASE_DIR.parent)}")
    
    print(f"\n🎉 Fixed {fixed_count} files!")
    
    # Verify no relative URLs remain
    print("\n🔍 Verifying no relative URLs remain...")
    remaining = 0
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if "fetch('/api/v1" in content or 'fetch("/api/v1' in content:
                print(f"⚠️  Still has relative URL: {file_path.relative_to(BASE_DIR.parent)}")
                remaining += 1
        except:
            pass
    
    if remaining == 0:
        print("✅ All relative URLs fixed!")
    else:
        print(f"⚠️  {remaining} files still have relative URLs")

if __name__ == '__main__':
    main()
