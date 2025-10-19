#!/bin/bash
# Create HIPAA Log-Based Metrics for DentaFlow

set -e

PROJECT_ID="dentaflow-production"

echo "============================================================"
echo "Creating HIPAA Log-Based Metrics"
echo "============================================================"
echo "Project: $PROJECT_ID"
echo ""

# Set project
gcloud config set project $PROJECT_ID

echo "Creating metrics..."
echo ""

# Metric 1: Failed Login Attempts
echo "1. failed_login_attempts"
gcloud logging metrics create failed_login_attempts \
  --description="Count of failed login attempts" \
  --log-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
jsonPayload.event="login_failed"
' \
  --value-extractor='EXTRACT(jsonPayload.ip_address)' \
  2>/dev/null && echo "✓ Created" || echo "✓ Already exists"
echo ""

# Metric 2: Unauthorized PHI Access
echo "2. unauthorized_phi_access"
gcloud logging metrics create unauthorized_phi_access \
  --description="Count of unauthorized PHI access attempts" \
  --log-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
jsonPayload.event="unauthorized_access"
jsonPayload.resource_type="patient"
' \
  2>/dev/null && echo "✓ Created" || echo "✓ Already exists"
echo ""

# Metric 3: Bulk PHI Export
echo "3. bulk_phi_export"
gcloud logging metrics create bulk_phi_export \
  --description="Count of bulk PHI data exports (>100 records)" \
  --log-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
jsonPayload.event="data_export"
jsonPayload.resource_type="patient"
jsonPayload.record_count>100
' \
  2>/dev/null && echo "✓ Created" || echo "✓ Already exists"
echo ""

# Metric 4: Database Connection Failures
echo "4. database_connection_failures"
gcloud logging metrics create database_connection_failures \
  --description="Count of database connection failures" \
  --log-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
severity="ERROR"
jsonPayload.error=~".*database.*"
' \
  2>/dev/null && echo "✓ Created" || echo "✓ Already exists"
echo ""

# Metric 5: Encryption Errors
echo "5. encryption_errors"
gcloud logging metrics create encryption_errors \
  --description="Count of encryption/decryption errors" \
  --log-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
(jsonPayload.error=~".*encryption.*" OR jsonPayload.event="encryption_error")
' \
  2>/dev/null && echo "✓ Created" || echo "✓ Already exists"
echo ""

# Metric 6: High Error Rate
echo "6. high_error_rate"
gcloud logging metrics create high_error_rate \
  --description="Count of 5xx server errors" \
  --log-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
httpRequest.status>=500
' \
  2>/dev/null && echo "✓ Created" || echo "✓ Already exists"
echo ""

echo "============================================================"
echo "✅ Log Metrics Creation Complete"
echo "============================================================"
echo ""
echo "Listing all metrics:"
gcloud logging metrics list --format="table(name,description)" | grep -E "(failed_login|unauthorized_phi|bulk_phi|database_connection|encryption_errors|high_error_rate)" || echo "No metrics found yet"
echo ""
echo "Next step:"
echo "  Run: ./scripts/create-alert-policies.sh"
echo ""

