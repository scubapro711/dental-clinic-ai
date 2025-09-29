# 🦷 AI Dental Clinic Management System

**AI-Powered Dental Clinic Management System**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.11-green?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?logo=fastapi)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Redis](https://img.shields.io/badge/Redis-Latest-red?logo=redis)](https://redis.io)

## 🚨 **CRITICAL LEGAL WARNING** 🚨

```
⚖️  PROPRIETARY & PATENTABLE SOFTWARE - ALL RIGHTS RESERVED  ⚖️
🔒  COPYRIGHT © 2025 ERAN SARFATY - UNAUTHORIZED USE PROHIBITED  🔒
📋  PATENT PENDING - MULTIPLE INNOVATIONS UNDER PATENT PROTECTION  📋
⚠️  LEGAL ACTION WILL BE TAKEN AGAINST UNAUTHORIZED COPYING  ⚠️
```

**🛡️ PROTECTED INTELLECTUAL PROPERTY:**
- **Multi-Agent AI Orchestration System** (Patent Pending)
- **AI-Powered Dental Scheduling Algorithm** (Patent Pending)  
- **Medical Conversation Management Protocol** (Patent Pending)
- **Adaptive Healthcare Queue Management** (Patent Pending)

**📞 LICENSING CONTACT:** scubapro711@gmail.com | +972-53-555-0317

**⚖️ FULL TERMS:** See [LICENSE](LICENSE) | **🔍 PATENT ANALYSIS:** See [docs/patentability-analysis.md](docs/patentability-analysis.md)

---

## 🎯 Overview

A comprehensive AI-powered dental clinic management system that automates patient communication, appointment scheduling, and clinic operations using advanced AI agents and modern microservices architecture.

### ✨ Key Features

- 🤖 **Multi-Agent AI System** - Powered by the advanced OpenManus engine
- 📱 **Multi-Channel Support** - WhatsApp, Telegram, and API integration
- 🔄 **Async Message Processing** - Redis-based queue system
- 🏥 **Dental PMS Integration** - Ready for Open Dental integration
- 🌐 **Bilingual Support** - Hebrew and English
- 🐳 **Containerized Architecture** - Full Docker deployment
- 🚀 **Enhanced Capabilities** - Advanced intent analysis, emergency detection, and more

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Gateway Service               │
│         (FastAPI - Port 8000)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│            Redis Queue                  │
│         (Message Broker)                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│          AI Agents Service              │
│        (OpenManus - Port 8001)          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│           MySQL Database                │
│         (Patient Data - Port 3306)      │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- 4GB+ RAM
- 10GB+ Storage

### 1. Clone Repository

```bash
git clone <repository-url>
cd dental-clinic-ai
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your OpenAI API key
nano .env
```

### 3. Launch System

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Test AI message processing
curl -X POST http://localhost:8000/api/queue/process-async \
  -H "Content-Type: application/json" \
  -d '{"text": "I need to schedule an appointment", "sender_id": "test_user"}'
```

## 🤖 AI Agents

### 1. Receptionist Agent
- **Role**: First point of contact
- **Capabilities**: General inquiries, patient information
- **Languages**: Hebrew, English

### 2. Scheduler Agent  
- **Role**: Appointment management
- **Capabilities**: Booking, rescheduling, availability checks
- **Integration**: Full PMS integration

### 3. Confirmation Agent
- **Role**: Appointment confirmations and reminders
- **Capabilities**: Automated confirmations, reminder sending
- **Timing**: Smart scheduling based on appointment time

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/docs` | API documentation |
| `POST` | `/api/queue/process-async` | Process AI message |
| `GET` | `/api/queue/stats` | Queue statistics |

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/webhook/whatsapp` | WhatsApp webhook |
| `POST` | `/webhook/telegram` | Telegram webhook |

## 🗄️ Database Schema

### Core Tables

- **`patients`** - Patient information and contact details
- **`providers`** - Healthcare providers and dentists  
- **`appointments`** - Appointment scheduling and status
- **`treatment_types`** - Available treatments and procedures
- **`messages`** - Communication history and logs

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Database Configuration  
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=dental_clinic
MYSQL_USER=dental_user
MYSQL_PASSWORD=dental_password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

## 🧪 Testing

### Run All Tests

```bash
# Unit and integration tests
docker-compose exec gateway pytest tests/ -v

# Specific test categories
pytest tests/unit/ -v          # Unit tests
pytest tests/integration/ -v   # Integration tests
```

### Manual Testing

```bash
# Test message processing
curl -X POST http://localhost:8000/api/queue/process-async \
  -H "Content-Type: application/json" \
  -d '{"text": "אני רוצה לקבוע תור", "sender_id": "test_user"}'

# Check queue status
curl http://localhost:8000/api/queue/stats

# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
```

## 📚 Documentation

### Core Documentation

- **[📋 System Requirements](SYSTEM_REQUIREMENTS_ANALYSIS.md)** - Detailed requirements analysis
- **[📊 Progress Tracking](PROGRESS_TRACKING_UPDATE.md)** - Current development status
- **[🔮 OpenManus Integration](FUTURE_OPENMANUS_INTEGRATION_PLAN.md)** - Future AI engine integration
- **[⚖️ CrewAI vs OpenManus](OPENMANUS_VS_CREWAI_COMPARISON.md)** - Technology comparison

### UX/UI Documentation

- **[🎨 UX/UI Specifications](docs/ux-ui-specs/)** - Complete user experience and interface specifications
- **[📱 Chat Capabilities](docs/ux-ui-specs/chat-capabilities-analysis.md)** - Human handoff and chat system analysis ([English](docs/ux-ui-specs/chat-capabilities-analysis-en.md))
- **[⚙️ Implementation Report](docs/ux-ui-specs/implementation_capabilities_report.md)** - Technical implementation capabilities assessment ([English](docs/ux-ui-specs/implementation-capabilities-report-en.md))
- **[📋 UX/UI Analysis](docs/ux-ui-specs/ux-ui-spec-analysis.md)** - Detailed specification analysis ([English](docs/ux-ui-specs/ux-ui-spec-analysis-en.md))
- **[🤖 Agent Management Interface](docs/ux-ui-specs/agent-management-interface-analysis.md)** - Core UI/UX specification for agent team management ([English](docs/ux-ui-specs/agent-management-interface-analysis-en.md))
- **[🛠️ GUI Development Guidelines](docs/ux-ui-specs/gui-development-guidelines-manus-ai.md)** - Comprehensive GUI development and testing protocol for Manus AI ([English](docs/ux-ui-specs/gui-development-guidelines-manus-ai-en.md))

### Security & Privacy Documentation

- **[🔒 Comprehensive Security & Privacy Analysis](docs/comprehensive-security-privacy-analysis.md)** - Complete HIPAA, GDPR, and AWS security assessment with 8-week implementation roadmap
- **[🛡️ Code Quality Assessment](docs/code-quality-assessment.md)** - Enterprise-grade code quality evaluation and best practices analysis
- **[📋 Code Documentation Assessment](docs/code-documentation-assessment.md)** - Comprehensive code documentation quality analysis
- **[🔍 Code Review Tools Analysis](docs/code-review-tools-analysis.md)** - Analysis of enterprise code review tools and GitHub workflow enhancement
- **[⚖️ Legal Rights Analysis](docs/legal-rights-analysis.md)** - Copyright protection and licensing framework
- **[📋 Patentability Analysis](docs/patentability-analysis.md)** - Comprehensive patent potential assessment for core innovations
- **[🏛️ Repository Professionalism Assessment](docs/repository-professionalism-assessment.md)** - Professional repository standards evaluation

### Open Dental Integration

- **[🔌 Open Dental Resources Analysis](docs/open-dental-resources-analysis.md)** - Comprehensive analysis of Open Dental API and integration options ([English](docs/open-dental-resources-analysis-en.md))
- **[📧 Developer Request Status](docs/open-dental-request-status.md)** - Current status of Open Dental Developer Portal access request
- **[📝 Developer Request Letter](docs/eran-focused-open-dental-request.md)** - Submitted request letter for API access

## 🔮 Future Roadmap

### Phase 1: Foundation (90% Complete)
- ✅ Core system functionality
- ✅ AI agents with CrewAI
- ✅ Database and API layer
- ✅ **Open Dental API integration analysis**
- ✅ **UX/UI specifications and GUI development guidelines**
- ⏳ CI/CD pipeline

### Phase 2: Open Dental Integration (Awaiting API Access)
- ✅ **Developer Portal registration request submitted (Sept 26, 2025)**
- 🔌 **DentalPMS Tool development for AI agents**
- 📋 **Python SDK integration (opendental-sdk)**
- 🤖 **MCP server integration for documentation search**
- 🔐 **HIPAA-compliant security implementation**
- 📊 **Availability engine and appointment management**

### Phase 3: Enhancement & Scale
- ✅ **OpenManus Integration Complete**
- 📱 Mobile app development  
- 🔐 Advanced security features
- 📊 Analytics dashboard
- ☁️ Multi-region deployment
- 🤖 Advanced AI capabilities
- 🔗 Third-party integrations
- 📈 Performance optimization

## 🛠️ Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run services individually
python src/gateway/main.py
python src/ai_agents/enhanced_main.py

# Database migrations
docker-compose exec mysql mysql -u dental_user -p < scripts/init_db.sql
```

### Adding New Features

1. **Create feature branch**
2. **Implement changes**
3. **Add tests**
4. **Update documentation**
5. **Submit pull request**

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License & Copyright

**© 2025 Eran Sarfaty. All Rights Reserved.**

This project is proprietary software protected by copyright law. See the [LICENSE](LICENSE) file for complete terms and restrictions.

**⚠️ IMPORTANT:** Unauthorized copying, distribution, or commercial use is strictly prohibited and may result in legal action.

## 🆘 Support & Contact

- **Documentation**: Check the comprehensive documentation in `/docs`
- **Issues**: Create GitHub issue for bugs or feature requests
- **Commercial Licensing**: scubapro711@gmail.com
- **Developer**: Eran Sarfaty (+972-53-555-0317)

## 🙏 Acknowledgments

- **OpenManus** - The new, powerful AI engine for our system
- **CrewAI** - The original multi-agent AI framework
- **FastAPI** - Modern Python web framework
- **OpenAI** - AI language models
- **Docker** - Containerization platform

---

**Status**: 🟢 **Production Ready** (87.5% Complete)  
**Last Updated**: September 26, 2025  
**Version**: 2.0.0



---

## 🌟 Interactive Demo with Dana AI

In addition to the core microservices architecture, this repository includes a standalone, unified application (`app_unified.py`) that provides an interactive demonstration of the system's capabilities. This is the best way to quickly experience the AI assistant "Dana" and the investor dashboard.

### Features of the Interactive Demo

- **Live Chat with Dana**: A fully functional chat widget to interact with Dana in English, Hebrew, or Arabic.
- **Real-time Synthesis Agent**: Watch as the system routes your conversations to the correct agent (Dana, Booking, Emergency) based on your messages.
- **Investor & Technical Dashboard**: A comprehensive, single-page view combining business metrics, ROI, and live system monitoring.
- **No Dependencies Required**: Runs as a single Python script with Flask (after installing dependencies).

### How to Run the Interactive Demo

1.  **Ensure all dependencies are installed:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the `app_unified.py` script:**
    ```bash
    python app_unified.py
    ```

3.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000`.

    You will see the main dashboard. The chat widget with Dana will be in the bottom-right corner, ready for interaction.

