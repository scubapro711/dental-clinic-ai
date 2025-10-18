#!/bin/bash

###############################################################################
# Frontend Deployment Verification Script
#
# This script verifies that a frontend deployment was successful by:
# 1. Checking if the new files are in Cloud Storage
# 2. Verifying the CDN is serving the new version
# 3. Checking that the application loads correctly
#
# Usage:
#   ./verify-deployment.sh [bucket-name] [expected-hash]
#
# Example:
#   ./verify-deployment.sh dentaflow-frontend CFQKYyVh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="${1:-dentaflow-frontend}"
EXPECTED_HASH="${2:-}"
MAX_RETRIES=10
RETRY_DELAY=30

echo "========================================="
echo "Frontend Deployment Verification"
echo "========================================="
echo "Bucket: gs://$BUCKET_NAME/"
echo "Expected Hash: ${EXPECTED_HASH:-auto-detect}"
echo "========================================="
echo ""

###############################################################################
# Step 1: Verify files in Cloud Storage
###############################################################################

echo -e "${YELLOW}[1/4] Checking Cloud Storage...${NC}"

if ! gsutil ls gs://$BUCKET_NAME/index.html > /dev/null 2>&1; then
    echo -e "${RED}✗ index.html not found in Cloud Storage${NC}"
    exit 1
fi

echo -e "${GREEN}✓ index.html found in Cloud Storage${NC}"

# Get the actual bundle hash from Cloud Storage
ACTUAL_HASH=$(gsutil cat gs://$BUCKET_NAME/index.html | grep -o 'index-[^.]*\.js' | head -1 | sed 's/index-//;s/\.js//')

if [ -z "$ACTUAL_HASH" ]; then
    echo -e "${RED}✗ Could not extract bundle hash from index.html${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Bundle hash: $ACTUAL_HASH${NC}"

# Verify the JS bundle exists
if ! gsutil ls gs://$BUCKET_NAME/assets/index-$ACTUAL_HASH.js > /dev/null 2>&1; then
    echo -e "${RED}✗ Bundle file not found: index-$ACTUAL_HASH.js${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Bundle file exists in Cloud Storage${NC}"

# If expected hash was provided, verify it matches
if [ -n "$EXPECTED_HASH" ] && [ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]; then
    echo -e "${RED}✗ Hash mismatch! Expected: $EXPECTED_HASH, Got: $ACTUAL_HASH${NC}"
    exit 1
fi

echo ""

###############################################################################
# Step 2: Verify CDN is serving the new version
###############################################################################

echo -e "${YELLOW}[2/4] Checking CDN propagation...${NC}"

# Get the Load Balancer IP
LB_IP=$(gcloud compute forwarding-rules list --filter="name~dentaflow" --format="value(IPAddress)" 2>/dev/null | head -1)

if [ -z "$LB_IP" ]; then
    echo -e "${YELLOW}⚠ No Load Balancer found, checking Storage directly${NC}"
    CDN_URL="https://storage.googleapis.com/$BUCKET_NAME/index.html"
else
    echo "Load Balancer IP: $LB_IP"
    CDN_URL="http://$LB_IP/index.html"
fi

echo "CDN URL: $CDN_URL"

# Retry logic for CDN propagation
for i in $(seq 1 $MAX_RETRIES); do
    echo -n "Attempt $i/$MAX_RETRIES: "
    
    # Fetch index.html from CDN
    CDN_HASH=$(curl -s "$CDN_URL" | grep -o 'index-[^.]*\.js' | head -1 | sed 's/index-//;s/\.js//' || echo "")
    
    if [ "$CDN_HASH" = "$ACTUAL_HASH" ]; then
        echo -e "${GREEN}✓ CDN serving correct version ($CDN_HASH)${NC}"
        break
    else
        if [ $i -eq $MAX_RETRIES ]; then
            echo -e "${RED}✗ CDN still serving old version after $MAX_RETRIES attempts${NC}"
            echo "Expected: $ACTUAL_HASH"
            echo "Got: $CDN_HASH"
            exit 1
        else
            echo -e "${YELLOW}⏳ CDN serving old version ($CDN_HASH), waiting ${RETRY_DELAY}s...${NC}"
            sleep $RETRY_DELAY
        fi
    fi
done

echo ""

###############################################################################
# Step 3: Verify HTTP response codes
###############################################################################

echo -e "${YELLOW}[3/4] Checking HTTP response codes...${NC}"

# Check index.html
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$CDN_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ index.html returns 200 OK${NC}"
else
    echo -e "${RED}✗ index.html returns HTTP $HTTP_CODE${NC}"
    exit 1
fi

# Check bundle file
BUNDLE_URL=$(echo "$CDN_URL" | sed 's/index.html//')
BUNDLE_URL="${BUNDLE_URL}assets/index-${ACTUAL_HASH}.js"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BUNDLE_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Bundle file returns 200 OK${NC}"
else
    echo -e "${RED}✗ Bundle file returns HTTP $HTTP_CODE${NC}"
    exit 1
fi

echo ""

###############################################################################
# Step 4: Verify cache headers
###############################################################################

echo -e "${YELLOW}[4/4] Checking cache headers...${NC}"

# Check index.html cache headers (should be no-cache)
INDEX_CACHE=$(curl -s -I "$CDN_URL" | grep -i "cache-control" || echo "")

if echo "$INDEX_CACHE" | grep -qi "no-cache"; then
    echo -e "${GREEN}✓ index.html has correct cache headers${NC}"
else
    echo -e "${YELLOW}⚠ index.html cache headers: $INDEX_CACHE${NC}"
fi

# Check bundle cache headers (should be long-lived)
BUNDLE_CACHE=$(curl -s -I "$BUNDLE_URL" | grep -i "cache-control" || echo "")

if echo "$BUNDLE_CACHE" | grep -qi "max-age"; then
    echo -e "${GREEN}✓ Bundle has correct cache headers${NC}"
else
    echo -e "${YELLOW}⚠ Bundle cache headers: $BUNDLE_CACHE${NC}"
fi

echo ""

###############################################################################
# Summary
###############################################################################

echo "========================================="
echo -e "${GREEN}✅ Deployment Verification PASSED${NC}"
echo "========================================="
echo "Bucket: gs://$BUCKET_NAME/"
echo "Bundle Hash: $ACTUAL_HASH"
echo "CDN URL: $CDN_URL"
echo "Status: All checks passed"
echo "========================================="

exit 0

