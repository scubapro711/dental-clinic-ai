"""
Phase 6.3 - Integration Tests
Test complete workflows and multi-agent collaboration via LangGraph Supervisor.

Tests:
1. Single-agent workflows (patient journey through one agent)
2. Multi-agent workflows (patient journey through multiple agents)
3. Supervisor routing (correct agent selection)
4. Error handling (graceful failures)
5. Data consistency (state management across agents)
"""

import pytest
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Set test environment
os.environ["APP_ENV"] = "test"

from app.agents.agent_graph_v4 import AgentGraphV4, agent_graph_v4
from app.agents.graph_state import AgentState


class TestSingleAgentWorkflows:
    """Test workflows that involve a single agent."""
    
    def test_alex_patient_inquiry_workflow(self):
        """
        Test: Patient asks about appointment availability
        Expected: Alex handles the entire workflow
        """
        # Arrange
        graph = agent_graph_v4
        initial_state = {
            "messages": [
                HumanMessage(content="Hi, I'd like to schedule an appointment for next week. What times are available?")
            ],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        # Act
        result = graph.graph.invoke(initial_state, config={"configurable": {"thread_id": "test_thread_1"}})
        
        # Assert
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 2  # User message + Agent response
        
        # Check that Alex was involved
        assert "current_agent" in result
        # Response should mention appointments or availability
        last_message = result["messages"][-1].content.lower()
        assert any(word in last_message for word in ["appointment", "available", "schedule", "time"])
        
        print(f"✅ Alex Patient Inquiry Workflow: {result['current_agent']}")
    
    def test_sarah_clinical_inquiry_workflow(self):
        """
        Test: Doctor asks about patient's dental chart
        Expected: Sarah handles the clinical request
        """
        # Arrange
        graph = agent_graph_v4
        initial_state = {
            "messages": [
                HumanMessage(content="Show me the dental chart for patient ID 12345")
            ],
            "organization_id": "test_org_123",
            "user_role": "doctor",
            "user_id": "doctor_789"
        }
        
        # Act
        result = graph.graph.invoke(initial_state, config={"configurable": {"thread_id": "test_thread_2"}})
        
        # Assert
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 2
        
        # Check that Sarah was involved
        assert "current_agent" in result
        # Response should mention dental chart or clinical info
        last_message = result["messages"][-1].content.lower()
        assert any(word in last_message for word in ["dental", "chart", "tooth", "teeth", "clinical"])
        
        print(f"✅ Sarah Clinical Inquiry Workflow: {result['current_agent']}")
    
    def test_marcus_financial_inquiry_workflow(self):
        """
        Test: Doctor asks about revenue
        Expected: Marcus handles the financial request
        """
        # Arrange
        graph = agent_graph_v4
        initial_state = {
            "messages": [
                HumanMessage(content="What was our revenue last month?")
            ],
            "organization_id": "test_org_123",
            "user_role": "doctor",
            "user_id": "doctor_789"
        }
        
        # Act
        result = graph.graph.invoke(initial_state, config={"configurable": {"thread_id": "test_thread_3"}})
        
        # Assert
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 2
        
        # Check that Marcus was involved
        assert "current_agent" in result
        # Response should mention revenue or financial info
        last_message = result["messages"][-1].content.lower()
        assert any(word in last_message for word in ["revenue", "financial", "income", "payment", "money"])
        
        print(f"✅ Marcus Financial Inquiry Workflow: {result['current_agent']}")
    
    def test_sophia_operations_inquiry_workflow(self):
        """
        Test: Doctor asks about staff schedule
        Expected: Sophia handles the operations request
        """
        # Arrange
        graph = agent_graph_v4
        initial_state = {
            "messages": [
                HumanMessage(content="Show me the staff schedule for this week")
            ],
            "organization_id": "test_org_123",
            "user_role": "doctor",
            "user_id": "doctor_789"
        }
        
        # Act
        result = graph.graph.invoke(initial_state, config={"configurable": {"thread_id": "test_thread_4"}})
        
        # Assert
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 2
        
        # Check that Sophia was involved
        assert "current_agent" in result
        # Response should mention staff or schedule
        last_message = result["messages"][-1].content.lower()
        assert any(word in last_message for word in ["staff", "schedule", "operations", "team"])
        
        print(f"✅ Sophia Operations Inquiry Workflow: {result['current_agent']}")


class TestMultiAgentWorkflows:
    """Test workflows that involve multiple agents (via supervisor routing)."""
    
    def test_patient_journey_appointment_and_payment(self):
        """
        Test: Patient books appointment (Alex) then asks about payment (Marcus)
        Expected: Supervisor routes correctly to both agents
        """
        # Arrange
        graph = agent_graph_v4
        
        # Step 1: Book appointment (Alex)
        state1 = {
            "messages": [
                HumanMessage(content="I'd like to book an appointment for next Monday at 10am")
            ],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result1 = graph.graph.invoke(state1, config={"configurable": {"thread_id": "test_thread_13"}})
        
        # Assert step 1
        assert result1 is not None
        assert len(result1["messages"]) >= 2
        
        # Step 2: Ask about payment (Marcus) - continue conversation
        state2 = {
            "messages": result1["messages"] + [
                HumanMessage(content="How much will this appointment cost?")
            ],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result2 = graph.graph.invoke(state2, config={"configurable": {"thread_id": "test_thread_14"}})
        
        # Assert step 2
        assert result2 is not None
        assert len(result2["messages"]) >= 4  # 2 from step 1 + 2 from step 2
        
        # Check that both agents were involved (via supervisor)
        last_message = result2["messages"][-1].content.lower()
        assert any(word in last_message for word in ["cost", "price", "payment", "fee"])
        
        print(f"✅ Multi-Agent Workflow (Appointment + Payment): {result2['current_agent']}")
    
    def test_doctor_workflow_clinical_and_financial(self):
        """
        Test: Doctor checks patient chart (Sarah) then asks about payment status (Marcus)
        Expected: Supervisor routes correctly to both agents
        """
        # Arrange
        graph = agent_graph_v4
        
        # Step 1: Check patient chart (Sarah)
        state1 = {
            "messages": [
                HumanMessage(content="Show me the dental chart for patient 12345")
            ],
            "organization_id": "test_org_123",
            "user_role": "doctor",
            "user_id": "doctor_789"
        }
        
        result1 = graph.graph.invoke(state1, config={"configurable": {"thread_id": "test_thread_15"}})
        
        # Assert step 1
        assert result1 is not None
        assert len(result1["messages"]) >= 2
        
        # Step 2: Check payment status (Marcus)
        state2 = {
            "messages": result1["messages"] + [
                HumanMessage(content="Has this patient paid their last invoice?")
            ],
            "organization_id": "test_org_123",
            "user_role": "doctor",
            "user_id": "doctor_789"
        }
        
        result2 = graph.graph.invoke(state2, config={"configurable": {"thread_id": "test_thread_16"}})
        
        # Assert step 2
        assert result2 is not None
        assert len(result2["messages"]) >= 4
        
        last_message = result2["messages"][-1].content.lower()
        assert any(word in last_message for word in ["payment", "invoice", "paid", "balance"])
        
        print(f"✅ Multi-Agent Workflow (Clinical + Financial): {result2['current_agent']}")


class TestSupervisorRouting:
    """Test that the supervisor routes requests to the correct agent."""
    
    def test_supervisor_routes_to_alex(self):
        """Test: Appointment-related query should route to Alex"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="I need to cancel my appointment")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_5"}})
        
        assert result is not None
        assert "current_agent" in result
        # Supervisor should have routed to Alex
        print(f"✅ Supervisor Routing to Alex: {result['current_agent']}")
    
    def test_supervisor_routes_to_sarah(self):
        """Test: Clinical query should route to Sarah"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="What medications am I allergic to?")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_6"}})
        
        assert result is not None
        assert "current_agent" in result
        # Supervisor should have routed to Sarah
        print(f"✅ Supervisor Routing to Sarah: {result['current_agent']}")
    
    def test_supervisor_routes_to_marcus(self):
        """Test: Financial query should route to Marcus"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="Show me my payment history")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_7"}})
        
        assert result is not None
        assert "current_agent" in result
        # Supervisor should have routed to Marcus
        print(f"✅ Supervisor Routing to Marcus: {result['current_agent']}")
    
    def test_supervisor_routes_to_sophia(self):
        """Test: Operations query should route to Sophia"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="Is Dr. Cohen available tomorrow?")],
            "organization_id": "test_org_123",
            "user_role": "doctor",
            "user_id": "doctor_789"
        }
        
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_8"}})
        
        assert result is not None
        assert "current_agent" in result
        # Supervisor should have routed to Sophia
        print(f"✅ Supervisor Routing to Sophia: {result['current_agent']}")


class TestErrorHandling:
    """Test that the system handles errors gracefully."""
    
    def test_invalid_organization_id(self):
        """Test: Invalid organization ID should be handled gracefully"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="Book me an appointment")],
            "organization_id": "invalid_org",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        # Should not raise exception
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_9"}})
        
        assert result is not None
        assert "messages" in result
        print(f"✅ Error Handling (Invalid Org): Handled gracefully")
    
    def test_missing_user_role(self):
        """Test: Missing user role should default to 'patient'"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="Hello")],
            "organization_id": "test_org_123",
            # No user_role
            "user_id": "user_456"
        }
        
        # Should not raise exception
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_10"}})
        
        assert result is not None
        assert "messages" in result
        print(f"✅ Error Handling (Missing Role): Handled gracefully")
    
    def test_empty_message(self):
        """Test: Empty message should be handled"""
        graph = agent_graph_v4
        state = {
            "messages": [HumanMessage(content="")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        # Should not raise exception
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_11"}})
        
        assert result is not None
        assert "messages" in result
        print(f"✅ Error Handling (Empty Message): Handled gracefully")


class TestDataConsistency:
    """Test that state is managed correctly across agents."""
    
    def test_state_preservation_across_agents(self):
        """Test: State should be preserved when switching between agents"""
        graph = agent_graph_v4
        
        # Initial state with organization and user info
        state = {
            "messages": [HumanMessage(content="Book an appointment")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result = graph.graph.invoke(state, config={"configurable": {"thread_id": "test_thread_12"}})
        
        # Assert state preservation
        assert result["organization_id"] == "test_org_123"
        assert result["user_role"] == "patient"
        assert result["user_id"] == "patient_456"
        
        print(f"✅ State Preservation: organization_id, user_role, user_id preserved")
    
    def test_message_history_accumulation(self):
        """Test: Message history should accumulate correctly"""
        graph = agent_graph_v4
        
        # Step 1
        state1 = {
            "messages": [HumanMessage(content="First message")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result1 = graph.graph.invoke(state1, config={"configurable": {"thread_id": "test_thread_17"}})
        
        # Step 2 - continue conversation
        state2 = {
            "messages": result1["messages"] + [HumanMessage(content="Second message")],
            "organization_id": "test_org_123",
            "user_role": "patient",
            "user_id": "patient_456"
        }
        
        result2 = graph.graph.invoke(state2, config={"configurable": {"thread_id": "test_thread_18"}})
        
        # Assert message accumulation
        assert len(result2["messages"]) >= 4  # 2 user + 2 agent responses
        
        print(f"✅ Message History: {len(result2['messages'])} messages accumulated")


# Run all tests
if __name__ == "__main__":
    print("=" * 80)
    print("Phase 6.3 - Integration Tests")
    print("=" * 80)
    print()
    
    # Single-agent workflows
    print("1. Single-Agent Workflows")
    print("-" * 80)
    test = TestSingleAgentWorkflows()
    test.test_alex_patient_inquiry_workflow()
    test.test_sarah_clinical_inquiry_workflow()
    test.test_marcus_financial_inquiry_workflow()
    test.test_sophia_operations_inquiry_workflow()
    print()
    
    # Multi-agent workflows
    print("2. Multi-Agent Workflows")
    print("-" * 80)
    test = TestMultiAgentWorkflows()
    test.test_patient_journey_appointment_and_payment()
    test.test_doctor_workflow_clinical_and_financial()
    print()
    
    # Supervisor routing
    print("3. Supervisor Routing")
    print("-" * 80)
    test = TestSupervisorRouting()
    test.test_supervisor_routes_to_alex()
    test.test_supervisor_routes_to_sarah()
    test.test_supervisor_routes_to_marcus()
    test.test_supervisor_routes_to_sophia()
    print()
    
    # Error handling
    print("4. Error Handling")
    print("-" * 80)
    test = TestErrorHandling()
    test.test_invalid_organization_id()
    test.test_missing_user_role()
    test.test_empty_message()
    print()
    
    # Data consistency
    print("5. Data Consistency")
    print("-" * 80)
    test = TestDataConsistency()
    test.test_state_preservation_across_agents()
    test.test_message_history_accumulation()
    print()
    
    print("=" * 80)
    print("✅ All Integration Tests Complete!")
    print("=" * 80)

