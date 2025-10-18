#!/bin/bash

###############################################################################
# Deploy to Green Environment Script
#
# This script deploys the frontend to the green (standby) environment:
# 1. Builds the frontend
# 2. Deploys to green bucket
# 3. Verifies deployment
# 4. Updates deployment state
#
# This allows testing the new version before switching traffic.
#
# Usage:
#   ./deploy-to-green.sh [--skip-build]
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID="dentaflow-production"
GREEN_BUCKET="dentaflow-frontend-green"
TRACKING_BUCKET="dentaflow-deployment-tracking"
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../frontend" && pwd)"

# Parse arguments
SKIP_BUILD=false

for arg in "$@"; do
    case $arg in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
    esac
done

TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "========================================="
echo -e "${BLUE}Deploy to Green Environment${NC}"
echo "========================================="
echo "Target: gs://$GREEN_BUCKET/"
echo "Timestamp: $TIMESTAMP"
echo "========================================="
echo ""

###############################################################################
# Step 1: Build Frontend
###############################################################################

if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}[1/5] Building frontend...${NC}"
    cd "$FRONTEND_DIR"
    
    echo "Installing dependencies..."
    npm ci --quiet
    
    echo "Building production bundle..."
    npm run build
    
    if [ ! -d "dist" ]; then
        echo -e "${RED}✗ Build failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Build completed${NC}"
    echo ""
else
    echo -e "${YELLOW}[1/5] Skipping build${NC}"
    echo ""
fi

###############################################################################
# Step 2: Deploy to Green Bucket
###############################################################################

echo -e "${YELLOW}[2/5] Deploying to green bucket...${NC}"

cd "$FRONTEND_DIR"

echo "Uploading files to gs://$GREEN_BUCKET/..."
gsutil -m rsync -r -d dist/ gs://$GREEN_BUCKET/

echo "Setting cache headers..."
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
    "gs://$GREEN_BUCKET/assets/**" 2>/dev/null || true

gsutil setmeta -h "Cache-Control:no-cache, no-store, must-revalidate" \
    "gs://$GREEN_BUCKET/index.html"

echo -e "${GREEN}✓ Deployment completed${NC}"
echo ""

###############################################################################
# Step 3: Verify Deployment
###############################################################################

echo -e "${YELLOW}[3/5] Verifying deployment...${NC}"

# Extract bundle hash
BUNDLE_HASH=$(gsutil cat gs://$GREEN_BUCKET/index.html | grep -o 'index-[^.]*\.js' | head -1 | sed 's/index-//;s/\.js//')

if [ -z "$BUNDLE_HASH" ]; then
    echo -e "${RED}✗ Could not extract bundle hash${NC}"
    exit 1
fi

echo "Bundle hash: $BUNDLE_HASH"

# Verify bundle exists
if ! gsutil ls gs://$GREEN_BUCKET/assets/index-$BUNDLE_HASH.js > /dev/null 2>&1; then
    echo -e "${RED}✗ Bundle file not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Deployment verified${NC}"
echo ""

###############################################################################
# Step 4: Update State
###############################################################################

echo -e "${YELLOW}[4/5] Updating deployment state...${NC}"

# Download current state
gsutil cp gs://$TRACKING_BUCKET/deployment-state.json deployment-state.json 2>/dev/null || \
    echo '{"active":"blue","blue":{},"green":{},"history":[]}' > deployment-state.json

# Update state
jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
   --arg hash "$BUNDLE_HASH" \
   '.green.last_deployed = $timestamp |
    .green.version = $hash |
    .green.status = "standby" |
    .history += [{
      "timestamp": $timestamp,
      "action": "deploy_to_green",
      "bundle_hash": $hash
    }]' deployment-state.json > deployment-state-new.json

mv deployment-state-new.json deployment-state.json

# Upload updated state
gsutil cp deployment-state.json gs://$TRACKING_BUCKET/deployment-state.json

echo -e "${GREEN}✓ State updated${NC}"
echo ""

###############################################################################
# Step 5: Test Instructions
###############################################################################

echo -e "${YELLOW}[5/5] Testing instructions${NC}"

GREEN_URL="https://storage.googleapis.com/$GREEN_BUCKET/index.html"

echo ""
echo "Green environment deployed successfully!"
echo ""
echo "Test URL:"
echo "  $GREEN_URL"
echo ""
echo "To test in browser:"
echo "  1. Open: $GREEN_URL"
echo "  2. Verify functionality"
echo "  3. Check console for errors"
echo ""
echo "When ready to switch traffic:"
echo "  ./switch-deployment.sh green"
echo ""
echo "To rollback:"
echo "  ./switch-deployment.sh blue"
echo ""

###############################################################################
# Summary
###############################################################################

echo "========================================="
echo -e "${GREEN}✅ Green Deployment Complete!${NC}"
echo "========================================="
echo "Bucket: gs://$GREEN_BUCKET/"
echo "Bundle Hash: $BUNDLE_HASH"
echo "Status: STANDBY (not serving traffic)"
echo "Test URL: $GREEN_URL"
echo "========================================="

exit 0

