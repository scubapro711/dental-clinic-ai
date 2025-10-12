'''
import os

file_path = 'ALL_FILES.txt'
output_path = 'CODE_AUDIT_SUMMARY.md'

try:
    with open(file_path, 'r') as f:
        files = f.read().splitlines()
except FileNotFoundError:
    print(f"Error: {file_path} not found.")
    exit()

summary = {
    'backend': {'count': 0, 'dirs': {}},
    'frontend': {'count': 0, 'dirs': {}},
    'docs': {'count': 0, 'dirs': {}},
    'other': {'count': 0, 'dirs': {}}
}

for file in files:
    file = file.replace('\\', '/') # Correctly escape backslash
    if file.startswith('./backend/'):
        key = 'backend'
    elif file.startswith('./patient-portal/'):
        key = 'frontend'
    elif file.startswith('./docs/'):
        key = 'docs'
    else:
        key = 'other'
    
    summary[key]['count'] += 1
    dirname = os.path.dirname(file)
    summary[key]['dirs'][dirname] = summary[key]['dirs'].get(dirname, 0) + 1

with open(output_path, 'w') as f:
    f.write('# Code Audit Summary\n\n')
    f.write(f"**Total files:** {len(files)}\n\n")
    
    for key, value in summary.items():
        f.write(f"## {key.capitalize()}\n\n")
        count = value['count']
        dir_count = len(value['dirs'])
        f.write(f"**Total files:** {count}\n")
        f.write(f"**Total directories:** {dir_count}\n\n")
        f.write('| Directory | File Count |\n')
        f.write('|---|---|\n')
        sorted_dirs = sorted(value['dirs'].items(), key=lambda item: item[1], reverse=True)[:15]
        for dirname, d_count in sorted_dirs:
            f.write(f"| `{dirname}` | {d_count} |\n")
        f.write('\n')

print(f"✅ Created {output_path}")
'''
