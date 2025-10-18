#!/bin/bash

#############################################################################
# Migrate Secrets to GCP Secret Manager
#
# This script migrates encryption keys and other secrets from environment
# variables to Google Cloud Secret Manager for enhanced security.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - GCP_PROJECT_ID environment variable set
#   - Secret Manager API enabled in GCP project
#   - Appropriate IAM permissions (roles/secretmanager.admin)
#
# Usage:
#   ./scripts/migrate-secrets-to-gcp.sh
#   ./scripts/migrate-secrets-to-gcp.sh --dry-run
#
# Author: Eran Sarfaty
# Date: 2025-10-18
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
PROJECT_ID="${GCP_PROJECT_ID:-}"
ENV_FILE="backend/.env"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --project)
            PROJECT_ID="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Please install it first."
        exit 1
    fi
    
    # Check project ID
    if [ -z "$PROJECT_ID" ]; then
        log_error "GCP_PROJECT_ID not set. Please set it or use --project flag."
        exit 1
    fi
    
    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_error "Not authenticated with gcloud. Run 'gcloud auth login' first."
        exit 1
    fi
    
    # Check Secret Manager API
    if ! gcloud services list --enabled --project="$PROJECT_ID" | grep -q secretmanager.googleapis.com; then
        log_warning "Secret Manager API not enabled. Enabling it now..."
        if [ "$DRY_RUN" = false ]; then
            gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"
            log_success "Secret Manager API enabled"
        else
            log_info "[DRY RUN] Would enable Secret Manager API"
        fi
    fi
    
    log_success "Prerequisites check passed"
}

create_secret() {
    local secret_id="$1"
    local secret_value="$2"
    local description="$3"
    
    log_info "Creating secret: $secret_id"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would create secret: $secret_id"
        log_info "[DRY RUN] Description: $description"
        log_info "[DRY RUN] Value length: ${#secret_value} characters"
        return 0
    fi
    
    # Check if secret already exists
    if gcloud secrets describe "$secret_id" --project="$PROJECT_ID" &> /dev/null; then
        log_warning "Secret $secret_id already exists. Adding new version..."
        echo -n "$secret_value" | gcloud secrets versions add "$secret_id" \
            --project="$PROJECT_ID" \
            --data-file=- &> /dev/null
    else
        # Create new secret
        echo -n "$secret_value" | gcloud secrets create "$secret_id" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=- &> /dev/null
    fi
    
    # Add labels
    gcloud secrets update "$secret_id" \
        --project="$PROJECT_ID" \
        --update-labels="managed-by=dentaflow,env=production" &> /dev/null
    
    log_success "Created/updated secret: $secret_id"
}

migrate_secrets() {
    log_info "Starting secrets migration..."
    
    # Load environment variables
    if [ -f "$ENV_FILE" ]; then
        log_info "Loading secrets from $ENV_FILE"
        source "$ENV_FILE"
    else
        log_warning "$ENV_FILE not found. Using current environment variables."
    fi
    
    # 1. Encryption Key
    if [ -n "${ENCRYPTION_KEY:-}" ]; then
        create_secret "encryption-key" "$ENCRYPTION_KEY" "AES encryption key for PHI data"
    else
        log_warning "ENCRYPTION_KEY not found in environment"
    fi
    
    # 2. JWT Secret Key
    if [ -n "${SECRET_KEY:-}" ]; then
        create_secret "jwt-secret-key" "$SECRET_KEY" "JWT secret key for authentication"
    else
        log_warning "SECRET_KEY not found in environment"
    fi
    
    # 3. Odoo API Key
    if [ -n "${ODOO_API_KEY:-}" ]; then
        create_secret "odoo-api-key" "$ODOO_API_KEY" "Odoo API key for ERP integration"
    else
        log_warning "ODOO_API_KEY not found in environment"
    fi
    
    # 4. Stripe Secret Key
    if [ -n "${STRIPE_SECRET_KEY:-}" ]; then
        create_secret "stripe-secret-key" "$STRIPE_SECRET_KEY" "Stripe secret key for billing"
    else
        log_warning "STRIPE_SECRET_KEY not found in environment"
    fi
    
    # 5. Database URL (if contains password)
    if [ -n "${DATABASE_URL:-}" ]; then
        create_secret "database-url" "$DATABASE_URL" "PostgreSQL database connection string"
    else
        log_warning "DATABASE_URL not found in environment"
    fi
    
    # 6. OpenAI API Key (if used)
    if [ -n "${OPENAI_API_KEY:-}" ]; then
        create_secret "openai-api-key" "$OPENAI_API_KEY" "OpenAI API key for AI agents"
    else
        log_info "OPENAI_API_KEY not found (optional)"
    fi
    
    # 7. Anthropic API Key (if used)
    if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
        create_secret "anthropic-api-key" "$ANTHROPIC_API_KEY" "Anthropic API key for AI agents"
    else
        log_info "ANTHROPIC_API_KEY not found (optional)"
    fi
    
    log_success "Secrets migration completed"
}

setup_iam_permissions() {
    log_info "Setting up IAM permissions..."
    
    # Get Cloud Run service account
    SERVICE_ACCOUNT="dentaflow-backend@${PROJECT_ID}.iam.gserviceaccount.com"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would grant Secret Manager access to: $SERVICE_ACCOUNT"
        return 0
    fi
    
    # Grant Secret Manager Secret Accessor role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" \
        --condition=None &> /dev/null || true
    
    log_success "IAM permissions configured"
}

verify_secrets() {
    log_info "Verifying secrets..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would verify all secrets"
        return 0
    fi
    
    # List all secrets
    log_info "Secrets in GCP Secret Manager:"
    gcloud secrets list --project="$PROJECT_ID" --format="table(name,createTime,labels)"
    
    # Test access to encryption key
    log_info "Testing access to encryption-key..."
    if gcloud secrets versions access latest --secret="encryption-key" --project="$PROJECT_ID" &> /dev/null; then
        log_success "Successfully accessed encryption-key"
    else
        log_error "Failed to access encryption-key"
        exit 1
    fi
    
    log_success "Secrets verification passed"
}

generate_env_template() {
    log_info "Generating .env.gcp template..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would generate .env.gcp template"
        return 0
    fi
    
    cat > backend/.env.gcp << EOF
# DentaFlow.AI Environment Configuration (GCP Secret Manager)
# Generated: $(date)
# 
# Secrets are now stored in GCP Secret Manager.
# The backend will automatically fetch them at runtime.
#
# Required environment variables:
GCP_PROJECT_ID=$PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Optional: Fallback to environment variables if GCP Secret Manager is unavailable
# ENCRYPTION_KEY=<fallback-value>
# SECRET_KEY=<fallback-value>
# ODOO_API_KEY=<fallback-value>
# STRIPE_SECRET_KEY=<fallback-value>

# Non-secret configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=dentaflow
DATABASE_USER=dentaflow
# DATABASE_PASSWORD is in Secret Manager as part of DATABASE_URL

# Application settings
APP_ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://dentaflow.ai,https://www.dentaflow.ai

# Odoo settings
ODOO_URL=https://dentaflow.odoo.com
ODOO_DB=dentaflow
ODOO_USERNAME=admin

# Feature flags
ENABLE_MFA=true
ENABLE_AUDIT_LOGS=true
ENABLE_HIPAA_COMPLIANCE=true
EOF
    
    log_success "Generated backend/.env.gcp"
}

print_next_steps() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Migration completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo ""
    echo "1. Update backend code to use GCP Secret Manager:"
    echo "   - Update encryption_service.py to use gcp_secrets.get_encryption_key()"
    echo "   - Update config.py to use gcp_secrets.get_jwt_secret()"
    echo "   - Update other services to use GCP Secret Manager"
    echo ""
    echo "2. Update deployment configuration:"
    echo "   - Copy backend/.env.gcp to backend/.env"
    echo "   - Update Cloud Run service to use GCP_PROJECT_ID"
    echo "   - Ensure service account has secretmanager.secretAccessor role"
    echo ""
    echo "3. Test the migration:"
    echo "   - Run backend locally with new configuration"
    echo "   - Verify encryption/decryption works"
    echo "   - Test all integrations (Odoo, Stripe, etc.)"
    echo ""
    echo "4. Remove old secrets from .env file:"
    echo "   - Keep .env.gcp as reference"
    echo "   - Remove sensitive values from .env"
    echo "   - Update .gitignore to exclude .env files"
    echo ""
    echo "5. Update documentation:"
    echo "   - Update KEY_MANAGEMENT_PROCEDURES.md"
    echo "   - Update deployment guides"
    echo "   - Update HIPAA compliance checklist"
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC}"
    echo "   - Do NOT delete old .env file until migration is verified"
    echo "   - Keep backup of all secrets in secure location"
    echo "   - Test rollback procedure before removing fallbacks"
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}DentaFlow Secrets Migration to GCP${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "Running in DRY RUN mode - no changes will be made"
        echo ""
    fi
    
    log_info "Project ID: $PROJECT_ID"
    log_info "Environment file: $ENV_FILE"
    echo ""
    
    check_prerequisites
    migrate_secrets
    setup_iam_permissions
    verify_secrets
    generate_env_template
    print_next_steps
}

# Run main function
main

