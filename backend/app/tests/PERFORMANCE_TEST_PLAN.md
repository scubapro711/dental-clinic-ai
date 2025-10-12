# Phase 6.5 - Performance Testing Plan

**Based on:** NVIDIA Best Practices for Scaling LangGraph Agents  
**Date:** 2025-10-10  
**Status:** DRAFT

---

## 🎯 Objectives

Test DentaFlow's ability to handle production load with acceptable performance:

1. **Response Time:** < 2 seconds for 95% of requests
2. **Concurrency:** Support 100 concurrent users
3. **Memory:** < 512MB per agent instance
4. **Throughput:** > 50 requests/minute
5. **Stability:** No crashes or errors under load

---

## 📋 Three-Phase Approach

### Phase 1: Single-User Profiling (Bottleneck Identification)

**Goal:** Understand how the system performs for ONE user

**Tools:**
- `pytest-benchmark` - Python benchmarking
- `memory_profiler` - Memory usage tracking
- `cProfile` - Python profiling
- Custom timing decorators

**Tests:**
1. Profile each agent individually (Alex, Sarah, Marcus, Sophia)
2. Profile supervisor routing overhead
3. Profile tool execution time
4. Profile LLM call latency
5. Profile database queries

**Metrics to Collect:**
- Total workflow time (p50, p95, p99)
- Time per agent invocation
- Time per tool call
- Time per LLM call
- Memory usage per agent
- Token usage per request

**Expected Bottlenecks:**
- LLM API calls (gpt-4.1-mini)
- Odoo API calls (if real Odoo connected)
- Database queries (PostgreSQL checkpoint)
- RAG retrieval (Pinecone)

**Deliverable:** Gantt chart showing timing breakdown

---

### Phase 2: Load Testing (Concurrency Testing)

**Goal:** Test system under increasing concurrent load

**Tools:**
- `locust` - Load testing framework
- `pytest-xdist` - Parallel test execution
- Custom load test scripts

**Test Scenarios:**

#### Scenario 1: Gradual Ramp-Up
- Start: 1 concurrent user
- Increment: +5 users every 30 seconds
- Max: 50 concurrent users
- Duration: 10 minutes
- Goal: Find breaking point

#### Scenario 2: Spike Test
- Baseline: 10 concurrent users
- Spike: Jump to 50 users for 2 minutes
- Return: Back to 10 users
- Goal: Test recovery from spike

#### Scenario 3: Sustained Load
- Load: 25 concurrent users
- Duration: 30 minutes
- Goal: Test stability over time

#### Scenario 4: Mixed Workload
- 40% Patient queries (Alex)
- 30% Clinical queries (Sarah)
- 20% Financial queries (Marcus)
- 10% Admin queries (Sophia)
- Goal: Test realistic usage pattern

**Metrics to Collect:**
- Response time (p50, p95, p99) at each concurrency level
- Throughput (requests/second)
- Error rate (%)
- CPU usage (%)
- Memory usage (MB)
- LLM queue depth
- Database connection pool usage

**Success Criteria:**
- p95 response time < 2s up to 50 concurrent users
- Error rate < 1%
- No memory leaks
- No crashes

**Deliverable:** 
- Performance graphs (response time vs concurrency)
- Resource usage charts
- Bottleneck analysis report

---

### Phase 3: Monitoring & Optimization

**Goal:** Identify and fix performance issues

**Tools:**
- `prometheus` - Metrics collection
- `grafana` - Visualization
- Custom logging

**Monitoring Points:**
1. **Application Level:**
   - Request count
   - Response time distribution
   - Error count
   - Active sessions

2. **Agent Level:**
   - Invocations per agent
   - Average time per agent
   - Tool usage statistics
   - LLM token usage

3. **System Level:**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

**Optimization Strategies:**

1. **LLM Optimization:**
   - Implement response caching
   - Use streaming where possible
   - Batch similar requests
   - Consider smaller models for simple tasks

2. **Database Optimization:**
   - Add indexes on frequently queried fields
   - Implement connection pooling
   - Cache frequent queries
   - Use read replicas

3. **Application Optimization:**
   - Implement request queuing
   - Add rate limiting
   - Use async/await properly
   - Minimize tool calls

4. **Infrastructure Optimization:**
   - Scale horizontally (multiple instances)
   - Use load balancer
   - Add Redis for caching
   - Use CDN for static assets

**Deliverable:**
- Performance monitoring dashboard
- Optimization recommendations
- Before/after comparison

---

## 🧪 Test Implementation

### Test 1: Single Agent Profiling

```python
import pytest
import time
from memory_profiler import profile

@pytest.mark.benchmark
def test_alex_response_time(benchmark):
    """Benchmark Alex agent response time"""
    def run_alex():
        result = agent_graph.invoke({
            "messages": [{"role": "user", "content": "Book appointment"}],
            "user_role": "patient"
        })
        return result
    
    result = benchmark(run_alex)
    assert result is not None
```

### Test 2: Concurrent Load Test

```python
from locust import HttpUser, task, between

class DentaFlowUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(4)  # 40% weight
    def patient_query(self):
        self.client.post("/api/chat", json={
            "message": "I need to book an appointment",
            "user_role": "patient"
        })
    
    @task(3)  # 30% weight
    def clinical_query(self):
        self.client.post("/api/chat", json={
            "message": "Show patient chart for ID 123",
            "user_role": "doctor"
        })
```

### Test 3: Memory Profiling

```python
@profile
def test_memory_usage():
    """Profile memory usage during agent execution"""
    for i in range(100):
        agent_graph.invoke({
            "messages": [{"role": "user", "content": f"Query {i}"}],
            "user_role": "patient"
        })
```

---

## 📊 Expected Results

### Baseline Performance (Single User)

| Metric | Target | Acceptable |
|--------|--------|------------|
| Total Response Time | < 1s | < 2s |
| LLM Call Time | < 500ms | < 1s |
| Tool Execution | < 200ms | < 500ms |
| Memory Usage | < 256MB | < 512MB |

### Load Performance (50 Concurrent Users)

| Metric | Target | Acceptable |
|--------|--------|------------|
| p95 Response Time | < 2s | < 3s |
| Throughput | > 50 req/min | > 30 req/min |
| Error Rate | < 0.5% | < 1% |
| CPU Usage | < 70% | < 90% |
| Memory Usage | < 4GB | < 8GB |

---

## 🚨 Failure Scenarios to Test

1. **LLM Timeout:** What happens when OpenAI API is slow?
2. **Database Connection Loss:** What happens when PostgreSQL is down?
3. **Memory Exhaustion:** What happens when system runs out of memory?
4. **Concurrent Tool Calls:** What happens when 50 users call the same tool?
5. **Invalid Input:** What happens with malformed requests?

---

## 📅 Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Profiling | 4 hours | Bottleneck analysis |
| Phase 2: Load Testing | 6 hours | Performance report |
| Phase 3: Optimization | 8 hours | Optimized system |
| **Total** | **18 hours** | **Complete performance suite** |

---

## ✅ Success Criteria

Phase 6.5 is complete when:

1. ✅ All profiling tests pass
2. ✅ System handles 50 concurrent users with < 2s p95 response time
3. ✅ No memory leaks detected
4. ✅ Error rate < 1% under load
5. ✅ Performance monitoring dashboard deployed
6. ✅ Optimization recommendations documented

---

## 📚 References

- NVIDIA: "How to Scale Your LangGraph Agents in Production"
- LangChain: Testing Documentation
- Locust: Load Testing Best Practices
- pytest-benchmark: Benchmarking Guide

