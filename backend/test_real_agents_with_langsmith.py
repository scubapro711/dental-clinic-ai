#!/usr/bin/env python3
"""
Test REAL DentaFlow Agents with LangSmith Tracing

This script tests the actual agent graph with real LangSmith tracing enabled.
"""

import os
import sys
import asyncio
from datetime import datetime

# Set environment variables for LangSmith
# LANGSMITH_API_KEY should be set in environment variables
os.environ["LANGSMITH_PROJECT"] = "dentaflow-agent-eval"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["TESTING"] = "1"

# Add the backend directory to the path
sys.path.insert(0, '/home/ubuntu/backend/backend')

from app.agents.agent_graph_v5 import create_agent_graph
from app.integrations.mock_odoo_realistic import RealisticMockOdooClient

print("=" * 80)
print("TESTING REAL DENTAFLOW AGENTS WITH LANGSMITH TRACING")
print("=" * 80)
print(f"Time: {datetime.now()}")
print(f"LangSmith Project: {os.getenv('LANGSMITH_PROJECT')}")
print(f"Tracing Enabled: {os.getenv('LANGSMITH_TRACING')}")
print("=" * 80)
print()

async def test_alex_patient_registration():
    """Test Alex agent with patient registration workflow."""
    print("=" * 80)
    print("TEST 1: Alex - New Patient Registration")
    print("=" * 80)
    
    try:
        # Create the agent graph
        graph = create_agent_graph()
        
        # Test input
        test_input = {
            "messages": [{
                "role": "user",
                "content": "I want to register a new patient named John Doe, phone +1234567890, email john.doe@example.com"
            }],
            "user_id": "test_receptionist",
            "user_role": "receptionist",
            "organization_id": "test_org"
        }
        
        print(f"Input: {test_input['messages'][0]['content']}")
        print()
        print("⏳ Running agent...")
        
        # Run the agent
        result = await graph.ainvoke(test_input)
        
        print()
        print("✅ Agent completed!")
        print(f"Final messages: {len(result.get('messages', []))}")
        
        # Print last message
        if result.get('messages'):
            last_message = result['messages'][-1]
            print(f"Last message: {last_message.get('content', 'N/A')[:200]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_alex_find_patient():
    """Test Alex agent with patient search workflow."""
    print()
    print("=" * 80)
    print("TEST 2: Alex - Find Existing Patient")
    print("=" * 80)
    
    try:
        graph = create_agent_graph()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "Find patient named Avi Goldstein"
            }],
            "user_id": "test_receptionist",
            "user_role": "receptionist",
            "organization_id": "test_org"
        }
        
        print(f"Input: {test_input['messages'][0]['content']}")
        print()
        print("⏳ Running agent...")
        
        result = await graph.ainvoke(test_input)
        
        print()
        print("✅ Agent completed!")
        
        if result.get('messages'):
            last_message = result['messages'][-1]
            print(f"Last message: {last_message.get('content', 'N/A')[:200]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_alex_get_doctors():
    """Test Alex agent with get doctors workflow."""
    print()
    print("=" * 80)
    print("TEST 3: Alex - Get Available Doctors")
    print("=" * 80)
    
    try:
        graph = create_agent_graph()
        
        test_input = {
            "messages": [{
                "role": "user",
                "content": "Show me all available doctors"
            }],
            "user_id": "test_receptionist",
            "user_role": "receptionist",
            "organization_id": "test_org"
        }
        
        print(f"Input: {test_input['messages'][0]['content']}")
        print()
        print("⏳ Running agent...")
        
        result = await graph.ainvoke(test_input)
        
        print()
        print("✅ Agent completed!")
        
        if result.get('messages'):
            last_message = result['messages'][-1]
            print(f"Last message: {last_message.get('content', 'N/A')[:200]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("Starting agent tests...")
    print()
    
    results = []
    
    # Test Alex agent
    results.append(("Alex - Patient Registration", await test_alex_patient_registration()))
    results.append(("Alex - Find Patient", await test_alex_find_patient()))
    results.append(("Alex - Get Doctors", await test_alex_get_doctors()))
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print()
    print("🔍 Check LangSmith for detailed traces:")
    print("   https://smith.langchain.com/")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
