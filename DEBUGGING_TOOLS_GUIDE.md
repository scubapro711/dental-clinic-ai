# Professional Debugging Tools Guide

## Created: 2025-11-09
## Purpose: Master all debugging tools for network/CORS/axios issues

---

## 1. Chrome DevTools Network Tab

### Key Features:
1. **HAR Export**
   - Right-click request → "Save all as HAR (sanitized)"
   - Contains full request/response details
   - Can be analyzed offline or shared

2. **Preserve Log**
   - Checkbox at top of Network tab
   - Keeps requests across page navigations
   - Essential for debugging redirects

3. **Disable Cache**
   - Checkbox next to Preserve Log
   - Forces fresh requests
   - Bypasses browser cache

4. **Filter Requests**
   - Filter by type: XHR, JS, CSS, Img, etc.
   - Filter by domain
   - Filter by status code

5. **Timing Tab**
   - Shows request lifecycle:
     - Queueing
     - Stalled
     - DNS Lookup
     - Initial connection
     - SSL
     - Request sent
     - Waiting (TTFB)
     - Content Download

6. **Headers Tab**
   - Request headers
   - Response headers
   - **CORS headers** (Access-Control-*)
   - Query string parameters

7. **Preview/Response Tab**
   - Formatted response
   - Raw response

### CORS Preflight Debugging:
- **Problem**: Chrome hides OPTIONS preflight requests by default
- **Solution**: Look for them in Network tab
- **What to check**:
  - Does OPTIONS request appear?
  - Does it return 200?
  - Are Access-Control-* headers present?
  - Does Access-Control-Allow-Origin match the origin?

---

## 2. Axios Error Handling

### Error Structure:
```javascript
{
  message: string,    // Error summary
  name: 'AxiosError', // Always AxiosError
  code: string,       // ERR_NETWORK, ERR_BAD_REQUEST, etc.
  config: object,     // Request configuration
  request: object,    // XMLHttpRequest or http.ClientRequest
  response: object,   // Server response (if received)
  stack: string       // Stack trace
}
```

### Error Types:

#### 1. error.response (Server responded with error)
```javascript
if (error.response) {
  // Server sent a response (status outside 2xx)
  console.log(error.response.status);    // 404, 500, etc.
  console.log(error.response.data);      // Error message from server
  console.log(error.response.headers);   // Response headers
}
```

**Causes:**
- 4xx errors (client error)
- 5xx errors (server error)
- Backend validation errors

#### 2. error.request (No response received)
```javascript
else if (error.request) {
  // Request sent but no response
  console.log(error.request);
  console.log(error.code); // ERR_NETWORK, ECONNREFUSED, etc.
}
```

**Causes:**
- **CORS preflight failure** ← Most common!
- Network timeout
- DNS resolution failure
- Server not responding
- Firewall/proxy blocking
- Ad blockers

#### 3. Setup error
```javascript
else {
  // Error before request was sent
  console.log(error.message);
}
```

**Causes:**
- Invalid URL
- Invalid configuration
- Missing required parameters

### Error Codes:
- `ERR_NETWORK` - General network error (CORS, timeout, etc.)
- `ECONNREFUSED` - Connection refused
- `ENOTFOUND` - DNS lookup failed
- `ETIMEDOUT` - Request timeout
- `ERR_BAD_REQUEST` - Invalid request
- `ERR_BAD_RESPONSE` - Invalid response

### Debugging Methods:

#### Method 1: error.toJSON()
```javascript
catch (error) {
  console.log(error.toJSON());
  // Returns full error object with all properties
}
```

#### Method 2: Interceptors
```javascript
axios.interceptors.request.use(
  config => {
    console.log('REQUEST:', config);
    return config;
  },
  error => {
    console.log('REQUEST ERROR:', error);
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  response => {
    console.log('RESPONSE:', response);
    return response;
  },
  error => {
    console.log('RESPONSE ERROR:', error);
    if (error.response) {
      console.log('Server error:', error.response.status);
    } else if (error.request) {
      console.log('No response:', error.code);
    }
    return Promise.reject(error);
  }
);
```

---

## 3. CORS Debugging

### What is CORS?
Cross-Origin Resource Sharing - browser security feature that blocks requests to different origins.

### How CORS Works:

1. **Simple Requests** (GET, POST with simple headers)
   - Browser sends request with `Origin` header
   - Server responds with `Access-Control-Allow-Origin`
   - If origins match, browser allows response

2. **Preflight Requests** (POST with custom headers, PUT, DELETE)
   - Browser sends OPTIONS request first
   - Server responds with allowed methods/headers
   - If allowed, browser sends actual request

### CORS Headers to Check:

**Request Headers:**
- `Origin: https://example.com`
- `Access-Control-Request-Method: POST`
- `Access-Control-Request-Headers: content-type`

**Response Headers:**
- `Access-Control-Allow-Origin: https://example.com` (or *)
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE`
- `Access-Control-Allow-Headers: Content-Type, Authorization`
- `Access-Control-Allow-Credentials: true`
- `Access-Control-Max-Age: 600` (cache preflight for 10 min)

### Common CORS Errors:

1. **"No 'Access-Control-Allow-Origin' header"**
   - Server didn't send CORS headers
   - Check backend CORS configuration

2. **"Origin not allowed"**
   - Server sent different origin than requested
   - Check backend allowed origins list

3. **"Method not allowed"**
   - OPTIONS preflight failed
   - Check backend allows the HTTP method

4. **"Header not allowed"**
   - Custom header not in allowed list
   - Check Access-Control-Allow-Headers

### CORS Debugging Tools:

#### curl test:
```bash
# Test preflight
curl -v -X OPTIONS \
  -H "Origin: https://frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  https://backend.com/api/endpoint

# Test actual request
curl -v -X POST \
  -H "Origin: https://frontend.com" \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' \
  https://backend.com/api/endpoint
```

---

## 4. Browser Console Debugging

### Console Methods:
```javascript
console.log()    // General logging
console.error()  // Error logging (red)
console.warn()   // Warning (yellow)
console.info()   // Info (blue)
console.table()  // Display as table
console.group()  // Group logs
console.time()   // Start timer
console.timeEnd() // End timer
```

### Network Inspection:
```javascript
// In browser console
performance.getEntriesByType('resource')
  .filter(r => r.name.includes('api'))
  .forEach(r => console.log(r.name, r.duration));
```

---

## 5. Systematic Debugging Process

### Step 1: Identify Error Type
```javascript
catch (error) {
  if (error.response) {
    console.log('SERVER ERROR:', error.response.status);
    // → Check backend logs
  } else if (error.request) {
    console.log('NETWORK ERROR:', error.code);
    // → Check CORS, network, DNS
  } else {
    console.log('SETUP ERROR:', error.message);
    // → Check code configuration
  }
}
```

### Step 2: Check Network Tab
1. Open DevTools → Network
2. Enable "Preserve log"
3. Enable "Disable cache"
4. Reproduce the error
5. Look for:
   - Failed requests (red)
   - OPTIONS preflight requests
   - Response status codes
   - Response headers

### Step 3: Export HAR
1. Right-click → "Save all as HAR"
2. Analyze offline
3. Share with team if needed

### Step 4: Test with curl
1. Copy request as curl
2. Test from command line
3. Compare browser vs curl results

### Step 5: Check CORS
1. Look for OPTIONS request
2. Check Access-Control-* headers
3. Verify origin matches
4. Test preflight with curl

### Step 6: Add Logging
1. Add axios interceptors
2. Log request config
3. Log error details
4. Use error.toJSON()

---

## 6. Common Issues & Solutions

### Issue: ERR_NETWORK with error.request
**Causes:**
1. CORS preflight failure
2. Network timeout
3. DNS failure
4. Ad blocker

**Debug:**
1. Check Network tab for OPTIONS request
2. Check CORS headers
3. Test with curl
4. Disable ad blocker
5. Check DNS resolution

### Issue: Request works in curl but not browser
**Cause:** CORS!
**Solution:** Fix backend CORS configuration

### Issue: Request works sometimes
**Causes:**
1. Race condition
2. Cache issues
3. Network instability

**Debug:**
1. Add timing logs
2. Clear cache
3. Test with "Disable cache"

---

## 7. Tools Checklist

Before debugging:
- [ ] Chrome DevTools open
- [ ] Network tab open
- [ ] Preserve log enabled
- [ ] Disable cache enabled
- [ ] Console tab visible
- [ ] axios interceptors added
- [ ] error.toJSON() in catch block
- [ ] curl commands ready
- [ ] Backend logs accessible

---

## 8. Next Steps

For this specific issue (ERR_NETWORK):
1. ✅ Open real frontend in browser
2. ✅ Open DevTools Network tab
3. ✅ Enable Preserve log
4. ✅ Try login
5. ✅ Export HAR file
6. ✅ Check for OPTIONS request
7. ✅ Check CORS headers
8. ✅ Compare with curl results
9. ✅ Identify root cause
10. ✅ Fix and verify
