# 🦷 AI Dental Clinic Management System

**AI-Powered Dental Clinic Management System**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.11-green?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?logo=fastapi)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Redis](https://img.shields.io/badge/Redis-Latest-red?logo=redis)](https://redis.io)

## 🎯 Overview

A comprehensive AI-powered dental clinic management system that automates patient communication, appointment scheduling, and clinic operations using advanced AI agents and modern microservices architecture.

### ✨ Key Features

- 🤖 **Multi-Agent AI System** - Three specialized AI agents for different tasks
- 📱 **Multi-Channel Support** - WhatsApp, Telegram, and API integration
- 🔄 **Async Message Processing** - Redis-based queue system
- 🏥 **Dental PMS Integration** - Ready for Open Dental integration
- 🌐 **Bilingual Support** - Hebrew and English
- 🐳 **Containerized Architecture** - Full Docker deployment
- 🔮 **Future-Ready** - Modular design for OpenManus integration

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
│         (CrewAI - Port 8001)            │
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

## 🔮 Future Roadmap

### Phase 1: Current (87.5% Complete)
- ✅ Core system functionality
- ✅ AI agents with CrewAI
- ✅ Database and API layer
- ⏳ CI/CD pipeline

### Phase 2: Enhancement
- 🔄 OpenManus integration
- 📱 Mobile app development  
- 🔐 Advanced security features
- 📊 Analytics dashboard

### Phase 3: Scale
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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the documentation files
- **Issues**: Create GitHub issue
- **Email**: support@dental-clinic-ai.com

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent AI framework
- **FastAPI** - Modern Python web framework
- **OpenAI** - AI language models
- **Docker** - Containerization platform

---

**Status**: 🟢 **Production Ready** (87.5% Complete)  
**Last Updated**: September 26, 2025  
**Version**: 2.0.0
