#!/bin/bash

###############################################################################
# Blue-Green Deployment Setup Script
#
# This script sets up the infrastructure for Blue-Green deployments:
# 1. Creates blue and green Cloud Storage buckets
# 2. Configures bucket permissions and settings
# 3. Sets up Load Balancer backend buckets
# 4. Creates deployment tracking file
#
# Usage:
#   ./setup-blue-green.sh
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
REGION="us-central1"

echo "========================================="
echo -e "${BLUE}Blue-Green Deployment Setup${NC}"
echo "========================================="
echo "Project: $PROJECT_ID"
echo "Blue Bucket: gs://$BLUE_BUCKET/"
echo "Green Bucket: gs://$GREEN_BUCKET/"
echo "Active Bucket: gs://$ACTIVE_BUCKET/"
echo "========================================="
echo ""

###############################################################################
# Step 1: Create Blue Bucket
###############################################################################

echo -e "${YELLOW}[1/5] Creating Blue bucket...${NC}"

if gsutil ls -b gs://$BLUE_BUCKET > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Blue bucket already exists${NC}"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BLUE_BUCKET/
    echo -e "${GREEN}✓ Blue bucket created${NC}"
fi

# Configure bucket
gsutil uniformbucketlevelaccess set on gs://$BLUE_BUCKET/
gsutil iam ch allUsers:objectViewer gs://$BLUE_BUCKET/
gsutil web set -m index.html -e 404.html gs://$BLUE_BUCKET/

echo ""

###############################################################################
# Step 2: Create Green Bucket
###############################################################################

echo -e "${YELLOW}[2/5] Creating Green bucket...${NC}"

if gsutil ls -b gs://$GREEN_BUCKET > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Green bucket already exists${NC}"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$GREEN_BUCKET/
    echo -e "${GREEN}✓ Green bucket created${NC}"
fi

# Configure bucket
gsutil uniformbucketlevelaccess set on gs://$GREEN_BUCKET/
gsutil iam ch allUsers:objectViewer gs://$GREEN_BUCKET/
gsutil web set -m index.html -e 404.html gs://$GREEN_BUCKET/

echo ""

###############################################################################
# Step 3: Initialize with Current Version
###############################################################################

echo -e "${YELLOW}[3/5] Initializing buckets...${NC}"

# Copy current production to blue bucket
if gsutil ls gs://$ACTIVE_BUCKET/index.html > /dev/null 2>&1; then
    echo "Copying current production to blue bucket..."
    gsutil -m rsync -r gs://$ACTIVE_BUCKET/ gs://$BLUE_BUCKET/
    echo -e "${GREEN}✓ Blue bucket initialized with current production${NC}"
else
    echo -e "${YELLOW}⚠ No current production to copy${NC}"
fi

echo ""

###############################################################################
# Step 4: Create Deployment State File
###############################################################################

echo -e "${YELLOW}[4/5] Creating deployment state file...${NC}"

STATE_FILE="deployment-state.json"

cat > $STATE_FILE <<EOF
{
  "active": "blue",
  "blue": {
    "bucket": "$BLUE_BUCKET",
    "last_deployed": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "version": "initial",
    "status": "active"
  },
  "green": {
    "bucket": "$GREEN_BUCKET",
    "last_deployed": null,
    "version": null,
    "status": "standby"
  },
  "history": []
}
EOF

echo "State file created: $STATE_FILE"
echo -e "${GREEN}✓ Deployment state initialized${NC}"

echo ""

###############################################################################
# Step 5: Create Deployment Tracking Bucket
###############################################################################

echo -e "${YELLOW}[5/5] Setting up deployment tracking...${NC}"

TRACKING_BUCKET="dentaflow-deployment-tracking"

if gsutil ls -b gs://$TRACKING_BUCKET > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Tracking bucket already exists${NC}"
else
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$TRACKING_BUCKET/
    echo -e "${GREEN}✓ Tracking bucket created${NC}"
fi

# Upload state file
gsutil cp $STATE_FILE gs://$TRACKING_BUCKET/deployment-state.json

echo -e "${GREEN}✓ Deployment tracking configured${NC}"

echo ""

###############################################################################
# Summary
###############################################################################

echo "========================================="
echo -e "${GREEN}✅ Blue-Green Setup Complete!${NC}"
echo "========================================="
echo "Blue Bucket: gs://$BLUE_BUCKET/ (ACTIVE)"
echo "Green Bucket: gs://$GREEN_BUCKET/ (STANDBY)"
echo "Tracking: gs://$TRACKING_BUCKET/deployment-state.json"
echo ""
echo "Next steps:"
echo "1. Deploy to green: ./deploy-to-green.sh"
echo "2. Test green environment"
echo "3. Switch traffic: ./switch-deployment.sh green"
echo "4. Rollback if needed: ./switch-deployment.sh blue"
echo "========================================="

exit 0

