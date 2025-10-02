"""
Quick test for new natural agents (Emma, Lisa, Robert, Jessica)
"""

import asyncio
from uuid import uuid4
from app.agents.agent_graph import AgentGraph


async def test_all_agents():
    """Test all 4 new agents with natural conversations."""
    graph = AgentGraph()
    
    print("🧪 Testing New Natural Agents\n")
    print("=" * 80)
    
    # Test 1: Medical (Lisa)
    print("\n1️⃣ Testing Lisa (Medical) - Toothache")
    print("-" * 80)
    response = await graph.process_message(
        user_id=str(uuid4()),
        organization_id=str(uuid4()),
        conversation_id=str(uuid4()),
        message="Hi, I have a toothache",
    )
    print(f"Agent: {response['agent']}")
    print(f"Response:\n{response['response']}\n")
    
    # Test 2: Billing (Robert)
    print("\n2️⃣ Testing Robert (Billing) - Invoice inquiry")
    print("-" * 80)
    response = await graph.process_message(
        user_id=str(uuid4()),
        organization_id=str(uuid4()),
        conversation_id=str(uuid4()),
        message="What's my invoice?",
    )
    print(f"Agent: {response['agent']}")
    print(f"Response:\n{response['response']}\n")
    
    # Test 3: Scheduling (Jessica)
    print("\n3️⃣ Testing Jessica (Scheduling) - Availability")
    print("-" * 80)
    response = await graph.process_message(
        user_id=str(uuid4()),
        organization_id=str(uuid4()),
        conversation_id=str(uuid4()),
        message="When are you available?",
    )
    print(f"Agent: {response['agent']}")
    print(f"Response:\n{response['response']}\n")
    
    # Test 4: Hebrew (Multi-language)
    print("\n4️⃣ Testing Hebrew - כאב שיניים")
    print("-" * 80)
    response = await graph.process_message(
        user_id=str(uuid4()),
        organization_id=str(uuid4()),
        conversation_id=str(uuid4()),
        message="שלום, יש לי כאב שיניים",
    )
    print(f"Agent: {response['agent']}")
    print(f"Response:\n{response['response']}\n")
    
    # Test 5: General (Emma)
    print("\n5️⃣ Testing Emma (General) - Clinic hours")
    print("-" * 80)
    response = await graph.process_message(
        user_id=str(uuid4()),
        organization_id=str(uuid4()),
        conversation_id=str(uuid4()),
        message="What are your clinic hours?",
    )
    print(f"Agent: {response['agent']}")
    print(f"Response:\n{response['response']}\n")
    
    print("=" * 80)
    print("✅ All agent tests completed!")


if __name__ == "__main__":
    asyncio.run(test_all_agents())
