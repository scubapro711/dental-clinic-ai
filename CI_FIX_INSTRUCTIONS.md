# CI/CD Workflow Fix Instructions

## Problem
The staging migration workflow is failing with:
```
ModuleNotFoundError: No module named 'pydantic'
```

## Root Cause
The workflow only installs minimal dependencies (`alembic psycopg2-binary sqlalchemy`) but the migration files import models that depend on `pydantic` and other packages.

## Solution
Edit these files directly on GitHub (requires workflows permission):

### File 1: `.github/workflows/migrate-staging.yml`
**Line 42** - Change from:
```yaml
pip install alembic psycopg2-binary sqlalchemy
```
To:
```yaml
pip install -r requirements.txt
```

### File 2: `.github/workflows/migrate-production.yml`
**Line 42** - Same change as above

## Why This Fixes It
- `requirements.txt` includes all dependencies (pydantic, sqlalchemy, fastapi, etc.)
- Migration files import models from `app.models.demo_lead` which need pydantic
- Installing full requirements ensures all imports work

## How to Apply
1. Go to GitHub repository
2. Navigate to `.github/workflows/migrate-staging.yml`
3. Click "Edit" button
4. Change line 42 as shown above
5. Commit directly to `develop` branch
6. Repeat for `migrate-production.yml`

## After Fix
The next push to `develop` will trigger the workflow with correct dependencies.
