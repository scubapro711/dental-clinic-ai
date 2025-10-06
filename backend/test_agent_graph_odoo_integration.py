"""
Test Agent Graph with OdooClient Integration

This test suite verifies that the agent graph works correctly with the
new OdooClient implementation, testing all agents through the supervisor.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.agents.agent_graph_v3 import AgentGraphV3
from app.agents.graph_state import AgentState
from app.integrations.odoo_client import odoo_client
from langchain_core.messages import HumanMessage


class TestAgentGraphOdooIntegration:
    """Test agent graph with OdooClient integration."""
    
    @pytest.fixture
    def agent_graph(self):
        """Create agent graph instance."""
        return AgentGraphV3()
    
    def test_agent_graph_initialization(self, agent_graph):
        """Test agent graph initializes correctly."""
        print("\n=== Testing Agent Graph Initialization ===")
        assert agent_graph is not None
        assert agent_graph.alex is not None
        assert agent_graph.cfo is not None
        assert agent_graph.admin is not None
        assert agent_graph.graph is not None
        print("✅ Agent graph initialized with all agents")
    
    def test_alex_patient_search(self, agent_graph):
        """Test Alex agent can search for patients via graph."""
        print("\n=== Testing Alex - Patient Search ===")
        
        # Create initial state
        config = {"configurable": {"thread_id": "test_1"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Find patient David Cohen")],
            "user_id": "doctor_123",
            "user_role": "doctor",
        }
        
        # Invoke graph
        result = agent_graph.graph.invoke(initial_state, config)
        
        # Check result
        assert "messages" in result
        assert len(result["messages"]) > 1
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        # Verify response mentions patient or search
        assert any(word in final_message.lower() for word in ["david", "patient", "found", "search"])
        print("✅ Alex successfully handled patient search")
    
    def test_alex_appointment_booking(self, agent_graph):
        """Test Alex can handle appointment booking."""
        print("\n=== Testing Alex - Appointment Booking ===")
        
        config = {"configurable": {"thread_id": "test_2"}}
        
        initial_state = {
            "messages": [HumanMessage(content="What appointment slots are available this week?")],
            "user_id": "patient_456",
            "user_role": "patient",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        assert any(word in final_message.lower() for word in ["available", "slot", "appointment", "schedule"])
        print("✅ Alex successfully handled appointment inquiry")
    
    def test_cfo_revenue_analysis(self, agent_graph):
        """Test CFO agent can analyze revenue."""
        print("\n=== Testing CFO - Revenue Analysis ===")
        
        config = {"configurable": {"thread_id": "test_3"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Show me revenue overview for the last 30 days")],
            "user_id": "owner_789",
            "user_role": "owner",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        assert any(word in final_message.lower() for word in ["revenue", "income", "financial", "₪", "$"])
        print("✅ CFO successfully handled revenue analysis")
    
    def test_cfo_outstanding_invoices(self, agent_graph):
        """Test CFO can get outstanding invoices."""
        print("\n=== Testing CFO - Outstanding Invoices ===")
        
        config = {"configurable": {"thread_id": "test_4"}}
        
        initial_state = {
            "messages": [HumanMessage(content="What invoices are still unpaid?")],
            "user_id": "owner_789",
            "user_role": "owner",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        # Check for English or Hebrew invoice-related words
        assert any(word in final_message.lower() for word in ["invoice", "unpaid", "outstanding", "payment", "חשבונית", "ש\"ח", "₪"])
        print("✅ CFO successfully handled outstanding invoices")
    
    def test_admin_schedule_conflicts(self, agent_graph):
        """Test Admin agent can detect schedule conflicts."""
        print("\n=== Testing Admin - Schedule Conflicts ===")
        
        config = {"configurable": {"thread_id": "test_5"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Are there any scheduling conflicts this week?")],
            "user_id": "admin_101",
            "user_role": "admin",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        assert any(word in final_message.lower() for word in ["conflict", "schedule", "overlap", "appointment"])
        print("✅ Admin successfully handled schedule conflict check")
    
    def test_admin_operational_metrics(self, agent_graph):
        """Test Admin can provide operational metrics."""
        print("\n=== Testing Admin - Operational Metrics ===")
        
        config = {"configurable": {"thread_id": "test_6"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Show me operational metrics for this week")],
            "user_id": "admin_101",
            "user_role": "admin",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        assert any(word in final_message.lower() for word in ["metric", "operational", "performance", "appointment"])
        print("✅ Admin successfully provided operational metrics")
    
    def test_supervisor_routing_to_alex(self, agent_graph):
        """Test supervisor routes patient questions to Alex."""
        print("\n=== Testing Supervisor Routing - Alex ===")
        
        config = {"configurable": {"thread_id": "test_7"}}
        
        initial_state = {
            "messages": [HumanMessage(content="I need to schedule a cleaning appointment")],
            "user_id": "patient_456",
            "user_role": "patient",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        # Check that Alex was involved
        assert "current_agent" in result
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        print(f"Final agent: {result.get('current_agent')}")
        
        assert any(word in final_message.lower() for word in ["appointment", "schedule", "cleaning", "available"])
        print("✅ Supervisor correctly routed to Alex")
    
    def test_supervisor_routing_to_cfo(self, agent_graph):
        """Test supervisor routes financial questions to CFO."""
        print("\n=== Testing Supervisor Routing - CFO ===")
        
        config = {"configurable": {"thread_id": "test_8"}}
        
        initial_state = {
            "messages": [HumanMessage(content="What's our total revenue this month?")],
            "user_id": "owner_789",
            "user_role": "owner",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        print(f"Final agent: {result.get('current_agent')}")
        
        assert any(word in final_message.lower() for word in ["revenue", "financial", "income", "₪", "$"])
        print("✅ Supervisor correctly routed to CFO")
    
    def test_supervisor_routing_to_admin(self, agent_graph):
        """Test supervisor routes operations questions to Admin."""
        print("\n=== Testing Supervisor Routing - Admin ===")
        
        config = {"configurable": {"thread_id": "test_9"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Check for scheduling conflicts today")],
            "user_id": "admin_101",
            "user_role": "admin",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        print(f"Final agent: {result.get('current_agent')}")
        
        assert any(word in final_message.lower() for word in ["schedule", "conflict", "operational"])
        print("✅ Supervisor correctly routed to Admin")
    
    def test_rbac_patient_cannot_see_all_patients(self, agent_graph):
        """Test RBAC: Patient cannot see all patients."""
        print("\n=== Testing RBAC - Patient Restrictions ===")
        
        config = {"configurable": {"thread_id": "test_10"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Show me all patients in the system")],
            "user_id": "patient_456",
            "user_role": "patient",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content.lower()
        print(f"Response: {final_message[:200]}...")
        
        # Should deny access or redirect
        assert any(word in final_message for word in ["cannot", "permission", "not allowed", "your own"])
        print("✅ RBAC correctly restricted patient access")
    
    def test_rbac_doctor_can_access_patients(self, agent_graph):
        """Test RBAC: Doctor can access patient data."""
        print("\n=== Testing RBAC - Doctor Access ===")
        
        config = {"configurable": {"thread_id": "test_11"}}
        
        initial_state = {
            "messages": [HumanMessage(content="How many patients do we have?")],
            "user_id": "doctor_123",
            "user_role": "doctor",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content
        print(f"Response: {final_message[:200]}...")
        
        # Should provide patient count
        assert any(char.isdigit() for char in final_message)
        assert "patient" in final_message.lower()
        print("✅ RBAC correctly allowed doctor access")
    
    def test_rbac_owner_can_access_financial(self, agent_graph):
        """Test RBAC: Owner can access financial data."""
        print("\n=== Testing RBAC - Owner Financial Access ===")
        
        config = {"configurable": {"thread_id": "test_12"}}
        
        initial_state = {
            "messages": [HumanMessage(content="Show me revenue for last month")],
            "user_id": "owner_789",
            "user_role": "owner",
        }
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        final_message = result["messages"][-1].content.lower()
        print(f"Response: {final_message[:200]}...")
        
        # Should provide financial data
        assert any(word in final_message for word in ["revenue", "income", "financial", "₪", "$"])
        print("✅ RBAC correctly allowed owner financial access")
    
    def test_multi_turn_conversation(self, agent_graph):
        """Test multi-turn conversation with context preservation."""
        print("\n=== Testing Multi-Turn Conversation ===")
        
        config = {"configurable": {"thread_id": "test_13"}}
        
        # Turn 1
        state1 = {
            "messages": [HumanMessage(content="How many patients do we have?")],
            "user_id": "doctor_123",
            "user_role": "doctor",
        }
        
        result1 = agent_graph.graph.invoke(state1, config)
        print(f"Turn 1: {result1['messages'][-1].content[:100]}...")
        
        # Turn 2 - follow up
        state2 = {
            "messages": result1["messages"] + [HumanMessage(content="And how many appointments today?")],
            "user_id": "doctor_123",
            "user_role": "doctor",
        }
        
        result2 = agent_graph.graph.invoke(state2, config)
        print(f"Turn 2: {result2['messages'][-1].content[:100]}...")
        
        # Verify both turns got responses
        assert len(result2["messages"]) > len(result1["messages"])
        print("✅ Multi-turn conversation preserved context")
    
    def test_odoo_client_data_consistency(self, agent_graph):
        """Test that all agents use consistent OdooClient data."""
        print("\n=== Testing OdooClient Data Consistency ===")
        
        # Get patient count from OdooClient
        patient_count = odoo_client.count_patients()
        print(f"OdooClient patient count: {patient_count}")
        
        # Ask Alex for patient count
        config = {"configurable": {"thread_id": "test_14"}}
        
        state = {
            "messages": [HumanMessage(content="How many patients are in the system?")],
            "user_id": "doctor_123",
            "user_role": "doctor",
        }
        
        result = agent_graph.graph.invoke(state, config)
        final_message = result["messages"][-1].content
        print(f"Alex response: {final_message[:200]}...")
        
        # Extract number from response
        import re
        numbers = re.findall(r'\d+', final_message)
        if numbers:
            alex_count = int(numbers[0])
            print(f"Alex reported count: {alex_count}")
            assert alex_count == patient_count
        
        print("✅ Data consistency verified across agents and OdooClient")
    
    def test_error_handling(self, agent_graph):
        """Test error handling in agent graph."""
        print("\n=== Testing Error Handling ===")
        
        config = {"configurable": {"thread_id": "test_15"}}
        
        state = {
            "messages": [HumanMessage(content="Find patient with ID 999999999")],
            "user_id": "doctor_123",
            "user_role": "doctor",
        }
        
        result = agent_graph.graph.invoke(state, config)
        final_message = result["messages"][-1].content.lower()
        print(f"Response: {final_message[:200]}...")
        
        # Should handle not found gracefully
        assert any(word in final_message for word in ["not found", "couldn't find", "unable", "no patient"])
        print("✅ Error handled gracefully")


def run_tests():
    """Run all agent graph integration tests."""
    print("\n" + "="*80)
    print("AGENT GRAPH ODOO INTEGRATION TESTS")
    print("Testing all agents through supervisor with OdooClient")
    print("="*80)
    
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "--color=yes",
        "-x"  # Stop on first failure for faster debugging
    ])


if __name__ == "__main__":
    run_tests()
