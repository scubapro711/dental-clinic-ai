# 🚀 Staging Deployment Guide
**Created:** October 25, 2025  
**Purpose:** Guide for setting up and using staging environment

---

## 📋 Overview

This guide explains how to set up and use the staging environment for DentaFlow. The staging environment allows you to test changes safely before deploying to production.

---

## 🎯 What is Staging?

**Staging** is a production-like environment where you can:
- ✅ Test new features safely
- ✅ Validate bug fixes before production
- ✅ Run integration tests
- ✅ Perform QA testing
- ✅ Test database migrations
- ✅ Verify security fixes

---

## 🏗️ Architecture

### Staging Environment:
```
┌─────────────────────────────────────────────────────────┐
│                    GCP Project                          │
│              dentaflow-production                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Production                    Staging                  │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │ Cloud Run        │         │ Cloud Run        │    │
│  │ dentaflow-       │         │ dentaflow-       │    │
│  │ backend          │         │ backend-staging  │    │
│  │ (2 CPU, 4GB)     │         │ (1 CPU, 2GB)     │    │
│  └────────┬─────────┘         └────────┬─────────┘    │
│           │                            │               │
│  ┌────────▼─────────┐         ┌───────▼──────────┐    │
│  │ Cloud SQL        │         │ Cloud SQL        │    │
│  │ dentaflow-db-    │         │ dentaflow-db-    │    │
│  │ instance         │         │ staging          │    │
│  │ (db-n1-standard) │         │ (db-f1-micro)    │    │
│  └──────────────────┘         └──────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Git Workflow:
```
main (production)
  ↑
  │ merge after testing
  │
staging (staging environment)
  ↑
  │ merge bug fixes
  │
fix/* branches (individual bug fixes)
```

---

## 🚀 Quick Start

### Step 1: Setup Staging Environment

Run the setup script:
```bash
cd /home/ubuntu/dental-clinic-ai
./scripts/setup-staging.sh
```

This will:
1. Create `staging` branch
2. Create GCP secrets for staging
3. Create Cloud SQL instance (dentaflow-db-staging)
4. Create database (dentaflow_staging)
5. Push staging branch to GitHub

**Time:** ~10-15 minutes (Cloud SQL creation takes time)

---

### Step 2: Merge Bug Fixes to Staging

```bash
# Switch to staging branch
git checkout staging

# Merge bug fixes (example: Bug #26)
git merge origin/fix/bug26-missing-rate-limiting

# Resolve conflicts if any
git add .
git commit -m "Merge Bug #26 to staging"

# Push to trigger deployment
git push origin staging
```

**GitHub Actions will automatically deploy to staging!**

---

### Step 3: Test Staging

Wait for deployment to complete (~5 minutes), then run tests:

```bash
# Automated tests
./scripts/test-staging.sh

# Manual testing
# Get staging URL
gcloud run services describe dentaflow-backend-staging \
  --region=us-central1 \
  --format='value(status.url)'

# Visit the URL and test manually
```

---

### Step 4: Deploy to Production

If all tests pass:

```bash
# Merge staging to main
git checkout main
git merge staging
git push origin main
```

**GitHub Actions will automatically deploy to production!**

---

## 📋 Detailed Setup Instructions

### Prerequisites

1. **GCP Access:**
   - Project: `dentaflow-production`
   - Permissions: Cloud Run Admin, Cloud SQL Admin, Secret Manager Admin

2. **GitHub Access:**
   - Repository: `scubapro711/dental-clinic-ai`
   - Permissions: Push to branches

3. **Tools Installed:**
   - `gcloud` CLI
   - `git`
   - `gh` (GitHub CLI)

---

### Manual Setup (Alternative)

If you prefer manual setup instead of using the script:

#### 1. Create Staging Branch

```bash
git checkout -b staging
git push -u origin staging
```

#### 2. Create GCP Secrets

```bash
PROJECT_ID="dentaflow-production"

# Generate random secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Create secrets
echo -n "$SECRET_KEY" | gcloud secrets create secret-key-staging \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-

echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret-staging \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-
```

#### 3. Create Cloud SQL Instance

```bash
gcloud sql instances create dentaflow-db-staging \
  --project="$PROJECT_ID" \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --network=default \
  --no-assign-ip \
  --backup \
  --backup-start-time=03:00
```

#### 4. Create Database

```bash
gcloud sql databases create dentaflow_staging \
  --instance=dentaflow-db-staging \
  --project="$PROJECT_ID"
```

#### 5. Set Database Password & Create Secret

```bash
DB_PASSWORD=$(openssl rand -base64 32)

gcloud sql users set-password postgres \
  --instance=dentaflow-db-staging \
  --project="$PROJECT_ID" \
  --password="$DB_PASSWORD"

# Create database URL
DB_CONNECTION_NAME="$PROJECT_ID:us-central1:dentaflow-db-staging"
DATABASE_URL="postgresql://postgres:$DB_PASSWORD@/dentaflow_staging?host=/cloudsql/$DB_CONNECTION_NAME"

echo -n "$DATABASE_URL" | gcloud secrets create database-url-staging \
  --project="$PROJECT_ID" \
  --replication-policy="automatic" \
  --data-file=-
```

---

## 🧪 Testing Guide

### Automated Tests

Run the test script:
```bash
./scripts/test-staging.sh
```

This tests:
- ✅ Health endpoints
- ✅ API documentation
- ✅ Authentication endpoints
- ✅ API endpoints (authorization)
- ✅ CORS headers
- ✅ Rate limiting
- ✅ Response time

---

### Manual Testing Checklist

#### 1. Authentication
- [ ] Register new user
- [ ] Login with credentials
- [ ] Logout
- [ ] Password reset

#### 2. Patient Management
- [ ] Create patient
- [ ] View patient list
- [ ] Update patient
- [ ] Delete patient
- [ ] Search patients

#### 3. Appointments
- [ ] Book appointment
- [ ] View appointments
- [ ] Update appointment
- [ ] Cancel appointment

#### 4. AI Agents
- [ ] Chat with Alex (Appointment Agent)
- [ ] Chat with Sarah (Clinical Agent)
- [ ] Chat with Marcus (Financial Agent)
- [ ] Test Harper (HIPAA Monitor)

#### 5. Billing
- [ ] Create invoice
- [ ] Process payment
- [ ] View billing history

#### 6. Security
- [ ] Test rate limiting (make 100 requests)
- [ ] Test CSRF protection
- [ ] Test XSS protection
- [ ] Test SQL injection protection
- [ ] Verify JWT security

---

### Integration Tests

Run pytest:
```bash
cd backend

# Set staging environment
export DATABASE_URL="<staging-db-url>"
export APP_ENV="staging"

# Run tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

---

## 📊 Monitoring Staging

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read dentaflow-backend-staging \
  --region=us-central1 \
  --project=dentaflow-production \
  --limit=100

# Follow logs (real-time)
gcloud run services logs tail dentaflow-backend-staging \
  --region=us-central1 \
  --project=dentaflow-production
```

### View Metrics

```bash
# Get service details
gcloud run services describe dentaflow-backend-staging \
  --region=us-central1 \
  --project=dentaflow-production

# Get revision details
gcloud run revisions list \
  --service=dentaflow-backend-staging \
  --region=us-central1 \
  --project=dentaflow-production
```

---

## 🔄 Deployment Workflow

### Standard Workflow

```
1. Create bug fix branch
   git checkout -b fix/bug-name

2. Fix bug & test locally
   pytest

3. Push to GitHub
   git push origin fix/bug-name

4. Merge to staging
   git checkout staging
   git merge fix/bug-name
   git push origin staging

5. Wait for staging deployment
   (GitHub Actions runs automatically)

6. Test staging
   ./scripts/test-staging.sh

7. If tests pass, merge to main
   git checkout main
   git merge staging
   git push origin main

8. Production deployment
   (GitHub Actions runs automatically)
```

---

### Batch Deployment (Multiple Bug Fixes)

```bash
# Merge multiple fixes to staging
git checkout staging

git merge origin/fix/bug26-missing-rate-limiting
git merge origin/fix/bug30-xss-doctor-chat
git merge origin/fix/bug31-sql-injection
git merge origin/fix/bug32-csrf-protection
git merge origin/fix/bug33-insecure-jwt-secret

# Resolve conflicts if any
git add .
git commit -m "Merge Bugs #26, #30-33 to staging"

# Push to deploy
git push origin staging

# Test thoroughly
./scripts/test-staging.sh

# If all tests pass
git checkout main
git merge staging
git push origin main
```

---

## 🚨 Troubleshooting

### Issue: Staging deployment failed

**Solution:**
```bash
# Check GitHub Actions logs
gh run list --branch staging

# View specific run
gh run view <run-id>

# Check Cloud Run logs
gcloud run services logs read dentaflow-backend-staging \
  --region=us-central1 \
  --limit=100
```

---

### Issue: Database connection failed

**Solution:**
```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe dentaflow-db-staging

# Test connection
gcloud sql connect dentaflow-db-staging --user=postgres

# Check database exists
\l

# Check secrets
gcloud secrets versions access latest --secret=database-url-staging
```

---

### Issue: Tests failing in staging

**Solution:**
1. Check logs for errors
2. Verify all secrets are created
3. Ensure database migrations ran
4. Check service configuration
5. Test endpoints manually

---

## 💰 Cost Optimization

### Staging Environment Costs

**Monthly Costs:**
- Cloud Run (staging): ~$20-30 (1 CPU, 2GB, min 0 instances)
- Cloud SQL (staging): ~$10-15 (db-f1-micro, shared CPU)
- Secrets Manager: ~$1
- **Total: ~$30-45/month**

### Cost Saving Tips

1. **Use smaller instance:**
   - Staging: db-f1-micro (0.6GB RAM)
   - Production: db-n1-standard-1 (3.75GB RAM)

2. **Min instances = 0:**
   - Staging scales to zero when not in use
   - Production keeps min 1 instance

3. **Delete when not needed:**
   ```bash
   # Delete staging (if not using for a while)
   gcloud run services delete dentaflow-backend-staging
   gcloud sql instances delete dentaflow-db-staging
   ```

4. **Recreate when needed:**
   ```bash
   # Recreate staging
   ./scripts/setup-staging.sh
   ```

---

## 📋 Maintenance

### Weekly Tasks

- [ ] Review staging logs
- [ ] Check for failed deployments
- [ ] Update staging with latest main
- [ ] Run security scans

### Monthly Tasks

- [ ] Review staging costs
- [ ] Clean up old revisions
- [ ] Update staging secrets (if needed)
- [ ] Backup staging database

---

## 🎯 Best Practices

### DO:
- ✅ Always test in staging before production
- ✅ Merge multiple related fixes together
- ✅ Run full test suite in staging
- ✅ Perform manual QA in staging
- ✅ Keep staging up-to-date with main

### DON'T:
- ❌ Skip staging for "small" changes
- ❌ Deploy directly to production without testing
- ❌ Use production data in staging
- ❌ Share staging credentials publicly
- ❌ Leave staging running if not using (costs money)

---

## 📚 Additional Resources

### Files Created:
- `.github/workflows/staging-deploy.yml` - Staging deployment workflow
- `terraform/environments/staging/` - Staging infrastructure
- `scripts/setup-staging.sh` - Setup script
- `scripts/test-staging.sh` - Testing script
- `STAGING_DEPLOYMENT_GUIDE.md` - This guide

### Related Documentation:
- `DEPLOYMENT_REPORT_2025-10-24.md` - Production deployment
- `DEPLOYMENT_CHECKLIST.md` - Deployment checklist
- `DEPLOYMENT_RUNBOOK.md` - Deployment procedures

---

## 🆘 Support

If you encounter issues:

1. Check this guide
2. Review GitHub Actions logs
3. Check Cloud Run logs
4. Consult deployment reports
5. Ask for help!

---

**End of Guide**  
**Created by:** Manus AI Agent  
**Date:** October 25, 2025  
**Version:** 1.0

