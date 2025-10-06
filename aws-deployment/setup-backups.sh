#!/bin/bash

###############################################################################
# Dental Clinic SaaS - Automated Backup Setup
# This script sets up automated backups for Odoo database and filestore
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Dental Clinic - Backup Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Configuration
BACKUP_DIR="/var/backups/odoo"
DB_NAME="dental_prod"
ODOO_DATA_DIR="/var/lib/odoo"
RETENTION_DAYS=30

echo -e "${GREEN}[1/4] Creating backup directory...${NC}"
mkdir -p $BACKUP_DIR
chown odoo:odoo $BACKUP_DIR

echo -e "${GREEN}[2/4] Creating backup script...${NC}"
cat > /usr/local/bin/odoo-backup.sh << 'EOFBACKUP'
#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/odoo"
DB_NAME="dental_prod"
ODOO_DATA_DIR="/var/lib/odoo"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory for today
TODAY_DIR="$BACKUP_DIR/$TIMESTAMP"
mkdir -p $TODAY_DIR

echo "Starting Odoo backup at $(date)"

# Backup database
echo "Backing up database: $DB_NAME"
sudo -u postgres pg_dump $DB_NAME | gzip > $TODAY_DIR/database_$TIMESTAMP.sql.gz

# Backup filestore
echo "Backing up filestore..."
tar -czf $TODAY_DIR/filestore_$TIMESTAMP.tar.gz -C $ODOO_DATA_DIR filestore

# Create backup manifest
cat > $TODAY_DIR/manifest.txt << EOF
Backup Date: $(date)
Database: $DB_NAME
Database Size: $(du -h $TODAY_DIR/database_$TIMESTAMP.sql.gz | cut -f1)
Filestore Size: $(du -h $TODAY_DIR/filestore_$TIMESTAMP.tar.gz | cut -f1)
Total Size: $(du -sh $TODAY_DIR | cut -f1)
EOF

# Remove old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

echo "Backup completed successfully at $(date)"
echo "Backup location: $TODAY_DIR"

# Log backup size
du -sh $TODAY_DIR
EOFBACKUP

chmod +x /usr/local/bin/odoo-backup.sh

echo -e "${GREEN}[3/4] Setting up cron job (daily at 2 AM)...${NC}"
cat > /etc/cron.d/odoo-backup << 'EOFCRON'
# Odoo automated backup - runs daily at 2 AM
0 2 * * * root /usr/local/bin/odoo-backup.sh >> /var/log/odoo-backup.log 2>&1
EOFCRON

chmod 644 /etc/cron.d/odoo-backup

echo -e "${GREEN}[4/4] Running initial backup...${NC}"
/usr/local/bin/odoo-backup.sh

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Backup Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Backup Configuration:${NC}"
echo -e "  Backup Directory: ${YELLOW}$BACKUP_DIR${NC}"
echo -e "  Database: ${YELLOW}$DB_NAME${NC}"
echo -e "  Schedule: ${YELLOW}Daily at 2:00 AM${NC}"
echo -e "  Retention: ${YELLOW}$RETENTION_DAYS days${NC}"
echo ""
echo -e "${GREEN}Manual Backup:${NC}"
echo -e "  ${YELLOW}sudo /usr/local/bin/odoo-backup.sh${NC}"
echo ""
echo -e "${GREEN}View Backup Log:${NC}"
echo -e "  ${YELLOW}tail -f /var/log/odoo-backup.log${NC}"
echo ""
echo -e "${GREEN}List Backups:${NC}"
echo -e "  ${YELLOW}ls -lh $BACKUP_DIR${NC}"
echo ""
