#!/bin/bash
# DentaFlow MCP Appointments Debugger
# Usage: ./mcp-debug-appointments.sh

echo "🔍 Debugging Appointments Widget..."

# Login
./mcp-login.sh

# Wait for dashboard load
echo "⏳ Waiting for dashboard to load..."
sleep 3

# List all network requests
echo ""
echo "📡 Network requests:"
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}' > /tmp/network.txt

# Find appointments requests
echo ""
echo "🎯 Appointments-related requests:"
grep "appointments" /tmp/network.txt

# Get request details for today-enriched
REQID=$(grep "appointments/today-enriched" /tmp/network.txt | grep -oP 'reqid=\K[0-9]+' | head -1)

if [ -n "$REQID" ]; then
  echo ""
  echo "📋 Request details for /today-enriched (reqid=$REQID):"
  manus-mcp-cli tool call get_network_request --server chrome-devtools \
    --input "{\"reqid\": $REQID}" | grep -A 20 "Response Body"
else
  echo "❌ No /today-enriched request found!"
fi

# Check console errors
echo ""
echo "❌ Console errors:"
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error"]}' > /tmp/console.txt
grep -i "appointment" /tmp/console.txt || echo "No appointment-related errors"

# Take screenshot
echo ""
echo "📸 Taking screenshot..."
manus-mcp-cli tool call take_screenshot --server chrome-devtools \
  --input '{"filePath": "/tmp/appointments-widget.png", "fullPage": false}' > /dev/null

echo ""
echo "✅ Debug complete!"
echo "📁 Results saved to:"
echo "   - /tmp/network.txt"
echo "   - /tmp/console.txt"
echo "   - /tmp/appointments-widget.png"
