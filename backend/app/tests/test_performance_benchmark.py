"""
Phase 6.5 - Performance Testing: Benchmarking
==============================================

Use pytest-benchmark for precise performance measurements.

Goals:
- Establish performance baselines
- Compare different implementations
- Track performance regressions
- Generate benchmark reports

Success Criteria:
- All benchmarks complete successfully
- Results documented for future comparison
"""

import pytest
from unittest.mock import Mock, patch

from app.agents.agent_graph_v4 import AgentGraphV4
from app.agents.alex_v2 import AlexAgent
from app.agents.sarah_clinical import sarah_agent
from app.agents.cfo import CFOAgent
from app.agents.practice_admin import PracticeAdminAgent


@pytest.fixture
def agent_graph():
    """Create agent graph for benchmarking"""
    return AgentGraphV4(memory=None)


@pytest.fixture
def alex_agent():
    """Create Alex agent for benchmarking"""
    return AlexAgent()


@pytest.fixture
def marcus_agent():
    """Create Marcus agent for benchmarking"""
    return CFOAgent()


@pytest.fixture
def sophia_agent():
    """Create Sophia agent for benchmarking"""
    return PracticeAdminAgent()


# ============================================================================
# Benchmark 1: Agent Initialization
# ============================================================================

@pytest.mark.benchmark(group="initialization")
def test_benchmark_agent_graph_init(benchmark):
    """Benchmark agent graph initialization time"""
    
    def init_graph():
        return AgentGraphV4(memory=None)
    
    result = benchmark(init_graph)
    assert result is not None


@pytest.mark.benchmark(group="initialization")
def test_benchmark_alex_init(benchmark):
    """Benchmark Alex agent initialization time"""
    
    def init_alex():
        return AlexAgent()
    
    result = benchmark(init_alex)
    assert result is not None


@pytest.mark.benchmark(group="initialization")
def test_benchmark_marcus_init(benchmark):
    """Benchmark Marcus agent initialization time"""
    
    def init_marcus():
        return CFOAgent()
    
    result = benchmark(init_marcus)
    assert result is not None


@pytest.mark.benchmark(group="initialization")
def test_benchmark_sophia_init(benchmark):
    """Benchmark Sophia agent initialization time"""
    
    def init_sophia():
        return PracticeAdminAgent()
    
    result = benchmark(init_sophia)
    assert result is not None


# ============================================================================
# Benchmark 2: Simple Query Processing
# ============================================================================

@pytest.mark.benchmark(group="simple_queries")
def test_benchmark_alex_simple_query(benchmark, alex_agent):
    """Benchmark Alex processing simple patient query"""
    
    def process_query():
        with patch('app.agents.alex_v2.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "I can help you book an appointment."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "I need to book an appointment"}],
                "user_role": "patient"
            }
            
            return alex_agent.process(state)
    
    result = benchmark(process_query)


@pytest.mark.benchmark(group="simple_queries")
def test_benchmark_sarah_simple_query(benchmark):
    """Benchmark Sarah processing simple clinical query"""
    
    def process_query():
        with patch('app.agents.sarah_clinical.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Here is the patient chart."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "Show patient chart"}],
                "user_role": "doctor"
            }
            
            return sarah_agent(state)
    
    result = benchmark(process_query)


@pytest.mark.benchmark(group="simple_queries")
def test_benchmark_marcus_simple_query(benchmark, marcus_agent):
    """Benchmark Marcus processing simple financial query"""
    
    def process_query():
        with patch('app.agents.cfo.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Here is the revenue data."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "Show revenue"}],
                "user_role": "admin"
            }
            
            return marcus_agent.process(state)
    
    result = benchmark(process_query)


@pytest.mark.benchmark(group="simple_queries")
def test_benchmark_sophia_simple_query(benchmark, sophia_agent):
    """Benchmark Sophia processing simple admin query"""
    
    def process_query():
        with patch('app.agents.practice_admin.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Here is the inventory data."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "Check inventory"}],
                "user_role": "admin"
            }
            
            return sophia_agent.process(state)
    
    result = benchmark(process_query)


# ============================================================================
# Benchmark 3: Complex Query Processing
# ============================================================================

@pytest.mark.benchmark(group="complex_queries")
def test_benchmark_alex_complex_query(benchmark, alex_agent):
    """Benchmark Alex processing complex multi-step query"""
    
    def process_query():
        with patch('app.agents.alex_v2.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "I've checked availability and can book you for Tuesday at 2pm."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [
                    {"role": "user", "content": "I need to book an appointment for a cleaning next week, preferably Tuesday afternoon"}
                ],
                "user_role": "patient"
            }
            
            return alex_agent.process(state)
    
    result = benchmark(process_query)


@pytest.mark.benchmark(group="complex_queries")
def test_benchmark_sarah_complex_query(benchmark):
    """Benchmark Sarah processing complex clinical query"""
    
    def process_query():
        with patch('app.agents.sarah_clinical.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Patient has completed 2 of 3 root canal sessions."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [
                    {"role": "user", "content": "Show me the treatment history and current status for patient ID 123"}
                ],
                "user_role": "doctor"
            }
            
            return sarah_agent(state)
    
    result = benchmark(process_query)


# ============================================================================
# Benchmark 4: End-to-End Workflows
# ============================================================================

@pytest.mark.benchmark(group="e2e_workflows")
def test_benchmark_e2e_patient_booking(benchmark, agent_graph):
    """Benchmark end-to-end patient booking workflow"""
    
    def run_workflow():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Appointment booked successfully."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "I need to book an appointment"}],
                "user_role": "patient"
            }
            
            return agent_graph.graph.invoke(state)
    
    result = benchmark(run_workflow)


@pytest.mark.benchmark(group="e2e_workflows")
def test_benchmark_e2e_clinical_workflow(benchmark, agent_graph):
    """Benchmark end-to-end clinical workflow"""
    
    def run_workflow():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Patient chart retrieved."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "Show patient chart for ID 123"}],
                "user_role": "doctor"
            }
            
            return agent_graph.graph.invoke(state)
    
    result = benchmark(run_workflow)


@pytest.mark.benchmark(group="e2e_workflows")
def test_benchmark_e2e_financial_workflow(benchmark, agent_graph):
    """Benchmark end-to-end financial workflow"""
    
    def run_workflow():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Revenue data retrieved."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "Show revenue for this month"}],
                "user_role": "admin"
            }
            
            return agent_graph.graph.invoke(state)
    
    result = benchmark(run_workflow)


# ============================================================================
# Benchmark 5: Message Processing Overhead
# ============================================================================

@pytest.mark.benchmark(group="overhead")
def test_benchmark_message_cleaning(benchmark):
    """Benchmark message cleaning overhead"""
    from app.agents.agent_graph_v4 import remove_handoff_messages
    from langchain_core.messages import HumanMessage, AIMessage
    
    messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="I will delegate to Alex"),
        HumanMessage(content="Book appointment"),
        AIMessage(content="I will transfer to Sarah"),
        HumanMessage(content="Show chart")
    ]
    
    def clean_messages():
        return remove_handoff_messages(messages)
    
    result = benchmark(clean_messages)
    assert len(result) < len(messages)


@pytest.mark.benchmark(group="overhead")
def test_benchmark_state_creation(benchmark):
    """Benchmark state creation overhead"""
    
    def create_state():
        return {
            "messages": [{"role": "user", "content": "Test message"}],
            "user_role": "patient",
            "next": None
        }
    
    result = benchmark(create_state)
    assert result is not None


# ============================================================================
# Benchmark 6: Repeated Operations
# ============================================================================

@pytest.mark.benchmark(group="repeated", warmup=True)
def test_benchmark_repeated_queries(benchmark, agent_graph):
    """Benchmark repeated query processing (tests caching effects)"""
    
    def run_repeated():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Response"
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "What are your hours?"}],
                "user_role": "patient"
            }
            
            # Run same query 10 times
            results = []
            for _ in range(10):
                result = agent_graph.graph.invoke(state)
                results.append(result)
            
            return results
    
    result = benchmark(run_repeated)
    assert len(result) == 10


# ============================================================================
# Benchmark 7: Different Query Complexities
# ============================================================================

@pytest.mark.benchmark(group="complexity")
def test_benchmark_short_query(benchmark, agent_graph):
    """Benchmark short query processing"""
    
    def run_query():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "Yes"
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "Are you open?"}],
                "user_role": "patient"
            }
            
            return agent_graph.graph.invoke(state)
    
    result = benchmark(run_query)


@pytest.mark.benchmark(group="complexity")
def test_benchmark_medium_query(benchmark, agent_graph):
    """Benchmark medium query processing"""
    
    def run_query():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "I can help you with that."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{"role": "user", "content": "I need to book an appointment for next Tuesday"}],
                "user_role": "patient"
            }
            
            return agent_graph.graph.invoke(state)
    
    result = benchmark(run_query)


@pytest.mark.benchmark(group="complexity")
def test_benchmark_long_query(benchmark, agent_graph):
    """Benchmark long query processing"""
    
    def run_query():
        with patch('app.agents.agent_graph_v4.ChatOpenAI') as mock_llm:
            mock_response = Mock()
            mock_response.content = "I understand your request."
            mock_llm.return_value.invoke.return_value = mock_response
            
            state = {
                "messages": [{
                    "role": "user",
                    "content": "I need to book an appointment for a dental cleaning next week, preferably on Tuesday or Wednesday afternoon, and I also need to update my insurance information and check if you accept my new insurance plan"
                }],
                "user_role": "patient"
            }
            
            return agent_graph.graph.invoke(state)
    
    result = benchmark(run_query)


if __name__ == "__main__":
    # Run benchmarks with detailed output
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--benchmark-only",
        "--benchmark-verbose",
        "--benchmark-sort=mean",
        "--benchmark-columns=min,max,mean,stddev,median,ops",
        "--benchmark-group-by=group"
    ])

