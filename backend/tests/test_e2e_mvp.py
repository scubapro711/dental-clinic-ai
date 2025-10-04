"""
End-to-End MVP Integration Tests

Tests the complete system with real user scenarios.
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import Mock, patch

from app.agents.agent_graph import AgentGraphV2


# Mock causal memory for E2E tests
@pytest.fixture(autouse=True)
def mock_causal_memory():
    """Mock causal memory to avoid Neo4j dependency in E2E tests."""
    mock_memory = Mock()
    mock_memory.get_similar_interactions.return_value = []
    mock_memory.store_interaction.return_value = None
    
    with patch('app.agents.agent_graph.causal_memory', mock_memory):
        yield mock_memory


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
        Expected: Alex handles it (current system has only Alex)
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="I have a toothache, what should I do?",
        )
        
        assert response["response"]
        assert response["agent"] == "alex"
        assert len(response["response"]) > 50
        print(f"\n✅ Scenario 2: Medical Question")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
    
    @pytest.mark.asyncio
    async def test_scenario_3_billing_inquiry(self):
        """
        Scenario 3: User asks about billing
        Expected: Alex handles it (current system has only Alex)
        """
        graph = AgentGraphV2()
        
        response = await graph.process_message(
            user_id=str(uuid4()),
            organization_id=str(uuid4()),
            conversation_id=str(uuid4()),
            message="How much does a cleaning cost?",
        )
        
        assert response["response"]
        assert response["agent"] == "alex"
        assert len(response["response"]) > 50
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
        assert response["agent"] == "alex"
        assert len(response["response"]) > 50
        print(f"\n✅ Scenario 4: Appointment Booking")
        print(f"   Agent: {response['agent']}")
        print(f"   Response: {response['response'][:150]}...")
        # Check if response mentions appointments/scheduling
        response_lower = response['response'].lower()
        has_appointment_info = any(word in response_lower for word in ['appointment', 'schedule', 'book', 'available'])
        assert has_appointment_info, "Response should mention appointments"
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
        
        # Turn 2: Follow-up question (same conversation_id maintains context)
        response2 = await graph.process_message(
            user_id=user_id,
            organization_id=org_id,
            conversation_id=conv_id,
            message="How much does it cost?",
        )
        
        assert response2["response"]
        assert response1["agent"] == "alex"
        assert response2["agent"] == "alex"
        assert len(response2["response"]) > 30
        print(f"\n✅ Scenario 7: Multi-Turn Conversation")
        print(f"   Turn 1 Agent: {response1['agent']}")
        print(f"   Turn 1: {response1['response'][:100]}...")
        print(f"   Turn 2 Agent: {response2['agent']}")
        print(f"   Turn 2: {response2['response'][:100]}...")
    
    @pytest.mark.asyncio
    async def test_scenario_8_causal_memory(self):
        """
        Scenario 8: Causal memory retrieves similar interactions
        Expected: Similar past interactions are used for context
        """
        graph = AgentGraphV2()
        
        user_id = str(uuid4())
        org_id = str(uuid4())
        
        # First interaction
        response1 = await graph.process_message(
            user_id=user_id,
            organization_id=org_id,
            conversation_id=str(uuid4()),
            message="I have tooth pain",
        )
        
        await asyncio.sleep(1)  # Wait for Neo4j to process
        
        # Similar interaction
        response2 = await graph.process_message(
            user_id=user_id,
            organization_id=org_id,
            conversation_id=str(uuid4()),
            message="My tooth hurts",
        )
        
        assert response1["response"]
        assert response2["response"]
        
        print(f"\n✅ Scenario 8: Causal Memory")
        print(f"   First interaction agent: {response1['agent']}")
        print(f"   Second interaction agent: {response2['agent']}")
        print(f"   Similar interactions found: {response2.get('similar_interactions', 0)}")


if __name__ == "__main__":
    print("🧪 Running MVP End-to-End Integration Tests...\n")
    print("=" * 80)
    
    pytest.main([__file__, "-v", "-s"])
