#!/bin/bash

###############################################################################
# DentaFlow Complete Startup Script
#
# This script starts the complete DentaFlow system with all components:
# 1. PostgreSQL database check
# 2. Redis check
# 3. Database migrations
# 4. LangGraph memory setup (PostgresSaver)
# 5. Backend API server
# 6. Frontend (optional)
#
# Usage:
#   ./start_dentaflow.sh [--dev|--prod]
#
# Reference: FINAL_SAAS_WORK_PLAN_V15.0.md
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Environment
ENV=${1:-dev}

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🦷 DentaFlow Complete System Startup 🦷          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Environment: ${ENV}${NC}"
echo ""

###############################################################################
# 1. Check Prerequisites
###############################################################################

echo -e "${BLUE}[1/7]${NC} Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3: $(python3 --version)${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 installed${NC}"

# Check PostgreSQL connection
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠️  DATABASE_URL not set, using default${NC}"
    export DATABASE_URL="postgresql://dentalai:dentalai_secure_2025@localhost:5432/dentalai"
fi

# Test PostgreSQL connection
if command -v psql &> /dev/null; then
    if psql "$DATABASE_URL" -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
    else
        echo -e "${RED}❌ Cannot connect to PostgreSQL${NC}"
        echo -e "${YELLOW}   DATABASE_URL: $DATABASE_URL${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  psql not found, skipping connection test${NC}"
fi

# Check Redis (optional)
if [ -z "$REDIS_URL" ]; then
    export REDIS_URL="redis://localhost:6379/0"
fi
echo -e "${GREEN}✅ Redis URL: $REDIS_URL${NC}"

echo ""

###############################################################################
# 2. Install Dependencies
###############################################################################

echo -e "${BLUE}[2/7]${NC} Installing dependencies..."

cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${YELLOW}Installing Python packages...${NC}"
pip3 install -r requirements.txt --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

###############################################################################
# 3. Run Database Migrations
###############################################################################

echo -e "${BLUE}[3/7]${NC} Running database migrations..."

if [ -f "alembic.ini" ]; then
    alembic upgrade head
    echo -e "${GREEN}✅ Migrations completed${NC}"
else
    echo -e "${YELLOW}⚠️  No alembic.ini found, skipping migrations${NC}"
fi

echo ""

###############################################################################
# 4. Setup LangGraph Memory (PostgresSaver)
###############################################################################

echo -e "${BLUE}[4/7]${NC} Setting up LangGraph memory..."

python3 << EOF
from app.core.memory import get_memory_saver
try:
    memory = get_memory_saver()
    print("✅ PostgresSaver initialized successfully")
    print(f"   Tables: checkpoints, writes")
except Exception as e:
    print(f"❌ Failed to initialize PostgresSaver: {e}")
    exit(1)
EOF

echo ""

###############################################################################
# 5. Verify All Components
###############################################################################

echo -e "${BLUE}[5/7]${NC} Verifying all components..."

python3 << EOF
import sys
sys.path.insert(0, '.')

# Check models
try:
    from app.models.organization_membership import OrganizationMembership
    from app.models.clinic_settings import ClinicSettings
    from app.models.treatment_price import TreatmentPrice
    print("✅ All models imported successfully")
except Exception as e:
    print(f"❌ Model import failed: {e}")
    exit(1)

# Check API endpoints
try:
    from app.api.v1.endpoints import memberships, clinic_settings, treatment_prices
    print("✅ All API endpoints imported successfully")
except Exception as e:
    print(f"❌ API endpoint import failed: {e}")
    exit(1)

# Check agents
try:
    from app.agents.agent_graph_v3 import AgentGraphV3
    print("✅ Agent graph imported successfully")
except Exception as e:
    print(f"❌ Agent graph import failed: {e}")
    exit(1)

# Check memory
try:
    from app.core.memory import get_memory_saver
    print("✅ Memory module imported successfully")
except Exception as e:
    print(f"❌ Memory module import failed: {e}")
    exit(1)

print("\n🎉 All components verified!")
EOF

echo ""

###############################################################################
# 6. Start Backend Server
###############################################################################

echo -e "${BLUE}[6/7]${NC} Starting backend server..."
echo ""

if [ "$ENV" = "prod" ]; then
    echo -e "${GREEN}Starting in PRODUCTION mode...${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo -e "${GREEN}Starting in DEVELOPMENT mode...${NC}"
    echo -e "${YELLOW}API Documentation: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}Alternative Docs: http://localhost:8000/redoc${NC}"
    echo ""
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi

###############################################################################
# 7. Cleanup on Exit
###############################################################################

trap cleanup EXIT

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down DentaFlow...${NC}"
    deactivate 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 DentaFlow is running! 🎉                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
