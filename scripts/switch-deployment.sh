#!/bin/bash

###############################################################################
# Blue-Green Deployment Switch Script
#
# This script switches traffic between blue and green environments by:
# 1. Syncing the target environment to the active bucket
# 2. Invalidating CDN cache
# 3. Verifying the switch
# 4. Updating deployment state
#
# Usage:
#   ./switch-deployment.sh <blue|green>
#
# Example:
#   ./switch-deployment.sh green   # Switch to green
#   ./switch-deployment.sh blue    # Rollback to blue
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
BLUE_BUCKET="dentaflow-frontend-blue"
GREEN_BUCKET="dentaflow-frontend-green"
ACTIVE_BUCKET="dentaflow-frontend"
TRACKING_BUCKET="dentaflow-deployment-tracking"
CDN_URL_MAP="dentaflow-lb"

# Parse arguments
TARGET="${1:-}"

if [ -z "$TARGET" ]; then
    echo -e "${RED}Error: Target environment not specified${NC}"
    echo "Usage: $0 <blue|green>"
    exit 1
fi

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
    echo -e "${RED}Error: Invalid target. Must be 'blue' or 'green'${NC}"
    exit 1
fi

# Determine source bucket
if [ "$TARGET" = "blue" ]; then
    SOURCE_BUCKET=$BLUE_BUCKET
else
    SOURCE_BUCKET=$GREEN_BUCKET
fi

echo "========================================="
echo -e "${BLUE}Blue-Green Deployment Switch${NC}"
echo "========================================="
echo "Target: $TARGET"
echo "Source: gs://$SOURCE_BUCKET/"
echo "Active: gs://$ACTIVE_BUCKET/"
echo "========================================="
echo ""

###############################################################################
# Step 1: Download Current State
###############################################################################

echo -e "${YELLOW}[1/6] Checking current state...${NC}"

gsutil cp gs://$TRACKING_BUCKET/deployment-state.json deployment-state.json

CURRENT_ACTIVE=$(jq -r '.active' deployment-state.json)

echo "Current active: $CURRENT_ACTIVE"

if [ "$CURRENT_ACTIVE" = "$TARGET" ]; then
    echo -e "${YELLOW}⚠ Target environment is already active${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""

###############################################################################
# Step 2: Verify Source Bucket
###############################################################################

echo -e "${YELLOW}[2/6] Verifying source bucket...${NC}"

if ! gsutil ls gs://$SOURCE_BUCKET/index.html > /dev/null 2>&1; then
    echo -e "${RED}✗ Source bucket is empty or index.html not found${NC}"
    exit 1
fi

# Get bundle hash
BUNDLE_HASH=$(gsutil cat gs://$SOURCE_BUCKET/index.html | grep -o 'index-[^.]*\.js' | head -1 | sed 's/index-//;s/\.js//')

if [ -z "$BUNDLE_HASH" ]; then
    echo -e "${RED}✗ Could not extract bundle hash from source${NC}"
    exit 1
fi

echo "Bundle hash: $BUNDLE_HASH"
echo -e "${GREEN}✓ Source bucket verified${NC}"

echo ""

###############################################################################
# Step 3: Backup Current Active
###############################################################################

echo -e "${YELLOW}[3/6] Backing up current active...${NC}"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="gs://dentaflow-frontend-backups/switch-$TIMESTAMP"

echo "Creating backup at: $BACKUP_PATH"
gsutil -m rsync -r gs://$ACTIVE_BUCKET/ $BACKUP_PATH/

echo -e "${GREEN}✓ Backup created${NC}"

echo ""

###############################################################################
# Step 4: Switch Traffic
###############################################################################

echo -e "${YELLOW}[4/6] Switching traffic to $TARGET...${NC}"

echo "Syncing $SOURCE_BUCKET to $ACTIVE_BUCKET..."
gsutil -m rsync -r -d gs://$SOURCE_BUCKET/ gs://$ACTIVE_BUCKET/

echo "Setting cache headers..."
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
    "gs://$ACTIVE_BUCKET/assets/**" 2>/dev/null || true

gsutil setmeta -h "Cache-Control:no-cache, no-store, must-revalidate" \
    "gs://$ACTIVE_BUCKET/index.html"

echo -e "${GREEN}✓ Traffic switched${NC}"

echo ""

###############################################################################
# Step 5: Invalidate CDN Cache
###############################################################################

echo -e "${YELLOW}[5/6] Invalidating CDN cache...${NC}"

if gcloud compute url-maps invalidate-cdn-cache $CDN_URL_MAP --path "/*" --async 2>/dev/null; then
    echo -e "${GREEN}✓ CDN cache invalidation initiated${NC}"
else
    echo -e "${YELLOW}⚠ CDN invalidation failed or CDN not configured${NC}"
fi

echo ""

###############################################################################
# Step 6: Update State
###############################################################################

echo -e "${YELLOW}[6/6] Updating deployment state...${NC}"

# Update state file
jq --arg target "$TARGET" \
   --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
   --arg hash "$BUNDLE_HASH" \
   --arg previous "$CURRENT_ACTIVE" \
   '.active = $target | 
    .[$target].status = "active" | 
    .[$target].last_switched = $timestamp |
    .[$previous].status = "standby" |
    .history += [{
      "timestamp": $timestamp,
      "action": "switch",
      "from": $previous,
      "to": $target,
      "bundle_hash": $hash
    }]' deployment-state.json > deployment-state-new.json

mv deployment-state-new.json deployment-state.json

# Upload updated state
gsutil cp deployment-state.json gs://$TRACKING_BUCKET/deployment-state.json

echo -e "${GREEN}✓ State updated${NC}"

echo ""

###############################################################################
# Verification
###############################################################################

echo -e "${YELLOW}Verifying switch...${NC}"

sleep 10

ACTIVE_HASH=$(gsutil cat gs://$ACTIVE_BUCKET/index.html | grep -o 'index-[^.]*\.js' | head -1 | sed 's/index-//;s/\.js//')

if [ "$ACTIVE_HASH" = "$BUNDLE_HASH" ]; then
    echo -e "${GREEN}✓ Switch verified${NC}"
else
    echo -e "${RED}✗ Verification failed!${NC}"
    echo "Expected: $BUNDLE_HASH"
    echo "Got: $ACTIVE_HASH"
    exit 1
fi

echo ""

###############################################################################
# Summary
###############################################################################

echo "========================================="
echo -e "${GREEN}✅ Switch Successful!${NC}"
echo "========================================="
echo "Active Environment: $TARGET"
echo "Bundle Hash: $BUNDLE_HASH"
echo "Backup: $BACKUP_PATH"
echo "Timestamp: $TIMESTAMP"
echo ""
echo "The $TARGET environment is now serving traffic."
echo ""
echo "To rollback:"
echo "  ./switch-deployment.sh $CURRENT_ACTIVE"
echo "========================================="

exit 0

