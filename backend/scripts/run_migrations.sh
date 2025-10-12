#!/bin/bash

#
# Database Migration Script
# 
# Automatically runs pending Alembic migrations
# Usage: ./scripts/run_migrations.sh [--dry-run]
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DentaFlow Database Migration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo -e "${RED}✗ Alembic is not installed${NC}"
    echo -e "${YELLOW}  Install it with: pip install alembic${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo -e "${YELLOW}  Please create .env file with database configuration${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}✗ DATABASE_URL not set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment loaded${NC}"
echo -e "${BLUE}Database: ${DATABASE_URL%%@*}@...${NC}"
echo ""

# Check current migration status
echo -e "${YELLOW}Checking current migration status...${NC}"
alembic current

echo ""
echo -e "${YELLOW}Pending migrations:${NC}"
alembic history | head -20

echo ""

# Check if dry-run
if [ "$1" == "--dry-run" ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
    echo -e "${GREEN}✓ Dry run complete${NC}"
    exit 0
fi

# Ask for confirmation
echo -e "${YELLOW}Do you want to run pending migrations? (y/N)${NC}"
read -r response

if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Migration cancelled${NC}"
    exit 0
fi

# Run migrations
echo ""
echo -e "${BLUE}Running migrations...${NC}"

if alembic upgrade head; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Migrations completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Show current status
    echo ""
    echo -e "${BLUE}Current migration status:${NC}"
    alembic current
    
    exit 0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Migration failed!${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Please check the error above and fix any issues.${NC}"
    echo -e "${YELLOW}You can rollback with: alembic downgrade -1${NC}"
    exit 1
fi

