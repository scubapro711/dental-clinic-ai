# MCP Debugging Scripts for DentaFlow

**Created:** November 14, 2025  
**Purpose:** Ready-to-use scripts for debugging DentaFlow dashboard using Chrome DevTools MCP

---

## 📁 Available Scripts

### 1. `mcp-login.sh`
**Purpose:** Automated login to DentaFlow dashboard

**Usage:**
```bash
./mcp-login.sh
```

**What it does:**
- Navigates to login page
- Fills in admin credentials (rachel@dentaflow.ai / demo123)
- Clicks login button
- Waits for dashboard to load

**Output:**
```
🔐 Logging into DentaFlow dashboard...
📝 Filling credentials...
🚀 Clicking login...
✅ Logged in successfully!
```

---

### 2. `mcp-debug-appointments.sh`
**Purpose:** Debug Today's Patients widget and appointments endpoint

**Usage:**
```bash
./mcp-debug-appointments.sh
```

**What it does:**
- Logs in to dashboard
- Lists all network requests
- Finds appointments-related requests
- Gets details of `/today-enriched` endpoint
- Checks console errors
- Takes screenshot

**Output:**
```
🔍 Debugging Appointments Widget...
📡 Network requests:
🎯 Appointments-related requests:
reqid=20 GET .../appointments/today-enriched [success - 200]
📋 Request details for /today-enriched (reqid=20):
### Response Body
[{"id": 1, "patient_name": "John Smith", ...}]
❌ Console errors:
No appointment-related errors
📸 Taking screenshot...
✅ Debug complete!
📁 Results saved to:
   - /tmp/network.txt
   - /tmp/console.txt
   - /tmp/appointments-widget.png
```

---

### 3. `mcp-debug-widget.sh`
**Purpose:** Generic widget debugger for any widget

**Usage:**
```bash
./mcp-debug-widget.sh [widget_name]

# Examples:
./mcp-debug-widget.sh revenue
./mcp-debug-widget.sh agents
./mcp-debug-widget.sh decisions
```

**What it does:**
- Logs in to dashboard
- Lists network requests related to widget
- Checks console errors related to widget
- Takes screenshot
- Takes page snapshot

**Output:**
```
🔍 Debugging revenue...
📡 Checking network requests...
🎯 revenue-related requests:
reqid=21 GET .../revenue/dashboard [success - 200]
❌ Console errors:
No errors found for revenue
📸 Taking screenshot...
📄 Taking page snapshot...
✅ Debug complete!
📁 Results in /tmp/revenue-*
```

---

## 🚀 Quick Start

### First Time Setup
```bash
# Navigate to scripts directory
cd /home/ubuntu/dental-clinic-ai/scripts

# Verify scripts are executable
ls -l mcp-*.sh

# Test login
./mcp-login.sh
```

### Debug Appointments Widget
```bash
cd /home/ubuntu/dental-clinic-ai/scripts
./mcp-debug-appointments.sh
```

### Debug Any Widget
```bash
cd /home/ubuntu/dental-clinic-ai/scripts
./mcp-debug-widget.sh revenue
./mcp-debug-widget.sh agents
./mcp-debug-widget.sh decisions
```

---

## 📊 Output Files

All scripts save results to `/tmp/`:

| File | Content |
|------|---------|
| `/tmp/network.txt` | All network requests |
| `/tmp/console.txt` | All console messages |
| `/tmp/login-snapshot.txt` | Login page snapshot |
| `/tmp/appointments-widget.png` | Screenshot of dashboard |
| `/tmp/{widget}-widget.png` | Screenshot for specific widget |
| `/tmp/{widget}-snapshot.txt` | Page snapshot for specific widget |

---

## 🔧 Customization

### Change Login Credentials
Edit `mcp-login.sh`:
```bash
# Line 20-21
manus-mcp-cli tool call fill_form --server chrome-devtools \
  --input "{\"elements\": [{\"uid\": \"$EMAIL_UID\", \"value\": \"YOUR_EMAIL\"}, {\"uid\": \"$PASSWORD_UID\", \"value\": \"YOUR_PASSWORD\"}]}"
```

### Change Dashboard URL
Edit any script:
```bash
# Change this line
--input '{"url": "https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app/login"}'

# To production URL
--input '{"url": "https://dentaflow-frontend-prod.../login"}'
```

### Add More Debugging Steps
Example: Check localStorage
```bash
# Add to any script
echo "🔍 Checking localStorage..."
manus-mcp-cli tool call evaluate_script --server chrome-devtools \
  --input '{"function": "() => { return localStorage.getItem(\"access_token\"); }"}'
```

---

## 🐛 Troubleshooting

### Script Fails to Login
**Problem:** UIDs change between page loads

**Solution:** Script automatically extracts UIDs from snapshot

**Manual fix:**
```bash
# Take snapshot manually
manus-mcp-cli tool call take_snapshot --server chrome-devtools \
  --input '{}' > /tmp/snapshot.txt

# Find correct UIDs
grep "textbox.*Email" /tmp/snapshot.txt
grep "button.*Login" /tmp/snapshot.txt
```

### Network Requests Not Found
**Problem:** Page not fully loaded

**Solution:** Increase sleep time in script
```bash
# Change this line in script
sleep 3

# To longer wait
sleep 5
```

### Screenshot is Blank
**Problem:** Page still loading when screenshot taken

**Solution:** Wait for specific element
```bash
# Add before screenshot
manus-mcp-cli tool call wait_for --server chrome-devtools \
  --input '{"text": "Dashboard", "timeout": 10000}'
```

---

## 📚 Related Documentation

- **MCP Playbook:** `/home/ubuntu/dental-clinic-ai/MCP-Debugging-Playbook.md`
- **MCP Success Story:** `/home/ubuntu/MCP-Debugging-Success-Story.md`
- **Chrome DevTools 142 Notes:** `/home/ubuntu/Chrome-DevTools-142-Study-Notes.md`

---

## ✅ Testing

### Test All Scripts
```bash
cd /home/ubuntu/dental-clinic-ai/scripts

# Test login
./mcp-login.sh

# Test appointments debugger
./mcp-debug-appointments.sh

# Test generic debugger
./mcp-debug-widget.sh revenue
```

### Verify Output
```bash
# Check if files were created
ls -lh /tmp/*.txt /tmp/*.png

# View network requests
cat /tmp/network.txt

# View console errors
cat /tmp/console.txt

# View screenshot
# (Copy to local machine or use image viewer)
```

---

## 🎯 Use Cases

### 1. Widget Not Loading Data
```bash
./mcp-debug-widget.sh [widget_name]
# Check network.txt for failed requests
# Check console.txt for JavaScript errors
```

### 2. API Endpoint Returning Error
```bash
./mcp-debug-appointments.sh
# Look for 4xx or 5xx status codes
# Check response body for error details
```

### 3. Authentication Issues
```bash
./mcp-login.sh
# Check if login succeeds
# Verify token in localStorage
```

### 4. Performance Issues
```bash
# Add to script:
manus-mcp-cli tool call performance_start_trace --server chrome-devtools \
  --input '{"reload": true, "autoStop": true}'
```

---

## 🚀 Advanced Usage

### Chain Multiple Scripts
```bash
# Login once, then debug multiple widgets
./mcp-login.sh
./mcp-debug-widget.sh appointments
./mcp-debug-widget.sh revenue
./mcp-debug-widget.sh agents
```

### Save Results with Timestamp
```bash
# Modify script to use timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
manus-mcp-cli tool call take_screenshot --server chrome-devtools \
  --input "{\"filePath\": \"/tmp/dashboard-${TIMESTAMP}.png\"}"
```

### Compare Before/After Fix
```bash
# Before fix
./mcp-debug-appointments.sh
mv /tmp/network.txt /tmp/network-before.txt

# After fix (deploy new code)
./mcp-debug-appointments.sh
mv /tmp/network.txt /tmp/network-after.txt

# Compare
diff /tmp/network-before.txt /tmp/network-after.txt
```

---

**Last Updated:** November 14, 2025  
**Status:** ✅ Tested and ready for use  
**Tested On:** DentaFlow Staging Environment
