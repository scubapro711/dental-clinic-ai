#!/usr/bin/env python3
"""
Test Real DentaFlow Agent Graph with LangSmith Tracing

This runs the actual LangGraph agent system with LangSmith tracing enabled.
"""

import os
import asyncio
from datetime import datetime

# Load test environment (but preserve OPENAI_API_KEY)
openai_key = os.getenv('OPENAI_API_KEY')
with open('.env.test') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            if key != 'OPENAI_API_KEY':  # Don't overwrite real API key
                os.environ[key] = value
if openai_key:
    os.environ['OPENAI_API_KEY'] = openai_key

# Set LangSmith environment
# LANGSMITH_API_KEY should be set in environment variables
os.environ["LANGSMITH_PROJECT"] = "dentaflow-agent-eval"
os.environ["LANGSMITH_TRACING"] = "true"

from app.agents.agent_graph_v5 import AgentGraphV5
from langchain_core.messages import HumanMessage

print("=" * 80)
print("TESTING REAL DENTAFLOW AGENT GRAPH WITH LANGSMITH TRACING")
print("=" * 80)
print(f"Time: {datetime.now()}")
print(f"LangSmith Project: {os.getenv('LANGSMITH_PROJECT')}")
print(f"Tracing Enabled: {os.getenv('LANGSMITH_TRACING')}")
print("=" * 80)
print()

async def test_alex_patient_search():
    """Test Alex agent with patient search."""
    print("=" * 80)
    print("TEST 1: Alex - Search for Patient")
    print("=" * 80)
    
    try:
        graph = AgentGraphV5().graph
        
        config = {"configurable": {"thread_id": "test-alex-search"}}
        
        input_state = {
            "messages": [HumanMessage(content="Find patient named Cohen")],
            "user_id": "test_receptionist",
            "user_role": "receptionist",
            "organization_id": "test_org"
        }
        
        print(f"Input: {input_state['messages'][0].content}")
        print()
        print("⏳ Running agent graph...")
        
        result = await graph.ainvoke(input_state, config)
        
        print()
        print("✅ Agent completed!")
        print(f"Messages: {len(result.get('messages', []))}")
        
        if result.get('messages'):
            last_msg = result['messages'][-1]
            content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            print(f"Response: {content[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_alex_get_doctors():
    """Test Alex agent with get doctors."""
    print()
    print("=" * 80)
    print("TEST 2: Alex - Get Available Doctors")
    print("=" * 80)
    
    try:
        graph = AgentGraphV5().graph
        
        config = {"configurable": {"thread_id": "test-alex-doctors"}}
        
        input_state = {
            "messages": [HumanMessage(content="Who are the available doctors?")],
            "user_id": "test_receptionist",
            "user_role": "receptionist",
            "organization_id": "test_org"
        }
        
        print(f"Input: {input_state['messages'][0].content}")
        print()
        print("⏳ Running agent graph...")
        
        result = await graph.ainvoke(input_state, config)
        
        print()
        print("✅ Agent completed!")
        
        if result.get('messages'):
            last_msg = result['messages'][-1]
            content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            print(f"Response: {content[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rbac_patient_access():
    """Test RBAC - patient trying to access data."""
    print()
    print("=" * 80)
    print("TEST 3: RBAC - Patient Access Control")
    print("=" * 80)
    
    try:
        graph = AgentGraphV5().graph
        
        config = {"configurable": {"thread_id": "test-rbac-patient"}}
        
        input_state = {
            "messages": [HumanMessage(content="Show me patient details for ID 999")],
            "user_id": "patient_123",
            "user_role": "patient",
            "organization_id": "test_org"
        }
        
        print(f"Input: {input_state['messages'][0].content}")
        print(f"User Role: {input_state['user_role']}")
        print()
        print("⏳ Running agent graph...")
        
        result = await graph.ainvoke(input_state, config)
        
        print()
        print("✅ Agent completed!")
        
        if result.get('messages'):
            last_msg = result['messages'][-1]
            content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            print(f"Response: {content[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("Starting agent graph tests...")
    print()
    
    results = []
    
    results.append(("Alex - Patient Search", await test_alex_patient_search()))
    results.append(("Alex - Get Doctors", await test_alex_get_doctors()))
    results.append(("RBAC - Patient Access", await test_rbac_patient_access()))
    
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
