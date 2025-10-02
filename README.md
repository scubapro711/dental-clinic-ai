# DentalAI SaaS Platform

**Version:** 14.0  
**Status:** In Development  
**Started:** 2025-10-02

---

## 🎯 Project Overview

DentalAI is a state-of-the-art, AI-powered SaaS platform for dental clinics, providing:

- **Tier 1 (Basic - Free):** Conversational patient management with 4 specialized agents
- **Tier 2 (Professional - ₪1,500/month):** Basic business management with CFO and Operations agents
- **Tier 3 (Enterprise - ₪4,500/month):** Complete business management with 7 executive agents and self-healing system

---

## 📚 Documentation

- **[Work Plan V14.0](./WORK_PLAN_V14.0.md)** - Complete development plan (16 weeks, 12 Epics)
- **[Vision Document](./docs/vision_document.pdf)** - Original vision and requirements
- **[LICENSE](./LICENSE)** - Apache 2.0 License
- **[NOTICE](./NOTICE)** - Third-party attributions

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

**Current Phase:** Epic 0 - Project Setup & Infrastructure  
**Progress:** 0% (Just started!)

### Milestones

- [ ] Week -1: Deep Learning Phase
- [ ] Week 0: Project Setup & Infrastructure
- [ ] Week 0.5: Migration, Demo Data & Backups
- [ ] Week 1: SaaS Foundation & Security
- [ ] Weeks 2-3: Agent Architecture & State Management
- [ ] Week 3.5: Streaming & Real-Time Updates
- [ ] Week 4: Centralized Odoo Integration
- [ ] **MVP Deployment** (End of Week 4)
- [ ] Weeks 5-13: Post-MVP Features

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
