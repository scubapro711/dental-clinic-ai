#!/bin/bash
# Professional build script for DentaFlow Backend
# Generates git info and builds Docker image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 DentaFlow Backend Build Script${NC}"
echo ""

# Step 1: Generate git info
echo -e "${YELLOW}Step 1: Generating Git info...${NC}"
"$SCRIPT_DIR/generate-git-info.sh"
echo ""

# Step 2: Get build parameters
IMAGE_TAG="${1:-$(date +%s)}"
IMAGE_REPO="${2:-us-central1-docker.pkg.dev/dentaflow-production/dentaflow/dentaflow-backend}"
FULL_IMAGE="$IMAGE_REPO:$IMAGE_TAG"

echo -e "${YELLOW}Step 2: Build parameters${NC}"
echo "  Image: $FULL_IMAGE"
echo "  Backend dir: $BACKEND_DIR"
echo ""

# Step 3: Build Docker image
echo -e "${YELLOW}Step 3: Building Docker image...${NC}"
cd "$BACKEND_DIR"

if command -v gcloud &> /dev/null; then
    echo "  Using Google Cloud Build..."
    gcloud builds submit \
        --tag="$FULL_IMAGE" \
        --project=dentaflow-production \
        --timeout=20m \
        .
else
    echo "  Using local Docker build..."
    docker build -t "$FULL_IMAGE" .
fi

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo "  Image: $FULL_IMAGE"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Test the image locally: docker run -p 8080:8080 $FULL_IMAGE"
echo "  2. Deploy to Cloud Run: gcloud run deploy ... --image=$FULL_IMAGE"
