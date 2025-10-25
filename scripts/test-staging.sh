#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 DentaFlow Staging Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="dentaflow-production"
REGION="us-central1"
SERVICE_NAME="dentaflow-backend-staging"

# Get staging URL
echo "Getting staging service URL..."
STAGING_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format='value(status.url)' 2>/dev/null)

if [ -z "$STAGING_URL" ]; then
    echo -e "${RED}❌ Error: Could not get staging URL. Is the service deployed?${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Staging URL: $STAGING_URL${NC}"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name=$1
    local test_command=$2
    local expected_status=${3:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Test $TOTAL_TESTS: $test_name... "
    
    HTTP_STATUS=$(eval "$test_command" 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $HTTP_STATUS)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected $expected_status, got $HTTP_STATUS)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 Health & Status Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Health endpoint" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/health"
run_test "API documentation" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/docs"
run_test "OpenAPI schema" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/openapi.json"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 Authentication Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Login endpoint exists" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/api/v1/auth/login" "422"
run_test "Register endpoint exists" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/api/v1/auth/register" "422"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 API Endpoints Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Patients endpoint (requires auth)" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/api/v1/patients" "401"
run_test "Appointments endpoint (requires auth)" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/api/v1/appointments" "401"
run_test "Treatments endpoint (requires auth)" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/api/v1/treatments" "401"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 AI Agent Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Chat endpoint (requires auth)" "curl -s -o /dev/null -w '%{http_code}' $STAGING_URL/api/v1/chat" "401"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 Security Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test CORS headers
echo -n "Test: CORS headers... "
CORS_HEADER=$(curl -s -I -X OPTIONS "$STAGING_URL/api/v1/patients" \
    -H "Origin: https://dentaflow.ai" \
    -H "Access-Control-Request-Method: GET" | grep -i "access-control-allow-origin" || echo "")

if [ ! -z "$CORS_HEADER" ]; then
    echo -e "${GREEN}✅ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (CORS headers not found)"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test rate limiting (if implemented)
echo -n "Test: Rate limiting headers... "
RATE_LIMIT=$(curl -s -I "$STAGING_URL/health" | grep -i "x-ratelimit" || echo "")

if [ ! -z "$RATE_LIMIT" ]; then
    echo -e "${GREEN}✅ PASSED${NC} (Rate limiting active)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} (Rate limiting not detected)"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 Performance Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test response time
echo -n "Test: Response time... "
RESPONSE_TIME=$(curl -s -o /dev/null -w '%{time_total}' "$STAGING_URL/health")
RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc)

if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
    echo -e "${GREEN}✅ PASSED${NC} (${RESPONSE_TIME_MS}ms)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  SLOW${NC} (${RESPONSE_TIME_MS}ms)"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

PASS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
echo "Pass Rate: ${PASS_RATE}%"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "🎯 Staging environment is ready!"
    echo ""
    echo "Next steps:"
    echo "1. Run integration tests: cd backend && pytest"
    echo "2. Perform manual QA testing"
    echo "3. If all tests pass, merge to main for production deployment"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failures above and fix before deploying to production."
    echo ""
    exit 1
fi

