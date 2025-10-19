#!/bin/bash
# Deploy Cloud Scheduler jobs for data retention automation
# HIPAA-compliant automated data lifecycle management

set -e

PROJECT_ID="${GCP_PROJECT_ID:-dentaflow-prod}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_URL="${BACKEND_URL:-https://dentaflow-backend-xxxxx.run.app}"
SERVICE_ACCOUNT="${SCHEDULER_SA:-cloud-scheduler@dentaflow-prod.iam.gserviceaccount.com}"

echo "========================================="
echo "Deploying Data Retention Scheduler Jobs"
echo "========================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Backend URL: $BACKEND_URL"
echo "Service Account: $SERVICE_ACCOUNT"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Enable Cloud Scheduler API
echo "Enabling Cloud Scheduler API..."
gcloud services enable cloudscheduler.googleapis.com

# Create service account if it doesn't exist
echo "Checking service account..."
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT" &> /dev/null; then
    echo "Creating service account..."
    gcloud iam service-accounts create cloud-scheduler \
        --display-name="Cloud Scheduler Service Account" \
        --description="Service account for Cloud Scheduler jobs"
    
    # Grant Cloud Run Invoker role
    gcloud run services add-iam-policy-binding dentaflow-backend \
        --region="$REGION" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/run.invoker"
fi

# ==================== Daily Retention Check ====================

echo ""
echo "Creating daily retention check job..."

# Delete existing job if it exists
gcloud scheduler jobs delete dentaflow-daily-retention-check \
    --location="$REGION" \
    --quiet 2>/dev/null || true

# Create new job
gcloud scheduler jobs create http dentaflow-daily-retention-check \
    --location="$REGION" \
    --schedule="0 2 * * *" \
    --time-zone="UTC" \
    --uri="$BACKEND_URL/api/v1/data-retention/jobs/daily-check" \
    --http-method="POST" \
    --headers="Content-Type=application/json" \
    --oidc-service-account-email="$SERVICE_ACCOUNT" \
    --oidc-token-audience="$BACKEND_URL" \
    --max-retry-attempts=3 \
    --max-retry-duration=3600s \
    --min-backoff=5s \
    --max-backoff=300s \
    --max-doublings=5 \
    --description="Daily check for expired patient records and audit logs"

echo "✅ Daily retention check job created"

# ==================== Monthly Data Cleanup ====================

echo ""
echo "Creating monthly data cleanup job..."

# Delete existing job if it exists
gcloud scheduler jobs delete dentaflow-monthly-data-cleanup \
    --location="$REGION" \
    --quiet 2>/dev/null || true

# Create new job
gcloud scheduler jobs create http dentaflow-monthly-data-cleanup \
    --location="$REGION" \
    --schedule="0 3 1 * *" \
    --time-zone="UTC" \
    --uri="$BACKEND_URL/api/v1/data-retention/jobs/monthly-cleanup" \
    --http-method="POST" \
    --headers="Content-Type=application/json" \
    --oidc-service-account-email="$SERVICE_ACCOUNT" \
    --oidc-token-audience="$BACKEND_URL" \
    --max-retry-attempts=3 \
    --max-retry-duration=3600s \
    --min-backoff=5s \
    --max-backoff=300s \
    --max-doublings=5 \
    --description="Monthly automated data cleanup and archival"

echo "✅ Monthly data cleanup job created"

# ==================== Quarterly Retention Report ====================

echo ""
echo "Creating quarterly retention report job..."

# Delete existing job if it exists
gcloud scheduler jobs delete dentaflow-quarterly-retention-report \
    --location="$REGION" \
    --quiet 2>/dev/null || true

# Create new job
gcloud scheduler jobs create http dentaflow-quarterly-retention-report \
    --location="$REGION" \
    --schedule="0 4 1 1,4,7,10 *" \
    --time-zone="UTC" \
    --uri="$BACKEND_URL/api/v1/data-retention/report" \
    --http-method="GET" \
    --headers="Content-Type=application/json" \
    --oidc-service-account-email="$SERVICE_ACCOUNT" \
    --oidc-token-audience="$BACKEND_URL" \
    --max-retry-attempts=3 \
    --max-retry-duration=3600s \
    --min-backoff=5s \
    --max-backoff=300s \
    --max-doublings=5 \
    --description="Quarterly data retention compliance report"

echo "✅ Quarterly retention report job created"

# ==================== List Jobs ====================

echo ""
echo "========================================="
echo "Deployed Cloud Scheduler Jobs:"
echo "========================================="
gcloud scheduler jobs list --location="$REGION" | grep dentaflow

echo ""
echo "========================================="
echo "✅ Data Retention Scheduler Deployment Complete"
echo "========================================="
echo ""
echo "Jobs created:"
echo "  1. dentaflow-daily-retention-check (Daily at 2 AM UTC)"
echo "  2. dentaflow-monthly-data-cleanup (1st of month at 3 AM UTC)"
echo "  3. dentaflow-quarterly-retention-report (Quarterly at 4 AM UTC)"
echo ""
echo "To manually trigger a job:"
echo "  gcloud scheduler jobs run dentaflow-daily-retention-check --location=$REGION"
echo ""
echo "To view job logs:"
echo "  gcloud logging read 'resource.type=cloud_scheduler_job' --limit=50"
echo ""

