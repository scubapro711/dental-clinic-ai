# MCP Debugging Playbook for DentaFlow
**Created:** November 14, 2025  
**Purpose:** Quick reference for using Chrome DevTools MCP for debugging  
**Status:** ✅ Active - Use for all future debugging tasks

---

## 🚀 Quick Start

### Check MCP Availability
```bash
# Verify MCP CLI is installed
which manus-mcp-cli

# List available servers
manus-mcp-cli server list

# List Chrome DevTools tools
manus-mcp-cli tool list --server chrome-devtools
```

---

## 📋 Common Debugging Workflows

### Workflow 1: Debug Failed API Request

**Use case:** Widget not loading data, API returning errors

**Steps:**
```bash
# 1. Navigate to page
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/clinic/dashboard"}'

# 2. Login (if needed)
manus-mcp-cli tool call take_snapshot --server chrome-devtools --input '{}'
# Note the UIDs from snapshot

manus-mcp-cli tool call fill_form --server chrome-devtools \
  --input '{"elements": [
    {"uid": "EMAIL_UID", "value": "rachel@dentaflow.ai"},
    {"uid": "PASSWORD_UID", "value": "demo123"}
  ]}'

manus-mcp-cli tool call click --server chrome-devtools \
  --input '{"uid": "LOGIN_BUTTON_UID"}'

# 3. Wait for page load
sleep 5

# 4. List all network requests
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}'

# 5. Get details of failed request
manus-mcp-cli tool call get_network_request --server chrome-devtools \
  --input '{"reqid": REQUEST_ID}'

# 6. Check console errors
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error"]}'
```

**Expected output:**
- Request URL
- Status code
- Request/Response headers
- Response body (error message)
- Console errors

---

### Workflow 2: Debug Widget Not Displaying Data

**Use case:** Widget shows empty state despite data existing

**Steps:**
```bash
# 1. Navigate and login (see Workflow 1)

# 2. Take page snapshot to see widget state
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input '{"filePath": "/tmp/dashboard-snapshot.txt"}'

# 3. Check if widget is rendered
cat /tmp/dashboard-snapshot.txt | grep -i "widget_name"

# 4. List network requests to see what data was fetched
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}'

# 5. Check specific API endpoint
manus-mcp-cli tool call get_network_request --server chrome-devtools \
  --input '{"reqid": REQUEST_ID}'

# 6. Execute JavaScript to check widget state
manus-mcp-cli tool call evaluate_script --server chrome-devtools \
  --input '{"function": "() => { return document.querySelector(\".widget-class\")?.textContent; }"}'
```

---

### Workflow 3: Debug Authentication Issues

**Use case:** Login fails, token issues, 401 errors

**Steps:**
```bash
# 1. Navigate to login page
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/login"}'

# 2. Check localStorage before login
manus-mcp-cli tool call evaluate_script --server chrome-devtools \
  --input '{"function": "() => { return localStorage.getItem(\"access_token\"); }"}'

# 3. Perform login
# (see Workflow 1 for login steps)

# 4. Check localStorage after login
manus-mcp-cli tool call evaluate_script --server chrome-devtools \
  --input '{"function": "() => { return localStorage.getItem(\"access_token\"); }"}'

# 5. Check if token is sent in requests
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}'

manus-mcp-cli tool call get_network_request --server chrome-devtools \
  --input '{"reqid": REQUEST_ID}'
# Check Authorization header

# 6. Check for 401 responses
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}' | grep "401"
```

---

### Workflow 4: Debug Performance Issues

**Use case:** Page loads slowly, widget takes long to render

**Steps:**
```bash
# 1. Navigate to page
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/clinic/dashboard"}'

# 2. Start performance trace
manus-mcp-cli tool call performance_start_trace --server chrome-devtools \
  --input '{"reload": true, "autoStop": true}'

# 3. Stop trace (if autoStop is false)
manus-mcp-cli tool call performance_stop_trace --server chrome-devtools \
  --input '{}'

# 4. Analyze specific insight
manus-mcp-cli tool call performance_analyze_insight --server chrome-devtools \
  --input '{"insightSetId": "INSIGHT_SET_ID", "insightName": "LCPBreakdown"}'

# 5. Check network timing
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}'
# Look for slow requests
```

---

### Workflow 5: Debug Console Errors

**Use case:** JavaScript errors in console

**Steps:**
```bash
# 1. Navigate to page
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/clinic/dashboard"}'

# 2. List all console messages
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error", "warning"]}'

# 3. Get specific console message details
manus-mcp-cli tool call get_console_message --server chrome-devtools \
  --input '{"msgid": MESSAGE_ID}'

# 4. Check if error is related to specific API call
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}'
```

---

## 🔧 Useful MCP Commands

### Navigation
```bash
# Navigate to URL
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "URL", "timeout": 30000}'

# Navigate back
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"type": "back"}'

# Reload page
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"type": "reload", "ignoreCache": true}'
```

### Page Inspection
```bash
# Take text snapshot
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input '{"filePath": "/tmp/snapshot.txt", "verbose": false}'

# Take screenshot
manus-mcp-cli tool call take_screenshot --server chrome-devtools \
  --input '{"filePath": "/tmp/screenshot.png", "fullPage": true}'

# Take element screenshot
manus-mcp-cli tool call take_screenshot --server chrome-devtools \
  --input '{"uid": "ELEMENT_UID", "filePath": "/tmp/element.png"}'
```

### Interaction
```bash
# Click element
manus-mcp-cli tool call click --server chrome-devtools \
  --input '{"uid": "ELEMENT_UID"}'

# Double click
manus-mcp-cli tool call click --server chrome-devtools \
  --input '{"uid": "ELEMENT_UID", "dblClick": true}'

# Fill input
manus-mcp-cli tool call fill --server chrome-devtools \
  --input '{"uid": "INPUT_UID", "value": "text"}'

# Fill form (multiple fields)
manus-mcp-cli tool call fill_form --server chrome-devtools \
  --input '{"elements": [
    {"uid": "UID1", "value": "value1"},
    {"uid": "UID2", "value": "value2"}
  ]}'

# Hover
manus-mcp-cli tool call hover --server chrome-devtools \
  --input '{"uid": "ELEMENT_UID"}'

# Press key
manus-mcp-cli tool call press_key --server chrome-devtools \
  --input '{"key": "Enter"}'

# Press key combination
manus-mcp-cli tool call press_key --server chrome-devtools \
  --input '{"key": "Control+Shift+R"}'
```

### Network
```bash
# List all requests
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{}'

# List specific resource types
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr", "script", "stylesheet"]}'

# Get request details
manus-mcp-cli tool call get_network_request --server chrome-devtools \
  --input '{"reqid": REQUEST_ID}'

# Get currently selected request in DevTools
manus-mcp-cli tool call get_network_request --server chrome-devtools \
  --input '{}'
```

### Console
```bash
# List all messages
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{}'

# List specific message types
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error", "warning"]}'

# Get message details
manus-mcp-cli tool call get_console_message --server chrome-devtools \
  --input '{"msgid": MESSAGE_ID}'

# Execute JavaScript
manus-mcp-cli tool call evaluate_script --server chrome-devtools \
  --input '{"function": "() => { return document.title; }"}'

# Execute with arguments
manus-mcp-cli tool call evaluate_script --server chrome-devtools \
  --input '{"function": "(el) => { return el.innerText; }", "args": [{"uid": "ELEMENT_UID"}]}'
```

### Performance
```bash
# Start trace with reload
manus-mcp-cli tool call performance_start_trace --server chrome-devtools \
  --input '{"reload": true, "autoStop": true}'

# Stop trace
manus-mcp-cli tool call performance_stop_trace --server chrome-devtools \
  --input '{}'

# Analyze insight
manus-mcp-cli tool call performance_analyze_insight --server chrome-devtools \
  --input '{"insightSetId": "ID", "insightName": "LCPBreakdown"}'
```

---

## 📝 DentaFlow-Specific Shortcuts

### Login to Dashboard
```bash
# Save as script: /home/ubuntu/dental-clinic-ai/scripts/mcp-login.sh
#!/bin/bash

# Navigate to login
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/login"}'

# Take snapshot to get UIDs
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input '{}' > /tmp/login-snapshot.txt

# Extract UIDs (adjust based on actual snapshot)
EMAIL_UID=$(grep "textbox.*Email" /tmp/login-snapshot.txt | grep -oP 'uid=\K[^ ]+' | head -1)
PASSWORD_UID=$(grep "textbox.*Password" /tmp/login-snapshot.txt | grep -oP 'uid=\K[^ ]+' | head -1)
LOGIN_BTN_UID=$(grep "button.*Login" /tmp/login-snapshot.txt | grep -oP 'uid=\K[^ ]+' | head -1)

# Fill and submit
manus-mcp-cli tool call fill_form --server chrome-devtools \
  --input "{\"elements\": [{\"uid\": \"$EMAIL_UID\", \"value\": \"rachel@dentaflow.ai\"}, {\"uid\": \"$PASSWORD_UID\", \"value\": \"demo123\"}]}"

manus-mcp-cli tool call click --server chrome-devtools \
  --input "{\"uid\": \"$LOGIN_BTN_UID\"}"

echo "✅ Logged in successfully"
```

### Check Widget Data
```bash
# Save as script: /home/ubuntu/dental-clinic-ai/scripts/mcp-check-widget.sh
#!/bin/bash

WIDGET_NAME=$1

# List network requests
echo "📡 Checking network requests..."
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}' > /tmp/network.txt

# Find widget-related requests
echo "🔍 Widget-related requests:"
cat /tmp/network.txt | grep -i "$WIDGET_NAME"

# List console errors
echo "❌ Console errors:"
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error"]}' | grep -i "$WIDGET_NAME"

# Take screenshot
echo "📸 Taking screenshot..."
manus-mcp-cli tool call take_screenshot --server chrome-devtools \
  --input "{\"filePath\": \"/tmp/${WIDGET_NAME}-widget.png\", \"fullPage\": false}"

echo "✅ Check complete. Results in /tmp/"
```

### Debug Appointments Widget
```bash
# Save as script: /home/ubuntu/dental-clinic-ai/scripts/mcp-debug-appointments.sh
#!/bin/bash

echo "🔍 Debugging Appointments Widget..."

# Login
./mcp-login.sh

# Wait for dashboard load
sleep 3

# Check appointments endpoint
echo "📡 Checking /appointments/today-enriched..."
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}' | grep "appointments"

# Get request details
REQID=$(manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"resourceTypes": ["fetch", "xhr"]}' | grep "appointments/today-enriched" | grep -oP 'reqid=\K[0-9]+')

if [ -n "$REQID" ]; then
  echo "📋 Request details for reqid=$REQID:"
  manus-mcp-cli tool call get_network_request --server chrome-devtools \
    --input "{\"reqid\": $REQID}"
else
  echo "❌ No appointments request found!"
fi

# Check console errors
echo "❌ Console errors:"
manus-mcp-cli tool call list_console_messages --server chrome-devtools \
  --input '{"types": ["error"]}' | grep -i "appointment"

echo "✅ Debug complete"
```

---

## 🎯 Best Practices

### 1. Always Take Snapshots First
- Snapshots provide element UIDs
- More reliable than guessing UIDs
- Shows current page state

### 2. Filter Network Requests
- Use `resourceTypes` to reduce noise
- Focus on `fetch` and `xhr` for API calls
- Save time by not listing all resources

### 3. Save Results to Files
- MCP auto-saves to `/home/ubuntu/.mcp/tool-results/`
- Use `filePath` parameter for custom locations
- Easier to analyze large outputs

### 4. Use Scripts for Repetitive Tasks
- Create bash scripts for common workflows
- Save in `/home/ubuntu/dental-clinic-ai/scripts/`
- Make executable: `chmod +x script.sh`

### 5. Check Both Network and Console
- Network shows API failures
- Console shows JavaScript errors
- Both are needed for complete picture

---

## 🐛 Troubleshooting

### MCP Server Not Responding
```bash
# Check if server is running
manus-mcp-cli server list

# Restart MCP (if needed)
# Usually handled automatically
```

### Element UID Not Found
```bash
# Take fresh snapshot
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input '{"verbose": true}'

# Check if element exists in snapshot
cat /home/ubuntu/.mcp/tool-results/latest_snapshot.txt | grep "element_text"
```

### Navigation Timeout
```bash
# Increase timeout
manus-mcp-cli tool call navigate_page --server chrome-devtools \
  --input '{"url": "URL", "timeout": 60000}'

# Check if page is actually loading
manus-mcp-cli tool call list_pages --server chrome-devtools --input '{}'
```

### Request Not Found
```bash
# List all requests without filters
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{}'

# Check if request was made before current navigation
manus-mcp-cli tool call list_network_requests --server chrome-devtools \
  --input '{"includePreservedRequests": true}'
```

---

## 📚 Resources

- **MCP Study Notes:** `/home/ubuntu/Chrome-DevTools-142-Study-Notes.md`
- **Success Story:** `/home/ubuntu/MCP-Debugging-Success-Story.md`
- **Tool Results:** `/home/ubuntu/.mcp/tool-results/`
- **Official Docs:** https://github.com/chrome-devtools/mcp-server

---

## ✅ Checklist for Each Debugging Session

- [ ] Navigate to page
- [ ] Take snapshot (if interaction needed)
- [ ] Login (if needed)
- [ ] List network requests
- [ ] Check failed requests (4xx, 5xx)
- [ ] Get request details
- [ ] List console messages
- [ ] Check errors and warnings
- [ ] Take screenshot (for documentation)
- [ ] Save findings to file

---

**Last Updated:** November 14, 2025  
**Status:** ✅ Active and ready for use  
**Tested On:** DentaFlow Appointments Widget debugging
