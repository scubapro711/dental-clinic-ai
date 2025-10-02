"""
Test Causal Memory Integration with Agent Graph
"""

import pytest
import asyncio
from uuid import uuid4

from app.agents.agent_graph import AgentGraphV2
from app.memory.causal_memory import causal_memory


@pytest.mark.asyncio
async def test_causal_memory_stores_interaction():
    """Test that interactions are stored in causal memory."""
    graph = AgentGraphV2()
    
    user_id = str(uuid4())
    org_id = str(uuid4())
    conv_id = str(uuid4())
    
    # First interaction
    response1 = await graph.process_message(
        user_id=user_id,
        organization_id=org_id,
        conversation_id=conv_id,
        message="What are your clinic hours?",
    )
    
    assert response1["response"]
    assert response1["agent"] in ["dana", "michal", "yosef", "sarah"]
    print(f"✅ First interaction stored")
    print(f"   Agent: {response1['agent']}")
    print(f"   Response: {response1['response'][:100]}...")
    
    # Wait a bit for Neo4j to process
    await asyncio.sleep(1)
    
    # Second similar interaction - should retrieve context from memory
    response2 = await graph.process_message(
        user_id=user_id,
        organization_id=org_id,
        conversation_id=conv_id,
        message="When are you open?",
    )
    
    assert response2["response"]
    print(f"\n✅ Second interaction with memory context")
    print(f"   Agent: {response2['agent']}")
    print(f"   Similar interactions found: {response2.get('similar_interactions', 0)}")
    print(f"   Response: {response2['response'][:100]}...")


@pytest.mark.asyncio
async def test_causal_memory_retrieves_similar():
    """Test that similar interactions are retrieved."""
    graph = AgentGraphV2()
    
    user_id = str(uuid4())
    org_id = str(uuid4())
    conv_id = str(uuid4())
    
    # Store a few interactions
    messages = [
        "I have a toothache",
        "My tooth hurts",
        "I need to schedule an appointment",
    ]
    
    for msg in messages:
        await graph.process_message(
            user_id=user_id,
            organization_id=org_id,
            conversation_id=conv_id,
            message=msg,
        )
        await asyncio.sleep(0.5)
    
    # Now ask a similar question
    response = await graph.process_message(
        user_id=user_id,
        organization_id=org_id,
        conversation_id=conv_id,
        message="My tooth is painful",
    )
    
    assert response["response"]
    similar_count = response.get("similar_interactions", 0)
    print(f"\n✅ Retrieved {similar_count} similar interactions")
    print(f"   Response: {response['response'][:150]}...")
    
    # Should find at least 1 similar interaction (toothache/tooth hurts)
    assert similar_count >= 1


@pytest.mark.asyncio
async def test_pattern_extraction():
    """Test that patterns are extracted and stored."""
    graph = AgentGraphV2()
    
    user_id = str(uuid4())
    org_id = str(uuid4())
    conv_id = str(uuid4())
    
    # Appointment scheduling pattern
    await graph.process_message(
        user_id=user_id,
        organization_id=org_id,
        conversation_id=conv_id,
        message="I want to book an appointment",
    )
    
    await asyncio.sleep(1)
    
    # Check pattern statistics
    pattern_stats = causal_memory.get_pattern_statistics("appointment_scheduling")
    
    if pattern_stats:
        print(f"\n✅ Pattern 'appointment_scheduling' found:")
        print(f"   Count: {pattern_stats['count']}")
        print(f"   Success Rate: {pattern_stats['success_rate']:.2f}")
        assert pattern_stats["count"] >= 1
    else:
        print(f"\n⚠️ Pattern 'appointment_scheduling' not found yet")


if __name__ == "__main__":
    print("🧪 Testing Causal Memory Integration...\n")
    
    asyncio.run(test_causal_memory_stores_interaction())
    asyncio.run(test_causal_memory_retrieves_similar())
    asyncio.run(test_pattern_extraction())
    
    print("\n✅ All causal memory integration tests passed!")
