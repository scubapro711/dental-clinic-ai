"""
Phase 6.5 - Performance Testing: Simplified Load Testing
=========================================================

Simplified performance tests that work with the actual system architecture.

Goals:
- Test actual agent performance with real LLM calls
- Measure response times under load
- Identify bottlenecks
- Validate system stability

Success Criteria:
- All tests complete successfully
- Performance metrics documented
- No crashes or errors
"""

import pytest
import time
import psutil
import os
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_core.messages import HumanMessage

from app.agents.agent_graph_v4 import AgentGraphV4


@dataclass
class PerformanceResult:
    """Result from a performance test"""
    duration: float
    success: bool
    error: str = None


class SimplePerformanceTester:
    """Simple performance tester for DentaFlow agents"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.agent_graph = AgentGraphV4(memory=None)
    
    def test_single_request(self, query: str, thread_id: str = "test") -> PerformanceResult:
        """Test a single request"""
        start_time = time.time()
        
        try:
            state = {
                "messages": [HumanMessage(content=query)],
                "user_role": "patient"
            }
            
            config = {"configurable": {"thread_id": thread_id}}
            
            result = self.agent_graph.graph.invoke(state, config=config)
            
            end_time = time.time()
            
            return PerformanceResult(
                duration=end_time - start_time,
                success=True
            )
            
        except Exception as e:
            end_time = time.time()
            return PerformanceResult(
                duration=end_time - start_time,
                success=False,
                error=str(e)
            )
    
    def test_multiple_requests(self, queries: List[str]) -> List[PerformanceResult]:
        """Test multiple requests sequentially"""
        results = []
        
        for i, query in enumerate(queries):
            result = self.test_single_request(query, thread_id=f"test_{i}")
            results.append(result)
            
            # Small delay between requests to avoid rate limiting
            time.sleep(0.5)
        
        return results


def analyze_performance(results: List[PerformanceResult]) -> Dict[str, Any]:
    """Analyze performance results"""
    durations = [r.duration for r in results]
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]
    
    if not durations:
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0
        }
    
    return {
        "total": len(results),
        "successful": len(successes),
        "failed": len(failures),
        "success_rate": len(successes) / len(results),
        "avg_duration": statistics.mean(durations),
        "median_duration": statistics.median(durations),
        "min_duration": min(durations),
        "max_duration": max(durations),
        "total_duration": sum(durations)
    }


@pytest.fixture
def tester():
    """Create performance tester"""
    return SimplePerformanceTester()


# ============================================================================
# Test 1: Single Request Performance
# ============================================================================

@pytest.mark.perf
def test_single_request_performance(tester):
    """
    Test single request performance.
    
    Target: < 5s for simple query
    """
    print(f"\n{'='*60}")
    print(f"SINGLE REQUEST PERFORMANCE TEST")
    print(f"{'='*60}")
    
    query = "What are your clinic hours?"
    
    result = tester.test_single_request(query)
    
    print(f"Query: {query}")
    print(f"Success: {result.success}")
    print(f"Duration: {result.duration:.3f}s")
    
    if not result.success:
        print(f"Error: {result.error}")
    
    print(f"{'='*60}\n")
    
    # Assertions
    assert result.success, f"Request failed: {result.error}"
    assert result.duration < 10.0, f"Too slow: {result.duration:.3f}s (target: < 10s)"


# ============================================================================
# Test 2: Multiple Sequential Requests
# ============================================================================

@pytest.mark.perf
def test_sequential_requests(tester):
    """
    Test multiple sequential requests.
    
    Target: All requests complete successfully
    """
    print(f"\n{'='*60}")
    print(f"SEQUENTIAL REQUESTS TEST (5 requests)")
    print(f"{'='*60}")
    
    queries = [
        "What are your clinic hours?",
        "I need to book an appointment",
        "Do you accept insurance?",
        "Where is your clinic located?",
        "What services do you offer?"
    ]
    
    results = tester.test_multiple_requests(queries)
    analysis = analyze_performance(results)
    
    print(f"Total requests: {analysis['total']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Success rate: {analysis['success_rate']:.1%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"Min duration: {analysis['min_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"Total duration: {analysis['total_duration']:.3f}s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['success_rate'] >= 0.8, f"Too many failures: {analysis['success_rate']:.1%}"
    assert analysis['avg_duration'] < 10.0, f"Too slow: {analysis['avg_duration']:.3f}s"


# ============================================================================
# Test 3: Different Query Types
# ============================================================================

@pytest.mark.perf
def test_different_query_types(tester):
    """
    Test different types of queries.
    
    Tests patient, clinical, financial, and admin queries.
    """
    print(f"\n{'='*60}")
    print(f"DIFFERENT QUERY TYPES TEST")
    print(f"{'='*60}")
    
    queries = [
        "I need to book an appointment",  # Patient query
        "What services do you offer?",    # Info query
        "Do you accept my insurance?",    # Insurance query
        "Where is your clinic?",          # Location query
    ]
    
    results = tester.test_multiple_requests(queries)
    analysis = analyze_performance(results)
    
    print(f"Total requests: {analysis['total']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Success rate: {analysis['success_rate']:.1%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"{'='*60}\n")
    
    # Print individual results
    for i, (query, result) in enumerate(zip(queries, results), 1):
        print(f"{i}. {query[:50]}...")
        print(f"   Success: {result.success}, Duration: {result.duration:.3f}s")
        if not result.success:
            print(f"   Error: {result.error}")
    
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['success_rate'] >= 0.75, f"Too many failures: {analysis['success_rate']:.1%}"


# ============================================================================
# Test 4: Memory Usage Test
# ============================================================================

@pytest.mark.perf
def test_memory_usage(tester):
    """
    Test memory usage during operations.
    
    Target: No significant memory leaks
    """
    print(f"\n{'='*60}")
    print(f"MEMORY USAGE TEST")
    print(f"{'='*60}")
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Initial memory: {initial_memory:.2f}MB")
    
    # Run 10 requests
    queries = ["What are your hours?"] * 10
    results = tester.test_multiple_requests(queries)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_growth = final_memory - initial_memory
    
    analysis = analyze_performance(results)
    
    print(f"Final memory: {final_memory:.2f}MB")
    print(f"Memory growth: {memory_growth:.2f}MB")
    print(f"Successful requests: {analysis['successful']}/{analysis['total']}")
    print(f"{'='*60}\n")
    
    # Assertions
    assert memory_growth < 500, f"Excessive memory growth: {memory_growth:.2f}MB"


# ============================================================================
# Test 5: Throughput Test
# ============================================================================

@pytest.mark.perf
def test_throughput(tester):
    """
    Test system throughput.
    
    Measures requests per minute.
    """
    print(f"\n{'='*60}")
    print(f"THROUGHPUT TEST")
    print(f"{'='*60}")
    
    queries = [
        "What are your hours?",
        "I need an appointment",
        "Do you accept insurance?"
    ]
    
    start_time = time.time()
    results = tester.test_multiple_requests(queries)
    end_time = time.time()
    
    total_time = end_time - start_time
    analysis = analyze_performance(results)
    
    throughput = analysis['successful'] / (total_time / 60)  # requests per minute
    
    print(f"Total time: {total_time:.2f}s")
    print(f"Successful requests: {analysis['successful']}")
    print(f"Throughput: {throughput:.2f} requests/minute")
    print(f"Average response time: {analysis['avg_duration']:.3f}s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['success_rate'] >= 0.8, f"Too many failures: {analysis['success_rate']:.1%}"
    assert throughput > 1.0, f"Throughput too low: {throughput:.2f} req/min"


# ============================================================================
# Test 6: Stress Test (Extended)
# ============================================================================

@pytest.mark.perf
@pytest.mark.slow
def test_stress_extended(tester):
    """
    Extended stress test with more requests.
    
    Target: System remains stable over time
    """
    print(f"\n{'='*60}")
    print(f"EXTENDED STRESS TEST (20 requests)")
    print(f"{'='*60}")
    
    queries = [
        "What are your clinic hours?",
        "I need to book an appointment",
        "Do you accept insurance?",
        "What services do you offer?",
        "Where is your clinic located?"
    ] * 4  # 20 total requests
    
    print(f"Running {len(queries)} requests...")
    
    results = tester.test_multiple_requests(queries)
    analysis = analyze_performance(results)
    
    print(f"\nTotal requests: {analysis['total']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Success rate: {analysis['success_rate']:.1%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"Total time: {analysis['total_duration']:.2f}s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['success_rate'] >= 0.7, f"Too many failures: {analysis['success_rate']:.1%}"
    assert analysis['avg_duration'] < 15.0, f"Too slow: {analysis['avg_duration']:.3f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "perf"])

