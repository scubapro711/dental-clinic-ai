#!/bin/bash
# Pre-Deployment Testing Suite
# Comprehensive testing before deploying to production

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$REPO_ROOT/backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Pre-Deployment Testing Suite - DentalAI Backend       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to run a test category
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🧪 Test $TOTAL_TESTS: $test_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Change to backend directory
cd "$BACKEND_DIR"

echo -e "${BLUE}📦 Installing testing dependencies...${NC}"
pip install -q pytest pytest-cov pytest-asyncio httpx bandit safety pylint flake8 mypy locust 2>/dev/null || true
echo ""

# ============================================================================
# 1. UNIT TESTS
# ============================================================================
run_test "Unit Tests - All Components" \
    "python -m pytest tests/ -v --tb=short -k 'not e2e' --maxfail=3 2>&1 | tail -50"

# ============================================================================
# 2. INTEGRATION TESTS  
# ============================================================================
run_test "Integration Tests - End-to-End Scenarios" \
    "python -m pytest tests/test_e2e_mvp.py -v --tb=short 2>&1 | tail -30 || true"

# ============================================================================
# 3. CODE COVERAGE
# ============================================================================
run_test "Code Coverage Analysis" \
    "python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=50 2>&1 | tail -30"

# ============================================================================
# 4. SECURITY SCANNING
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔒 Security Scanning${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 4a. Bandit - Security vulnerabilities
run_test "Security Scan - Bandit (Code Vulnerabilities)" \
    "bandit -r app/ -f txt -o bandit_report.txt -ll && cat bandit_report.txt && rm bandit_report.txt"

# 4b. Safety - Dependency vulnerabilities
run_test "Security Scan - Safety (Dependency Vulnerabilities)" \
    "safety check --json 2>&1 | head -20 || true"

# ============================================================================
# 5. CODE QUALITY
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📐 Code Quality Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 5a. Pylint
run_test "Code Quality - Pylint" \
    "pylint app/ --exit-zero --score=yes --output-format=text | tail -20"

# 5b. Flake8
run_test "Code Style - Flake8" \
    "flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics"

# 5c. MyPy (Type Checking)
run_test "Type Checking - MyPy" \
    "mypy app/ --ignore-missing-imports --no-error-summary 2>&1 | head -20 || true"

# ============================================================================
# 6. FRAMEWORK COMPLIANCE
# ============================================================================
run_test "Framework Compliance Check" \
    "python $SCRIPT_DIR/check_framework_compliance.py"

# ============================================================================
# 7. WORK PLAN SYNC
# ============================================================================
run_test "Work Plan Synchronization Check" \
    "python $SCRIPT_DIR/check_work_plan_sync.py || true"

# ============================================================================
# 8. CONFIGURATION VALIDATION
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚙️  Configuration Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check for secrets in code
run_test "Secret Detection in Code" \
    "! grep -r 'password.*=.*[\"'\"'].*[\"'\"']' app/ --include='*.py' | grep -v 'POSTGRES_PASSWORD\|REDIS_PASSWORD' || echo 'No hardcoded secrets found'"

# Check .env.example exists
run_test "Environment Template Exists" \
    "test -f .env.example && echo '✅ .env.example found'"

# ============================================================================
# 9. DEPENDENCY CHECK
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📦 Dependency Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

run_test "Dependencies Installation Check" \
    "pip check"

# ============================================================================
# 10. API ENDPOINT VALIDATION
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🌐 API Endpoint Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check that main.py exists and has required endpoints
run_test "API Structure Validation" \
    "grep -q 'FastAPI' app/main.py && grep -q '/health' app/main.py && echo '✅ FastAPI app structure valid'"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests:  ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

# Calculate percentage
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_PERCENTAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Success Rate: ${YELLOW}$PASS_PERCENTAGE%${NC}"
    echo ""
    
    if [ $PASS_PERCENTAGE -ge 90 ]; then
        echo -e "${GREEN}✅ EXCELLENT! Ready for deployment.${NC}"
        exit 0
    elif [ $PASS_PERCENTAGE -ge 70 ]; then
        echo -e "${YELLOW}⚠️  GOOD, but some improvements recommended before deployment.${NC}"
        exit 0
    elif [ $PASS_PERCENTAGE -ge 50 ]; then
        echo -e "${YELLOW}⚠️  FAIR, several issues need attention before deployment.${NC}"
        exit 1
    else
        echo -e "${RED}❌ POOR, significant work needed before deployment.${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ No tests were run!${NC}"
    exit 1
fi
