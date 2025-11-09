# Deep Analysis: Login ERR_CONNECTION_REFUSED Issue

## Problem Statement
Frontend login fails with `ERR_CONNECTION_REFUSED` despite backend being operational.

## Known Facts

### ✅ Backend Status
- **URL**: `https://dentaflow-backend-staging-688311017213.us-central1.run.app`
- **Endpoint**: `/api/v1/auth/login`
- **Status**: ✅ WORKING
- **Evidence**: 
  ```bash
  curl -X POST https://dentaflow-backend-staging-688311017213.us-central1.run.app/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"demo@dentaflow.ai","password":"Demo123!"}' 
  # Returns: 200 OK with JWT tokens
  ```
- **Cloud Logging**: Shows 5 successful login requests in last 10 minutes (all 200 OK)

### ❌ Frontend Status
- **URL**: `https://dentaflow-frontend-staging-688311017213.us-central1.run.app`
- **Current Revision**: `00417-put` (commit: a1bdc62)
- **JavaScript Bundle**: `index-BMTgObwc.js`
- **Error**: `ERR_CONNECTION_REFUSED`
- **Login Component**: `RealLogin.jsx`

### 🔍 Code Analysis

#### RealLogin.jsx (Current State)
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dentaflow-backend-staging-688311017213.us-central1.run.app';

const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, {
  email: email.trim(),
  password: password
}, {
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000
});
```

#### JavaScript Bundle Analysis
```bash
# URL in bundle:
curl -s https://dentaflow-frontend-staging-688311017213.us-central1.run.app/assets/index-BMTgObwc.js | grep -o 'dentaflow-backend-staging[^"]*'
# Result: dentaflow-backend-staging-688311017213.us-central1.run.app ✅

# Endpoint in bundle:
curl -s https://dentaflow-frontend-staging-688311017213.us-central1.run.app/assets/index-BMTgObwc.js | grep -o '/api/v1/auth/login'
# Result: /api/v1/auth/login ✅
```

### 🏗️ Build Analysis

#### Cloud Build Configuration
- **File**: `frontend/cloudbuild-staging.yaml`
- **Build Args**:
  ```yaml
  --build-arg VITE_APP_ENV=staging
  --build-arg VITE_API_URL=https://dentaflow-backend-staging-688311017213.us-central1.run.app
  ```
- **Latest Build**: `e90d17bd-a76e-4edd-8d8b-cf456c184243`
- **Commit**: `a1bdc62`
- **Status**: ✅ SUCCESS

#### Dockerfile
```dockerfile
ARG VITE_APP_ENV=production
ARG VITE_API_URL

ENV VITE_APP_ENV=$VITE_APP_ENV
ENV VITE_API_URL=$VITE_API_URL

RUN pnpm build
```

## Hypotheses to Test

### Hypothesis 1: Browser is calling wrong URL
**Test**: Intercept actual network request in browser
**Status**: ⏳ PENDING

### Hypothesis 2: CORS issue
**Test**: Check CORS headers and preflight requests
**Status**: ⏳ PENDING

### Hypothesis 3: Mixed content (HTTP/HTTPS)
**Test**: Check if axios is trying HTTP instead of HTTPS
**Status**: ⏳ PENDING

### Hypothesis 4: Axios configuration issue
**Test**: Check axios defaults and interceptors
**Status**: ⏳ PENDING

### Hypothesis 5: Environment variable not injected
**Test**: Check if `import.meta.env.VITE_API_URL` is actually set
**Status**: ⏳ PENDING

### Hypothesis 6: Multiple versions of RealLogin.jsx
**Test**: Check if there are other login components being used
**Status**: ⏳ PENDING

## Next Steps

1. Create debugging script to intercept browser requests
2. Use Sentry to see actual error details
3. Check Cloud Trace for request flow
4. Create minimal test case
5. Add logging to RealLogin.jsx
6. Test with different browsers/incognito

## Tools Needed

- [ ] Browser DevTools Network tab export
- [ ] Sentry error tracking
- [ ] Cloud Logging queries
- [ ] Axios request interceptor
- [ ] Test script for login endpoint
