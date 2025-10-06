"""
Test Alex Agent with OdooClient Integration

This test suite verifies that Alex agent works correctly with the
new OdooClient implementation.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.agents.alex import AlexAgent
from app.agents.graph_state import AgentState
from app.integrations.odoo_client import odoo_client
from langchain_core.messages import HumanMessage


class TestAlexAgentOdoo:
    """Test Alex agent with OdooClient integration."""
    
    @pytest.fixture
    def alex(self):
        """Create Alex agent instance."""
        return AlexAgent()
    
    @pytest.fixture
    def base_state(self):
        """Create base agent state."""
        return AgentState(
            messages=[],
            current_agent="alex",
            next_agent="",
            user_id="test_doctor",
            user_role="doctor",
            suggested_actions=[]
        )
    
    def test_alex_initialization(self, alex):
        """Test Alex agent initializes correctly."""
        print("\n=== Testing Alex Initialization ===")
        assert alex is not None
        assert alex.name == "Alex"
        assert alex.llm is not None
        assert len(alex.tools) > 0
        print(f"✅ Alex initialized with {len(alex.tools)} tools")
    
    def test_alex_search_patient(self, alex, base_state):
        """Test Alex can search for patients."""
        print("\n=== Testing Alex Search Patient ===")
        
        # Create state with user message
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content="Can you find patient David Cohen?")
        ]
        
        # Invoke Alex
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        # Verify response
        assert len(result["messages"]) > len(state["messages"])
        response_content = result["messages"][-1].content.lower()
        assert "david" in response_content or "patient" in response_content
        print("✅ Alex successfully searched for patient")
    
    def test_alex_create_appointment(self, alex, base_state):
        """Test Alex can create appointments."""
        print("\n=== Testing Alex Create Appointment ===")
        
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content="Schedule an appointment for Test Patient, phone +972501234567, on 2025-10-20 at 14:00 for a checkup")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        assert "appointment" in response_content
        print("✅ Alex successfully handled appointment creation")
    
    def test_alex_get_available_slots(self, alex, base_state):
        """Test Alex can get available slots."""
        print("\n=== Testing Alex Get Available Slots ===")
        
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content="What appointment slots are available this week?")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        assert "available" in response_content or "slot" in response_content
        print("✅ Alex successfully retrieved available slots")
    
    def test_alex_patient_appointments(self, alex, base_state):
        """Test Alex can get patient appointments."""
        print("\n=== Testing Alex Get Patient Appointments ===")
        
        # First find a patient
        patient_ids = odoo_client.search_patients(name="David")
        if not patient_ids:
            pytest.skip("No patients found for testing")
        
        patient = odoo_client.get_patient(patient_ids[0])
        
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content=f"Show me appointments for {patient['name']}")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        assert "appointment" in response_content
        print("✅ Alex successfully retrieved patient appointments")
    
    def test_alex_patient_invoices(self, alex, base_state):
        """Test Alex can get patient invoices."""
        print("\n=== Testing Alex Get Patient Invoices ===")
        
        # Find a patient
        patient_ids = odoo_client.search_patients(name="David")
        if not patient_ids:
            pytest.skip("No patients found for testing")
        
        patient = odoo_client.get_patient(patient_ids[0])
        
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content=f"Show me invoices for {patient['name']}")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        assert "invoice" in response_content or "payment" in response_content
        print("✅ Alex successfully retrieved patient invoices")
    
    def test_alex_rbac_patient_role(self, alex):
        """Test Alex respects RBAC for patient role."""
        print("\n=== Testing Alex RBAC - Patient Role ===")
        
        state = AgentState(
            messages=[HumanMessage(content="Show me all patients")],
            current_agent="alex",
            next_agent="",
            user_id="patient_123",
            user_role="patient",
            suggested_actions=[]
        )
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        # Patient should not be able to see all patients
        assert "permission" in response_content or "cannot" in response_content or "not allowed" in response_content
        print("✅ Alex correctly enforced RBAC for patient role")
    
    def test_alex_rbac_doctor_role(self, alex, base_state):
        """Test Alex allows doctor role to access patient data."""
        print("\n=== Testing Alex RBAC - Doctor Role ===")
        
        state = base_state.copy()
        state["user_role"] = "doctor"
        state["messages"] = [
            HumanMessage(content="How many patients do we have?")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        # Doctor should be able to see patient count
        assert "patient" in response_content
        assert any(char.isdigit() for char in response_content)
        print("✅ Alex correctly allowed doctor role access")
    
    def test_alex_tool_usage(self, alex, base_state):
        """Test Alex uses tools correctly."""
        print("\n=== Testing Alex Tool Usage ===")
        
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content="Find patient David and show their appointments")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        # Verify Alex used tools
        assert len(result["messages"]) > len(state["messages"])
        response_content = result["messages"][-1].content
        assert len(response_content) > 0
        print("✅ Alex successfully used tools to complete request")
    
    def test_alex_error_handling(self, alex, base_state):
        """Test Alex handles errors gracefully."""
        print("\n=== Testing Alex Error Handling ===")
        
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content="Find patient with ID 999999999")
        ]
        
        result = alex.invoke(state)
        
        print(f"Alex response: {result['messages'][-1].content[:200]}...")
        
        response_content = result["messages"][-1].content.lower()
        # Should handle not found gracefully
        assert "not found" in response_content or "couldn't find" in response_content or "unable" in response_content
        print("✅ Alex handled error gracefully")
    
    def test_alex_multi_turn_conversation(self, alex, base_state):
        """Test Alex handles multi-turn conversations."""
        print("\n=== Testing Alex Multi-Turn Conversation ===")
        
        # Turn 1
        state = base_state.copy()
        state["messages"] = [
            HumanMessage(content="How many patients do we have?")
        ]
        
        result1 = alex.invoke(state)
        print(f"Turn 1 response: {result1['messages'][-1].content[:100]}...")
        
        # Turn 2 - follow up
        state["messages"] = result1["messages"]
        state["messages"].append(
            HumanMessage(content="And how many appointments?")
        )
        
        result2 = alex.invoke(state)
        print(f"Turn 2 response: {result2['messages'][-1].content[:100]}...")
        
        # Verify both turns got responses
        assert len(result2["messages"]) > len(result1["messages"])
        print("✅ Alex successfully handled multi-turn conversation")


def run_tests():
    """Run all Alex agent tests."""
    print("\n" + "="*80)
    print("ALEX AGENT ODOO INTEGRATION TESTS")
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
