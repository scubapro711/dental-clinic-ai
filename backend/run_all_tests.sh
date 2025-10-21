#!/bin/bash
#
# DentaFlow SaaS - Comprehensive Test Runner
# ==========================================
# Runs all test suites with proper reporting
#

set -e

echo "========================================"
echo "DentaFlow SaaS - Comprehensive Testing"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create test results directory
mkdir -p test-results/{coverage,reports}

# Function to run test suite
run_test_suite() {
    local suite_name=$1
    local test_path=$2
    local markers=$3
    
    echo -e "${YELLOW}Running ${suite_name}...${NC}"
    
    if pytest "$test_path" -m "$markers" -v --tb=short; then
        echo -e "${GREEN}✅ ${suite_name} PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ ${suite_name} FAILED${NC}"
        return 1
    fi
}

# Track results
declare -A results

echo "1️⃣  Unit Tests - Models"
run_test_suite "Unit Tests (Models)" "app/tests/unit/models/" "unit and models" && results[unit_models]=1 || results[unit_models]=0
echo ""

echo "2️⃣  Unit Tests - Services"
run_test_suite "Unit Tests (Services)" "app/tests/unit/services/" "unit and services" && results[unit_services]=1 || results[unit_services]=0
echo ""

echo "3️⃣  Unit Tests - Agents"
run_test_suite "Unit Tests (Agents)" "app/tests/unit/agents/" "unit and agents" && results[unit_agents]=1 || results[unit_agents]=0
echo ""

echo "4️⃣  Integration Tests - API"
run_test_suite "Integration Tests (API)" "app/tests/integration/api/" "integration and api" && results[integration_api]=1 || results[integration_api]=0
echo ""

echo "5️⃣  Integration Tests - Services"
run_test_suite "Integration Tests (Services)" "app/tests/integration/services/" "integration and requires_external" && results[integration_services]=1 || results[integration_services]=0
echo ""

echo "6️⃣  E2E Tests (Critical)"
run_test_suite "E2E Tests (Critical)" "app/tests/e2e/" "e2e and critical" && results[e2e]=1 || results[e2e]=0
echo ""

echo "7️⃣  Security Tests"
run_test_suite "Security Tests" "app/tests/security/" "security" && results[security]=1 || results[security]=0
echo ""

echo "8️⃣  Regression Tests"
run_test_suite "Regression Tests" "app/tests/regression/" "regression and critical" && results[regression]=1 || results[regression]=0
echo ""

echo "9️⃣  Performance Tests (Quick)"
run_test_suite "Performance Tests" "app/tests/performance/" "performance and fast" && results[performance]=1 || results[performance]=0
echo ""

# Generate coverage report
echo "📊 Generating Coverage Report..."
pytest app/tests/ \
    --cov=app \
    --cov-report=html:test-results/coverage/html \
    --cov-report=xml:test-results/coverage/coverage.xml \
    --cov-report=term-missing:skip-covered \
    --cov-fail-under=80 \
    -v \
    -m "not slow" || true

echo ""
echo "========================================"
echo "Test Results Summary"
echo "========================================"

# Calculate pass rate
total=0
passed=0
for result in "${results[@]}"; do
    ((total++))
    ((passed+=result))
done

pass_rate=$((passed * 100 / total))

echo "Unit Tests (Models):       ${results[unit_models]}"
echo "Unit Tests (Services):     ${results[unit_services]}"
echo "Unit Tests (Agents):       ${results[unit_agents]}"
echo "Integration Tests (API):   ${results[integration_api]}"
echo "Integration Tests (Svcs):  ${results[integration_services]}"
echo "E2E Tests:                 ${results[e2e]}"
echo "Security Tests:            ${results[security]}"
echo "Regression Tests:          ${results[regression]}"
echo "Performance Tests:         ${results[performance]}"
echo ""
echo "Pass Rate: ${passed}/${total} (${pass_rate}%)"
echo ""

if [ "$pass_rate" -ge 90 ]; then
    echo -e "${GREEN}✅ EXCELLENT! All critical tests passed!${NC}"
    exit 0
elif [ "$pass_rate" -ge 70 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Some tests failed. Review required.${NC}"
    exit 1
else
    echo -e "${RED}❌ CRITICAL: Too many test failures!${NC}"
    exit 1
fi
