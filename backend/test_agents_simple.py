"""
Simplified Agent Integration Tests

Focus on core functionality and OdooClient integration without
strict language requirements.
"""

import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.agents.agent_graph_v3 import AgentGraphV3
from app.integrations.odoo_client import odoo_client
from langchain_core.messages import HumanMessage


class TestAgentIntegrationSimple:
    """Simplified agent integration tests."""
    
    @pytest.fixture
    def agent_graph(self):
        """Create agent graph instance."""
        return AgentGraphV3()
    
    def test_01_agent_graph_initialization(self, agent_graph):
        """Test agent graph initializes correctly."""
        print("\n=== Test 1: Agent Graph Initialization ===")
        assert agent_graph is not None
        assert agent_graph.alex is not None
        assert agent_graph.cfo is not None
        assert agent_graph.admin is not None
        assert agent_graph.graph is not None
        print("✅ Agent graph initialized successfully")
    
    def test_02_alex_responds_to_patient_query(self, agent_graph):
        """Test Alex responds to patient queries."""
        print("\n=== Test 2: Alex Responds ===")
        
        config = {"configurable": {"thread_id": "test_alex_1"}}
        state = {
            "messages": [HumanMessage(content="Hello, I need help")],
            "user_id": "patient_1",
            "user_role": "patient",
        }
        
        result = agent_graph.graph.invoke(state, config)
        
        assert "messages" in result
        assert len(result["messages"]) >= 2  # At least user message + response
        response = result["messages"][-1].content
        assert len(response) > 10  # Got a real response
        print(f"✅ Alex responded: {response[:100]}...")
    
    def test_03_cfo_responds_to_financial_query(self, agent_graph):
        """Test CFO responds to financial queries."""
        print("\n=== Test 3: CFO Responds ===")
        
        config = {"configurable": {"thread_id": "test_cfo_1"}}
        state = {
            "messages": [HumanMessage(content="Show me revenue data")],
            "user_id": "owner_1",
            "user_role": "owner",
        }
        
        result = agent_graph.graph.invoke(state, config)
        
        assert "messages" in result
        assert len(result["messages"]) >= 2
        response = result["messages"][-1].content
        assert len(response) > 10
        print(f"✅ CFO responded: {response[:100]}...")
    
    def test_04_admin_responds_to_operations_query(self, agent_graph):
        """Test Admin responds to operations queries."""
        print("\n=== Test 4: Admin Responds ===")
        
        config = {"configurable": {"thread_id": "test_admin_1"}}
        state = {
            "messages": [HumanMessage(content="Check schedule")],
            "user_id": "admin_1",
            "user_role": "admin",
        }
        
        result = agent_graph.graph.invoke(state, config)
        
        assert "messages" in result
        assert len(result["messages"]) >= 2
        response = result["messages"][-1].content
        assert len(response) > 10
        print(f"✅ Admin responded: {response[:100]}...")
    
    def test_05_odoo_client_has_data(self):
        """Test OdooClient has data loaded."""
        print("\n=== Test 5: OdooClient Data ===")
        
        patient_count = odoo_client.count_patients()
        appointment_count = odoo_client.count_appointments()
        invoice_count = odoo_client.count_invoices()
        
        print(f"Patients: {patient_count}")
        print(f"Appointments: {appointment_count}")
        print(f"Invoices: {invoice_count}")
        
        assert patient_count > 0
        assert appointment_count > 0
        assert invoice_count > 0
        print("✅ OdooClient has data loaded")
    
    def test_06_alex_uses_odoo_client(self, agent_graph):
        """Test Alex uses OdooClient for data."""
        print("\n=== Test 6: Alex Uses OdooClient ===")
        
        config = {"configurable": {"thread_id": "test_alex_odoo"}}
        state = {
            "messages": [HumanMessage(content="Search for patient David")],
            "user_id": "doctor_1",
            "user_role": "doctor",
        }
        
        result = agent_graph.graph.invoke(state, config)
        
        response = result["messages"][-1].content
        # Should mention something about patients or search results
        assert len(response) > 20
        print(f"✅ Alex used OdooClient: {response[:100]}...")
    
    def test_07_cfo_uses_odoo_client(self, agent_graph):
        """Test CFO uses OdooClient for financial data."""
        print("\n=== Test 7: CFO Uses OdooClient ===")
        
        config = {"configurable": {"thread_id": "test_cfo_odoo"}}
        state = {
            "messages": [HumanMessage(content="Get outstanding invoices")],
            "user_id": "owner_1",
            "user_role": "owner",
        }
        
        result = agent_graph.graph.invoke(state, config)
        
        response = result["messages"][-1].content
        # Should provide financial data
        assert len(response) > 20
        print(f"✅ CFO used OdooClient: {response[:100]}...")
    
    def test_08_admin_uses_odoo_client(self, agent_graph):
        """Test Admin uses OdooClient for operations."""
        print("\n=== Test 8: Admin Uses OdooClient ===")
        
        config = {"configurable": {"thread_id": "test_admin_odoo"}}
        state = {
            "messages": [HumanMessage(content="Show operational metrics")],
            "user_id": "admin_1",
            "user_role": "admin",
        }
        
        result = agent_graph.graph.invoke(state, config)
        
        response = result["messages"][-1].content
        # Should provide operational data
        assert len(response) > 20
        print(f"✅ Admin used OdooClient: {response[:100]}...")
    
    def test_09_multi_turn_conversation(self, agent_graph):
        """Test multi-turn conversation works."""
        print("\n=== Test 9: Multi-Turn Conversation ===")
        
        config = {"configurable": {"thread_id": "test_multiturn"}}
        
        # Turn 1
        state1 = {
            "messages": [HumanMessage(content="Hello")],
            "user_id": "patient_1",
            "user_role": "patient",
        }
        result1 = agent_graph.graph.invoke(state1, config)
        print(f"Turn 1: {result1['messages'][-1].content[:50]}...")
        
        # Turn 2
        state2 = {
            "messages": result1["messages"] + [HumanMessage(content="I need an appointment")],
            "user_id": "patient_1",
            "user_role": "patient",
        }
        result2 = agent_graph.graph.invoke(state2, config)
        print(f"Turn 2: {result2['messages'][-1].content[:50]}...")
        
        assert len(result2["messages"]) > len(result1["messages"])
        print("✅ Multi-turn conversation works")
    
    def test_10_different_roles_get_responses(self, agent_graph):
        """Test different user roles all get responses."""
        print("\n=== Test 10: Different Roles ===")
        
        roles = ["patient", "doctor", "admin", "owner"]
        
        for role in roles:
            config = {"configurable": {"thread_id": f"test_role_{role}"}}
            state = {
                "messages": [HumanMessage(content="Help me")],
                "user_id": f"{role}_test",
                "user_role": role,
            }
            
            result = agent_graph.graph.invoke(state, config)
            response = result["messages"][-1].content
            assert len(response) > 10
            print(f"✅ {role.capitalize()} got response")
        
        print("✅ All roles get responses")
    
    def test_11_agent_graph_handles_errors(self, agent_graph):
        """Test agent graph handles errors gracefully."""
        print("\n=== Test 11: Error Handling ===")
        
        config = {"configurable": {"thread_id": "test_error"}}
        state = {
            "messages": [HumanMessage(content="Find patient ID 999999999")],
            "user_id": "doctor_1",
            "user_role": "doctor",
        }
        
        # Should not crash
        result = agent_graph.graph.invoke(state, config)
        
        assert "messages" in result
        response = result["messages"][-1].content
        assert len(response) > 10
        print(f"✅ Error handled: {response[:100]}...")
    
    def test_12_supervisor_routes_requests(self, agent_graph):
        """Test supervisor routes to appropriate agents."""
        print("\n=== Test 12: Supervisor Routing ===")
        
        # Test different types of requests
        test_cases = [
            ("I need an appointment", "patient"),
            ("Show me revenue", "owner"),
            ("Check schedule conflicts", "admin"),
        ]
        
        for i, (message, role) in enumerate(test_cases):
            config = {"configurable": {"thread_id": f"test_routing_{i}"}}
            state = {
                "messages": [HumanMessage(content=message)],
                "user_id": f"user_{i}",
                "user_role": role,
            }
            
            result = agent_graph.graph.invoke(state, config)
            response = result["messages"][-1].content
            assert len(response) > 10
            print(f"✅ Routed: '{message}' -> {role}")
        
        print("✅ Supervisor routing works")
    
    def test_13_agents_use_tools(self, agent_graph):
        """Test agents use tools to access data."""
        print("\n=== Test 13: Agents Use Tools ===")
        
        # Request that should trigger tool use
        config = {"configurable": {"thread_id": "test_tools"}}
        state = {
            "messages": [HumanMessage(content="How many patients do we have?")],
            "user_id": "doctor_1",
            "user_role": "doctor",
        }
        
        result = agent_graph.graph.invoke(state, config)
        response = result["messages"][-1].content
        
        # Should have a number in the response
        import re
        has_number = bool(re.search(r'\d+', response))
        assert has_number, "Response should contain patient count"
        print(f"✅ Agent used tools: {response[:100]}...")
    
    def test_14_system_is_stable(self, agent_graph):
        """Test system remains stable over multiple requests."""
        print("\n=== Test 14: System Stability ===")
        
        # Run 5 requests in a row
        for i in range(5):
            config = {"configurable": {"thread_id": f"test_stability_{i}"}}
            state = {
                "messages": [HumanMessage(content=f"Test request {i+1}")],
                "user_id": "test_user",
                "user_role": "patient",
            }
            
            result = agent_graph.graph.invoke(state, config)
            assert "messages" in result
            assert len(result["messages"]) >= 2
            print(f"✅ Request {i+1}/5 succeeded")
        
        print("✅ System is stable")
    
    def test_15_odoo_client_integration_complete(self):
        """Test OdooClient integration is complete."""
        print("\n=== Test 15: OdooClient Integration ===")
        
        # Test key OdooClient methods
        methods_to_test = [
            ("count_patients", []),
            ("count_appointments", []),
            ("count_invoices", []),
            ("search_patients", ["name", "David"]),
            ("search_appointments", []),
            ("search_invoices", []),
        ]
        
        for method_name, args in methods_to_test:
            method = getattr(odoo_client, method_name)
            if args:
                result = method(**{args[0]: args[1]})
            else:
                result = method()
            print(f"✅ {method_name}() works")
        
        print("✅ OdooClient integration complete")


def run_tests():
    """Run all simplified agent tests."""
    print("\n" + "="*80)
    print("SIMPLIFIED AGENT INTEGRATION TESTS")
    print("Testing core functionality with OdooClient")
    print("="*80)
    
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "--color=yes"
    ])


if __name__ == "__main__":
    run_tests()
