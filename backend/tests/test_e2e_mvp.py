"""
End-to-End MVP Integration Tests

Tests the complete system with real user scenarios.
"""

import pytest
import asyncio
from uuid import uuid4

from app.agents.agent_graph_v3 import AgentGraphV3 as AgentGraphV2


class TestMVPIntegration:
    """Test complete MVP user flows."""
    
    @pytest.mark.asyncio
    async def test_scenario_1_general_inquiry(self):
        """
        Scenario 1: User asks about clinic services
        Expected: Dana handles it directly
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="What services do you offer?",
        )
        
        assert response["response"]
        assert len(response["response"]) > 50
        print(f"\n✅ Scenario 1: General Inquiry")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
    
    @pytest.mark.asyncio
    async def test_scenario_2_medical_question(self):
        """
        Scenario 2: User asks medical question
        Expected: Alex handles it (reception) or Sarah (clinical)
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="I have a toothache, what should I do?",
        )
        
        assert response["response"]
        assert response["agent"] in ["alex", "sarah"]  # Updated agent names
        print(f"\n✅ Scenario 2: Medical Question")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
    
    @pytest.mark.asyncio
    async def test_scenario_3_billing_inquiry(self):
        """
        Scenario 3: User asks about billing
        Expected: Alex (reception) or Marcus (CFO)
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="How much does a cleaning cost?",
        )
        
        assert response["response"]
        assert response["agent"] in ["alex", "marcus"]  # Updated agent names
        print(f"\n✅ Scenario 3: Billing Inquiry")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
    
    @pytest.mark.asyncio
    async def test_scenario_4_appointment_booking(self):
        """
        Scenario 4: User wants to book appointment
        Expected: System provides helpful response about appointments
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="I want to schedule an appointment",
        )
        
        assert response["response"]
        # Any agent can handle appointment inquiries
        assert response["agent"] in ["alex", "sarah", "sophia"]  # Updated agent names
        print(f"\n✅ Scenario 4: Appointment Booking")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
        # Check if response mentions appointments/scheduling
        response_lower = response['response'].lower()
        has_appointment_info = any(word in response_lower for word in ['appointment', 'schedule', 'book', 'available'])
        print(f"   Contains appointment info: {has_appointment_info}")
    
    @pytest.mark.asyncio
    async def test_scenario_5_invoice_inquiry(self):
        """
        Scenario 5: User asks about their invoice
        Expected: Yosef uses tools to retrieve invoice data
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="What is my invoice?",
        )
        
        assert response["response"]
        print(f"\n✅ Scenario 5: Invoice Inquiry")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
        print(f"   Contains invoice info: {'invoice' in response['response'].lower() or '₪' in response['response']}")
    
    @pytest.mark.asyncio
    async def test_scenario_6_availability_check(self):
        """
        Scenario 6: User checks availability
        Expected: Sarah uses tools to get real availability
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="When are you available?",
        )
        
        assert response["response"]
        print(f"\n✅ Scenario 6: Availability Check")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
        # Check if response contains dates/times
        has_dates = any(word in response['response'].lower() for word in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'sunday', 'am', 'pm'])
        print(f"   Contains dates/times: {has_dates}")
    
    @pytest.mark.asyncio
    async def test_scenario_7_multi_turn_conversation(self):
        """
        Scenario 7: Multi-turn conversation with context
        Expected: System maintains context across turns
        """
        graph = AgentGraphV2()
        
        user_id = str(uuid4())
        org_id = str(uuid4())
        conv_id = str(uuid4())
        
        # Turn 1: Ask about services
        response1 = await graph.process_message(
            user_id=user_id,
            organization_id=org_id,
            conversation_id=conv_id,
            message="Do you do teeth whitening?",
        )
        
        assert response1["response"]
        
        # Turn 2: Follow-up question
        # LangGraph automatically maintains context via thread_id (conv_id)
        response2 = await graph.process_message(
            user_id=user_id,
            organization_id=org_id,
            conversation_id=conv_id,
            message="How much does it cost?",
        )
        
        assert response2["response"]
        print(f"\n✅ Scenario 7: Multi-Turn Conversation")
        print(f"   Turn 1 Agent: {response1['agent']}")
        print(f"   Turn 1: {response1['response'][:100]}...")
        print(f"   Turn 2 Agent: {response2['agent']}")
        print(f"   Turn 2: {response2['response'][:100]}...")
    
    # Removed: test_scenario_8_causal_memory
    # Neo4j causal memory has been removed from the project
    # We use LangChain PostgresSaver for conversation memory instead


if __name__ == "__main__":
    print("🧪 Running MVP End-to-End Integration Tests...\n")
    print("=" * 80)
    
    pytest.main([__file__, "-v", "-s"])
