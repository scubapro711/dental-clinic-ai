# DentaFlow Development Guide

**Status:** ✅ Current | **Last Updated:** November 21, 2025

This document provides a comprehensive guide for setting up and developing the DentaFlow application. It is optimized for AI development agents.

---

## 1. Prerequisites

- **Python:** 3.11
- **Node.js:** 20.x
- **pnpm:** 8.x
- **Docker:** Latest version
- **Git:** Latest version

---

## 2. Local Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# NOTE: You will need to fill in the .env file with credentials for:
# - DATABASE_URL (local PostgreSQL)
# - ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
# - OPENAI_API_KEY
# - SENTRY_DSN
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env

# NOTE: The frontend requires the backend API URL:
# VITE_API_BASE_URL=http://localhost:8000
```

### Step 4: Running Development Servers

Run each command in a separate terminal from the root directory.

**Terminal 1: Backend Server**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Frontend Server**
```bash
cd frontend
pnpm run dev
```

| Service | Local URL |
|---|---|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

---

## 3. Code Structure

### Backend (`/backend`)

```
backend/
├── app/                # Main application source code
│   ├── agents/         # AI agent definitions and tools
│   ├── api/            # FastAPI routers and endpoints
│   ├── auth/           # Authentication logic (JWT)
│   ├── core/           # Configuration and core settings
│   ├── crud/           # CRUD operations for database models
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic data validation schemas
│   ├── services/       # Business logic and service layers (e.g., OdooService)
│   └── main.py         # FastAPI application entry point
├── alembic/            # Database migration scripts
├── tests/              # Pytest unit and integration tests
├── .env.example        # Environment variable template
└── requirements.txt    # Python dependencies
```

### Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── assets/         # Static assets (images, fonts)
│   ├── components/     # Reusable React components
│   ├── contexts/       # React Context providers (e.g., AuthContext)
│   ├── hooks/          # Custom React hooks
│   ├── layouts/        # Page layouts (e.g., ClinicLayout)
│   ├── pages/          # Top-level page components
│   ├── services/       # API client and data fetching logic
│   ├── styles/         # Global CSS and Tailwind config
│   ├── utils/          # Utility functions
│   └── App.jsx         # Main application component with routing
├── .env.example        # Environment variable template
└── package.json        # Node.js dependencies
```

---

## 4. Development Workflows

### Git Branching Strategy

- **`main`:** Production-ready code. All pushes trigger production deployment.
- **`develop`:** Staging and integration branch. All pushes trigger staging deployment.
- **`feat/...`:** Feature branches. Create from `develop`.
- **`fix/...`:** Bugfix branches. Create from `develop`.
- **`hotfix/...`:** Urgent production fixes. Create from `main`.

### Committing Code

We use the **Conventional Commits** specification. This is essential for automated versioning and changelog generation.

**Format:** `type(scope): subject`

- **`feat`:** A new feature.
- **`fix`:** A bug fix.
- **`docs`:** Documentation only changes.
- **`style`:** Code style changes (formatting, etc).
- **`refactor`:** A code change that neither fixes a bug nor adds a feature.
- **`perf`:** A code change that improves performance.
- **`test`:** Adding missing tests or correcting existing tests.
- **`chore`:** Changes to the build process or auxiliary tools.

**Example:** `feat(api): add new endpoint for patient search`

### Pull Requests (PRs)

- All PRs must be made to the `develop` branch.
- PRs require at least one approval from a team member.
- PRs must pass all CI checks (linting, testing).

---

## 5. Testing

### Backend Testing

- **Framework:** Pytest
- **Location:** `/backend/tests`
- **How to Run:**
  ```bash
  cd backend
  source venv/bin/activate
  pytest
  ```

### Frontend Testing

- **Framework:** Vitest and React Testing Library
- **Location:** `/frontend/src` (co-located with components)
- **How to Run:**
  ```bash
  cd frontend
  pnpm test
  ```

---

## 6. Related Documents

- **[ARCHITECTURE.md](ARCHITECTURE.md):** System architecture overview.
- **[API_REFERENCE.md](API_REFERENCE.md):** Detailed API endpoint documentation.
- **[DEPLOYMENT.md](DEPLOYMENT.md):** Deployment processes.
- **[CONTRIBUTING.md](CONTRIBUTING.md):** Contribution guidelines.
