# 🚀 DentaFlow SaaS - Deployment Runbook

**Date:** October 24, 2025  
**Version:** 1.0  
**Owner:** Manus AI Agent

---

## 📋 Overview

This runbook provides a step-by-step guide for deploying the DentaFlow SaaS backend to Google Cloud Run. It covers pre-deployment checks, the deployment process, and post-deployment verification.

### Production Environment

| Component | URL |
|-----------|-----|
| **Frontend** | https://dentaflow.ai |
| **Backend** | https://dentaflow-backend-gmi5lyn5wq-uc.a.run.app |
| **Health Check** | `/health` |
| **API Docs** | `/docs` |

### CI/CD Pipeline

- **GitHub Repository:** https://github.com/scubapro711/dental-clinic-ai
- **GitHub Actions:** https://github.com/scubapro711/dental-clinic-ai/actions
- **Deployment Workflow:** `backend-deploy.yml`
- **Test Workflow:** `tests.yml`

---

## ⚙️ Pre-Deployment Checklist

Before initiating a deployment, ensure the following steps are completed:

### 1. Code Quality & Testing

**Goal:** Ensure code is production-ready and all tests pass.

- [ ] **Feature Complete:** All new features are fully implemented and tested.
- [ ] **Code Review:** All code has been reviewed by at least one other developer.
- [ ] **Run Local Tests:**
  ```bash
  cd backend && python3.11 -m pytest
  ```
- [ ] **100% Pass Rate:** All 738 critical tests must pass.
- [ ] **Coverage Check:** Ensure coverage is above 40% (or target threshold).
- [ ] **No Regressions:** Verify no existing functionality is broken.

### 2. Git Workflow

**Goal:** Create a clean and well-documented commit.

- [ ] **Pull Latest Changes:**
  ```bash
  git pull origin main
  ```
- [ ] **Check Git Status:**
  ```bash
  git status --short
  ```
- [ ] **Add All Changes:**
  ```bash
  git add -A
  ```
- [ ] **Create Comprehensive Commit:**
  ```bash
  git commit -m "feat: [Your Feature] - [Brief Description]"
  ```
  *Include details on tests, infrastructure changes, and documentation.*

### 3. Push to GitHub

**Goal:** Trigger the automated CI/CD pipeline.

- [ ] **Push to `main` branch:**
  ```bash
  git push origin main
  ```
- [ ] **Verify Workflow Start:** Check GitHub Actions to ensure the `Deploy Backend to Cloud Run` workflow has started.

---

## 🚀 Deployment Process (Automated)

This process is fully automated by GitHub Actions. No manual intervention is required.

### Workflow: `Deploy Backend to Cloud Run`

**Trigger:** Push to `main` branch with backend changes.

**Steps:**
1. ✅ **Checkout code**
2. ✅ **Authenticate to Google Cloud** (using `GCP_SA_KEY` secret)
3. ✅ **Set up Cloud SDK**
4. ✅ **Configure Docker for GCR**
5. ✅ **Build and Push Docker Image**
   - Image is tagged with `v<date>-<commit-hash>`
   - Pushed to Google Container Registry (GCR)
6. ✅ **Deploy to Cloud Run**
   - New revision created for `dentaflow-backend` service
   - Secrets from Secret Manager are injected
   - Environment variables are set
7. ✅ **Get Service URL**
8. ✅ **Verify Deployment**
   - `curl` request to `/health` endpoint
   - Fails if health check returns non-200 status

### Monitoring the Deployment

- **GitHub Actions:**
  ```bash
  gh run list --limit 5
  gh run watch <run-id>
  ```
- **Google Cloud Console:**
  - Cloud Run: `https://console.cloud.google.com/run`
  - Cloud Build: `https://console.cloud.google.com/cloud-build`

---

## 🧪 Post-Deployment Verification

After a successful deployment, perform the following checks to ensure the system is fully operational.

### 1. Automated Health Check

- **Status:** ✅ Completed by GitHub Actions
- **URL:** `https://dentaflow-backend-gmi5lyn5wq-uc.a.run.app/health`
- **Expected Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "service": "dentaflow-backend",
    "version": "24.0.3",
    "phase": "Phase 4 - Production Ready"
  }
  ```

### 2. Manual API Verification

- **API Docs:**
  - **URL:** `https://dentaflow-backend-gmi5lyn5wq-uc.a.run.app/docs`
  - **Note:** Swagger UI may have loading issues. Use `openapi.json` instead.
- **OpenAPI Schema:**
  - **URL:** `https://dentaflow-backend-gmi5lyn5wq-uc.a.run.app/openapi.json`
  - **Command:**
    ```bash
    curl -s <backend-url>/openapi.json | jq ".info.version, .paths | keys | length"
    ```
  - **Expected:** `"24.0.3"` and `236`

### 3. Smoke Tests

**Goal:** Perform a quick validation of critical user flows.

- [ ] **User Login:**
  - Attempt to log in with a test user.
  - Verify successful token generation.
- [ ] **Dashboard Access:**
  - Access a key dashboard endpoint (e.g., `/dashboard/overview`).
  - Verify successful response.
- [ ] **Patient Search:**
  - Search for a test patient.
  - Verify correct results are returned.
- [ ] **AI Chat:**
  - Send a message to an AI agent.
  - Verify a valid response is received.

### 4. Load Testing (Optional)

**Goal:** Assess system performance under load.

- **Tool:** Locust
- **Script:** `backend/tests/load/locustfile.py`
- **Command:**
  ```bash
  locust -f locustfile.py --host=<backend-url> --headless -u 10 -r 2 -t 2m
  ```
- **Note:** Requires pre-existing test users in the database.

---

## 🆘 Troubleshooting

### Deployment Failures

| Issue | Action |
|-------|--------|
| **Test Failures** | - Check local tests first
  - Review GitHub Actions logs
  - Fix failing tests and re-run |
| **Build Failures** | - Check `Dockerfile` for errors
  - Ensure all dependencies are in `requirements.txt`
  - Review Cloud Build logs |
| **Health Check Failures** | - Check Cloud Run logs for application errors
  - Verify database connectivity
  - Ensure all secrets are correctly configured |
| **Permission Errors** | - Verify service account has `Cloud Run Admin` and `Secret Manager Secret Accessor` roles
  - Check IAM permissions in GCP |

### Common Errors

- **`Streaming is not supported`:** OpenAI mock in tests needs to be updated.
- **`AttributeError` in tests:** Fixture conflict or incorrect test setup.
- **Swagger UI blank page:** CORS issue or JavaScript error. Check browser console.

---

## 📞 Support

- **Primary Contact:** Manus AI Agent
- **GitHub Issues:** https://github.com/scubapro711/dental-clinic-ai/issues
- **GCP Support:** https://console.cloud.google.com/support

---

**Runbook Status:** ✅ **COMPLETE**  
**Last Updated:** October 24, 2025

