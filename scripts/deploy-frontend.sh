#!/bin/bash

###############################################################################
# Frontend Deployment Script
#
# This script builds and deploys the frontend to GCP Cloud Storage with:
# - Automatic backup of current version
# - Cache header configuration
# - CDN cache invalidation
# - Deployment verification
# - Automatic rollback on failure
#
# Usage:
#   ./deploy-frontend.sh [--skip-build] [--skip-verification]
#
# Options:
#   --skip-build         Skip the build step (use existing dist/)
#   --skip-verification  Skip deployment verification
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="dentaflow-production"
BUCKET_NAME="dentaflow-frontend"
BACKUP_BUCKET="dentaflow-frontend-backups"
CDN_URL_MAP="dentaflow-lb"
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../frontend" && pwd)"

# Parse arguments
SKIP_BUILD=false
SKIP_VERIFICATION=false

for arg in "$@"; do
    case $arg in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-verification)
            SKIP_VERIFICATION=true
            shift
            ;;
    esac
done

# Generate timestamp for backup
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="gs://$BACKUP_BUCKET/$TIMESTAMP"

echo "========================================="
echo -e "${BLUE}DentaFlow Frontend Deployment${NC}"
echo "========================================="
echo "Project: $PROJECT_ID"
echo "Bucket: gs://$BUCKET_NAME/"
echo "Backup: $BACKUP_PATH"
echo "Timestamp: $TIMESTAMP"
echo "========================================="
echo ""

###############################################################################
# Step 1: Build Frontend
###############################################################################

if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}[1/6] Building frontend...${NC}"
    cd "$FRONTEND_DIR"
    
    echo "Installing dependencies..."
    npm ci --quiet
    
    echo "Building production bundle..."
    npm run build
    
    if [ ! -d "dist" ]; then
        echo -e "${RED}✗ Build failed: dist/ directory not found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Build completed${NC}"
    echo ""
else
    echo -e "${YELLOW}[1/6] Skipping build (using existing dist/)${NC}"
    
    if [ ! -d "$FRONTEND_DIR/dist" ]; then
        echo -e "${RED}✗ dist/ directory not found${NC}"
        exit 1
    fi
    
    echo ""
fi

###############################################################################
# Step 2: Backup Current Version
###############################################################################

echo -e "${YELLOW}[2/6] Backing up current version...${NC}"

if gsutil ls gs://$BUCKET_NAME/index.html > /dev/null 2>&1; then
    echo "Creating backup at: $BACKUP_PATH"
    gsutil -m rsync -r gs://$BUCKET_NAME/ $BACKUP_PATH/
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}⚠ No existing deployment to backup${NC}"
fi

echo ""

###############################################################################
# Step 3: Deploy to Cloud Storage
###############################################################################

echo -e "${YELLOW}[3/6] Deploying to Cloud Storage...${NC}"

cd "$FRONTEND_DIR"

echo "Uploading files to gs://$BUCKET_NAME/..."
gsutil -m rsync -r -d dist/ gs://$BUCKET_NAME/

echo "Setting cache headers..."

# Set cache headers for assets (1 year - immutable)
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
    "gs://$BUCKET_NAME/assets/**" 2>/dev/null || echo "No assets to update"

# Set cache headers for HTML (no cache)
gsutil setmeta -h "Cache-Control:no-cache, no-store, must-revalidate" \
    "gs://$BUCKET_NAME/index.html"

echo -e "${GREEN}✓ Deployment completed${NC}"
echo ""

###############################################################################
# Step 4: Invalidate CDN Cache
###############################################################################

echo -e "${YELLOW}[4/6] Invalidating CDN cache...${NC}"

if gcloud compute url-maps invalidate-cdn-cache $CDN_URL_MAP --path "/*" --async 2>/dev/null; then
    echo -e "${GREEN}✓ CDN cache invalidation initiated${NC}"
else
    echo -e "${YELLOW}⚠ CDN invalidation failed or CDN not configured${NC}"
fi

echo ""

###############################################################################
# Step 5: Verify Deployment
###############################################################################

if [ "$SKIP_VERIFICATION" = false ]; then
    echo -e "${YELLOW}[5/6] Verifying deployment...${NC}"
    
    # Extract bundle hash from deployed index.html
    BUNDLE_HASH=$(gsutil cat gs://$BUCKET_NAME/index.html | grep -o 'index-[^.]*\.js' | head -1 | sed 's/index-//;s/\.js//')
    
    if [ -z "$BUNDLE_HASH" ]; then
        echo -e "${RED}✗ Could not extract bundle hash${NC}"
        echo "Rolling back..."
        gsutil -m rsync -r -d $BACKUP_PATH/ gs://$BUCKET_NAME/
        exit 1
    fi
    
    echo "Bundle hash: $BUNDLE_HASH"
    
    # Run verification script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/verify-deployment.sh" ]; then
        if ! "$SCRIPT_DIR/verify-deployment.sh" "$BUCKET_NAME" "$BUNDLE_HASH"; then
            echo -e "${RED}✗ Deployment verification failed${NC}"
            echo "Rolling back..."
            gsutil -m rsync -r -d $BACKUP_PATH/ gs://$BUCKET_NAME/
            gcloud compute url-maps invalidate-cdn-cache $CDN_URL_MAP --path "/*" --async 2>/dev/null || true
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ Verification script not found, skipping detailed verification${NC}"
    fi
    
    echo -e "${GREEN}✓ Verification passed${NC}"
    echo ""
else
    echo -e "${YELLOW}[5/6] Skipping verification${NC}"
    echo ""
fi

###############################################################################
# Step 6: Cleanup Old Backups
###############################################################################

echo -e "${YELLOW}[6/6] Cleaning up old backups...${NC}"

# Keep only the last 10 backups
BACKUPS=$(gsutil ls gs://$BACKUP_BUCKET/ | sort -r | tail -n +11)

if [ -n "$BACKUPS" ]; then
    echo "Removing old backups..."
    echo "$BACKUPS" | xargs -r gsutil -m rm -r
    echo -e "${GREEN}✓ Cleanup completed${NC}"
else
    echo "No old backups to clean"
fi

echo ""

###############################################################################
# Summary
###############################################################################

echo "========================================="
echo -e "${GREEN}✅ Deployment Successful!${NC}"
echo "========================================="
echo "Timestamp: $TIMESTAMP"
echo "Bucket: gs://$BUCKET_NAME/"
echo "Backup: $BACKUP_PATH"
echo ""
echo "Access your frontend at:"
echo "  https://dentaflow.ai"
echo "  or"
echo "  https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo "========================================="

exit 0

