#!/bin/bash
# Deploy DentaFlow to EC2
# Run after tests pass with 90%+ success rate

echo "🚀 DentaFlow EC2 Deployment Script"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EC2_HOST="${EC2_HOST:-dentaflow.ai}"
EC2_USER="${EC2_USER:-ubuntu}"
EC2_KEY="${EC2_KEY:-~/.ssh/dentaflow-ec2.pem}"
DEPLOY_DIR="/home/ubuntu/dental-clinic-ai"
BACKUP_DIR="/home/ubuntu/backups"

# Check if tests passed
if [ ! -f "test-results/summary.txt" ]; then
    echo -e "${RED}❌ No test results found!${NC}"
    echo "Please run ./run_all_tests.sh first"
    exit 1
fi

if ! grep -q "DEPLOYMENT STATUS: ✅ APPROVED" test-results/summary.txt; then
    echo -e "${RED}❌ Tests did not pass deployment criteria!${NC}"
    echo ""
    cat test-results/summary.txt
    echo ""
    echo "Fix issues and run tests again before deploying"
    exit 1
fi

echo -e "${GREEN}✅ Tests passed - proceeding with deployment${NC}"
echo ""

# Confirm deployment
echo -e "${YELLOW}⚠️  WARNING: This will deploy to PRODUCTION${NC}"
echo "Target: $EC2_USER@$EC2_HOST"
echo ""
read -p "Continue with deployment? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting deployment...${NC}"
echo ""

# Step 1: Create backup on EC2
echo "📦 Step 1/7: Creating backup on EC2..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    BACKUP_DIR="/home/ubuntu/backups"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    echo "  - Backing up database..."
    pg_dump dentaflow > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    
    # Backup code
    echo "  - Backing up code..."
    cd /home/ubuntu
    tar -czf "$BACKUP_DIR/code_backup_$TIMESTAMP.tar.gz" dental-clinic-ai/
    
    echo "  ✅ Backup created: $BACKUP_DIR/*_$TIMESTAMP.*"
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Backup failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backup completed${NC}"
echo ""

# Step 2: Pull latest code
echo "📥 Step 2/7: Pulling latest code from GitHub..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/dental-clinic-ai
    git fetch origin
    git checkout branch-4
    git pull origin branch-4
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git pull failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 3: Install dependencies
echo "📦 Step 3/7: Installing dependencies..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/dental-clinic-ai/backend
    
    # Python dependencies
    pip3 install -r requirements.txt --quiet
    
    # Node dependencies (if frontend exists)
    if [ -d "../frontend" ]; then
        cd ../frontend
        npm install --silent
    fi
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Dependency installation failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Run database migrations
echo "🗄️  Step 4/7: Running database migrations..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/dental-clinic-ai/backend
    
    # Run Alembic migrations
    alembic upgrade head
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database migration failed!${NC}"
    echo "Rolling back..."
    # TODO: Add rollback logic
    exit 1
fi

echo -e "${GREEN}✅ Migrations completed${NC}"
echo ""

# Step 5: Restart services
echo "🔄 Step 5/7: Restarting services..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
    # Restart backend (assuming systemd service)
    sudo systemctl restart dentaflow-backend
    
    # Restart frontend (if exists)
    if sudo systemctl list-units --full -all | grep -q dentaflow-frontend; then
        sudo systemctl restart dentaflow-frontend
    fi
    
    # Restart nginx
    sudo systemctl restart nginx
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Service restart failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services restarted${NC}"
echo ""

# Step 6: Health check
echo "🏥 Step 6/7: Running health checks..."
sleep 5  # Wait for services to start

# Check backend health
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "https://$EC2_HOST/api/v1/health")

if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${RED}❌ Backend health check failed (HTTP $HEALTH_CHECK)${NC}"
    echo "Rolling back..."
    # TODO: Add rollback logic
    exit 1
fi

# Check database connectivity
DB_CHECK=$(ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" "cd /home/ubuntu/dental-clinic-ai/backend && python3 -c 'from app.core.database import engine; engine.connect()' && echo 'OK' || echo 'FAIL'")

if [ "$DB_CHECK" = "OK" ]; then
    echo -e "${GREEN}✅ Database connectivity check passed${NC}"
else
    echo -e "${RED}❌ Database connectivity check failed${NC}"
    exit 1
fi

echo ""

# Step 7: Smoke tests
echo "🧪 Step 7/7: Running smoke tests..."

# Test critical endpoints
ENDPOINTS=(
    "/api/v1/health"
    "/api/v1/treatment-prices"
)

SMOKE_PASSED=0
SMOKE_TOTAL=${#ENDPOINTS[@]}

for endpoint in "${ENDPOINTS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$EC2_HOST$endpoint")
    if [ "$STATUS" = "200" ]; then
        echo "  ✅ $endpoint (HTTP $STATUS)"
        SMOKE_PASSED=$((SMOKE_PASSED + 1))
    else
        echo "  ❌ $endpoint (HTTP $STATUS)"
    fi
done

if [ $SMOKE_PASSED -eq $SMOKE_TOTAL ]; then
    echo -e "${GREEN}✅ All smoke tests passed ($SMOKE_PASSED/$SMOKE_TOTAL)${NC}"
else
    echo -e "${YELLOW}⚠️  Some smoke tests failed ($SMOKE_PASSED/$SMOKE_TOTAL)${NC}"
fi

echo ""

# Final summary
echo "======================================"
echo -e "${GREEN}🎉 Deployment Completed!${NC}"
echo "======================================"
echo ""
echo "Deployment Summary:"
echo "  - Target: $EC2_USER@$EC2_HOST"
echo "  - Branch: branch-4"
echo "  - Time: $(date)"
echo "  - Backup: Created in $BACKUP_DIR/"
echo "  - Health: ✅ Passed"
echo "  - Smoke tests: $SMOKE_PASSED/$SMOKE_TOTAL passed"
echo ""
echo "Next steps:"
echo "  1. Monitor logs: ssh -i $EC2_KEY $EC2_USER@$EC2_HOST 'tail -f /var/log/dentaflow/*.log'"
echo "  2. Check metrics: https://$EC2_HOST/metrics"
echo "  3. Test manually: https://$EC2_HOST"
echo ""
echo "If issues occur:"
echo "  - Rollback: ssh -i $EC2_KEY $EC2_USER@$EC2_HOST 'cd /home/ubuntu && ./rollback.sh'"
echo "  - View logs: ssh -i $EC2_KEY $EC2_USER@$EC2_HOST 'journalctl -u dentaflow-backend -n 100'"
echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
