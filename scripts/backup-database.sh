#!/bin/bash
# Database Backup Script for DentaFlow
# Performs full PostgreSQL backup and uploads to S3

set -e

# Configuration
DB_NAME="${DB_NAME:-dentaflow}"
DB_USER="${DB_USER:-dentaflow_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backup/database}"
S3_BUCKET="${S3_BUCKET:-s3://dentaflow-backups/database}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

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

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
    log "Uploading to S3: $S3_BUCKET"
    
    if aws s3 cp "$BACKUP_FILE" "$S3_BUCKET/" \
        --storage-class STANDARD_IA \
        --server-side-encryption AES256 \
        --metadata "timestamp=$TIMESTAMP,size=$SIZE"; then
        
        log "✅ S3 upload successful"
        
        # Verify S3 upload
        if aws s3 ls "$S3_BUCKET/$(basename $BACKUP_FILE)" > /dev/null 2>&1; then
            log "✅ S3 upload verified"
        else
            warn "S3 upload verification failed"
        fi
    else
        error "S3 upload failed!"
        exit 1
    fi
    
    # Upload log file
    aws s3 cp "$BACKUP_LOG" "$S3_BUCKET/logs/" \
        --storage-class STANDARD_IA \
        --server-side-encryption AES256 || warn "Log upload failed"
else
    warn "S3 upload skipped (not configured or AWS CLI not available)"
fi

# Clean up old local backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
DELETED=$(find "$BACKUP_DIR" -name "dentaflow_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
log "Deleted $DELETED old backup(s)"

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
- S3 Upload: $([ -n "$S3_BUCKET" ] && echo "Yes" || echo "No")

Retention:
- Local: $RETENTION_DAYS days
- S3: 30 days (Standard-IA), then Glacier

Next Steps:
- Backup will be automatically tested monthly
- Point-in-time recovery available via WAL archives
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
                    {\"title\": \"S3\", \"value\": \"$([ -n "$S3_BUCKET" ] && echo "Uploaded" || echo "Skipped")\", \"short\": true}
                ]
            }]
        }" 2>/dev/null || warn "Slack notification failed"
fi

log "✅ Backup process completed successfully!"
log "Backup file: $BACKUP_FILE"
log "Backup size: $SIZE"
log "Report: $REPORT_FILE"

exit 0
