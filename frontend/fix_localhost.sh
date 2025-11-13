#!/bin/bash

# Script to replace all hardcoded localhost:8000 references with environment variables

# Define the base URL variable
API_VAR="import.meta.env.VITE_API_URL?.replace('/api/v1', '') || 'https://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app'"
WS_VAR="import.meta.env.VITE_WS_URL || 'wss://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app'"

# Find all files with localhost:8000
FILES=$(grep -rl "localhost:8000" src/ --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx")

echo "Found $(echo "$FILES" | wc -l) files with localhost:8000"
echo "Files to fix:"
echo "$FILES"
echo ""
echo "Replacing..."

# Replace HTTP localhost references
find src/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -exec sed -i "s|'http://localhost:8000'|\${$API_VAR}|g" {} \;
find src/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's|"http://localhost:8000"|${'"$API_VAR"'}|g' {} \;

# Replace WebSocket localhost references
find src/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -exec sed -i "s|'ws://localhost:8000'|\${$WS_VAR}|g" {} \;
find src/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's|"ws://localhost:8000"|${'"$WS_VAR"'}|g' {} \;

echo "Done!"
echo ""
echo "Verifying..."
grep -r "localhost:8000" src/ --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" || echo "✅ No more localhost:8000 references found!"
