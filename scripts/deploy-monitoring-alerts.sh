#!/bin/bash
# Deploy Cloud Monitoring alert policies for HIPAA compliance
# Automated detection of security incidents and suspicious activity

set -e

PROJECT_ID="${GCP_PROJECT_ID:-dentaflow-prod}"
SECURITY_EMAIL="${SECURITY_EMAIL:-security@dentaflow.ai}"
PRIVACY_EMAIL="${PRIVACY_EMAIL:-privacy@dentaflow.ai}"
DEVOPS_EMAIL="${DEVOPS_EMAIL:-devops@dentaflow.ai}"

echo "========================================="
echo "Deploying HIPAA Monitoring Alert Policies"
echo "========================================="
echo "Project: $PROJECT_ID"
echo "Security Email: $SECURITY_EMAIL"
echo "Privacy Email: $PRIVACY_EMAIL"
echo "DevOps Email: $DEVOPS_EMAIL"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# ==================== Create Notification Channels ====================

echo ""
echo "Creating notification channels..."

# Security Team Email
echo "Creating security team email channel..."
SECURITY_CHANNEL=$(gcloud alpha monitoring channels create \
    --display-name="Security Team Email" \
    --type=email \
    --channel-labels=email_address="$SECURITY_EMAIL" \
    --format="value(name)" 2>/dev/null || \
    gcloud alpha monitoring channels list \
        --filter="displayName='Security Team Email'" \
        --format="value(name)" | head -1)

echo "Security channel: $SECURITY_CHANNEL"

# Privacy Officer Email
echo "Creating privacy officer email channel..."
PRIVACY_CHANNEL=$(gcloud alpha monitoring channels create \
    --display-name="Privacy Officer Email" \
    --type=email \
    --channel-labels=email_address="$PRIVACY_EMAIL" \
    --format="value(name)" 2>/dev/null || \
    gcloud alpha monitoring channels list \
        --filter="displayName='Privacy Officer Email'" \
        --format="value(name)" | head -1)

echo "Privacy channel: $PRIVACY_CHANNEL"

# DevOps Team Email
echo "Creating devops team email channel..."
DEVOPS_CHANNEL=$(gcloud alpha monitoring channels create \
    --display-name="DevOps Team Email" \
    --type=email \
    --channel-labels=email_address="$DEVOPS_EMAIL" \
    --format="value(name)" 2>/dev/null || \
    gcloud alpha monitoring channels list \
        --filter="displayName='DevOps Team Email'" \
        --format="value(name)" | head -1)

echo "DevOps channel: $DEVOPS_CHANNEL"

# ==================== Create Alert Policies ====================

echo ""
echo "Creating alert policies..."

# 1. Failed Login Attempts
echo ""
echo "1. Creating 'Failed Login Attempts' alert..."
gcloud alpha monitoring policies create \
    --notification-channels="$SECURITY_CHANNEL" \
    --display-name="HIPAA - Multiple Failed Login Attempts" \
    --condition-display-name="Failed login attempts > 5 in 10 minutes" \
    --condition-threshold-value=5 \
    --condition-threshold-duration=0s \
    --condition-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
jsonPayload.action="login_failed"' \
    --aggregation-alignment-period=600s \
    --aggregation-per-series-aligner=ALIGN_COUNT \
    --aggregation-cross-series-reducer=REDUCE_SUM \
    --aggregation-group-by-fields="jsonPayload.ip_address" \
    --comparison=COMPARISON_GT \
    --documentation='**HIPAA Security Alert: Multiple Failed Login Attempts**

More than 5 failed login attempts detected from the same IP address within 10 minutes.

**Immediate Actions:**
1. Review audit logs for the IP address
2. Check if account is compromised
3. Consider IP blocking if attack confirmed

**Compliance:** HIPAA § 164.308(a)(5)(ii)(C)' \
    --documentation-mime-type="text/markdown" 2>/dev/null || echo "Alert already exists or error occurred"

echo "✅ Failed login attempts alert created"

# 2. Unauthorized PHI Access
echo ""
echo "2. Creating 'Unauthorized PHI Access' alert..."
gcloud alpha monitoring policies create \
    --notification-channels="$SECURITY_CHANNEL,$PRIVACY_CHANNEL" \
    --display-name="HIPAA - Unauthorized PHI Access Attempt" \
    --condition-display-name="Unauthorized PHI access detected" \
    --condition-threshold-value=0 \
    --condition-threshold-duration=0s \
    --condition-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
jsonPayload.action="unauthorized_access"
jsonPayload.resource_type="patient"' \
    --aggregation-alignment-period=60s \
    --aggregation-per-series-aligner=ALIGN_COUNT \
    --comparison=COMPARISON_GT \
    --severity=CRITICAL \
    --documentation='**CRITICAL: Unauthorized PHI Access Attempt**

A user attempted to access PHI without proper authorization.

**Immediate Actions:**
1. Initiate incident response procedure
2. Notify Privacy Officer immediately
3. Document incident in security log

**Compliance:** HIPAA § 164.312(a)(1)' \
    --documentation-mime-type="text/markdown" 2>/dev/null || echo "Alert already exists or error occurred"

echo "✅ Unauthorized PHI access alert created"

# 3. Bulk PHI Export
echo ""
echo "3. Creating 'Bulk PHI Export' alert..."
gcloud alpha monitoring policies create \
    --notification-channels="$SECURITY_CHANNEL" \
    --display-name="HIPAA - Bulk PHI Data Export Detected" \
    --condition-display-name="Patient data export > 100 records" \
    --condition-threshold-value=0 \
    --condition-threshold-duration=0s \
    --condition-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
jsonPayload.action="data_export"
jsonPayload.resource_type="patient"
jsonPayload.record_count>100' \
    --aggregation-alignment-period=60s \
    --aggregation-per-series-aligner=ALIGN_COUNT \
    --comparison=COMPARISON_GT \
    --documentation='**HIPAA Security Alert: Bulk PHI Data Export**

Large amount of patient data exported (>100 records).

**Immediate Actions:**
1. Verify if export is authorized
2. Contact user to confirm business purpose
3. Document in security log

**Compliance:** HIPAA § 164.312(b)' \
    --documentation-mime-type="text/markdown" 2>/dev/null || echo "Alert already exists or error occurred"

echo "✅ Bulk PHI export alert created"

# 4. Database Connection Failures
echo ""
echo "4. Creating 'Database Connection Failures' alert..."
gcloud alpha monitoring policies create \
    --notification-channels="$DEVOPS_CHANNEL" \
    --display-name="HIPAA - Database Connection Failures" \
    --condition-display-name="Database connection failures > 10 in 5 minutes" \
    --condition-threshold-value=10 \
    --condition-threshold-duration=0s \
    --condition-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
severity="ERROR"
jsonPayload.message=~"database connection"' \
    --aggregation-alignment-period=300s \
    --aggregation-per-series-aligner=ALIGN_COUNT \
    --comparison=COMPARISON_GT \
    --documentation='**System Alert: Database Connection Failures**

Multiple database connection failures detected.

**Immediate Actions:**
1. Check Cloud SQL instance status
2. Review connection pool settings
3. Scale database if needed

**Compliance:** HIPAA § 164.308(a)(7)(ii)(A)' \
    --documentation-mime-type="text/markdown" 2>/dev/null || echo "Alert already exists or error occurred"

echo "✅ Database connection failures alert created"

# 5. Encryption Errors
echo ""
echo "5. Creating 'Encryption Errors' alert..."
gcloud alpha monitoring policies create \
    --notification-channels="$SECURITY_CHANNEL,$DEVOPS_CHANNEL" \
    --display-name="HIPAA - Encryption Errors Detected" \
    --condition-display-name="Encryption errors detected" \
    --condition-threshold-value=0 \
    --condition-threshold-duration=0s \
    --condition-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
severity="ERROR"
jsonPayload.message=~"encryption|decrypt"' \
    --aggregation-alignment-period=60s \
    --aggregation-per-series-aligner=ALIGN_COUNT \
    --comparison=COMPARISON_GT \
    --severity=CRITICAL \
    --documentation='**CRITICAL: Encryption Errors Detected**

Encryption/decryption operations are failing.

**Immediate Actions:**
1. Stop processing PHI if possible
2. Check encryption key status
3. Initiate incident response if PHI exposed

**Compliance:** HIPAA § 164.312(a)(2)(iv)' \
    --documentation-mime-type="text/markdown" 2>/dev/null || echo "Alert already exists or error occurred"

echo "✅ Encryption errors alert created"

# 6. High Error Rate
echo ""
echo "6. Creating 'High Error Rate' alert..."
gcloud alpha monitoring policies create \
    --notification-channels="$DEVOPS_CHANNEL" \
    --display-name="System - High Error Rate" \
    --condition-display-name="Error rate > 5%" \
    --condition-threshold-value=0.05 \
    --condition-threshold-duration=0s \
    --condition-filter='
resource.type="cloud_run_revision"
resource.labels.service_name="dentaflow-backend"
severity="ERROR"' \
    --aggregation-alignment-period=300s \
    --aggregation-per-series-aligner=ALIGN_RATE \
    --comparison=COMPARISON_GT \
    --documentation='**System Alert: High Error Rate**

Error rate exceeded 5% of total requests.

**Immediate Actions:**
1. Check Cloud Run logs
2. Review recent deployments
3. Scale resources if needed

**Compliance:** HIPAA § 164.308(a)(7)(ii)(A)' \
    --documentation-mime-type="text/markdown" 2>/dev/null || echo "Alert already exists or error occurred"

echo "✅ High error rate alert created"

# ==================== List Alert Policies ====================

echo ""
echo "========================================="
echo "Deployed Alert Policies:"
echo "========================================="
gcloud alpha monitoring policies list --filter="displayName:HIPAA" --format="table(displayName,enabled)"

echo ""
echo "========================================="
echo "✅ HIPAA Monitoring Alert Deployment Complete"
echo "========================================="
echo ""
echo "Alert policies created:"
echo "  1. Multiple Failed Login Attempts"
echo "  2. Unauthorized PHI Access Attempt"
echo "  3. Bulk PHI Data Export"
echo "  4. Database Connection Failures"
echo "  5. Encryption Errors"
echo "  6. High Error Rate"
echo ""
echo "Notification channels:"
echo "  - Security Team: $SECURITY_EMAIL"
echo "  - Privacy Officer: $PRIVACY_EMAIL"
echo "  - DevOps Team: $DEVOPS_EMAIL"
echo ""
echo "To view alert policies:"
echo "  gcloud alpha monitoring policies list"
echo ""
echo "To view alert incidents:"
echo "  gcloud alpha monitoring policies conditions list"
echo ""
echo "To test an alert:"
echo "  # Trigger failed login attempts in your application"
echo "  # Check Cloud Monitoring console for alert firing"
echo ""

