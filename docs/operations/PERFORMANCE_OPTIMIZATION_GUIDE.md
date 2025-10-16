# Performance Optimization Guide for DentaFlow SaaS

**Author:** Manus AI  
**Date:** October 16, 2025  
**Version:** 1.0

---

## 1. Overview

This document provides guidelines and best practices for optimizing the performance of the DentaFlow SaaS platform. It covers database optimization, caching strategies, API performance, and infrastructure tuning.

## 2. Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **API Response Time (p50)** | <200ms | TBD | ⏳ |
| **API Response Time (p95)** | <500ms | TBD | ⏳ |
| **API Response Time (p99)** | <1000ms | TBD | ⏳ |
| **Database Query Time (p95)** | <100ms | TBD | ⏳ |
| **Page Load Time (First Contentful Paint)** | <1.5s | TBD | ⏳ |
| **Time to Interactive** | <3s | TBD | ⏳ |
| **Concurrent Users (without degradation)** | 500 | TBD | ⏳ |
| **Requests per Second** | 1000 | TBD | ⏳ |

## 3. Database Optimization

### 3.1. Indexing Strategy

**Current Indexes:**
```sql
-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization_id ON users(organization_id);

-- Patients table
CREATE INDEX idx_patients_organization_id ON patients(organization_id);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_email ON patients(email);

-- Appointments table
CREATE INDEX idx_appointments_organization_id ON appointments(organization_id);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_appointments_start_time ON appointments(start_time);
CREATE INDEX idx_appointments_status ON appointments(status);

-- Conversations table
CREATE INDEX idx_conversations_organization_id ON conversations(organization_id);
CREATE INDEX idx_conversations_patient_id ON conversations(patient_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- Subscriptions table
CREATE INDEX idx_subscriptions_organization_id ON subscriptions(organization_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

**Recommended Additional Indexes:**
```sql
-- Composite indexes for common queries
CREATE INDEX idx_appointments_org_date ON appointments(organization_id, start_time);
CREATE INDEX idx_conversations_org_patient ON conversations(organization_id, patient_id);
CREATE INDEX idx_users_org_role ON users(organization_id, role);

-- Partial indexes for active records
CREATE INDEX idx_active_subscriptions ON subscriptions(organization_id) WHERE status = 'active';
CREATE INDEX idx_active_users ON users(organization_id) WHERE is_active = true;
```

### 3.2. Query Optimization

**Common Slow Queries:**

1. **Dashboard Overview Query**
   ```python
   # BEFORE (N+1 query problem)
   organizations = db.query(Organization).all()
   for org in organizations:
       patient_count = db.query(Patient).filter(Patient.organization_id == org.id).count()
       appointment_count = db.query(Appointment).filter(Appointment.organization_id == org.id).count()
   
   # AFTER (single query with joins)
   from sqlalchemy import func
   
   results = db.query(
       Organization,
       func.count(Patient.id).label('patient_count'),
       func.count(Appointment.id).label('appointment_count')
   ).outerjoin(Patient).outerjoin(Appointment).group_by(Organization.id).all()
   ```

2. **Patient Search Query**
   ```python
   # BEFORE (full table scan)
   patients = db.query(Patient).filter(
       Patient.name.like(f'%{search_term}%')
   ).all()
   
   # AFTER (use trigram index for fuzzy search)
   from sqlalchemy import func
   
   patients = db.query(Patient).filter(
       func.similarity(Patient.name, search_term) > 0.3
   ).order_by(func.similarity(Patient.name, search_term).desc()).limit(20)
   
   # Enable pg_trgm extension
   # CREATE EXTENSION IF NOT EXISTS pg_trgm;
   # CREATE INDEX idx_patients_name_trgm ON patients USING gin (name gin_trgm_ops);
   ```

### 3.3. Connection Pooling

**Current Configuration:**
```python
# backend/app/core/database.py
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,           # Increase from default 5
    max_overflow=40,        # Increase from default 10
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False
)
```

**Recommended for Production:**
```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=50,           # For high concurrency
    max_overflow=100,
    pool_pre_ping=True,
    pool_recycle=1800,      # Recycle every 30 minutes
    pool_timeout=30,        # Wait max 30s for connection
    echo=False
)
```

### 3.4. Database Maintenance

**Weekly Tasks:**
```sql
-- Analyze tables to update statistics
ANALYZE users;
ANALYZE patients;
ANALYZE appointments;
ANALYZE conversations;

-- Vacuum to reclaim storage
VACUUM ANALYZE users;
VACUUM ANALYZE patients;
```

**Monthly Tasks:**
```sql
-- Full vacuum (requires downtime)
VACUUM FULL users;
VACUUM FULL patients;

-- Reindex
REINDEX TABLE users;
REINDEX TABLE patients;
```

## 4. Caching Strategy

### 4.1. Redis Caching

**Cache Layers:**

1. **Session Cache** (TTL: 24 hours)
   - User sessions
   - JWT tokens
   - Authentication state

2. **Data Cache** (TTL: 5-60 minutes)
   - Dashboard statistics
   - Organization settings
   - User preferences

3. **Query Cache** (TTL: 1-5 minutes)
   - Frequently accessed patient records
   - Appointment lists
   - Search results

**Implementation Example:**
```python
import redis
from functools import wraps
import json

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=6379,
    db=0,
    decode_responses=True
)

def cache_result(ttl=300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=300)  # Cache for 5 minutes
def get_dashboard_stats(organization_id: int):
    # Expensive database query
    ...
```

### 4.2. HTTP Caching

**Frontend Static Assets:**
```nginx
# nginx.conf
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location /api/ {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

**API Response Caching:**
```python
from fastapi import Response

@router.get("/dashboard/stats")
def get_stats(response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes
    return {"stats": ...}
```

### 4.3. Cache Invalidation

**Strategies:**

1. **Time-based (TTL):** Simplest, works for most cases
2. **Event-based:** Invalidate on data changes
3. **Version-based:** Include version number in cache key

**Example:**
```python
def invalidate_dashboard_cache(organization_id: int):
    """Invalidate dashboard cache when data changes."""
    pattern = f"get_dashboard_stats:*{organization_id}*"
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

# Call after data modification
@router.post("/appointments")
def create_appointment(appointment: AppointmentCreate):
    # Create appointment
    db.add(appointment)
    db.commit()
    
    # Invalidate cache
    invalidate_dashboard_cache(appointment.organization_id)
```

## 5. API Optimization

### 5.1. Pagination

**Always paginate large result sets:**
```python
from fastapi import Query

@router.get("/patients")
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    patients = db.query(Patient).offset(skip).limit(limit).all()
    total = db.query(Patient).count()
    
    return {
        "items": patients,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### 5.2. Field Selection

**Allow clients to request only needed fields:**
```python
from typing import Optional, List

@router.get("/patients/{patient_id}")
def get_patient(
    patient_id: int,
    fields: Optional[List[str]] = Query(None)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if fields:
        # Return only requested fields
        return {field: getattr(patient, field) for field in fields if hasattr(patient, field)}
    
    return patient
```

### 5.3. Async Operations

**Use async for I/O-bound operations:**
```python
from fastapi import BackgroundTasks

@router.post("/appointments")
async def create_appointment(
    appointment: AppointmentCreate,
    background_tasks: BackgroundTasks
):
    # Create appointment (fast)
    db.add(appointment)
    db.commit()
    
    # Send notifications in background (slow)
    background_tasks.add_task(send_appointment_notification, appointment.id)
    
    return appointment
```

### 5.4. Response Compression

**Enable gzip compression:**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## 6. Frontend Optimization

### 6.1. Code Splitting

**Lazy load routes:**
```javascript
// App.jsx
import React, { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Patients = lazy(() => import('./pages/Patients'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/patients" element={<Patients />} />
      </Routes>
    </Suspense>
  );
}
```

### 6.2. Image Optimization

**Use WebP format and lazy loading:**
```javascript
<img 
  src="patient-photo.webp" 
  loading="lazy" 
  alt="Patient Photo"
/>
```

### 6.3. Bundle Size Optimization

**Analyze and reduce bundle size:**
```bash
# Build with source map analysis
npm run build -- --stats

# Analyze with webpack-bundle-analyzer
npx webpack-bundle-analyzer build/stats.json
```

## 7. Infrastructure Tuning

### 7.1. Cloud Run Configuration

**Recommended Settings:**
```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: dentaflow-backend
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "2"      # Always keep 2 instances warm
        autoscaling.knative.dev/maxScale: "100"    # Scale up to 100 instances
        autoscaling.knative.dev/target: "80"       # Target 80 concurrent requests per instance
    spec:
      containerConcurrency: 100                     # Max 100 concurrent requests per container
      timeoutSeconds: 300                           # 5 minute timeout
      containers:
      - image: gcr.io/dentaflow-saas/backend
        resources:
          limits:
            cpu: "2000m"                            # 2 vCPUs
            memory: "2Gi"                           # 2 GB RAM
```

### 7.2. Cloud SQL Configuration

**Recommended Settings:**
```
Machine Type: db-n1-standard-4 (4 vCPUs, 15 GB RAM)
Storage: 100 GB SSD
Backups: Automated daily backups, 7-day retention
High Availability: Enabled (for production)
Maintenance Window: Sunday 2:00 AM - 6:00 AM UTC
```

**Connection Pooling:**
```
Max Connections: 500
```

### 7.3. CDN Configuration

**Cloud CDN for static assets:**
```bash
# Enable Cloud CDN for frontend bucket
gcloud compute backend-buckets update dentaflow-frontend \
    --enable-cdn \
    --cache-mode=CACHE_ALL_STATIC
```

## 8. Monitoring and Profiling

### 8.1. Application Performance Monitoring (APM)

**Install OpenTelemetry:**
```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Set up tracing
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
trace.set_tracer_provider(tracer_provider)

# Use in code
tracer = trace.get_tracer(__name__)

@router.get("/patients")
def list_patients():
    with tracer.start_as_current_span("list_patients"):
        # Your code here
        ...
```

### 8.2. Database Query Profiling

**Enable slow query logging:**
```sql
-- PostgreSQL configuration
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries >1s
SELECT pg_reload_conf();
```

**Analyze slow queries:**
```sql
-- Find slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## 9. Load Testing Results

**Test Configuration:**
- Users: 100 concurrent
- Duration: 10 minutes
- Ramp-up: 10 users/second

**Target Results:**
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Requests/sec | >500 | TBD | ⏳ |
| Error Rate | <1% | TBD | ⏳ |
| p95 Response Time | <500ms | TBD | ⏳ |
| p99 Response Time | <1000ms | TBD | ⏳ |

## 10. Optimization Checklist

### Before Launch
- [ ] All database indexes created
- [ ] Redis caching implemented for hot paths
- [ ] API pagination implemented
- [ ] Response compression enabled
- [ ] Frontend code splitting implemented
- [ ] Images optimized and lazy-loaded
- [ ] Cloud Run autoscaling configured
- [ ] Cloud SQL properly sized
- [ ] CDN enabled for static assets
- [ ] APM/tracing enabled

### Post-Launch
- [ ] Load testing completed
- [ ] Slow query log reviewed
- [ ] Cache hit rate >80%
- [ ] API response times meet targets
- [ ] Database connection pool utilization <80%
- [ ] No N+1 query problems
- [ ] Frontend bundle size <500KB (gzipped)

## 11. Continuous Optimization

**Monthly Review:**
1. Review slow query log
2. Analyze cache hit rates
3. Check database indexes usage
4. Review API response times
5. Optimize top 10 slowest endpoints

**Quarterly Review:**
1. Load testing with increased traffic
2. Database schema optimization
3. Infrastructure cost optimization
4. Frontend performance audit

