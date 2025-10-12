#!/bin/bash

echo "🧪 DentaFlow Deployment Test Suite"
echo "=================================="
echo ""

API_URL="https://8000-if3mzj7ip62gvqnshd5a5-bd825c8a.manusvm.computer"

# Test 1: Health Check
echo "Test 1: Health Check"
response=$(curl -s "$API_URL/health")
if echo "$response" | grep -q "healthy"; then
    echo "✅ PASSED - Health check successful"
else
    echo "❌ FAILED - Health check failed"
fi
echo ""

# Test 2: Root Endpoint
echo "Test 2: Root Endpoint"
response=$(curl -s "$API_URL/")
if echo "$response" | grep -q "DentalAI API"; then
    echo "✅ PASSED - Root endpoint working"
else
    echo "❌ FAILED - Root endpoint failed"
fi
echo ""

# Test 3: OpenAPI Spec
echo "Test 3: OpenAPI Specification"
response=$(curl -s "$API_URL/openapi.json")
if echo "$response" | grep -q "openapi"; then
    endpoint_count=$(echo "$response" | python3.11 -c "import sys, json; print(len(json.load(sys.stdin)['paths']))")
    echo "✅ PASSED - OpenAPI spec available ($endpoint_count endpoints)"
else
    echo "❌ FAILED - OpenAPI spec not available"
fi
echo ""

# Test 4: Swagger UI
echo "Test 4: Swagger Documentation"
response=$(curl -s "$API_URL/docs")
if echo "$response" | grep -q "swagger-ui"; then
    echo "✅ PASSED - Swagger UI accessible"
else
    echo "❌ FAILED - Swagger UI not accessible"
fi
echo ""

# Test 5: ReDoc
echo "Test 5: ReDoc Documentation"
response=$(curl -s "$API_URL/redoc")
if echo "$response" | grep -q "redoc"; then
    echo "✅ PASSED - ReDoc accessible"
else
    echo "❌ FAILED - ReDoc not accessible"
fi
echo ""

# Test 6: API Status
echo "Test 6: API Status Endpoint"
response=$(curl -s "$API_URL/api/v1/status")
if [ ! -z "$response" ]; then
    echo "✅ PASSED - API status endpoint responding"
else
    echo "❌ FAILED - API status endpoint not responding"
fi
echo ""

echo "=================================="
echo "✅ Deployment Test Suite Complete"
echo "=================================="
