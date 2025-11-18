#!/bin/bash
# Generate Git info files for build
# This script should be run BEFORE building the Docker image

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="$BACKEND_DIR/backend/app"

echo "🔍 Generating Git info files..."

# Get git information
GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
GIT_COMMIT_SHORT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
GIT_DATE=$(git log -1 --format=%cd --date=iso 2>/dev/null || date -Iseconds)
GIT_MESSAGE=$(git log -1 --format=%s 2>/dev/null || echo "unknown")

# Create git info string
GIT_INFO="${GIT_COMMIT_SHORT}|${GIT_COMMIT}|${GIT_DATE}|${GIT_MESSAGE}"

# Write to files
echo "$GIT_COMMIT" > "$APP_DIR/GIT_COMMIT"
echo "$GIT_COMMIT_SHORT" > "$APP_DIR/GIT_COMMIT_SHORT"
echo "$GIT_INFO" > "$APP_DIR/GIT_INFO"

echo "✅ Git info files generated:"
echo "   Commit: $GIT_COMMIT_SHORT"
echo "   Branch: $GIT_BRANCH"
echo "   Date: $GIT_DATE"
echo "   Files: $APP_DIR/GIT_*"
