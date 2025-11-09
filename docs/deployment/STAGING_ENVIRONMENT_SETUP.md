# Staging Environment Setup Guide
## Safe Testing Before Production Deployment

**Date:** October 26, 2025  
**Status:** Ready to Deploy

---

## Why Staging Environment?

### The Problem We Had:
- Changes went directly from development to production
- No safe place to test before users see changes
- PropTypes bug crashed production site
- Had to fix forward instead of testing first

### The Solution:
- **Staging environment** - exact copy of production
- Test all changes in staging first
- Catch bugs before they reach users
- Safe rollback if something breaks

---

## Architecture Overview

```
Development → Staging → Production

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Developer  │────▶│   Staging   │────▶│ Production  │
│   Laptop    │     │  Cloud Run  │     │ Cloud Run   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      │                    │                    │
   develop              staging              main
   branch               branch              branch
```

### Workflow:
1. **Developer** makes changes locally
2. **Commit** to `develop` branch
3. **Auto-deploy** to staging environment
4. **Test** in staging (staging.dentaflow.ai)
5. **Merge** to `main` branch if tests pass
6. **Auto-deploy** to production (dentaflow.ai)

---

## Step-by-Step Setup

### Step 1: Create Staging Cloud Run Service

**Run these commands in Cloud Shell:**

```bash
# Set project
gcloud config set project dentaflow-production

# Deploy staging service
gcloud run deploy dentaflow-frontend-staging \
  --image us-central1-docker.pkg.dev/dentaflow-production/cloud-run-source-deploy/dentaflow-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "VITE_APP_ENV=staging" \
  --tag staging

# Get the staging URL
gcloud run services describe dentaflow-frontend-staging \
  --region us-central1 \
  --format "value(status.url)"
```

**Expected output:**
```
Service [dentaflow-frontend-staging] revision [dentaflow-frontend-staging-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://dentaflow-frontend-staging-gmi5lyn5wq-uc.a.run.app
```

### Step 2: Create Develop Branch

```bash
cd ~/dental-clinic-ai

# Create develop branch from main
git checkout -b develop
git push -u origin develop

# Set develop as default branch for staging
git branch --set-upstream-to=origin/develop develop
```

### Step 3: Create Staging Cloud Build Trigger

**Option A: Using gcloud CLI**

```bash
# Create Cloud Build trigger for staging
gcloud builds triggers create github \
  --name="frontend-staging-deploy" \
  --repo-name="dental-clinic-ai" \
  --repo-owner="scubapro711" \
  --branch-pattern="^develop$" \
  --build-config="frontend/cloudbuild-staging.yaml" \
  --description="Auto-deploy frontend to staging on develop branch push" \
  --region=us-central1
```

**Option B: Using Google Cloud Console**

1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click "Create Trigger"
3. Fill in:
   - **Name:** `frontend-staging-deploy`
   - **Event:** Push to a branch
   - **Source:** `scubapro711/dental-clinic-ai`
   - **Branch:** `^develop$`
   - **Build configuration:** Cloud Build configuration file
   - **Location:** `frontend/cloudbuild-staging.yaml`
4. Click "Create"

### Step 4: Create Staging Build Configuration

Create `frontend/cloudbuild-staging.yaml`:

```yaml
# Cloud Build configuration for staging deployment
# Triggers on push to 'develop' branch

steps:
  # Step 1: Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/dentaflow-frontend-staging:$SHORT_SHA'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/dentaflow-frontend-staging:latest'
      - '-f'
      - 'Dockerfile'
      - '.'
    dir: 'frontend'

  # Step 2: Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/dentaflow-frontend-staging:$SHORT_SHA'

  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/dentaflow-frontend-staging:latest'

  # Step 3: Deploy to Cloud Run (Staging)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'dentaflow-frontend-staging'
      - '--image'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/dentaflow-frontend-staging:$SHORT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'VITE_APP_ENV=staging'
      - '--tag'
      - 'staging-$SHORT_SHA'

# Build timeout
timeout: '1200s'

# Substitutions
substitutions:
  _SERVICE_NAME: dentaflow-frontend-staging
  _REGION: us-central1

# Options
options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'
```

### Step 5: Configure Domain Mapping (Optional)

**Map staging.dentaflow.ai to staging service:**

```bash
# Create domain mapping
gcloud run domain-mappings create \
  --service dentaflow-frontend-staging \
  --domain staging.dentaflow.ai \
  --region us-central1

# Get DNS records to configure
gcloud run domain-mappings describe \
  --domain staging.dentaflow.ai \
  --region us-central1
```

**Then add DNS records in your domain registrar:**
- Type: CNAME
- Name: staging
- Value: ghs.googlehosted.com

---

## Testing the Staging Environment

### Test 1: Manual Deployment

```bash
# Make a small change
cd ~/dental-clinic-ai/frontend
echo "// Staging test" >> src/main.jsx

# Commit to develop branch
git checkout develop
git add src/main.jsx
git commit -m "test: Staging environment test"
git push origin develop

# Wait 3-5 minutes for build
# Check build status:
gcloud builds list --limit=1
```

### Test 2: Verify Staging Site

```bash
# Get staging URL
STAGING_URL=$(gcloud run services describe dentaflow-frontend-staging \
  --region us-central1 \
  --format "value(status.url)")

# Test staging site
curl -I $STAGING_URL

# Should return: HTTP/2 200
```

### Test 3: Compare Staging vs Production

```bash
# Check staging version
curl -s $STAGING_URL | grep -o '<title>.*</title>'

# Check production version
curl -s https://dentaflow.ai | grep -o '<title>.*</title>'

# They should be identical (for now)
```

---

## Workflow Examples

### Example 1: Adding a New Feature

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-appointment-ui

# 2. Make changes
# ... edit files ...

# 3. Commit changes
git add .
git commit -m "feat: Add new appointment UI"

# 4. Merge to develop (triggers staging deployment)
git checkout develop
git merge feature/new-appointment-ui
git push origin develop

# 5. Wait for staging deployment (3-5 min)
# 6. Test on staging.dentaflow.ai
# 7. If good, merge to main
git checkout main
git merge develop
git push origin main

# 8. Production deployment happens automatically
```

### Example 2: Hotfix in Production

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix the bug
# ... edit files ...

# 3. Commit fix
git add .
git commit -m "fix: Critical bug in payment processing"

# 4. Merge to develop first (test in staging)
git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 5. Test in staging
# ... verify fix works ...

# 6. Merge to main (deploy to production)
git checkout main
git merge hotfix/critical-bug
git push origin main

# 7. Merge back to develop
git checkout develop
git merge main
git push origin develop
```

---

## Environment Differences

### Staging vs Production

| Aspect | Staging | Production |
|--------|---------|------------|
| **URL** | staging.dentaflow.ai | dentaflow.ai |
| **Branch** | develop | main |
| **Deployment** | Auto on push to develop | Auto on push to main |
| **Data** | Test data | Real user data |
| **Sentry** | staging environment tag | production environment tag |
| **Min instances** | 0 (can scale to zero) | 1 (always running) |
| **Users** | Internal team only | Public |
| **Purpose** | Testing & QA | Live service |

### Environment Variables

**Staging (.env.staging):**
```bash
VITE_APP_ENV=staging
VITE_API_URL=https://dentaflow-backend-staging-xxx.run.app/api/v1
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
VITE_SENTRY_ENVIRONMENT=staging
```

**Production (.env.production):**
```bash
VITE_APP_ENV=production
VITE_API_URL=https://dentaflow-backend-xxx.run.app/api/v1
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
VITE_SENTRY_ENVIRONMENT=production
```

---

## Monitoring Staging

### Check Deployment Status

```bash
# List recent builds
gcloud builds list --limit=5

# Get specific build details
gcloud builds describe BUILD_ID

# View build logs
gcloud builds log BUILD_ID
```

### Check Service Health

```bash
# Get service details
gcloud run services describe dentaflow-frontend-staging \
  --region us-central1

# Check recent revisions
gcloud run revisions list \
  --service dentaflow-frontend-staging \
  --region us-central1 \
  --limit=5
```

### View Logs

```bash
# View staging logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dentaflow-frontend-staging" \
  --limit=50 \
  --format=json
```

---

## Cost Considerations

### Staging Environment Costs

**Estimated monthly cost:**
- Cloud Run (staging): ~$5-10/month
  - Min instances: 0 (scales to zero when not used)
  - Only charged when running
  - Mostly used during work hours
- Cloud Build: ~$5/month
  - First 120 build-minutes/day free
  - Staging builds ~5 min each
- Artifact Registry: ~$1/month
  - Storage for Docker images

**Total: ~$10-15/month**

**Cost savings:**
- Prevents production outages (priceless!)
- Catches bugs before users see them
- Faster development (no fear of breaking prod)

---

## Best Practices

### 1. Always Test in Staging First

```bash
# ❌ DON'T: Push directly to main
git checkout main
git add .
git commit -m "feat: new feature"
git push origin main  # Goes straight to production!

# ✅ DO: Test in staging first
git checkout develop
git add .
git commit -m "feat: new feature"
git push origin develop  # Deploy to staging
# ... test in staging ...
# ... if good, merge to main ...
```

### 2. Keep Staging and Production in Sync

```bash
# Regularly sync develop with main
git checkout develop
git merge main
git push origin develop
```

### 3. Use Staging for Load Testing

```bash
# Run load tests against staging
ab -n 1000 -c 10 https://staging.dentaflow.ai/

# Or use k6, Artillery, etc.
```

### 4. Test Rollbacks in Staging

```bash
# Deploy bad version to staging
git checkout develop
# ... make breaking change ...
git push origin develop

# Practice rollback
gcloud run services update-traffic dentaflow-frontend-staging \
  --to-revisions PREVIOUS_REVISION=100 \
  --region us-central1
```

---

## Troubleshooting

### Issue: Staging deployment fails

**Check build logs:**
```bash
gcloud builds list --limit=1
gcloud builds log BUILD_ID
```

**Common causes:**
- Build timeout (increase in cloudbuild-staging.yaml)
- Missing dependencies (check package.json)
- Docker build errors (check Dockerfile)

### Issue: Staging site shows old version

**Force new deployment:**
```bash
# Trigger manual deployment
gcloud builds submit \
  --config=frontend/cloudbuild-staging.yaml \
  --substitutions=SHORT_SHA="manual-$(date +%s)" \
  frontend/
```

### Issue: Can't access staging site

**Check service status:**
```bash
gcloud run services describe dentaflow-frontend-staging \
  --region us-central1

# Check if service is public
gcloud run services get-iam-policy dentaflow-frontend-staging \
  --region us-central1
```

---

## Next Steps

### Immediate:
1. ✅ Create staging Cloud Run service
2. ✅ Create develop branch
3. ✅ Create Cloud Build trigger
4. ✅ Test deployment

### Short-term:
5. Configure domain mapping (staging.dentaflow.ai)
6. Set up staging backend service
7. Create staging database
8. Document staging testing procedures

### Ongoing:
9. Always test in staging before production
10. Monitor staging for errors
11. Keep staging in sync with production
12. Use staging for demos and training

---

## Success Criteria

**Staging environment is working when:**
- ✅ Push to develop triggers automatic deployment
- ✅ Staging site accessible at staging URL
- ✅ Can test changes without affecting production
- ✅ Can rollback staging deployments easily
- ✅ Staging errors don't affect production

---

**Document Version:** 1.0  
**Last Updated:** October 26, 2025  
**Next Review:** After staging deployment

