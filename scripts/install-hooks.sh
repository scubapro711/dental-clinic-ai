#!/bin/bash
# Install Git hooks for Dental Clinic AI project

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Installing Git hooks...${NC}"
echo ""

# Get the root directory of the git repo
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$GIT_ROOT" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Paths
HOOKS_DIR="$GIT_ROOT/.git/hooks"
SCRIPTS_DIR="$GIT_ROOT/scripts/hooks"

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
if [ -f "$SCRIPTS_DIR/pre-commit" ]; then
    cp "$SCRIPTS_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo -e "${GREEN}✅${NC} Installed pre-commit hook"
else
    echo "⚠️  Warning: pre-commit hook not found in $SCRIPTS_DIR"
fi

# Install commit-msg hook
if [ -f "$SCRIPTS_DIR/commit-msg" ]; then
    cp "$SCRIPTS_DIR/commit-msg" "$HOOKS_DIR/commit-msg"
    chmod +x "$HOOKS_DIR/commit-msg"
    echo -e "${GREEN}✅${NC} Installed commit-msg hook"
else
    echo "⚠️  Warning: commit-msg hook not found in $SCRIPTS_DIR"
fi

echo ""
echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo ""
echo "Hooks will now run automatically on:"
echo "  • git commit (pre-commit + commit-msg)"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To uninstall hooks:"
echo "  rm .git/hooks/pre-commit .git/hooks/commit-msg"
echo ""
