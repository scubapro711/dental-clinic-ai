# Build Scripts

Professional build scripts for DentaFlow Backend.

## Overview

These scripts solve the "chicken-and-egg" problem of embedding Git commit information into Docker images:

**Problem:** If we commit `GIT_COMMIT` files to Git, they're always one commit behind.  
**Solution:** Generate `GIT_COMMIT` files at **build time**, not commit time.

## Scripts

### `generate-git-info.sh`

Generates Git information files before building:

```bash
./scripts/generate-git-info.sh
```

**Output files:**
- `backend/app/GIT_COMMIT` - Full commit hash
- `backend/app/GIT_COMMIT_SHORT` - Short commit hash (8 chars)
- `backend/app/GIT_INFO` - Combined info string

**Note:** These files are in `.gitignore` and should NOT be committed.

### `build.sh`

Complete build process:

```bash
# Build with auto-generated tag
./scripts/build.sh

# Build with custom tag
./scripts/build.sh my-feature-v1

# Build with custom repo and tag
./scripts/build.sh my-tag my-repo-url
```

**What it does:**
1. Runs `generate-git-info.sh`
2. Builds Docker image with Google Cloud Build (or local Docker)
3. Tags image with timestamp or custom tag

## Usage

### Local Development

```bash
cd backend
./scripts/build.sh local-test
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
- name: Build Backend
  run: |
    cd backend
    ./scripts/build.sh ${{ github.sha }}
```

### Manual Deployment

```bash
# 1. Build
cd backend
./scripts/build.sh production-$(date +%Y%m%d)

# 2. Deploy
gcloud run deploy dentaflow-backend-staging \
  --image=us-central1-docker.pkg.dev/.../dentaflow-backend:production-20251115 \
  --region=us-central1
```

## Verification

After deployment, verify the correct commit is running:

```bash
curl https://your-service-url/health | jq '.git_commit_short'
```

This should match:
```bash
git rev-parse --short HEAD
```

## Troubleshooting

### "GIT_COMMIT_SHORT not found"

**Cause:** Build script wasn't run, or files weren't generated.  
**Fix:** Always use `./scripts/build.sh` instead of `docker build` directly.

### "Commit hash doesn't match"

**Cause:** Old image cached or wrong image deployed.  
**Fix:** Use image digest instead of tag:
```bash
gcloud run deploy ... --image=...@sha256:abc123...
```

## Architecture Decision

**Why not generate at runtime?**
- Would require Git in production container (security risk)
- Would require `.git` directory (large, unnecessary)
- Slower startup time

**Why not commit the files?**
- Always one commit behind (chicken-and-egg problem)
- Requires manual updates
- Error-prone

**Why generate at build time?** ✅
- Accurate commit info
- No Git needed in container
- Automated and reliable
- Industry best practice
