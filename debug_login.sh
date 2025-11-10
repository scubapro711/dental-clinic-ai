#!/bin/bash
# Login Debugging Script
# Tests all aspects of the login flow

set -e

BACKEND_URL="https://dentaflow-backend-staging-688311017213.us-central1.run.app"
FRONTEND_URL="https://dentaflow-frontend-staging-688311017213.us-central1.run.app"
EMAIL="demo@dentaflow.ai"
PASSWORD="Demo123!"

echo "🔍 DentaFlow Login Debugging Script"
echo "===================================="
echo ""

# Test 1: Backend Health
echo "📋 Test 1: Backend Health Check"
echo "--------------------------------"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ Backend health: OK ($HEALTH_STATUS)"
else
    echo "❌ Backend health: FAILED ($HEALTH_STATUS)"
fi
echo ""

# Test 2: Backend Login Endpoint
echo "📋 Test 2: Backend Login Endpoint"
echo "--------------------------------"
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Login endpoint: OK ($HTTP_CODE)"
    echo "   Access token: $(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 | cut -c1-50)..."
    
    # Extract and decode JWT
    ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    JWT_PAYLOAD=$(echo "$ACCESS_TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null || echo "$ACCESS_TOKEN" | cut -d. -f2 | base64 -D 2>/dev/null)
    echo "   JWT Payload:"
    echo "$JWT_PAYLOAD" | python3 -m json.tool 2>/dev/null || echo "$JWT_PAYLOAD"
else
    echo "❌ Login endpoint: FAILED ($HTTP_CODE)"
    echo "   Response: $RESPONSE_BODY"
fi
echo ""

# Test 3: Frontend Availability
echo "📋 Test 3: Frontend Availability"
echo "--------------------------------"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend: OK ($FRONTEND_STATUS)"
else
    echo "❌ Frontend: FAILED ($FRONTEND_STATUS)"
fi
echo ""

# Test 4: JavaScript Bundle Analysis
echo "📋 Test 4: JavaScript Bundle Analysis"
echo "--------------------------------"
JS_FILE=$(curl -s "$FRONTEND_URL" | grep -o 'src="/assets/[^"]*\.js"' | head -1 | cut -d'"' -f2)
echo "   JS Bundle: $JS_FILE"

if [ -n "$JS_FILE" ]; then
    # Check for backend URL in JS
    BACKEND_IN_JS=$(curl -s "$FRONTEND_URL$JS_FILE" | grep -o 'dentaflow-backend-staging[^"]*' | head -1)
    if [ -n "$BACKEND_IN_JS" ]; then
        echo "✅ Backend URL found in JS: $BACKEND_IN_JS"
    else
        echo "❌ Backend URL NOT found in JS"
    fi
    
    # Check for /api/v1/auth/login in JS
    LOGIN_ENDPOINT_IN_JS=$(curl -s "$FRONTEND_URL$JS_FILE" | grep -o '/api/v1/auth/login' | head -1)
    if [ -n "$LOGIN_ENDPOINT_IN_JS" ]; then
        echo "✅ Login endpoint found in JS: $LOGIN_ENDPOINT_IN_JS"
    else
        echo "❌ Login endpoint NOT found in JS"
    fi
fi
echo ""

# Test 5: CORS Headers
echo "📋 Test 5: CORS Headers"
echo "--------------------------------"
CORS_HEADERS=$(curl -s -I -X OPTIONS "$BACKEND_URL/api/v1/auth/login" \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type")

CORS_ALLOW_ORIGIN=$(echo "$CORS_HEADERS" | grep -i "access-control-allow-origin" | cut -d: -f2- | tr -d '\r\n ')
if [ -n "$CORS_ALLOW_ORIGIN" ]; then
    echo "✅ CORS Allow-Origin: $CORS_ALLOW_ORIGIN"
else
    echo "⚠️  CORS Allow-Origin: Not set"
fi

CORS_ALLOW_METHODS=$(echo "$CORS_HEADERS" | grep -i "access-control-allow-methods" | cut -d: -f2- | tr -d '\r\n ')
if [ -n "$CORS_ALLOW_METHODS" ]; then
    echo "✅ CORS Allow-Methods: $CORS_ALLOW_METHODS"
else
    echo "⚠️  CORS Allow-Methods: Not set"
fi
echo ""

# Test 6: DNS Resolution
echo "📋 Test 6: DNS Resolution"
echo "--------------------------------"
BACKEND_IP=$(dig +short dentaflow-backend-staging-688311017213.us-central1.run.app | tail -1)
if [ -n "$BACKEND_IP" ]; then
    echo "✅ Backend DNS: $BACKEND_IP"
else
    echo "❌ Backend DNS: FAILED"
fi

FRONTEND_IP=$(dig +short dentaflow-frontend-staging-688311017213.us-central1.run.app | tail -1)
if [ -n "$FRONTEND_IP" ]; then
    echo "✅ Frontend DNS: $FRONTEND_IP"
else
    echo "❌ Frontend DNS: FAILED"
fi
echo ""

# Test 7: SSL/TLS Certificate
echo "📋 Test 7: SSL/TLS Certificate"
echo "--------------------------------"
SSL_INFO=$(echo | openssl s_client -servername dentaflow-backend-staging-688311017213.us-central1.run.app -connect dentaflow-backend-staging-688311017213.us-central1.run.app:443 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null)
if [ -n "$SSL_INFO" ]; then
    echo "✅ SSL Certificate:"
    echo "$SSL_INFO" | sed 's/^/   /'
else
    echo "⚠️  SSL Certificate: Could not retrieve"
fi
echo ""

# Test 8: Cloud Run Revision
echo "📋 Test 8: Cloud Run Revision Status"
echo "--------------------------------"
FRONTEND_REVISION=$(gcloud run services describe dentaflow-frontend-staging --region=us-central1 --format="value(status.traffic[0].revisionName)" 2>/dev/null)
if [ -n "$FRONTEND_REVISION" ]; then
    echo "✅ Frontend Revision: $FRONTEND_REVISION"
else
    echo "❌ Frontend Revision: Could not retrieve"
fi

BACKEND_REVISION=$(gcloud run services describe dentaflow-backend-staging --region=us-central1 --format="value(status.traffic[0].revisionName)" 2>/dev/null)
if [ -n "$BACKEND_REVISION" ]; then
    echo "✅ Backend Revision: $BACKEND_REVISION"
else
    echo "❌ Backend Revision: Could not retrieve"
fi
echo ""

# Summary
echo "📊 Summary"
echo "=========="
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "Test completed at: $(date)"
echo ""
echo "💡 Next Steps:"
echo "1. If backend tests pass but frontend fails → Check browser console"
echo "2. If CORS headers missing → Check backend CORS configuration"
echo "3. If SSL issues → Check certificate validity"
echo "4. If DNS fails → Check Cloud Run service status"
