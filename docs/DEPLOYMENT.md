# DentaFlow Deployment Guide

**Status:** ✅ Current | **Last Updated:** November 21, 2025

This document explains the deployment process for DentaFlow's backend and frontend services. It is optimized for AI development agents.

---

## 1. Overview

- **Platform:** Google Cloud Run (Serverless Containers)
- **Automation:** GitHub Actions for CI/CD
- **Environments:** `staging` and `production`

---

## 2. CI/CD Workflows

All deployment workflows are located in `/.github/workflows`.

| Workflow File | Purpose | Trigger |
|---|---|---|
| `backend-deploy.yml` | Deploys the backend service | Push to `main` (production) or `develop` (staging) |
| `frontend-deploy.yml` | Deploys the frontend service | Push to `main` (production) or `develop` (staging) |
| `migrate-staging.yml` | Runs DB migrations on staging | Push to `develop` with `migrations/` changes |
| `migrate-production.yml` | Runs DB migrations on production | Push to `main` with `migrations/` changes |

---

## 3. Staging Environment

- **Purpose:** For testing, QA, and integration before production.
- **Trigger Branch:** `develop`

### Staging Deployment Process

1. **Push to `develop`:** A developer pushes code to the `develop` branch.
2. **GitHub Actions Trigger:**
   - If `backend/**` files were changed, `backend-deploy.yml` runs.
   - If `frontend/**` files were changed, `frontend-deploy.yml` runs.
   - If `backend/alembic/versions/**` files were changed, `migrate-staging.yml` runs.
3. **Build & Deploy:** The workflow builds the Docker image and deploys it to the staging Cloud Run service.
4. **Migration:** The migration workflow connects to the staging database and applies new migrations.

### Staging URLs

| Service | URL |
|---|---|
| **Frontend** | `https://dentaflow-frontend-staging-*.run.app` |
| **Backend** | `https://dentaflow-backend-staging-*.run.app` |

---

## 4. Production Environment

- **Purpose:** Live environment for real users.
- **Trigger Branch:** `main`

### Production Deployment Process

1. **Merge to `main`:** A pull request from `develop` is merged into the `main` branch.
2. **GitHub Actions Trigger:**
   - `backend-deploy.yml` runs for backend changes.
   - `frontend-deploy.yml` runs for frontend changes.
   - `migrate-production.yml` runs for migration changes.
3. **Build & Deploy:** The workflow builds and deploys to the production Cloud Run service.
4. **Migration:** The production migration workflow includes a **database backup step** before applying migrations.

### Production URLs

| Service | URL |
|---|---|
| **Frontend** | `https://app.dentaflow.ai` |
| **Backend** | `https://api.dentaflow.ai` |

---

## 5. Manual Deployment

While deployments are automated, you can manually trigger a deployment from the GitHub Actions tab if needed.

1. Go to the **Actions** tab in the GitHub repository.
2. Select the desired workflow (e.g., `backend-deploy.yml`).
3. Click **"Run workflow"** and select the branch to deploy from.

---

## 6. Environment Variables & Secrets

- **Cloud Run Environment Variables:** Set directly in the `*-deploy.yml` workflows under the `set-env-vars` flag.
- **Secrets:** Stored in Google Secret Manager and accessed by Cloud Run services via the `set-secrets` flag. Secrets are managed in GitHub repository secrets (`secrets.GCP_SA_KEY`, etc.) for CI/CD authentication.

---

## 7. Related Documents

- **[ARCHITECTURE.md](ARCHITECTURE.md):** System architecture overview.
- **[DEVELOPMENT.md](DEVELOPMENT.md):** How to set up and run the project locally.
