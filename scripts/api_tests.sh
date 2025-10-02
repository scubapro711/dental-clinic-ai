#!/bin/bash
# API Integration Tests
# Tests all API endpoints with real HTTP requests

set -e

API_URL="${API_URL:-http://localhost:8000}"
FAILED=0
PASSED=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              API Integration Tests                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Testing API: $API_URL${NC}"
echo ""

# Function to test an endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -e "${BLUE}Testing:${NC} $name"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC} - Status: $status_code"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC} - Expected: $expected_status, Got: $status_code"
        echo -e "${YELLOW}Response:${NC} $body"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Health & Status Endpoints${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "Health Check" "GET" "/health" "" "200"
test_endpoint "Root Endpoint" "GET" "/" "" "200"

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Chat Endpoints${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "Chat - Greeting" "POST" "/api/v1/chat" \
    '{"message":"שלום","conversation_id":"test-001"}' "200"

test_endpoint "Chat - Appointment Inquiry" "POST" "/api/v1/chat" \
    '{"message":"מתי יש תורים פנויים?","conversation_id":"test-002"}' "200"

test_endpoint "Chat - Price Inquiry" "POST" "/api/v1/chat" \
    '{"message":"כמה עולה ניקוי אבנית?","conversation_id":"test-003"}' "200"

test_endpoint "Chat - Medical Question" "POST" "/api/v1/chat" \
    '{"message":"יש לי כאב בשן","conversation_id":"test-004"}' "200"

test_endpoint "Chat - English" "POST" "/api/v1/chat" \
    '{"message":"Hello, I need an appointment","conversation_id":"test-005"}' "200"

test_endpoint "Chat - Empty Message (Should Fail)" "POST" "/api/v1/chat" \
    '{"message":"","conversation_id":"test-006"}' "422"

test_endpoint "Chat - Missing Conversation ID (Should Fail)" "POST" "/api/v1/chat" \
    '{"message":"test"}' "422"

# ============================================================================
# TELEGRAM ENDPOINTS
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Telegram Endpoints${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "Telegram Webhook (No Data)" "POST" "/api/v1/telegram/webhook" \
    '{}' "200"

# ============================================================================
# AUTHENTICATION ENDPOINTS (if implemented)
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Authentication Endpoints${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test if auth endpoints exist
curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/auth/register" > /dev/null 2>&1 && {
    test_endpoint "Register New User" "POST" "/api/v1/auth/register" \
        '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}' "200"
    
    test_endpoint "Login" "POST" "/api/v1/auth/login" \
        '{"username":"test@example.com","password":"Test123!"}' "200"
} || {
    echo -e "${YELLOW}ℹ️  Authentication endpoints not implemented yet${NC}"
    echo ""
}

# ============================================================================
# ERROR HANDLING
# ============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Error Handling${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_endpoint "404 - Non-existent Endpoint" "GET" "/api/v1/nonexistent" "" "404"

test_endpoint "405 - Wrong Method" "GET" "/api/v1/chat" "" "405"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
echo -e "Total Tests:  ${BLUE}$TOTAL${NC}"
echo -e "Passed:       ${GREEN}$PASSED${NC}"
echo -e "Failed:       ${RED}$FAILED${NC}"
echo ""

if [ $TOTAL -gt 0 ]; then
    PASS_PERCENTAGE=$((PASSED * 100 / TOTAL))
    echo -e "Success Rate: ${YELLOW}$PASS_PERCENTAGE%${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All API tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some API tests failed!${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ No tests were run!${NC}"
    exit 1
fi
