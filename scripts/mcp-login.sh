#!/bin/bash
# DentaFlow MCP Login Helper
# Usage: ./mcp-login.sh

echo "🔐 Logging into DentaFlow dashboard..."

# Navigate to login
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/login"}' > /dev/null

sleep 2

# Take snapshot to get UIDs
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input '{}' > /tmp/login-snapshot.txt

# Extract UIDs
EMAIL_UID=$(grep "textbox.*Email" /tmp/login-snapshot.txt | grep -oP 'uid=\K[^ ]+' | head -1)
PASSWORD_UID=$(grep "textbox.*Password" /tmp/login-snapshot.txt | grep -oP 'uid=\K[^ ]+' | head -1)
LOGIN_BTN_UID=$(grep "button.*Login" /tmp/login-snapshot.txt | grep -oP 'uid=\K[^ ]+' | head -1)

echo "📝 Filling credentials..."
# Fill and submit
manus-mcp-cli tool call fill_form --server chrome-devtools \
  --input "{\"elements\": [{\"uid\": \"$EMAIL_UID\", \"value\": \"rachel@dentaflow.ai\"}, {\"uid\": \"$PASSWORD_UID\", \"value\": \"demo123\"}]}" > /dev/null

echo "🚀 Clicking login..."
manus-mcp-cli tool call click --server chrome-devtools \
  --input "{\"uid\": \"$LOGIN_BTN_UID\"}" > /dev/null

sleep 3

echo "✅ Logged in successfully!"
