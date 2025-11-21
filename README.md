# DentaFlow - AI-Powered Dental Practice Management

**Version:** 26.0.0 | **Status:** 🟢 **97% Backend** / 🟡 **50% Frontend** | **Last Updated:** November 21, 2025

**This README is optimized for AI Development Agents.**

---

## 🎯 Quick Navigation for AI Agents

| Document | Purpose | Status |
|---|---|---|
| 📚 **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture, components, data flow | ✅ **Current** |
| 💻 **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** | Local setup, dev workflows, testing | ✅ **Current** |
| 🌐 **[API_REFERENCE.md](docs/API_REFERENCE.md)** | All API endpoints, request/response schemas | ✅ **Current** |
| 🚀 **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** | Staging & production deployment guides | ✅ **Current** |
| 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution guidelines, code style | ✅ **Current** |
| 🗂️ **[docs/INDEX.md](docs/INDEX.md)** | Full documentation navigation hub | ✅ **Current** |

---

## 🤖 What is DentaFlow?

DentaFlow is a multi-agent AI system designed to automate and optimize dental practice operations. It handles patient communication, appointment scheduling, billing, and clinical workflows, integrating seamlessly with existing ERP systems like Odoo.

### Key Features

- **Multi-Agent AI System:** 6 specialized AI agents (see table below) collaborate to manage the practice.
- **Omnichannel Communication:** Engages patients via Web Chat, SMS, Email, and soon WhatsApp/Telegram.
- **Smart Scheduling:** AI-powered appointment booking, reminders, and rescheduling.
- **Automated Billing:** Automated invoicing, payment tracking, and financial analytics.
- **Deep Odoo Integration:** Real-time integration with 21 Odoo models.
- **HIPAA & GDPR Compliant:** Enterprise-grade security and data privacy.

---

## 🏛️ System Architecture

**For a detailed breakdown, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).**

| Component | Technology | Location | Purpose |
|---|---|---|---|
| **Frontend** | React 18, Vite, Tailwind | `/frontend` | Clinic & patient web portals |
| **Backend** | FastAPI, Python 3.11 | `/backend` | Main API, business logic, AI agents |
| **AI Agents** | LangChain, LangGraph | `/backend/app/agents` | Core AI agent system |
| **Database** | PostgreSQL (Cloud SQL) | Google Cloud | Primary data store |
| **Cache** | Redis | Google Cloud | Session & cache management |
| **ERP** | Odoo 17 | External | Clinic management system |
| **Infrastructure** | Google Cloud Run, Docker | Google Cloud | Serverless container hosting |
| **CI/CD** | GitHub Actions | `/.github/workflows` | Automated build, test, deploy |

### AI Agent Roster

| Agent | Role | Status |
|---|---|---|
| **Supervisor** 🎯 | Orchestrator | ✅ Production Ready |
| **Alex** 📅 | Patient Care Coordinator | ✅ Production Ready |
| **Sarah** 🏥 | Clinical Assistant | ✅ Production Ready |
| **Marcus** 💰 | CFO & Financial Manager | ✅ Production Ready |
| **Sophia** 👥 | HR & Admin Manager | ✅ Production Ready |
| **Harper** 🔒 | HIPAA Compliance Officer | ✅ Production Ready |

---

## 📊 Project Status (November 21, 2025)

### Backend (97% Complete)
- ✅ Multi-agent system (6 agents)
- ✅ Odoo integration (21 models)
- ✅ PostgresSaver for conversation memory
- ✅ Authentication & RBAC
- ✅ HIPAA compliance features
- ✅ Sentry & OpenTelemetry integration
- ✅ Database migrations
- ⏳ Demo data population (in progress)

### Frontend (50% Complete)
- ✅ Dashboard service layer
- ✅ 3/8 widgets converted to TypeScript
- ✅ Login page (environment variables fixed)
- ⏳ 5 widgets remaining
- ⏳ Agent chat interface
- ⏳ E2E testing

---

## 🚀 Live Environments & Quick Start

| Environment | URL |
|---|---|
| **Staging Frontend** | [dentaflow-frontend-staging-*.run.app](https://dentaflow-frontend-staging-688311017213.us-central1.run.app) |
| **Staging Backend** | [dentaflow-backend-staging-*.run.app](https://dentaflow-backend-staging-688311017213.us-central1.run.app) |
| **API Docs** | [Staging Backend /docs](https://dentaflow-backend-staging-688311017213.us-central1.run.app/docs) |

### Demo Credentials
- **Email:** `demo@dentaflow.ai`
- **Password:** `Demo123!`

---

## 💻 Development

**For full instructions, see [DEVELOPMENT.md](docs/DEVELOPMENT.md).**

```bash
# 1. Clone & Setup
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai

# 2. Backend Setup
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cd ..

# 3. Frontend Setup
cd frontend && pnpm install && cd ..

# 4. Run (in separate terminals)
(cd backend && uvicorn app.main:app --reload) &
(cd frontend && pnpm run dev)
```

---

## 🤝 Contributing

**Please read [CONTRIBUTING.md](CONTRIBUTING.md) before making any changes.**

1. **Create a feature branch:** `git checkout -b feat/your-feature-name`
2. **Make your changes.**
3. **Run tests:** `cd backend && pytest`
4. **Commit with conventional commit message:** `feat: Add new feature`
5. **Push and create a Pull Request.**

---

## 🔗 Other Important Links

| Document | Location |
|---|---|
| **Changelog** | `CHANGELOG.md` |
| **Known Issues** | `docs/KNOWN_ISSUES.md` |
| **Remaining Work** | `docs/REMAINING_WORK_SUMMARY.md` |
| **License** | `LICENSE` |

---

## 🗂️ Full Documentation

For a complete list of all documentation, please see the **[Documentation Index](docs/INDEX.md)**.
