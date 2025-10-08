# DentalAI SaaS Platform

**Version:** 14.2.0  
**Status:** Production Ready  
**Last Updated:** October 7, 2025

---

## 🎯 Project Overview

DentalAI is a state-of-the-art, AI-powered SaaS platform for dental clinics, providing:

- **Tier 1 (Basic - Free):** Conversational patient management with 4 specialized agents
- **Tier 2 (Professional - ₪1,500/month):** Basic business management with CFO and Operations agents
- **Tier 3 (Enterprise - ₪4,500/month):** Complete business management with 7 executive agents and self-healing system

---

## 📚 Documentation

### Release Notes
- **[v14.2.0 Release Notes](./RELEASE_NOTES_V14.2.md)** - Hebrew Localization & RTL Support (Latest)
- **[v14.1.0 Release Notes](./RELEASE_NOTES_V14.1.md)** - Production-Ready Feedback System
- **[v14.0 Release Notes](./RELEASE_NOTES_V14.0.md)** - Agent-Driven System

### Development
- **[Work Plan V14.0](./WORK_PLAN_V14.0.md)** - Complete development plan (16 weeks, 12 Epics)
- **[Vision Document](./docs/vision_document.pdf)** - Original vision and requirements

### Legal
- **[LICENSE](./LICENSE)** - Apache 2.0 License
- **[NOTICE](./NOTICE)** - Third-party attributions
- **[Privacy Policy (Hebrew)](./docs/privacy-policy-he.md)** - מדיניות פרטיות

---

## 🏗️ Project Structure

```
dental-clinic-ai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   ├── api/          # API endpoints
│   │   └── core/         # Core utilities
│   ├── tests/            # Backend tests
│   └── alembic/          # Database migrations
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   └── lib/          # Utilities
│   ├── tests/            # Frontend tests
│   └── public/           # Static assets
├── scripts/              # Utility scripts
├── demo_data/            # Demo data for testing
├── docs/                 # Documentation
└── WORK_PLAN_V14.0.md    # Development plan
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 22+
- Docker & Docker Compose
- AWS CLI (for deployment)

### Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_ORG/dental-clinic-ai.git
cd dental-clinic-ai

# Start services with Docker Compose
docker-compose up

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
# Odoo will be available at http://localhost:8069
```

---

## 📋 Development Status

**Current Version:** 14.2.0  
**Current Phase:** Hebrew Localization & RTL Support  
**Progress:** Production Ready ✅

### Recent Milestones

- [x] v14.0 - Agent-Driven System
- [x] v14.1 - Production-Ready Feedback & Fine-Tuning
- [x] v14.2 - Complete Hebrew Localization & RTL Support (100%)
- [ ] v14.3 - Pragtech Module Translation (Planned)

### v14.2 Achievements

- ✅ **Complete RTL Support** - 450+ CSS rules for full right-to-left layout
- ✅ **Hebrew Localization** - 100% Hebrew interface support
- ✅ **Israeli Features** - Health Fund integration, Israeli ID validation
- ✅ **Enhanced Security** - Audit logging, encryption, enhanced RBAC
- ✅ **Production Ready** - Automated deployment, comprehensive documentation

---

## 🛠️ Tech Stack

**Frontend:**
- React 18 + TypeScript
- shadcn/ui (Tailwind CSS + Radix UI)
- Zustand (state management)
- TanStack Query (API client)

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy 2.0 + Alembic
- PostgreSQL 15
- Redis 7.0

**AI/ML:**
- Claude Sonnet 3.5 (primary LLM)
- Llama 3.1 8B (fine-tuned)
- LangGraph (agent framework)
- Neo4j (causal memory)

**Infrastructure:**
- AWS (EKS, RDS, ElastiCache, S3)
- Kubernetes
- Prometheus + Grafana
- ELK Stack

---

## 🤝 Contributing

This is a private project. For development guidelines, see [WORK_PLAN_V14.0.md](./WORK_PLAN_V14.0.md).

---

## 📄 License

Copyright 2025 DentalAI

Licensed under the Apache License, Version 2.0. See [LICENSE](./LICENSE) for details.

---

## 📧 Contact

For questions or support, contact: [Your Email]

---

**Built with ❤️ by the DentalAI Team**
