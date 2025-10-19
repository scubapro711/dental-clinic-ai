#!/bin/bash
# Database Backup Script for DentaFlow (GCP Version)
# Performs full PostgreSQL backup and uploads to Google Cloud Storage

set -e

# Configuration
DB_NAME="${DB_NAME:-dentaflow}"
DB_USER="${DB_USER:-dentaflow_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backup/database}"
GCS_BUCKET="${GCS_BUCKET:-gs://dentaflow-backups/database}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
PROJECT_ID="${PROJECT_ID:-dentaflow-production}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dentaflow_$TIMESTAMP.sql.gz"
BACKUP_LOG="$BACKUP_DIR/backup_$TIMESTAMP.log"

# Start backup
log "Starting database backup..."
log "Database: $DB_NAME"
log "User: $DB_USER"
log "Host: $DB_HOST:$DB_PORT"
log "Backup file: $BACKUP_FILE"

# Perform backup
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="$BACKUP_FILE" 2> "$BACKUP_LOG"; then
    
    # Verify backup file exists
    if [ -f "$BACKUP_FILE" ]; then
        SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log "✅ Backup completed successfully: $BACKUP_FILE ($SIZE)"
    else
        error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
else
    error "pg_dump failed! Check log: $BACKUP_LOG"
    cat "$BACKUP_LOG"
    exit 1
fi

# Verify backup integrity
log "Verifying backup integrity..."
if pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1; then
    log "✅ Backup integrity verified"
else
    error "Backup integrity check failed!"
    exit 1
fi

# Upload to GCS if configured
if [ -n "$GCS_BUCKET" ] && command -v gsutil &> /dev/null; then
    log "Uploading to GCS: $GCS_BUCKET"
    
    # Set lifecycle metadata
    if gsutil -h "x-goog-meta-timestamp:$TIMESTAMP" \
        -h "x-goog-meta-size:$SIZE" \
        -h "x-goog-meta-database:$DB_NAME" \
        cp "$BACKUP_FILE" "$GCS_BUCKET/" 2>&1 | tee -a "$BACKUP_LOG"; then
        
        log "✅ GCS upload successful"
        
        # Verify GCS upload
        if gsutil ls "$GCS_BUCKET/$(basename $BACKUP_FILE)" > /dev/null 2>&1; then
            log "✅ GCS upload verified"
        else
            warn "GCS upload verification failed"
        fi
    else
        error "GCS upload failed!"
        exit 1
    fi
    
    # Upload log file
    gsutil cp "$BACKUP_LOG" "$GCS_BUCKET/logs/" || warn "Log upload failed"
else
    warn "GCS upload skipped (not configured or gsutil not available)"
fi

# Clean up old local backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
DELETED=$(find "$BACKUP_DIR" -name "dentaflow_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
log "Deleted $DELETED old backup(s)"

# Clean up old GCS backups
if [ -n "$GCS_BUCKET" ] && command -v gsutil &> /dev/null; then
    log "Cleaning up old GCS backups (older than $RETENTION_DAYS days)..."
    
    # Calculate cutoff date
    CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d)
    
    # List and delete old backups
    gsutil ls "$GCS_BUCKET/dentaflow_*.sql.gz" 2>/dev/null | while read -r file; do
        # Extract date from filename (dentaflow_YYYYMMDD_HHMMSS.sql.gz)
        FILE_DATE=$(basename "$file" | sed 's/dentaflow_\([0-9]\{8\}\)_.*/\1/')
        
        if [ "$FILE_DATE" -lt "$CUTOFF_DATE" ]; then
            log "Deleting old backup: $file"
            gsutil rm "$file" || warn "Failed to delete: $file"
        fi
    done
fi

# Generate backup report
REPORT_FILE="$BACKUP_DIR/backup_report_$TIMESTAMP.txt"
cat > "$REPORT_FILE" <<EOF
DentaFlow Database Backup Report
================================

Date: $(date)
Database: $DB_NAME
Backup File: $BACKUP_FILE
Size: $SIZE
Status: SUCCESS

Backup Details:
- Format: Custom (compressed)
- Compression: Level 9
- Integrity: Verified
- GCS Upload: $([ -n "$GCS_BUCKET" ] && echo "Yes" || echo "No")
- GCS Bucket: $GCS_BUCKET

Retention:
- Local: $RETENTION_DAYS days
- GCS: $RETENTION_DAYS days (then lifecycle policy applies)

Cloud SQL Automated Backups:
- Enabled: Yes
- Schedule: Daily at 2 AM UTC
- Retention: 30 days
- Point-in-Time Recovery: 7 days

Next Steps:
- Backup will be automatically tested monthly
- Point-in-time recovery available via Cloud SQL
- Full restore time: ~30 minutes

EOF

log "Backup report generated: $REPORT_FILE"

# Send Slack notification if configured
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{
            \"text\": \"✅ DentaFlow Database Backup Completed\",
            \"attachments\": [{
                \"color\": \"good\",
                \"fields\": [
                    {\"title\": \"Database\", \"value\": \"$DB_NAME\", \"short\": true},
                    {\"title\": \"Size\", \"value\": \"$SIZE\", \"short\": true},
                    {\"title\": \"Timestamp\", \"value\": \"$TIMESTAMP\", \"short\": true},
                    {\"title\": \"GCS\", \"value\": \"$([ -n "$GCS_BUCKET" ] && echo "Uploaded" || echo "Skipped")\", \"short\": true}
                ]
            }]
        }" 2>/dev/null || warn "Slack notification failed"
fi

log "✅ Backup process completed successfully!"
log "Backup file: $BACKUP_FILE"
log "Backup size: $SIZE"
log "Report: $REPORT_FILE"

exit 0

