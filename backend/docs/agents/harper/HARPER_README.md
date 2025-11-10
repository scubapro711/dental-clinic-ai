# 🛡️ Harper - HIPAA Compliance Agent

> AI-powered HIPAA compliance monitoring and guidance for DentaFlow dental clinics

[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-V4-purple.svg)](https://langchain.com/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Frontend Components](#frontend-components)
- [Knowledge Base](#knowledge-base)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Harper** is DentaFlow's intelligent HIPAA Compliance Agent, designed to help dental clinics maintain HIPAA compliance through:

- **Real-time AI Guidance**: Instant answers to HIPAA questions powered by GPT-4.1-mini
- **Proactive Monitoring**: Automated compliance checks and alerts
- **Comprehensive Knowledge Base**: 33 HIPAA documents with 2,430+ lines of content
- **10 Specialized Tools**: From PHI compliance checks to breach report generation
- **Role-Based Access**: Secure access for clinic admins and super admins

---

## ✨ Features

### 🤖 AI-Powered Compliance Guidance

- **RAG-Powered Search**: Semantic search across 33 HIPAA documents stored in Pinecone
- **Contextual Responses**: Tailored advice based on your clinic's specific situation
- **Suggested Actions**: Proactive recommendations for compliance improvements
- **Conversation Memory**: Maintains context across multi-turn conversations

### 🛠️ 10 Specialized Compliance Tools

| Tool | Description |
|------|-------------|
| `search_hipaa_knowledge` | Search comprehensive HIPAA knowledge base |
| `check_phi_compliance` | Validate PHI handling and security measures |
| `validate_baa` | Verify Business Associate Agreements |
| `assess_security_controls` | Evaluate technical, administrative, and physical safeguards |
| `generate_breach_report` | Create breach notification reports |
| `audit_access_logs` | Review PHI access patterns and detect anomalies |
| `check_patient_rights` | Verify compliance with patient rights requests |
| `evaluate_risk` | Perform HIPAA risk assessments |
| `generate_compliance_report` | Create comprehensive compliance reports |
| `recommend_remediation` | Provide actionable remediation plans |

### 📊 Proactive Monitoring

Harper automatically monitors compliance and generates alerts for:

- ⏰ **BAA Expirations** - 30-day advance warning
- 🔒 **PHI Compliance Issues** - Encryption, access control violations
- 🛡️ **Security Gaps** - Missing or inadequate safeguards
- 👤 **Access Anomalies** - Suspicious PHI access patterns
- ⚠️ **Risk Threshold Violations** - Overall risk level monitoring
- 🚨 **Breach Detection** - Potential HIPAA breaches
- 📋 **Patient Rights Violations** - Request compliance tracking
- 📝 **Audit Findings** - Compliance gap documentation

### 📈 Compliance Dashboard

- **Real-time Scores**: Overall, PHI, and Security compliance scores
- **Alert Management**: Track and resolve compliance issues
- **Trend Analysis**: Historical metrics and trend visualization
- **Quick Actions**: One-click access to common tasks

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DentaFlow Platform                      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Multi-Agent System                     │ │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌─────┐│ │
│  │  │  Alex  │  │  Maya  │  │  Sam   │  │  Jamie │  │Harper││ │
│  │  │ (Chat) │  │(Sched.)│  │(Billing)│  │(Clinic)│  │(HIPAA)││ │
│  │  └────────┘  └────────┘  └────────┘  └────────┘  └─────┘│ │
│  │                                                           │ │
│  │  Supervisor Agent (LangGraph V4)                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Harper Agent                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  LangGraph V4 State Machine                         │ │ │
│  │  │  ├─ Input: Process queries                          │ │ │
│  │  │  ├─ Tools: Execute compliance tools                 │ │ │
│  │  │  └─ Output: Generate responses                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  10 Specialized Tools                               │ │ │
│  │  │  ├─ search_hipaa_knowledge (RAG)                    │ │ │
│  │  │  ├─ check_phi_compliance                            │ │ │
│  │  │  ├─ validate_baa                                    │ │ │
│  │  │  ├─ assess_security_controls                        │ │ │
│  │  │  ├─ generate_breach_report                          │ │ │
│  │  │  ├─ audit_access_logs                               │ │ │
│  │  │  ├─ check_patient_rights                            │ │ │
│  │  │  ├─ evaluate_risk                                   │ │ │
│  │  │  ├─ generate_compliance_report                      │ │ │
│  │  │  └─ recommend_remediation                           │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Pinecone Vector Database                     │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  HIPAA Knowledge Base (33 documents)                │ │ │
│  │  │  ├─ 4 Regulation Summaries                          │ │ │
│  │  │  ├─ 5 FAQ Documents (100 Q&A pairs)                 │ │ │
│  │  │  ├─ 3 Best Practice Guides                          │ │ │
│  │  │  └─ 7 Policy Templates                              │ │ │
│  │  │  Total: 2,430+ lines of HIPAA content               │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │           Harper Monitoring Service                       │ │
│  │  ├─ Daily Checks (BAA, PHI, Access, Risk)                │ │
│  │  ├─ Weekly Checks (Security, Score, Summary)             │ │
│  │  └─ Monthly Checks (Report, Trends, Assessment)          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL Database                          │ │
│  │  ├─ compliance_alerts (Alerts & tracking)                │ │
│  │  └─ compliance_metrics (Historical data)                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Pinecone account
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai-repo

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### Environment Variables

```bash
# backend/.env
PINECONE_API_KEY=pcsk_xxxxx...
OPENAI_API_KEY=sk-xxxxx...
DATABASE_URL=postgresql://user:pass@localhost:5432/dentaflow
```

### Database Setup

```bash
cd backend

# Run migrations
alembic upgrade head

# Upload HIPAA knowledge base
python scripts/upload_hipaa_knowledge.py
```

### Start Services

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Access Harper

- **Frontend**: http://localhost:3000/compliance
- **API Docs**: http://localhost:8000/docs
- **Harper Chat**: Click "Ask Harper" button in dashboard

---

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api/v1/compliance
```

### Authentication

All endpoints require Bearer token authentication:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

### Endpoints

#### Chat with Harper

```http
POST /chat
```

**Request:**
```json
{
  "message": "What are the requirements for PHI encryption?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Under HIPAA Security Rule...",
  "suggested_actions": [
    {
      "label": "Check current encryption status",
      "action": "check_phi_compliance"
    }
  ]
}
```

#### Get Compliance Score

```http
GET /score
```

**Response:**
```json
{
  "overall": 87,
  "phi": 90,
  "security": 85,
  "phi_findings": 3,
  "security_gaps": 5
}
```

#### Get Alerts

```http
GET /alerts?status=open&severity=critical
```

#### Manage Alerts

```http
POST /alerts/{alert_id}/acknowledge
POST /alerts/{alert_id}/start_progress
POST /alerts/{alert_id}/resolve
POST /alerts/{alert_id}/dismiss
```

#### Get Metrics

```http
GET /metrics
```

For complete API documentation, visit: http://localhost:8000/docs

---

## 🎨 Frontend Components

### HarperDashboard

Main compliance dashboard with:
- Compliance score cards
- Active alerts summary
- Quick actions
- Metrics visualization

**Location:** `frontend/src/components/compliance/HarperDashboard.jsx`

### HarperChat

Interactive chat interface with:
- Real-time messaging
- Suggested actions
- Conversation history

**Location:** `frontend/src/components/compliance/HarperChat.jsx`

### ComplianceAlerts

Alert management with:
- Tabbed interface
- Status tracking
- Action buttons

**Location:** `frontend/src/components/compliance/ComplianceAlerts.jsx`

### ComplianceMetrics

Metrics visualization with:
- Trend indicators
- Historical comparisons

**Location:** `frontend/src/components/compliance/ComplianceMetrics.jsx`

---

## 📖 Knowledge Base

Harper's knowledge base includes:

### Regulation Summaries (4 documents)
- Privacy Rule Summary
- Security Rule Summary
- Breach Notification Rule Summary
- Enforcement Rule Summary

### FAQ Documents (5 documents, 100 Q&A pairs)
- Business Associate Agreement FAQ
- PHI Handling FAQ
- Breach Response FAQ
- Patient Rights FAQ
- Technical Safeguards FAQ

### Best Practice Guides (3 documents)
- NIST Framework for Healthcare
- HITRUST Alignment Guide
- Dental-Specific HIPAA Best Practices

### Policy Templates (7 documents)
- Privacy Policy
- Security Policy
- Breach Response Plan
- BAA Template
- And more...

**Total:** 33 documents, 2,430+ lines of HIPAA content

**Location:** `backend/app/knowledge/hipaa/`

---

## 🚢 Deployment

See [HARPER_DEPLOYMENT_GUIDE.md](HARPER_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deploy

```bash
# 1. Database migration
alembic upgrade head

# 2. Upload knowledge base
python scripts/upload_hipaa_knowledge.py

# 3. Start services
docker-compose up -d
```

---

## 🧪 Testing

### Unit Tests

```bash
cd backend
pytest tests/test_harper_agent.py
pytest tests/test_hipaa_tools.py
pytest tests/test_monitoring_service.py
```

### Integration Tests

```bash
pytest tests/integration/test_harper_api.py
```

### End-to-End Tests

```bash
cd frontend
npm run test:e2e
```

### Manual Testing

1. **Chat Test:**
   - Navigate to `/compliance`
   - Click "Ask Harper"
   - Ask: "What is PHI?"
   - Verify response

2. **Alert Test:**
   - Create test alert via API
   - Acknowledge alert
   - Mark as resolved

3. **Score Test:**
   - Verify compliance score displays
   - Check trend indicators

---

## 👥 Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/harper-improvement`
2. Make changes
3. Run tests: `pytest`
4. Commit: `git commit -m "feat: add new compliance check"`
5. Push: `git push origin feature/harper-improvement`
6. Create Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Follow Airbnb style guide, use Prettier
- **Commits**: Follow Conventional Commits

---

## 📄 License

Copyright © 2025 DentaFlow. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 🆘 Support

- **Documentation**: https://docs.dentaflow.com/harper
- **Email**: support@dentaflow.com
- **Slack**: #harper-support
- **GitHub Issues**: https://github.com/scubapro711/dental-clinic-ai/issues

---

## 🙏 Acknowledgments

- **LangChain** - For LangGraph V4 framework
- **OpenAI** - For GPT-4.1-mini model
- **Pinecone** - For vector database
- **HHS.gov** - For HIPAA guidance and regulations
- **NIST** - For cybersecurity framework
- **HITRUST** - For compliance framework

---

**Built with ❤️ by the DentaFlow Team**

*Helping dental clinics stay HIPAA compliant, one conversation at a time.*

