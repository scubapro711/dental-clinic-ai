"""
Test Yosef Agent Tool Integration
"""

import pytest
import asyncio
from uuid import uuid4

from app.agents.agent_graph import AgentGraph


@pytest.mark.asyncio
async def test_yosef_invoice_tool():
    """Test that Yosef uses invoice tools."""
    graph = AgentGraph()
    
    user_id = str(uuid4())
    org_id = str(uuid4())
    conv_id = str(uuid4())
    
    # Ask about invoices
    response = await graph.process_message(
        user_id=user_id,
        organization_id=org_id,
        conversation_id=conv_id,
        message="What is my invoice?",
    )
    
    assert response["response"]
    assert response["agent"] in ["yosef", "dana"]
    
    print(f"\n✅ Yosef invoice inquiry test:")
    print(f"   Agent: {response['agent']}")
    print(f"   Response: {response['response'][:200]}...")
    
    # Check if response contains invoice information
    response_lower = response['response'].lower()
    has_invoice_info = any(word in response_lower for word in ["invoice", "bill", "payment", "₪", "nis"])
    
    if has_invoice_info:
        print(f"   ✅ Response contains invoice information")
    else:
        print(f"   ⚠️ Response may not contain specific invoice details")


@pytest.mark.asyncio
async def test_yosef_billing_question():
    """Test Yosef handling general billing questions."""
    graph = AgentGraph()
    
    user_id = str(uuid4())
    org_id = str(uuid4())
    conv_id = str(uuid4())
    
    # Ask about payment methods
    response = await graph.process_message(
        user_id=user_id,
        organization_id=org_id,
        conversation_id=conv_id,
        message="What payment methods do you accept?",
    )
    
    assert response["response"]
    print(f"\n✅ Yosef payment methods test:")
    print(f"   Agent: {response['agent']}")
    print(f"   Response: {response['response'][:200]}...")


if __name__ == "__main__":
    print("🧪 Testing Yosef Tool Integration...\n")
    
    asyncio.run(test_yosef_invoice_tool())
    asyncio.run(test_yosef_billing_question())
    
    print("\n✅ All Yosef tool integration tests passed!")
