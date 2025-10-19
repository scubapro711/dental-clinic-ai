# 🚀 DentaFlow Installation Guide

**Time Required:** 15-20 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Docker, Git

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Git** 2.30+ ([Install Git](https://git-scm.com/downloads))

### Optional (for development)
- **Node.js** 18+ ([Install Node](https://nodejs.org/))
- **Python** 3.11+ ([Install Python](https://www.python.org/downloads/))
- **PostgreSQL** 15+ ([Install PostgreSQL](https://www.postgresql.org/download/))

---

## 🎯 Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai
```

### 2. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env
```

**Minimum required variables:**
```env
# Database
POSTGRES_USER=dentaflow
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=dentaflow

# OpenAI (for AI agents)
OPENAI_API_KEY=your_openai_api_key_here

# JWT Secret
JWT_SECRET=your_jwt_secret_here

# Odoo (optional for demo)
ODOO_URL=http://odoo:8069
ODOO_DB=dentaflow
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Odoo ERP:** http://localhost:8069

**Default Credentials:**
- **Admin:** admin@dentaflow.ai / admin123
- **Odoo:** admin / admin

---

## 📦 What Gets Installed

### Services
1. **PostgreSQL** - Database (port 5432)
2. **Redis** - Cache (port 6379)
3. **Backend** - FastAPI + AI Agents (port 8000)
4. **Frontend** - React App (port 3000)
5. **Odoo** - ERP System (port 8069)

### Data
- Demo database with 5 patients
- 30 days of appointments
- Sample financial data
- AI agent knowledge base

---

## 🔧 Detailed Installation

### Option 1: Docker Compose (Recommended)

**Advantages:**
- ✅ Fastest setup
- ✅ All services included
- ✅ Consistent environment
- ✅ Easy to tear down

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai

# 2. Configure environment
cp .env.example .env
# Edit .env with your values

# 3. Start services
docker-compose up -d

# 4. Initialize database (first time only)
docker-compose exec backend python -m alembic upgrade head
docker-compose exec backend python seed_demo_data.py

# 5. Verify installation
docker-compose ps
curl http://localhost:8000/health
```

### Option 2: Manual Installation (Development)

**Advantages:**
- ✅ Full control
- ✅ Easier debugging
- ✅ Hot reload for development

**Backend Setup:**
```bash
# 1. Install Python dependencies
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Set up database
createdb dentaflow
python -m alembic upgrade head
python seed_demo_data.py

# 3. Start backend
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
# 1. Install Node dependencies
cd frontend
npm install

# 2. Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL

# 3. Start frontend
npm run dev
```

**Odoo Setup (Optional):**
```bash
# Use Docker for Odoo
docker run -d \
  --name odoo \
  -p 8069:8069 \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  odoo:17
```

---

## ✅ Verification

### 1. Check Services

```bash
# All services should be running
docker-compose ps

# Expected output:
# NAME                 STATUS
# dentaflow-backend    Up
# dentaflow-frontend   Up
# dentaflow-db         Up
# dentaflow-redis      Up
# dentaflow-odoo       Up
```

### 2. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "healthy"}

# API documentation
open http://localhost:8000/docs
```

### 3. Test Frontend

```bash
# Open in browser
open http://localhost:3000

# You should see the DentaFlow landing page
```

### 4. Test AI Agents

```bash
# Test Alex agent
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need to schedule an appointment"}'

# You should get a response from Alex
```

---

## 🐛 Troubleshooting

### Port Already in Use

**Problem:** Port 3000, 8000, or 5432 already in use

**Solution:**
```bash
# Find process using port
lsof -i :8000  # On Mac/Linux
netstat -ano | findstr :8000  # On Windows

# Kill process or change port in docker-compose.yml
```

### Database Connection Error

**Problem:** Backend can't connect to database

**Solution:**
```bash
# Check database is running
docker-compose ps dentaflow-db

# Check database logs
docker-compose logs dentaflow-db

# Restart database
docker-compose restart dentaflow-db
```

### OpenAI API Error

**Problem:** AI agents not working

**Solution:**
```bash
# Check API key in .env
cat .env | grep OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Frontend Build Error

**Problem:** Frontend won't start

**Solution:**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm cache clean --force
```

---

## 🔄 Updating

### Pull Latest Changes

```bash
# Pull from Git
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec backend python -m alembic upgrade head
```

---

## 🗑️ Uninstalling

### Remove All Services

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## 📚 Next Steps

1. **[Quick Start Guide](quick-start.md)** - Learn basic operations
2. **[Architecture Overview](../02-architecture/overview.md)** - Understand the system
3. **[Development Guide](../03-development/README.md)** - Start developing
4. **[API Documentation](http://localhost:8000/docs)** - Explore the API

---

## 💡 Tips

- **Use Docker Compose** for quickest setup
- **Check logs** if something doesn't work: `docker-compose logs -f`
- **Restart services** if needed: `docker-compose restart`
- **Backup data** before major updates
- **Read error messages** carefully - they usually tell you what's wrong

---

## 📞 Need Help?

- **GitHub Issues:** https://github.com/scubapro711/dental-clinic-ai/issues
- **Email:** support@dentaflow.ai
- **Documentation:** https://docs.dentaflow.ai

---

**Happy coding! 🚀**

