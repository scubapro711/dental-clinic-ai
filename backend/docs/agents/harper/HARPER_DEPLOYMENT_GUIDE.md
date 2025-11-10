# Harper Deployment Guide

## Pre-Deployment Checklist

### ✅ Prerequisites

- [ ] Pinecone account created (https://www.pinecone.io/)
- [ ] Pinecone API key obtained
- [ ] OpenAI API key obtained
- [ ] PostgreSQL database running
- [ ] Backend server accessible
- [ ] Frontend build environment ready

### ✅ Environment Variables

Ensure the following environment variables are set:

```bash
# Backend .env
PINECONE_API_KEY=pcsk_xxxxx...
OPENAI_API_KEY=sk-xxxxx...
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

---

## Step-by-Step Deployment

### Step 1: Database Migration

Run the Alembic migration to create Harper's database tables:

```bash
cd /home/ubuntu/dental-clinic-ai-repo/backend

# Run migration
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt compliance_*"
```

**Expected Output:**
```
                List of relations
 Schema |        Name         | Type  |  Owner
--------+---------------------+-------+---------
 public | compliance_alerts   | table | dentaflow
 public | compliance_metrics  | table | dentaflow
```

---

### Step 2: Upload HIPAA Knowledge Base to Pinecone

Upload all 34 HIPAA knowledge base documents to Pinecone:

```bash
cd /home/ubuntu/dental-clinic-ai-repo/backend

# Set environment variables
export PINECONE_API_KEY="your_pinecone_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Run upload script
python scripts/upload_hipaa_knowledge.py
```

**Expected Output:**
```
Processing: privacy_rule_summary.md
  ✓ Uploaded 1 chunks

Processing: security_rule_summary.md
  ✓ Uploaded 1 chunks

...

✅ Upload complete!
   Total files: 34
   Successfully uploaded: 34
   Failed: 0
   Success rate: 100%

Pinecone Index Stats:
   Total vectors: 33
   Dimension: 1536
   Index name: dentaflow-hipaa
```

---

### Step 3: Verify Pinecone Index

Verify the Pinecone index was created and populated:

```bash
python -c "
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('dentaflow-hipaa')
stats = index.describe_index_stats()
print(f'Total vectors: {stats.total_vector_count}')
print(f'Dimension: {stats.dimension}')
"
```

**Expected Output:**
```
Total vectors: 33
Dimension: 1536
```

---

### Step 4: Update RBAC Permissions

Verify RBAC permissions are configured correctly:

```bash
cd /home/ubuntu/dental-clinic-ai-repo/backend

# Check RBAC configuration
python -c "
from app.agents.rbac import ROLE_PERMISSIONS, Permission

print('Clinic Admin Permissions:')
print('  ACCESS_HARPER:', Permission.ACCESS_HARPER in ROLE_PERMISSIONS['clinic_admin'])

print('Super Admin Permissions:')
print('  ACCESS_HARPER:', Permission.ACCESS_HARPER in ROLE_PERMISSIONS['super_admin'])
"
```

**Expected Output:**
```
Clinic Admin Permissions:
  ACCESS_HARPER: True
Super Admin Permissions:
  ACCESS_HARPER: True
```

---

### Step 5: Test Harper Agent

Test Harper's functionality:

```bash
cd /home/ubuntu/dental-clinic-ai-repo/backend

# Test Harper agent
python -c "
import asyncio
from app.agents.harper_hipaa import HarperAgent

async def test_harper():
    harper = HarperAgent()
    response = await harper.process_message(
        message='What is PHI?',
        user_id=1,
        organization_id=1
    )
    print('Harper Response:', response['response'][:200], '...')

asyncio.run(test_harper())
"
```

**Expected Output:**
```
Harper Response: Protected Health Information (PHI) refers to any information about health status, provision of health care, or payment for health care that can be linked to a specific individual...
```

---

### Step 6: Start Backend Server

Start the FastAPI backend server:

```bash
cd /home/ubuntu/dental-clinic-ai-repo/backend

# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Verify Swagger Docs:**
Navigate to: `http://localhost:8000/docs`

Look for the **"Harper Compliance"** section with endpoints:
- `POST /api/v1/compliance/chat`
- `GET /api/v1/compliance/score`
- `GET /api/v1/compliance/alerts`
- `POST /api/v1/compliance/alerts/{alert_id}/acknowledge`
- `POST /api/v1/compliance/alerts/{alert_id}/resolve`
- `GET /api/v1/compliance/metrics`

---

### Step 7: Build and Start Frontend

Build and start the React frontend:

```bash
cd /home/ubuntu/dental-clinic-ai-repo/frontend

# Install dependencies (if needed)
npm install

# Development
npm run dev

# Production build
npm run build
npm run preview
```

**Verify Harper Dashboard:**
Navigate to: `http://localhost:3000/compliance`

You should see:
- Compliance score cards
- Active alerts (if any)
- Quick actions
- Metrics section
- "Ask Harper" button

---

### Step 8: Test End-to-End

#### Test 1: Harper Chat

1. Navigate to `/compliance`
2. Click "Ask Harper"
3. Type: "What are the requirements for PHI encryption?"
4. Verify Harper responds with accurate HIPAA information
5. Check for suggested actions

#### Test 2: Compliance Score

1. Navigate to `/compliance`
2. Verify compliance score displays (may be 0% initially)
3. Check PHI, Security, and Overall scores

#### Test 3: Alert Management

1. Create a test alert (via API or monitoring service)
2. Navigate to `/compliance`
3. View the alert in the "Open" tab
4. Click "Acknowledge"
5. Verify status changes to "Acknowledged"
6. Click "Mark Resolved" and add notes
7. Verify alert moves to "Resolved" tab

---

### Step 9: Configure Scheduled Monitoring

Set up scheduled compliance checks:

#### Option A: Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily check (runs at midnight)
0 0 * * * cd /home/ubuntu/dental-clinic-ai-repo/backend && python -c "from app.services.harper_monitoring import HarperMonitoringService; from app.core.database import SessionLocal; db = SessionLocal(); service = HarperMonitoringService(db); import asyncio; asyncio.run(service.run_daily_checks(1)); db.close()"

# Add weekly check (runs Monday at midnight)
0 0 * * 1 cd /home/ubuntu/dental-clinic-ai-repo/backend && python -c "from app.services.harper_monitoring import HarperMonitoringService; from app.core.database import SessionLocal; db = SessionLocal(); service = HarperMonitoringService(db); import asyncio; asyncio.run(service.run_weekly_checks(1)); db.close()"

# Add monthly check (runs 1st of month at midnight)
0 0 1 * * cd /home/ubuntu/dental-clinic-ai-repo/backend && python -c "from app.services.harper_monitoring import HarperMonitoringService; from app.core.database import SessionLocal; db = SessionLocal(); service = HarperMonitoringService(db); import asyncio; asyncio.run(service.run_monthly_checks(1)); db.close()"
```

#### Option B: Using Celery (Recommended for Production)

```python
# backend/app/tasks/compliance_tasks.py
from celery import Celery
from app.services.harper_monitoring import HarperMonitoringService
from app.core.database import SessionLocal

celery_app = Celery('dentaflow', broker='redis://localhost:6379/0')

@celery_app.task
def run_daily_compliance_checks():
    db = SessionLocal()
    try:
        service = HarperMonitoringService(db)
        # Run for all organizations
        orgs = db.query(Organization).all()
        for org in orgs:
            asyncio.run(service.run_daily_checks(org.id))
    finally:
        db.close()

@celery_app.task
def run_weekly_compliance_checks():
    db = SessionLocal()
    try:
        service = HarperMonitoringService(db)
        orgs = db.query(Organization).all()
        for org in orgs:
            asyncio.run(service.run_weekly_checks(org.id))
    finally:
        db.close()

@celery_app.task
def run_monthly_compliance_checks():
    db = SessionLocal()
    try:
        service = HarperMonitoringService(db)
        orgs = db.query(Organization).all()
        for org in orgs:
            asyncio.run(service.run_monthly_checks(org.id))
    finally:
        db.close()

# Schedule tasks
celery_app.conf.beat_schedule = {
    'daily-compliance-checks': {
        'task': 'app.tasks.compliance_tasks.run_daily_compliance_checks',
        'schedule': crontab(hour=0, minute=0),
    },
    'weekly-compliance-checks': {
        'task': 'app.tasks.compliance_tasks.run_weekly_compliance_checks',
        'schedule': crontab(hour=0, minute=0, day_of_week=1),
    },
    'monthly-compliance-checks': {
        'task': 'app.tasks.compliance_tasks.run_monthly_compliance_checks',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
}
```

---

### Step 10: Verify Deployment

Run final verification checks:

```bash
# Check backend health
curl http://localhost:8000/health

# Check Harper chat endpoint
curl -X POST http://localhost:8000/api/v1/compliance/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "What is HIPAA?"}'

# Check compliance score endpoint
curl http://localhost:8000/api/v1/compliance/score \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check frontend
curl http://localhost:3000/compliance
```

---

## Post-Deployment

### Monitoring

1. **Check Logs:**
   ```bash
   tail -f /var/log/dentaflow/backend.log
   tail -f /var/log/dentaflow/frontend.log
   ```

2. **Monitor Pinecone Usage:**
   - Log in to Pinecone console
   - Check query count and vector count

3. **Monitor OpenAI Usage:**
   - Log in to OpenAI platform
   - Check API usage and costs

### Backup

1. **Backup Pinecone Index:**
   ```bash
   python scripts/backup_pinecone_index.py
   ```

2. **Backup Database:**
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

### Updates

To update Harper's knowledge base:

```bash
# Add new documents to backend/app/knowledge/hipaa/
# Re-run upload script
python scripts/upload_hipaa_knowledge.py
```

---

## Troubleshooting

### Issue: Harper not responding

**Solution:**
1. Check OpenAI API key is valid
2. Verify Pinecone index exists
3. Check backend logs for errors

### Issue: Alerts not generating

**Solution:**
1. Verify monitoring service is running
2. Check scheduled tasks are configured
3. Manually run checks: `POST /api/v1/compliance/monitoring/run-checks?check_type=daily`

### Issue: Compliance score shows 0%

**Solution:**
1. Run initial compliance check manually
2. Verify organization has data (BAAs, security controls, etc.)
3. Check database for compliance_metrics records

### Issue: Frontend not loading

**Solution:**
1. Check backend API is accessible
2. Verify CORS settings
3. Check browser console for errors

---

## Rollback Plan

If deployment fails, rollback using:

```bash
# Rollback database migration
cd backend
alembic downgrade -1

# Restore previous backend
git checkout <previous_commit>

# Restore previous frontend
cd frontend
git checkout <previous_commit>
npm run build
```

---

## Success Criteria

✅ Harper chat responds to HIPAA questions  
✅ Compliance score displays correctly  
✅ Alerts can be created and managed  
✅ Scheduled monitoring runs automatically  
✅ All API endpoints return 200 status  
✅ Frontend loads without errors  
✅ Swagger documentation is accessible  

---

## Support

For deployment issues:
- Email: devops@dentaflow.com
- Slack: #harper-deployment
- Documentation: https://docs.dentaflow.com/harper/deployment

---

**Deployment Complete! 🎉**

Harper is now live and ready to help your dental clinics maintain HIPAA compliance!

