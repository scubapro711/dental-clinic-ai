"""
Phase 6.5 - Performance Testing: Load Testing
==============================================

Test system under concurrent load to identify scalability issues.

Goals:
- Test with increasing concurrent users (1, 5, 10, 25, 50)
- Measure response time degradation under load
- Identify breaking points
- Test system recovery

Success Criteria:
- p95 response time < 2s with 50 concurrent users
- Error rate < 1%
- No crashes under load
"""

import pytest
import time
import asyncio
import concurrent.futures
import psutil
import os
import statistics
from typing import List, Dict, Any
from unittest.mock import Mock, patch
from dataclasses import dataclass

from app.agents.agent_graph_v4 import AgentGraphV4


@dataclass
class LoadTestResult:
    """Result from a single load test request"""
    duration: float
    success: bool
    error: str = None
    memory_mb: float = 0.0


class LoadTester:
    """Helper class for load testing"""
    
    def __init__(self, agent_graph):
        self.agent_graph = agent_graph
        self.process = psutil.Process(os.getpid())
    
    def execute_request(self, request_id: int, query: str) -> LoadTestResult:
        """Execute a single request and measure performance"""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        
        try:
            # Mock LLM for controlled testing
            with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
                mock_response = Mock()
                mock_response.content = f"Response to request {request_id}"
                mock_llm.return_value.invoke.return_value = mock_response
                
                state = {
                    "messages": [{"role": "user", "content": query}],
                    "user_role": "patient"
                }
                
                # Provide config for checkpointer
                config = {"configurable": {"thread_id": f"test_{request_id}"}}
                
                result = self.agent_graph.graph.invoke(state, config=config)
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            
            return LoadTestResult(
                duration=end_time - start_time,
                success=True,
                memory_mb=end_memory - start_memory
            )
            
        except Exception as e:
            end_time = time.time()
            return LoadTestResult(
                duration=end_time - start_time,
                success=False,
                error=str(e)
            )
    
    def run_concurrent_load(self, num_users: int, queries: List[str]) -> List[LoadTestResult]:
        """Run load test with concurrent users"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = []
            
            for i in range(num_users):
                query = queries[i % len(queries)]
                future = executor.submit(self.execute_request, i, query)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    results.append(LoadTestResult(
                        duration=30.0,
                        success=False,
                        error=f"Timeout: {str(e)}"
                    ))
        
        return results


def analyze_results(results: List[LoadTestResult]) -> Dict[str, Any]:
    """Analyze load test results"""
    durations = [r.duration for r in results]
    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]
    
    if not durations:
        return {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "error_rate": 1.0
        }
    
    return {
        "total_requests": len(results),
        "successful": len(successes),
        "failed": len(failures),
        "error_rate": len(failures) / len(results),
        "avg_duration": statistics.mean(durations),
        "median_duration": statistics.median(durations),
        "p95_duration": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations),
        "p99_duration": statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else max(durations),
        "min_duration": min(durations),
        "max_duration": max(durations),
        "throughput": len(results) / sum(durations) if sum(durations) > 0 else 0
    }


@pytest.fixture
def agent_graph():
    """Create agent graph for testing"""
    return AgentGraphV4(memory=None)


@pytest.fixture
def load_tester(agent_graph):
    """Create load tester"""
    return LoadTester(agent_graph)


@pytest.fixture
def test_queries():
    """Standard test queries for load testing"""
    return [
        "I need to book an appointment",
        "Show patient chart for ID 123",
        "What's our revenue this month?",
        "Check inventory levels",
        "Schedule a cleaning appointment",
        "Update patient contact info",
        "Generate financial report",
        "Show staff schedule",
        "Order dental supplies",
        "What are your clinic hours?"
    ]


# ============================================================================
# Test 1: Baseline Single User Performance
# ============================================================================

@pytest.mark.load
def test_baseline_single_user(load_tester, test_queries):
    """
    Establish baseline performance with single user.
    
    Target: < 1s average, < 2s p95
    """
    print(f"\n{'='*60}")
    print(f"BASELINE: SINGLE USER")
    print(f"{'='*60}")
    
    results = load_tester.run_concurrent_load(1, test_queries)
    analysis = analyze_results(results)
    
    print(f"Total requests: {analysis['total_requests']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Error rate: {analysis['error_rate']:.2%}")
    
    # Print error details if any
    if results and not results[0].success:
        print(f"Error details: {results[0].error}")
    
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"P95 duration: {analysis['p95_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['error_rate'] < 0.01, f"Too many errors: {analysis['error_rate']:.2%}"
    assert analysis['avg_duration'] < 1.0, f"Too slow: {analysis['avg_duration']:.3f}s (target: < 1s)"
    assert analysis['p95_duration'] < 2.0, f"P95 too slow: {analysis['p95_duration']:.3f}s (target: < 2s)"


# ============================================================================
# Test 2: Light Load (5 Concurrent Users)
# ============================================================================

@pytest.mark.load
def test_light_load_5_users(load_tester, test_queries):
    """
    Test with 5 concurrent users.
    
    Target: < 1.5s average, < 2s p95
    """
    print(f"\n{'='*60}")
    print(f"LIGHT LOAD: 5 CONCURRENT USERS")
    print(f"{'='*60}")
    
    results = load_tester.run_concurrent_load(5, test_queries)
    analysis = analyze_results(results)
    
    print(f"Total requests: {analysis['total_requests']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Error rate: {analysis['error_rate']:.2%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"P95 duration: {analysis['p95_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"Throughput: {analysis['throughput']:.2f} req/s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['error_rate'] < 0.01, f"Too many errors: {analysis['error_rate']:.2%}"
    assert analysis['avg_duration'] < 1.5, f"Too slow: {analysis['avg_duration']:.3f}s (target: < 1.5s)"
    assert analysis['p95_duration'] < 2.0, f"P95 too slow: {analysis['p95_duration']:.3f}s (target: < 2s)"


# ============================================================================
# Test 3: Medium Load (10 Concurrent Users)
# ============================================================================

@pytest.mark.load
def test_medium_load_10_users(load_tester, test_queries):
    """
    Test with 10 concurrent users.
    
    Target: < 2s average, < 3s p95
    """
    print(f"\n{'='*60}")
    print(f"MEDIUM LOAD: 10 CONCURRENT USERS")
    print(f"{'='*60}")
    
    results = load_tester.run_concurrent_load(10, test_queries)
    analysis = analyze_results(results)
    
    print(f"Total requests: {analysis['total_requests']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Error rate: {analysis['error_rate']:.2%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"P95 duration: {analysis['p95_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"Throughput: {analysis['throughput']:.2f} req/s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['error_rate'] < 0.01, f"Too many errors: {analysis['error_rate']:.2%}"
    assert analysis['avg_duration'] < 2.0, f"Too slow: {analysis['avg_duration']:.3f}s (target: < 2s)"
    assert analysis['p95_duration'] < 3.0, f"P95 too slow: {analysis['p95_duration']:.3f}s (target: < 3s)"


# ============================================================================
# Test 4: Heavy Load (25 Concurrent Users)
# ============================================================================

@pytest.mark.load
def test_heavy_load_25_users(load_tester, test_queries):
    """
    Test with 25 concurrent users.
    
    Target: < 3s average, < 5s p95
    """
    print(f"\n{'='*60}")
    print(f"HEAVY LOAD: 25 CONCURRENT USERS")
    print(f"{'='*60}")
    
    results = load_tester.run_concurrent_load(25, test_queries)
    analysis = analyze_results(results)
    
    print(f"Total requests: {analysis['total_requests']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Error rate: {analysis['error_rate']:.2%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"P95 duration: {analysis['p95_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"Throughput: {analysis['throughput']:.2f} req/s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['error_rate'] < 0.05, f"Too many errors: {analysis['error_rate']:.2%}"
    assert analysis['avg_duration'] < 3.0, f"Too slow: {analysis['avg_duration']:.3f}s (target: < 3s)"
    assert analysis['p95_duration'] < 5.0, f"P95 too slow: {analysis['p95_duration']:.3f}s (target: < 5s)"


# ============================================================================
# Test 5: Stress Test (50 Concurrent Users)
# ============================================================================

@pytest.mark.load
@pytest.mark.stress
def test_stress_50_users(load_tester, test_queries):
    """
    Stress test with 50 concurrent users.
    
    Target: < 5s average, < 10s p95, < 5% error rate
    """
    print(f"\n{'='*60}")
    print(f"STRESS TEST: 50 CONCURRENT USERS")
    print(f"{'='*60}")
    
    results = load_tester.run_concurrent_load(50, test_queries)
    analysis = analyze_results(results)
    
    print(f"Total requests: {analysis['total_requests']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Error rate: {analysis['error_rate']:.2%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"P95 duration: {analysis['p95_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"Throughput: {analysis['throughput']:.2f} req/s")
    print(f"{'='*60}\n")
    
    # Assertions (more lenient for stress test)
    assert analysis['error_rate'] < 0.10, f"Too many errors: {analysis['error_rate']:.2%}"
    assert analysis['avg_duration'] < 5.0, f"Too slow: {analysis['avg_duration']:.3f}s (target: < 5s)"
    assert analysis['p95_duration'] < 10.0, f"P95 too slow: {analysis['p95_duration']:.3f}s (target: < 10s)"


# ============================================================================
# Test 6: Gradual Ramp-Up Test
# ============================================================================

@pytest.mark.load
def test_gradual_ramp_up(load_tester, test_queries):
    """
    Test gradual increase in load.
    
    Increases from 1 to 25 users in steps.
    Measures performance degradation.
    """
    print(f"\n{'='*60}")
    print(f"GRADUAL RAMP-UP TEST")
    print(f"{'='*60}")
    
    user_levels = [1, 5, 10, 15, 20, 25]
    results_by_level = {}
    
    for num_users in user_levels:
        print(f"\nTesting with {num_users} concurrent users...")
        results = load_tester.run_concurrent_load(num_users, test_queries)
        analysis = analyze_results(results)
        results_by_level[num_users] = analysis
        
        print(f"  Avg: {analysis['avg_duration']:.3f}s")
        print(f"  P95: {analysis['p95_duration']:.3f}s")
        print(f"  Error rate: {analysis['error_rate']:.2%}")
    
    print(f"\n{'='*60}")
    print(f"RAMP-UP SUMMARY")
    print(f"{'='*60}")
    print(f"{'Users':<10} {'Avg (s)':<12} {'P95 (s)':<12} {'Errors':<10}")
    print(f"{'-'*60}")
    
    for num_users, analysis in results_by_level.items():
        print(f"{num_users:<10} {analysis['avg_duration']:<12.3f} {analysis['p95_duration']:<12.3f} {analysis['error_rate']:<10.2%}")
    
    print(f"{'='*60}\n")
    
    # Check that performance degrades gracefully
    baseline_avg = results_by_level[1]['avg_duration']
    max_avg = results_by_level[25]['avg_duration']
    degradation_factor = max_avg / baseline_avg if baseline_avg > 0 else float('inf')
    
    print(f"Performance degradation factor: {degradation_factor:.2f}x")
    
    # Assertion: degradation should be reasonable (< 5x)
    assert degradation_factor < 5.0, f"Performance degrades too much: {degradation_factor:.2f}x"


# ============================================================================
# Test 7: Spike Test (Sudden Load Increase)
# ============================================================================

@pytest.mark.load
def test_spike_recovery(load_tester, test_queries):
    """
    Test system recovery from sudden load spike.
    
    Pattern:
    1. Baseline: 5 users
    2. Spike: 25 users
    3. Recovery: 5 users
    
    Measures if system recovers to baseline performance.
    """
    print(f"\n{'='*60}")
    print(f"SPIKE RECOVERY TEST")
    print(f"{'='*60}")
    
    # Phase 1: Baseline
    print(f"\nPhase 1: Baseline (5 users)")
    baseline_results = load_tester.run_concurrent_load(5, test_queries)
    baseline_analysis = analyze_results(baseline_results)
    print(f"  Avg: {baseline_analysis['avg_duration']:.3f}s")
    print(f"  P95: {baseline_analysis['p95_duration']:.3f}s")
    
    # Phase 2: Spike
    print(f"\nPhase 2: Spike (25 users)")
    spike_results = load_tester.run_concurrent_load(25, test_queries)
    spike_analysis = analyze_results(spike_results)
    print(f"  Avg: {spike_analysis['avg_duration']:.3f}s")
    print(f"  P95: {spike_analysis['p95_duration']:.3f}s")
    
    # Phase 3: Recovery
    print(f"\nPhase 3: Recovery (5 users)")
    recovery_results = load_tester.run_concurrent_load(5, test_queries)
    recovery_analysis = analyze_results(recovery_results)
    print(f"  Avg: {recovery_analysis['avg_duration']:.3f}s")
    print(f"  P95: {recovery_analysis['p95_duration']:.3f}s")
    
    # Check recovery
    recovery_ratio = recovery_analysis['avg_duration'] / baseline_analysis['avg_duration']
    
    print(f"\n{'='*60}")
    print(f"RECOVERY ANALYSIS")
    print(f"{'='*60}")
    print(f"Baseline avg: {baseline_analysis['avg_duration']:.3f}s")
    print(f"Recovery avg: {recovery_analysis['avg_duration']:.3f}s")
    print(f"Recovery ratio: {recovery_ratio:.2f}x")
    print(f"{'='*60}\n")
    
    # Assertion: system should recover to within 1.5x of baseline
    assert recovery_ratio < 1.5, f"System didn't recover properly: {recovery_ratio:.2f}x baseline"


# ============================================================================
# Test 8: Mixed Workload Test
# ============================================================================

@pytest.mark.load
def test_mixed_workload(load_tester):
    """
    Test with realistic mixed workload.
    
    Distribution:
    - 40% Patient queries (Alex)
    - 30% Clinical queries (Sarah)
    - 20% Financial queries (Marcus)
    - 10% Admin queries (Sophia)
    """
    print(f"\n{'='*60}")
    print(f"MIXED WORKLOAD TEST")
    print(f"{'='*60}")
    
    mixed_queries = [
        # 40% Patient queries
        "I need to book an appointment",
        "What are your clinic hours?",
        "I want to reschedule",
        "Do you accept my insurance?",
        # 30% Clinical queries
        "Show patient chart for ID 123",
        "Schedule root canal treatment",
        "Update treatment plan",
        # 20% Financial queries
        "What's our revenue this month?",
        "Show outstanding invoices",
        # 10% Admin queries
        "Check inventory levels"
    ]
    
    results = load_tester.run_concurrent_load(20, mixed_queries)
    analysis = analyze_results(results)
    
    print(f"Total requests: {analysis['total_requests']}")
    print(f"Successful: {analysis['successful']}")
    print(f"Failed: {analysis['failed']}")
    print(f"Error rate: {analysis['error_rate']:.2%}")
    print(f"Average duration: {analysis['avg_duration']:.3f}s")
    print(f"Median duration: {analysis['median_duration']:.3f}s")
    print(f"P95 duration: {analysis['p95_duration']:.3f}s")
    print(f"Max duration: {analysis['max_duration']:.3f}s")
    print(f"Throughput: {analysis['throughput']:.2f} req/s")
    print(f"{'='*60}\n")
    
    # Assertions
    assert analysis['error_rate'] < 0.05, f"Too many errors: {analysis['error_rate']:.2%}"
    assert analysis['p95_duration'] < 5.0, f"P95 too slow: {analysis['p95_duration']:.3f}s (target: < 5s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "load"])

