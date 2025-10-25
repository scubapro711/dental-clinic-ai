#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DentaFlow Staging Environment Setup"
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
STAGING_DB_INSTANCE="dentaflow-db-staging"
STAGING_DB_NAME="dentaflow_staging"
STAGING_SERVICE="dentaflow-backend-staging"

echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  DB Instance: $STAGING_DB_INSTANCE"
echo "  Service: $STAGING_SERVICE"
echo ""

# Step 1: Create staging branch
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Creating staging branch"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git show-ref --verify --quiet refs/heads/staging; then
    echo -e "${YELLOW}⚠️  Staging branch already exists${NC}"
    git checkout staging
    git pull origin main
else
    echo -e "${GREEN}✅ Creating new staging branch from main${NC}"
    git checkout -b staging
fi

echo ""

# Step 2: Create GCP secrets for staging
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Creating GCP Secrets for Staging"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        echo -e "${YELLOW}⚠️  Secret $secret_name already exists, updating...${NC}"
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --project="$PROJECT_ID" \
            --data-file=-
    else
        echo -e "${GREEN}✅ Creating secret $secret_name${NC}"
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=-
    fi
}

# Generate random secrets for staging
SECRET_KEY_STAGING=$(openssl rand -hex 32)
JWT_SECRET_STAGING=$(openssl rand -hex 32)

echo "Creating staging secrets..."
create_secret "secret-key-staging" "$SECRET_KEY_STAGING"
create_secret "jwt-secret-staging" "$JWT_SECRET_STAGING"

# Note: Database URL will be created after DB setup
echo -e "${YELLOW}⚠️  Note: database-url-staging needs to be created after DB setup${NC}"
echo -e "${YELLOW}⚠️  Note: Other secrets (redis, telegram) can reuse production or be created separately${NC}"

echo ""

# Step 3: Create Cloud SQL instance for staging
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Creating Cloud SQL Instance (Staging)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud sql instances describe "$STAGING_DB_INSTANCE" --project="$PROJECT_ID" &>/dev/null; then
    echo -e "${YELLOW}⚠️  Cloud SQL instance $STAGING_DB_INSTANCE already exists${NC}"
else
    echo -e "${GREEN}✅ Creating Cloud SQL instance (this may take 5-10 minutes)...${NC}"
    
    gcloud sql instances create "$STAGING_DB_INSTANCE" \
        --project="$PROJECT_ID" \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region="$REGION" \
        --network=default \
        --no-assign-ip \
        --database-flags=max_connections=100 \
        --backup \
        --backup-start-time=03:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --maintenance-release-channel=production
    
    echo -e "${GREEN}✅ Cloud SQL instance created${NC}"
fi

echo ""

# Step 4: Create database
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Creating Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud sql databases describe "$STAGING_DB_NAME" \
    --instance="$STAGING_DB_INSTANCE" \
    --project="$PROJECT_ID" &>/dev/null; then
    echo -e "${YELLOW}⚠️  Database $STAGING_DB_NAME already exists${NC}"
else
    echo -e "${GREEN}✅ Creating database $STAGING_DB_NAME${NC}"
    gcloud sql databases create "$STAGING_DB_NAME" \
        --instance="$STAGING_DB_INSTANCE" \
        --project="$PROJECT_ID"
fi

echo ""

# Step 5: Set database password
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Setting Database Password"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DB_PASSWORD=$(openssl rand -base64 32)
echo -e "${GREEN}✅ Setting postgres user password${NC}"
gcloud sql users set-password postgres \
    --instance="$STAGING_DB_INSTANCE" \
    --project="$PROJECT_ID" \
    --password="$DB_PASSWORD"

# Create database URL secret
DB_CONNECTION_NAME="$PROJECT_ID:$REGION:$STAGING_DB_INSTANCE"
DATABASE_URL="postgresql://postgres:$DB_PASSWORD@/$STAGING_DB_NAME?host=/cloudsql/$DB_CONNECTION_NAME"

create_secret "database-url-staging" "$DATABASE_URL"
create_secret "checkpoint-database-url-staging" "$DATABASE_URL"

echo ""

# Step 6: Run database migrations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Running Database Migrations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}⚠️  Note: Migrations should be run after first deployment${NC}"
echo "Run this command after staging service is deployed:"
echo ""
echo "  gcloud run jobs execute dentaflow-migration-staging \\"
echo "    --region=$REGION \\"
echo "    --project=$PROJECT_ID"
echo ""

# Step 7: Push staging branch
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 7: Pushing Staging Branch"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${GREEN}✅ Pushing staging branch to GitHub${NC}"
git push -u origin staging

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ STAGING ENVIRONMENT SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Summary:"
echo "  ✅ Staging branch created"
echo "  ✅ GCP secrets created"
echo "  ✅ Cloud SQL instance created: $STAGING_DB_INSTANCE"
echo "  ✅ Database created: $STAGING_DB_NAME"
echo "  ✅ Database URL secret created"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. GitHub Actions will automatically deploy to staging when you push to staging branch"
echo ""
echo "2. After deployment, verify staging service:"
echo "   gcloud run services describe $STAGING_SERVICE --region=$REGION --project=$PROJECT_ID"
echo ""
echo "3. Get staging URL:"
echo "   gcloud run services describe $STAGING_SERVICE --region=$REGION --format='value(status.url)'"
echo ""
echo "4. Run tests against staging:"
echo "   ./scripts/test-staging.sh"
echo ""
echo "5. If all tests pass, merge staging to main:"
echo "   git checkout main"
echo "   git merge staging"
echo "   git push origin main"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

