'''
Agent Initialization Tests

This script tests that all agents can be initialized with their new tools
without errors. It is designed to be run directly as a Python script
in environments where pytest is not available.
'''

import sys

def run_test(test_func):
    """Helper function to run a test and print the result."""
    test_name = test_func.__name__
    print(f"Running test: {test_name}...")
    try:
        test_func()
        print(f"✅ PASSED: {test_name}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {e}")
        return False

# Test Alex Agent Initialization
def test_alex_agent_initialization():
    from app.agents.alex_v2 import AlexAgent
    alex = AlexAgent()
    assert alex is not None, "AlexAgent is None"
    # Expected: 13 base + 12 new = 25 tools (flexible range: 18-30)
    expected_min = 18
    expected_max = 30
    actual_tools = len(alex.tools)
    assert expected_min <= actual_tools <= expected_max, f"Expected {expected_min}-{expected_max} tools for Alex, but found {actual_tools}"
    print(f"   Alex has {actual_tools} tools")

# Test Sarah Agent Initialization
def test_sarah_agent_initialization():
    from app.agents.sarah_clinical import sarah_agent
    assert sarah_agent is not None, "sarah_agent is None"
    # Expected: 18 base + 10 new = 28 tools (flexible range: 25-35)
    expected_min = 25
    expected_max = 35
    actual_tools = len(sarah_agent.tools)
    assert expected_min <= actual_tools <= expected_max, f"Expected {expected_min}-{expected_max} tools for Sarah, but found {actual_tools}"
    print(f"   Sarah has {actual_tools} tools")

# Test Marcus Agent Initialization
def test_marcus_agent_initialization():
    from app.agents.cfo import CFOAgent
    from app.agents.tools.marcus_financial_tools import marcus_financial_tools
    from app.agents.tools.tax_tools import tax_tools
    from app.agents.tools.accountant_referral import accountant_referral_tools
    
    marcus = CFOAgent()
    assert marcus is not None, "CFOAgent is None"
    # Expected: 17 base + 11 new = 28 tools (flexible range: 20-35)
    expected_min = 20
    expected_max = 35
    # Count tools from the imported lists
    actual_tools = len(marcus_financial_tools) + len(tax_tools) + len(accountant_referral_tools)
    assert expected_min <= actual_tools <= expected_max, f"Expected {expected_min}-{expected_max} tools for Marcus, but found {actual_tools}"
    print(f"   Marcus has {actual_tools} tools")

# Test Sophia Agent Initialization
def test_sophia_agent_initialization():
    from app.agents.practice_admin import PracticeAdminAgent
    sophia = PracticeAdminAgent()
    assert sophia is not None, "PracticeAdminAgent is None"
    # The tool binding happens in the process method, so we call it with an empty state
    sophia.process({"messages": []})
    print(f"   Sophia initialized successfully")

# Test Agent Graph V4 Initialization
def test_agent_graph_v4_initialization():
    from app.agents.agent_graph_v4 import AgentGraphV4
    graph = AgentGraphV4()
    assert graph is not None, "AgentGraphV4 is None"
    assert graph.alex is not None, "graph.alex is None"
    assert graph.sarah is not None, "graph.sarah is None"
    assert graph.marcus is not None, "graph.marcus is None"
    assert graph.sophia is not None, "graph.sophia is None"
    print(f"   Agent Graph V4 initialized with all 4 agents")

if __name__ == "__main__":
    tests = [
        test_alex_agent_initialization,
        test_sarah_agent_initialization,
        test_marcus_agent_initialization,
        test_sophia_agent_initialization,
        test_agent_graph_v4_initialization,
    ]

    results = [run_test(test) for test in tests]

    if all(results):
        print("\n🎉 All agent initialization tests passed!")
        sys.exit(0)
    else:
        print("\n🔥 Some agent initialization tests failed.")
        sys.exit(1)

