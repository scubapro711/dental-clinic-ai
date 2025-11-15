#!/bin/bash

# Script to verify and fix all API_CONFIG imports

echo "=== Verifying API_CONFIG imports ==="
echo ""

MISSING_IMPORTS=()

# Get all files that use API_CONFIG
while IFS= read -r file; do
  # Check if file uses API_CONFIG
  if grep -q "API_CONFIG" "$file"; then
    # Check if file has import
    if ! grep -q "import.*API_CONFIG.*from.*@/config/api" "$file"; then
      echo "❌ MISSING IMPORT: $file"
      MISSING_IMPORTS+=("$file")
    else
      echo "✅ Has import: $file"
    fi
  fi
done < <(find src -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) ! -path "*/config/api.js")

echo ""
echo "=== Summary ==="
echo "Files with missing imports: ${#MISSING_IMPORTS[@]}"

if [ ${#MISSING_IMPORTS[@]} -gt 0 ]; then
  echo ""
  echo "Missing imports in:"
  for file in "${MISSING_IMPORTS[@]}"; do
    echo "  - $file"
  done
fi
