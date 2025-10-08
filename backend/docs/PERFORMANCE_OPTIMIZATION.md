# Performance Optimization Guide

**Version:** 15.0.0  
**Last Updated:** October 8, 2025  
**Target:** < 200ms API response time (p95)

---

## 📊 Current Performance

### Baseline Metrics (Before Optimization)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| API Response Time (p50) | ~150ms | < 100ms | 🟡 Good |
| API Response Time (p95) | ~400ms | < 200ms | 🔴 Needs Work |
| API Response Time (p99) | ~800ms | < 500ms | 🔴 Needs Work |
| Database Query Time | ~50ms | < 20ms | 🟡 Good |
| Agent Response Time | ~3s | < 2s | 🟡 Good |
| Memory Usage | ~500MB | < 1GB | ✅ Excellent |
| CPU Usage | ~30% | < 50% | ✅ Excellent |

---

## 🎯 Optimization Strategy

### 1. Database Optimization ✅

#### Add Indexes
```sql
-- User lookups
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_cognito_sub ON users(cognito_sub);
CREATE INDEX CONCURRENTLY idx_users_organization_id ON users(organization_id);

-- Organization memberships
CREATE INDEX CONCURRENTLY idx_memberships_user_org ON organization_memberships(user_id, organization_id);
CREATE INDEX CONCURRENTLY idx_memberships_odoo_partner ON organization_memberships(odoo_partner_id);

-- Conversations
CREATE INDEX CONCURRENTLY idx_conversations_org ON conversations(organization_id);
CREATE INDEX CONCURRENTLY idx_conversations_user ON conversations(user_id);
CREATE INDEX CONCURRENTLY idx_conversations_status ON conversations(status);
CREATE INDEX CONCURRENTLY idx_conversations_created ON conversations(created_at DESC);

-- Messages
CREATE INDEX CONCURRENTLY idx_messages_conversation ON messages(conversation_id);
CREATE INDEX CONCURRENTLY idx_messages_created ON messages(created_at DESC);

-- Appointments
CREATE INDEX CONCURRENTLY idx_appointments_org ON appointments(organization_id);
CREATE INDEX CONCURRENTLY idx_appointments_patient ON appointments(patient_id);
CREATE INDEX CONCURRENTLY idx_appointments_date ON appointments(appointment_date);

-- Audit logs
CREATE INDEX CONCURRENTLY idx_audit_user ON audit_logs(user_id);
CREATE INDEX CONCURRENTLY idx_audit_org ON audit_logs(organization_id);
CREATE INDEX CONCURRENTLY idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX CONCURRENTLY idx_audit_created ON audit_logs(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_conversations_org_status_created 
    ON conversations(organization_id, status, created_at DESC);

CREATE INDEX CONCURRENTLY idx_appointments_org_date 
    ON appointments(organization_id, appointment_date);
```

#### Query Optimization
```python
# Before: N+1 query problem
conversations = db.query(Conversation).all()
for conv in conversations:
    messages = conv.messages  # Separate query for each!

# After: Eager loading
from sqlalchemy.orm import joinedload

conversations = db.query(Conversation)\
    .options(joinedload(Conversation.messages))\
    .all()

# Before: Loading all data
patients = db.query(Patient).all()

# After: Pagination
patients = db.query(Patient)\
    .limit(50)\
    .offset(page * 50)\
    .all()

# Before: No query optimization
recent_conversations = db.query(Conversation)\
    .filter(Conversation.organization_id == org_id)\
    .all()

# After: Optimized with index hints
recent_conversations = db.query(Conversation)\
    .filter(Conversation.organization_id == org_id)\
    .filter(Conversation.status == "active")\
    .order_by(Conversation.created_at.desc())\
    .limit(20)\
    .all()
```

#### Connection Pooling
```python
# config.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to keep open
    max_overflow=10,       # Additional connections when pool is full
    pool_timeout=30,       # Timeout for getting connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connections before using
)
```

### 2. API Response Optimization ✅

#### Response Compression
```python
# main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### Response Caching
```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Cache static data
@router.get("/treatments")
@cache(expire=3600)  # Cache for 1 hour
async def get_treatments():
    return db.query(Treatment).all()

# Cache user-specific data
@router.get("/patients/{patient_id}")
@cache(expire=300)  # Cache for 5 minutes
async def get_patient(patient_id: int):
    return db.query(Patient).get(patient_id)
```

#### Async Database Queries
```python
# Use async SQLAlchemy for better concurrency
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    pool_size=20
)

# Async queries
async def get_conversations(org_id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.organization_id == org_id)
            .options(joinedload(Conversation.messages))
        )
        return result.scalars().all()
```

### 3. Caching Strategy (Redis) ⏳

See [Component 4.5: Redis Caching](#component-4-5)

### 4. Agent Performance ✅

#### Streaming Responses
```python
# Stream agent responses for better perceived performance
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        async for chunk in agent.stream(message):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

#### Parallel Tool Execution
```python
# Execute multiple tools in parallel
import asyncio

async def execute_tools_parallel(tools: list):
    tasks = [tool.execute() for tool in tools]
    results = await asyncio.gather(*tasks)
    return results
```

#### Agent Response Caching
```python
# Cache common agent responses
@cache(expire=300)
async def get_agent_response(query: str, context: dict):
    return await agent.run(query, context)
```

### 5. Frontend Optimization ✅

#### Code Splitting
```typescript
// Lazy load components
const Dashboard = lazy(() => import('./components/Dashboard'));
const AgenticDashboard = lazy(() => import('./components/AgenticDashboard'));

// Route-based code splitting
<Route path="/dashboard" element={<Suspense fallback={<Loading />}><Dashboard /></Suspense>} />
```

#### API Request Batching
```typescript
// Batch multiple requests
const batchedFetch = async (requests: Request[]) => {
  const responses = await Promise.all(
    requests.map(req => fetch(req))
  );
  return responses;
};
```

#### Virtual Scrolling
```typescript
// For large lists
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={conversations.length}
  itemSize={80}
>
  {({ index, style }) => (
    <div style={style}>
      <ConversationItem conversation={conversations[index]} />
    </div>
  )}
</FixedSizeList>
```

---

## 📈 Monitoring & Profiling

### Application Performance Monitoring

```python
# Add APM middleware
from app.middleware.performance import PerformanceMiddleware

app.add_middleware(PerformanceMiddleware)
```

### Query Performance Logging

```python
# Log slow queries
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("sqlalchemy.performance")

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    if total > 0.1:  # Log queries > 100ms
        logger.warning(f"Slow query ({total:.2f}s): {statement}")
```

### Endpoint Performance Tracking

```python
@app.middleware("http")
async def track_performance(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log slow endpoints
    if duration > 0.5:  # > 500ms
        logger.warning(
            f"Slow endpoint: {request.method} {request.url.path} "
            f"took {duration:.2f}s"
        )
    
    # Add performance header
    response.headers["X-Process-Time"] = str(duration)
    
    return response
```

---

## 🎯 Performance Targets

### API Response Times

| Endpoint Type | p50 | p95 | p99 |
|---------------|-----|-----|-----|
| Simple GET | < 50ms | < 100ms | < 200ms |
| Complex GET | < 100ms | < 200ms | < 500ms |
| POST/PUT | < 150ms | < 300ms | < 600ms |
| Agent Chat | < 1s | < 2s | < 3s |

### Database Query Times

| Query Type | Target |
|------------|--------|
| Simple SELECT | < 10ms |
| JOIN (2-3 tables) | < 20ms |
| Complex JOIN | < 50ms |
| Aggregation | < 100ms |

### Frontend Metrics

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1s |
| Time to Interactive | < 2s |
| Largest Contentful Paint | < 2.5s |
| Cumulative Layout Shift | < 0.1 |

---

## 🔧 Implementation Checklist

### Database ✅
- [x] Add indexes for common queries
- [x] Implement connection pooling
- [x] Enable query result caching
- [x] Optimize N+1 queries
- [x] Add pagination

### API ✅
- [x] Enable response compression
- [x] Implement response caching
- [x] Add async database queries
- [x] Optimize serialization

### Agents ✅
- [x] Implement streaming responses
- [x] Add parallel tool execution
- [x] Cache common responses

### Frontend ✅
- [x] Code splitting
- [x] Lazy loading
- [x] Virtual scrolling
- [x] Request batching

### Monitoring ✅
- [x] APM middleware
- [x] Slow query logging
- [x] Endpoint performance tracking
- [x] Error rate monitoring

---

## 📊 Expected Results

After implementing all optimizations:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API p95 | 400ms | 180ms | 55% faster |
| API p99 | 800ms | 450ms | 44% faster |
| DB Query | 50ms | 18ms | 64% faster |
| Agent Response | 3s | 1.8s | 40% faster |
| Memory Usage | 500MB | 450MB | 10% less |

---

## 🚀 Next Steps

1. **Implement Redis caching** (Component 4.5)
2. **Load testing** with Locust
3. **Profile production** with APM tools
4. **Continuous optimization** based on metrics

---

**Status:** ✅ Complete  
**Performance Gain:** ~50% improvement expected
