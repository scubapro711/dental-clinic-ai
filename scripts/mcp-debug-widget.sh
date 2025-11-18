#!/bin/bash
# DentaFlow MCP Generic Widget Debugger
# Usage: ./mcp-debug-widget.sh [widget_name]

WIDGET_NAME=${1:-"widget"}

echo "🔍 Debugging $WIDGET_NAME..."

# Login if not already
./mcp-login.sh

sleep 3

# List network requests
echo ""
echo "📡 Checking network requests..."
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}' > /tmp/network.txt

# Find widget-related requests
echo ""
echo "🎯 $WIDGET_NAME-related requests:"
grep -i "$WIDGET_NAME" /tmp/network.txt || echo "No requests found for $WIDGET_NAME"

# List console errors
echo ""
echo "❌ Console errors:"
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error"]}' > /tmp/console.txt
grep -i "$WIDGET_NAME" /tmp/console.txt || echo "No errors found for $WIDGET_NAME"

# Take screenshot
echo ""
echo "📸 Taking screenshot..."
manus-mcp-cli tool call take_screenshot --server chrome-devtools \
  --input "{\"filePath\": \"/tmp/${WIDGET_NAME}-widget.png\", \"fullPage\": false}" > /dev/null

# Take page snapshot
echo "📄 Taking page snapshot..."
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input "{\"filePath\": \"/tmp/${WIDGET_NAME}-snapshot.txt\"}" > /dev/null

echo ""
echo "✅ Debug complete!"
echo "📁 Results in /tmp/${WIDGET_NAME}-*"
