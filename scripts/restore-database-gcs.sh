#!/bin/bash
# Database Restore Script for DentaFlow (GCP Version)
# Restores PostgreSQL database from backup

set -e

# Configuration
DB_NAME="${DB_NAME:-dentaflow}"
DB_USER="${DB_USER:-dentaflow_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/backup/database}"
GCS_BUCKET="${GCS_BUCKET:-gs://dentaflow-backups/database}"
PROJECT_ID="${PROJECT_ID:-dentaflow-production}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

# Usage
usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Restore DentaFlow database from backup.

OPTIONS:
    -f, --file FILE         Restore from specific backup file
    -l, --latest            Restore from latest backup (default)
    -g, --gcs               Download latest backup from GCS
    -d, --date DATE         Restore from backup on specific date (YYYYMMDD)
    -t, --target DB         Target database name (default: $DB_NAME)
    -p, --pitr TIMESTAMP    Restore to specific point-in-time (Cloud SQL only)
    --dry-run               Show what would be done without doing it
    -h, --help              Show this help message

EXAMPLES:
    # Restore from latest local backup
    $0 --latest

    # Restore from GCS
    $0 --gcs

    # Restore from specific file
    $0 --file /backup/database/dentaflow_20251008_020000.sql.gz

    # Restore from specific date
    $0 --date 20251008

    # Restore to test database
    $0 --latest --target dentaflow_test

    # Point-in-Time Recovery (Cloud SQL)
    $0 --pitr "2025-10-08T14:30:00Z"

EOF
    exit 1
}

# Parse arguments
BACKUP_FILE=""
USE_GCS=false
USE_LATEST=true
TARGET_DB="$DB_NAME"
DRY_RUN=false
SPECIFIC_DATE=""
PITR_TIMESTAMP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            BACKUP_FILE="$2"
            USE_LATEST=false
            shift 2
            ;;
        -l|--latest)
            USE_LATEST=true
            shift
            ;;
        -g|--gcs)
            USE_GCS=true
            shift
            ;;
        -d|--date)
            SPECIFIC_DATE="$2"
            USE_LATEST=false
            shift 2
            ;;
        -t|--target)
            TARGET_DB="$2"
            shift 2
            ;;
        -p|--pitr)
            PITR_TIMESTAMP="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            error "Unknown option: $1"
            usage
            ;;
    esac
done

# Point-in-Time Recovery (Cloud SQL only)
if [ -n "$PITR_TIMESTAMP" ]; then
    log "Point-in-Time Recovery requested: $PITR_TIMESTAMP"
    
    if [ "$DRY_RUN" = true ]; then
        log "DRY RUN MODE - Would perform PITR to: $PITR_TIMESTAMP"
        exit 0
    fi
    
    warn "⚠️  WARNING: This will create a new Cloud SQL instance from PITR"
    warn "⚠️  Original instance will NOT be modified"
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        log "PITR cancelled by user"
        exit 0
    fi
    
    # Perform PITR using gcloud
    log "Creating new instance from point-in-time: $PITR_TIMESTAMP"
    
    NEW_INSTANCE="dentaflow-db-pitr-$(date +%Y%m%d-%H%M%S)"
    
    gcloud sql backups restore \
        --backup-instance=dentaflow-db-instance \
        --backup-id=auto \
        --restore-instance="$NEW_INSTANCE" \
        --project="$PROJECT_ID" \
        --point-in-time="$PITR_TIMESTAMP" || {
        error "PITR failed!"
        exit 1
    }
    
    log "✅ PITR completed successfully!"
    log "New instance: $NEW_INSTANCE"
    log "Connect with: gcloud sql connect $NEW_INSTANCE --user=$DB_USER"
    
    exit 0
fi

# Find backup file
if [ -z "$BACKUP_FILE" ]; then
    if [ "$USE_GCS" = true ]; then
        log "Downloading latest backup from GCS..."
        
        # Get latest backup from GCS
        LATEST_GCS=$(gsutil ls "$GCS_BUCKET/dentaflow_*.sql.gz" 2>/dev/null | sort | tail -n 1)
        
        if [ -z "$LATEST_GCS" ]; then
            error "No backups found in GCS: $GCS_BUCKET"
            exit 1
        fi
        
        log "Latest GCS backup: $LATEST_GCS"
        
        # Download to temp directory
        BACKUP_FILE="/tmp/$(basename $LATEST_GCS)"
        gsutil cp "$LATEST_GCS" "$BACKUP_FILE"
        
        log "✅ Downloaded from GCS"
        
    elif [ -n "$SPECIFIC_DATE" ]; then
        log "Looking for backup from date: $SPECIFIC_DATE"
        
        BACKUP_FILE=$(find "$BACKUP_DIR" -name "dentaflow_${SPECIFIC_DATE}_*.sql.gz" | sort | tail -n 1)
        
        if [ -z "$BACKUP_FILE" ]; then
            error "No backup found for date: $SPECIFIC_DATE"
            exit 1
        fi
        
    elif [ "$USE_LATEST" = true ]; then
        log "Looking for latest local backup..."
        
        BACKUP_FILE=$(find "$BACKUP_DIR" -name "dentaflow_*.sql.gz" | sort | tail -n 1)
        
        if [ -z "$BACKUP_FILE" ]; then
            error "No local backups found in: $BACKUP_DIR"
            exit 1
        fi
    fi
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup file: $BACKUP_FILE ($SIZE)"

# Verify backup integrity
log "Verifying backup integrity..."
if ! pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1; then
    error "Backup file is corrupted or invalid!"
    exit 1
fi
log "✅ Backup integrity verified"

# Dry run mode
if [ "$DRY_RUN" = true ]; then
    log "DRY RUN MODE - No changes will be made"
    log "Would restore:"
    log "  From: $BACKUP_FILE"
    log "  To: $TARGET_DB"
    log "  Host: $DB_HOST:$DB_PORT"
    exit 0
fi

# Confirmation prompt
warn "⚠️  WARNING: This will REPLACE the database: $TARGET_DB"
warn "⚠️  All existing data will be LOST!"
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

# Create database if it doesn't exist
log "Preparing database: $TARGET_DB"
psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "SELECT 1 FROM pg_database WHERE datname='$TARGET_DB'" | grep -q 1 || \
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $TARGET_DB OWNER $DB_USER;"

# Perform restore
log "Starting database restore..."
log "This may take several minutes..."

if pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TARGET_DB" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    --verbose \
    "$BACKUP_FILE" 2>&1 | tee /tmp/restore.log; then
    
    log "✅ Database restore completed"
else
    error "Database restore failed! Check log: /tmp/restore.log"
    cat /tmp/restore.log
    exit 1
fi

# Verify restoration
log "Verifying restoration..."

# Check if tables exist
TABLE_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TARGET_DB" \
    -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")

if [ "$TABLE_COUNT" -gt 0 ]; then
    log "✅ Found $TABLE_COUNT tables"
else
    error "No tables found after restore!"
    exit 1
fi

# Check if data exists
USER_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TARGET_DB" \
    -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")

log "Found $USER_COUNT users in database"

# Generate restore report
REPORT_FILE="/tmp/restore_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$REPORT_FILE" <<EOF
DentaFlow Database Restore Report
==================================

Date: $(date)
Backup File: $BACKUP_FILE
Backup Size: $SIZE
Target Database: $TARGET_DB
Status: SUCCESS

Verification:
- Tables: $TABLE_COUNT
- Users: $USER_COUNT

Restore Time: $(date)

Next Steps:
- Verify application functionality
- Check data integrity
- Monitor for errors

EOF

log "Restore report generated: $REPORT_FILE"

log "✅ Database restore completed successfully!"
log "Backup file: $BACKUP_FILE"
log "Target database: $TARGET_DB"
log "Tables restored: $TABLE_COUNT"
log "Report: $REPORT_FILE"

exit 0

