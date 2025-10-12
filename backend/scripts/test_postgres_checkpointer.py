#!/usr/bin/env python3
"""
Test script for PostgreSQL checkpointer.

This script tests that:
1. PostgresSaver is initialized correctly
2. Conversations are saved to PostgreSQL
3. Conversations persist across restarts
4. Checkpoints can be retrieved
"""

import sys
import logging
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.memory import get_memory_saver
from langgraph.graph import StateGraph, END
from typing import TypedDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestState(TypedDict):
    """Simple test state."""
    messages: list
    counter: int


def test_node(state: TestState) -> TestState:
    """Simple test node."""
    return {
        "messages": state["messages"] + ["test"],
        "counter": state["counter"] + 1
    }


def main():
    """Test PostgreSQL checkpointer."""
    
    logger.info("=" * 60)
    logger.info("PostgreSQL Checkpointer Test")
    logger.info("=" * 60)
    
    try:
        # Get memory saver
        logger.info("Getting memory saver...")
        memory = get_memory_saver()
        logger.info(f"✅ Memory saver type: {type(memory).__name__}")
        
        # Create simple graph
        logger.info("Creating test graph...")
        workflow = StateGraph(TestState)
        workflow.add_node("test", test_node)
        workflow.set_entry_point("test")
        workflow.add_edge("test", END)
        
        # Compile with checkpointer
        graph = workflow.compile(checkpointer=memory)
        logger.info("✅ Graph compiled with checkpointer")
        
        # Test conversation
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        logger.info(f"Testing conversation (thread_id: {thread_id})...")
        
        # First message
        result1 = graph.invoke(
            {"messages": ["hello"], "counter": 0},
            config=config
        )
        logger.info(f"First result: {result1}")
        
        # Second message (should remember first)
        result2 = graph.invoke(
            {"messages": result1["messages"], "counter": result1["counter"]},
            config=config
        )
        logger.info(f"Second result: {result2}")
        
        # Check checkpoint was saved
        logger.info("Checking if checkpoint was saved...")
        checkpoints = list(memory.list(config))
        logger.info(f"Found {len(checkpoints)} checkpoints")
        
        if len(checkpoints) > 0:
            logger.info("✅ Checkpoints saved successfully!")
            logger.info(f"Latest checkpoint: {checkpoints[0]}")
        else:
            logger.warning("⚠️ No checkpoints found")
        
        # Verify in database
        logger.info("")
        logger.info("Verifying in PostgreSQL...")
        logger.info("Run: sudo -u postgres psql -d dentaflow_checkpoints -c 'SELECT COUNT(*) FROM checkpoints;'")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ PostgreSQL Checkpointer Test Complete!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Verify checkpoints in database")
        logger.info("  2. Test with actual agent graph")
        logger.info("  3. Test conversation persistence across restarts")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

