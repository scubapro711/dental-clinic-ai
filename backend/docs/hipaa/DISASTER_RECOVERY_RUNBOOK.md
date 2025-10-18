# DentaFlow - Disaster Recovery Runbook

**Version:** 1.0  
**Date:** October 18, 2025  
**Status:** Active  
**Owner:** Eran Sarfaty, CTO & Security Officer

---

## 1. Executive Summary

This Disaster Recovery (DR) Runbook provides step-by-step procedures for recovering DentaFlow SaaS infrastructure and data in the event of a disaster. The goal is to minimize downtime and data loss while ensuring HIPAA compliance throughout the recovery process.

**Recovery Objectives:**
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 1 hour
- **Data Loss Tolerance:** Maximum 1 hour of transactions

---

## 2. Disaster Scenarios

### 2.1 Severity Levels

| Level | Description | RTO | Example |
|-------|-------------|-----|---------|
| **P0 - Critical** | Complete service outage | 1 hour | Database corruption, GCP region failure |
| **P1 - High** | Major functionality impaired | 4 hours | Backend service crash, database connection loss |
| **P2 - Medium** | Partial functionality impaired | 8 hours | Single microservice failure, CDN issues |
| **P3 - Low** | Minor issues, workarounds available | 24 hours | Non-critical feature bug, UI glitch |

### 2.2 Disaster Types

1. **Infrastructure Failure**
   - GCP region outage
   - Cloud Run service failure
   - Cloud SQL database failure
   - Networking issues

2. **Data Loss/Corruption**
   - Database corruption
   - Accidental data deletion
   - Ransomware attack

3. **Security Incident**
   - Data breach
   - Unauthorized access
   - DDoS attack

4. **Human Error**
   - Accidental deployment of broken code
   - Configuration errors
   - Accidental data deletion

---

## 3. Contact Information

### 3.1 Incident Response Team

| Role | Name | Phone | Email | Availability |
|------|------|-------|-------|--------------|
| **Security Officer** | Eran Sarfaty | +972-XX-XXX-XXXX | eran@dentaflow.co.il | 24/7 |
| **Privacy Officer** | Eran Sarfaty | +972-XX-XXX-XXXX | eran@dentaflow.co.il | 24/7 |
| **Technical Lead** | Eran Sarfaty | +972-XX-XXX-XXXX | eran@dentaflow.co.il | 24/7 |
| **Legal Counsel** | [External] | [TBD] | [TBD] | Business hours |

### 3.2 External Contacts

| Service | Contact | Phone | Email | SLA |
|---------|---------|-------|-------|-----|
| **GCP Support** | Google Cloud | +1-877-355-5787 | - | 24/7, 15-min response |
| **Odoo Support** | Odoo S.A. | [TBD] | support@odoo.com | Business hours |
| **Stripe Support** | Stripe | - | support@stripe.com | 24/7 |

### 3.3 Customer Communication

| Channel | Contact | Purpose |
|---------|---------|---------|
| **Status Page** | status.dentaflow.ai | Public incident updates |
| **Email** | support@dentaflow.co.il | Direct customer communication |
| **Slack** | #dentaflow-status | Internal team communication |

---

## 4. Pre-Disaster Preparation

### 4.1 Backup Verification (Daily)

```bash
# Verify latest backup exists and is valid
cd /home/ubuntu/dental-clinic-ai-repo
./scripts/verify-backup.sh

# Expected output:
# ✅ Latest backup: dentaflow_YYYYMMDD_HHMMSS.sql.gz
# ✅ Backup integrity verified
# ✅ Backup size: XXX MB
# ✅ S3 upload confirmed
```

### 4.2 Recovery Testing (Monthly)

```bash
# Test restore to staging environment
./scripts/restore-database.sh \
  --latest \
  --target dentaflow_staging \
  --dry-run

# If dry-run succeeds, perform actual restore
./scripts/restore-database.sh \
  --latest \
  --target dentaflow_staging
```

### 4.3 Documentation Review (Quarterly)

- [ ] Review and update this runbook
- [ ] Test all recovery procedures
- [ ] Update contact information
- [ ] Verify backup retention policies

---

## 5. Disaster Recovery Procedures

### 5.1 P0 - Complete Database Failure

**Scenario:** Cloud SQL database is corrupted or inaccessible

**Detection:**
- Application logs show database connection errors
- Cloud SQL console shows instance as unhealthy
- Monitoring alerts triggered

**Recovery Steps:**

#### Step 1: Assess the Situation (5 minutes)

```bash
# Check Cloud SQL instance status
gcloud sql instances describe dentaflow-db --project=dentaflow-prod

# Check recent backups
gcloud sql backups list --instance=dentaflow-db --project=dentaflow-prod

# Check application logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 --format=json --project=dentaflow-prod
```

#### Step 2: Activate Incident Response (5 minutes)

1. **Declare P0 incident**
   ```bash
   # Post to Slack
   curl -X POST $SLACK_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text":"🚨 P0 INCIDENT: Database failure detected. DR procedures activated."}'
   ```

2. **Update status page**
   - Navigate to status.dentaflow.ai
   - Create incident: "Database connectivity issues"
   - Status: "Major outage"

3. **Notify customers**
   ```bash
   # Send email to all clinic admins
   python3 scripts/send-incident-notification.py \
     --severity=P0 \
     --message="We are experiencing database issues and are working to restore service."
   ```

#### Step 3: Attempt Quick Recovery (15 minutes)

```bash
# Option A: Restart Cloud SQL instance
gcloud sql instances restart dentaflow-db --project=dentaflow-prod

# Wait 2 minutes
sleep 120

# Test connection
psql -h <CLOUD_SQL_IP> -U dentaflow_user -d dentaflow -c "SELECT 1;"

# If successful, verify application
curl https://api.dentaflow.ai/health
```

#### Step 4: Full Database Restore (30-60 minutes)

If quick recovery fails:

```bash
# 1. Create new Cloud SQL instance (if needed)
gcloud sql instances create dentaflow-db-recovery \
  --database-version=POSTGRES_14 \
  --tier=db-n1-standard-2 \
  --region=us-central1 \
  --backup \
  --project=dentaflow-prod

# 2. Restore from latest automated backup
gcloud sql backups restore <BACKUP_ID> \
  --backup-instance=dentaflow-db \
  --backup-project=dentaflow-prod \
  --instance=dentaflow-db-recovery \
  --project=dentaflow-prod

# 3. Or restore from manual backup
./scripts/restore-database.sh \
  --s3 \
  --target dentaflow \
  --host <NEW_INSTANCE_IP>

# 4. Update application configuration
gcloud secrets versions add dentaflow-db-host \
  --data-file=- <<< "<NEW_INSTANCE_IP>"

# 5. Deploy new backend revision
gcloud run deploy dentaflow-backend \
  --image=gcr.io/dentaflow-prod/backend:latest \
  --update-secrets=DATABASE_HOST=dentaflow-db-host:latest \
  --project=dentaflow-prod

# 6. Verify recovery
curl https://api.dentaflow.ai/health
curl https://api.dentaflow.ai/api/v1/dashboard/metrics
```

#### Step 5: Verify Data Integrity (15 minutes)

```bash
# Connect to database
psql -h <INSTANCE_IP> -U dentaflow_user -d dentaflow

-- Check table counts
SELECT 
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Check latest records
SELECT MAX(created_at) FROM users;
SELECT MAX(created_at) FROM appointments;
SELECT MAX(created_at) FROM audit_logs;

-- Verify no corruption
SELECT * FROM users LIMIT 10;
SELECT * FROM appointments WHERE created_at > NOW() - INTERVAL '1 day';
```

#### Step 6: Resume Service (5 minutes)

```bash
# Update status page
# - Status: "Operational"
# - Post-mortem: Schedule within 24 hours

# Notify customers
python3 scripts/send-incident-notification.py \
  --severity=RESOLVED \
  --message="Service has been restored. All systems operational."

# Monitor for 30 minutes
watch -n 30 'curl -s https://api.dentaflow.ai/health | jq'
```

**Total Time:** 60-90 minutes  
**Data Loss:** Maximum 1 hour (last backup)

---

### 5.2 P0 - GCP Region Failure

**Scenario:** Entire GCP region (us-central1) is down

**Recovery Steps:**

#### Step 1: Activate Multi-Region Failover (Future)

*Note: Currently single-region. Multi-region setup is planned for Month 3-4.*

```bash
# Switch DNS to backup region
gcloud dns record-sets transaction start --zone=dentaflow-zone
gcloud dns record-sets transaction add <BACKUP_REGION_IP> \
  --name=api.dentaflow.ai. \
  --ttl=300 \
  --type=A \
  --zone=dentaflow-zone
gcloud dns record-sets transaction execute --zone=dentaflow-zone
```

#### Step 2: Deploy to Backup Region (Manual - 2-4 hours)

```bash
# 1. Create Cloud SQL instance in backup region
gcloud sql instances create dentaflow-db-backup \
  --database-version=POSTGRES_14 \
  --tier=db-n1-standard-2 \
  --region=europe-west1 \
  --project=dentaflow-prod

# 2. Restore database from S3 backup
./scripts/restore-database.sh \
  --s3 \
  --target dentaflow \
  --host <BACKUP_INSTANCE_IP>

# 3. Deploy backend to backup region
gcloud run deploy dentaflow-backend \
  --image=gcr.io/dentaflow-prod/backend:latest \
  --region=europe-west1 \
  --project=dentaflow-prod

# 4. Deploy frontend to backup region
gsutil -m rsync -r gs://dentaflow-frontend/ gs://dentaflow-frontend-backup/

# 5. Update DNS (see Step 1)
```

**Total Time:** 2-4 hours  
**Data Loss:** Maximum 1 hour

---

### 5.3 P1 - Backend Service Crash

**Scenario:** Cloud Run backend service is down or unresponsive

**Recovery Steps:**

#### Step 1: Check Service Status (2 minutes)

```bash
# Check Cloud Run service
gcloud run services describe dentaflow-backend \
  --region=us-central1 \
  --project=dentaflow-prod

# Check recent logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=100 --format=json --project=dentaflow-prod | jq
```

#### Step 2: Rollback to Previous Version (5 minutes)

```bash
# List recent revisions
gcloud run revisions list \
  --service=dentaflow-backend \
  --region=us-central1 \
  --project=dentaflow-prod

# Rollback to previous stable revision
gcloud run services update-traffic dentaflow-backend \
  --to-revisions=<PREVIOUS_REVISION>=100 \
  --region=us-central1 \
  --project=dentaflow-prod

# Verify
curl https://api.dentaflow.ai/health
```

#### Step 3: Investigate Root Cause (15 minutes)

```bash
# Download logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=1000 \
  --format=json \
  --project=dentaflow-prod > /tmp/backend-logs.json

# Analyze errors
cat /tmp/backend-logs.json | jq -r 'select(.severity=="ERROR") | .textPayload'

# Check for common issues:
# - Database connection errors
# - Memory leaks (OOM)
# - Unhandled exceptions
# - External API failures (Odoo, Stripe, LLM)
```

**Total Time:** 20-30 minutes  
**Data Loss:** None

---

### 5.4 P1 - Data Breach / Ransomware

**Scenario:** Unauthorized access detected or ransomware attack

**Recovery Steps:**

#### Step 1: Immediate Containment (5 minutes)

```bash
# 1. Isolate affected systems
gcloud run services update dentaflow-backend \
  --no-allow-unauthenticated \
  --region=us-central1 \
  --project=dentaflow-prod

# 2. Revoke all active sessions
psql -h <DB_HOST> -U dentaflow_user -d dentaflow -c \
  "UPDATE users SET session_token = NULL;"

# 3. Disable external access
gcloud sql instances patch dentaflow-db \
  --no-assign-ip \
  --project=dentaflow-prod

# 4. Take database snapshot
gcloud sql backups create \
  --instance=dentaflow-db \
  --description="Emergency backup - security incident" \
  --project=dentaflow-prod
```

#### Step 2: Assess Damage (15 minutes)

```bash
# Check audit logs for unauthorized access
psql -h <DB_HOST> -U dentaflow_user -d dentaflow <<EOF
SELECT 
  user_id,
  action,
  resource_type,
  resource_id,
  created_at,
  ip_address
FROM audit_logs
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND (
    action LIKE '%DELETE%' OR
    action LIKE '%EXPORT%' OR
    ip_address NOT IN (SELECT DISTINCT ip_address FROM audit_logs WHERE created_at < NOW() - INTERVAL '7 days')
  )
ORDER BY created_at DESC;
EOF

# Check for data exfiltration
SELECT 
  user_id,
  COUNT(*) as access_count,
  COUNT(DISTINCT resource_id) as unique_resources
FROM audit_logs
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND action = 'READ'
GROUP BY user_id
HAVING COUNT(*) > 100
ORDER BY access_count DESC;
```

#### Step 3: Breach Notification (Per HIPAA)

**If breach affects 500+ individuals:**

1. **Notify HHS within 60 days**
   - Submit breach report: https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf
   - Include: Date of breach, number affected, description, mitigation

2. **Notify affected clinics immediately**
   ```bash
   python3 scripts/send-breach-notification.py \
     --affected-clinics=<CLINIC_IDS> \
     --breach-date=<DATE> \
     --description="<DESCRIPTION>"
   ```

3. **Notify media (if 500+ in same jurisdiction)**
   - Draft press release
   - Coordinate with legal counsel

**If breach affects <500 individuals:**
- Maintain log for annual HHS reporting
- Notify affected clinics within 60 days

#### Step 4: Forensic Investigation (1-3 days)

```bash
# Preserve evidence
gcloud compute instances create forensics-vm \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --zone=us-central1-a \
  --project=dentaflow-prod

# Copy logs for analysis
gsutil -m cp -r gs://dentaflow-logs/* /forensics/logs/

# Engage external security firm (if needed)
# - Conduct forensic analysis
# - Identify attack vector
# - Assess damage
# - Provide remediation recommendations
```

#### Step 5: Remediation (1-2 weeks)

- [ ] Patch vulnerabilities
- [ ] Reset all passwords
- [ ] Implement additional security controls
- [ ] Conduct security audit
- [ ] Update incident response procedures

**Total Time:** 1-3 weeks  
**Data Loss:** Depends on attack

---

## 6. Post-Disaster Activities

### 6.1 Post-Mortem Report (Within 48 hours)

**Template:**

```markdown
# Incident Post-Mortem: [INCIDENT_NAME]

**Date:** [DATE]
**Severity:** P0/P1/P2/P3
**Duration:** [DURATION]
**Impact:** [DESCRIPTION]

## Timeline

| Time | Event |
|------|-------|
| 00:00 | Incident detected |
| 00:05 | P0 declared |
| 00:10 | Recovery started |
| 01:30 | Service restored |

## Root Cause

[DETAILED ANALYSIS]

## Resolution

[WHAT WAS DONE]

## Lessons Learned

### What Went Well
- [ITEM 1]
- [ITEM 2]

### What Went Wrong
- [ITEM 1]
- [ITEM 2]

### Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [ACTION 1] | [OWNER] | [DATE] | [ ] |
| [ACTION 2] | [OWNER] | [DATE] | [ ] |

## Prevention

[HOW TO PREVENT IN FUTURE]
```

### 6.2 Update Documentation

- [ ] Update this runbook with lessons learned
- [ ] Update monitoring alerts
- [ ] Update backup procedures
- [ ] Update security controls

### 6.3 Team Debrief

- [ ] Schedule team meeting within 1 week
- [ ] Review incident timeline
- [ ] Discuss improvements
- [ ] Assign action items

---

## 7. Testing Schedule

| Test Type | Frequency | Last Test | Next Test | Owner |
|-----------|-----------|-----------|-----------|-------|
| **Backup Verification** | Daily | Automated | Automated | System |
| **Restore Test (Staging)** | Monthly | [DATE] | [DATE] | Eran Sarfaty |
| **DR Drill (Full)** | Quarterly | [DATE] | [DATE] | Eran Sarfaty |
| **Tabletop Exercise** | Annually | [DATE] | [DATE] | Eran Sarfaty |

---

## 8. Compliance Requirements

### 8.1 HIPAA Requirements

- ✅ Backup and disaster recovery plan documented
- ✅ RTO/RPO defined
- ✅ Testing schedule established
- ✅ Incident response procedures documented
- ✅ Breach notification procedures documented

### 8.2 Audit Trail

All disaster recovery activities must be logged in:
- `/var/log/dentaflow/dr-activities.log`
- Audit logs table in database
- Incident tracking system

### 8.3 Retention

- Backup retention: 30 days (local), 90 days (S3), 7 years (Glacier)
- DR logs retention: 6 years (HIPAA requirement)
- Incident reports retention: 6 years (HIPAA requirement)

---

## 9. Appendix

### 9.1 Quick Reference Commands

```bash
# Check system health
curl https://api.dentaflow.ai/health

# Check database
psql -h <DB_HOST> -U dentaflow_user -d dentaflow -c "SELECT 1;"

# Backup database
./scripts/backup-database.sh

# Restore database
./scripts/restore-database.sh --latest

# Rollback backend
gcloud run services update-traffic dentaflow-backend \
  --to-revisions=<PREVIOUS_REVISION>=100 \
  --region=us-central1 \
  --project=dentaflow-prod

# Check logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 --project=dentaflow-prod
```

### 9.2 Emergency Contacts

**GCP Support:**
- Phone: +1-877-355-5787
- Portal: https://console.cloud.google.com/support

**Eran Sarfaty (Security Officer):**
- Phone: +972-XX-XXX-XXXX
- Email: eran@dentaflow.co.il
- Available: 24/7

---

**Document Control:**
- **Created:** October 18, 2025
- **Last Updated:** October 18, 2025
- **Next Review:** January 18, 2026
- **Owner:** Eran Sarfaty, CTO & Security Officer
- **Approved By:** Eran Sarfaty

---

*This document is confidential and proprietary to DentaFlow Ltd.*

