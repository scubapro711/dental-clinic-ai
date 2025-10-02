# LangGraph Core Concepts - Learning Notes

**Date:** 2025-10-02  
**Epic:** L - Deep Learning Phase  
**User Story:** L.1 - Master LangGraph and LangChain

---

## What is LangGraph?

LangGraph is a **low-level orchestration framework** for building, managing, and deploying **long-running, stateful agents**.

**Used by:** Klarna, Replit, Elastic, and more

---

## Core Benefits

### 1. **Reliability and Controllability**
- Steer agent actions with moderation checks
- Human-in-the-loop approvals
- Persists context for long-running workflows
- Keeps agents on course

### 2. **Low-level and Extensible**
- Fully descriptive, low-level primitives
- Free from rigid abstractions
- Design scalable multi-agent systems
- Each agent serves a specific role

### 3. **First-class Streaming Support**
- Token-by-token streaming
- Streaming of intermediate steps
- Clear visibility into agent reasoning and actions in real time

---

## Key Features

### 1. **Durable Execution**
- Agents persist through failures
- Run for extended periods
- Automatically resume from exactly where they left off

### 2. **Human-in-the-Loop**
- Inspect and modify agent state at any point during execution
- Seamless incorporation of human oversight

### 3. **Comprehensive Memory**
- **Short-term working memory** for ongoing reasoning
- **Long-term persistent memory** across sessions
- Truly stateful agents

### 4. **Debugging with LangSmith**
- Visualization tools that trace execution paths
- Capture state transitions
- Detailed runtime metrics

### 5. **Production-ready Deployment**
- Scalable infrastructure
- Handle unique challenges of stateful, long-running workflows

---

## LangGraph Basics Tutorial Series

To master LangGraph, complete these 6 tutorials:

1. ✅ **Build a basic chatbot** - Foundation
2. ✅ **Add tools** - Enable agent to use external tools
3. ✅ **Add memory** - Maintain conversation state
4. ✅ **Add human-in-the-loop** - Route complex queries to humans
5. ✅ **Customize state** - Control agent behavior
6. ✅ **Time travel** - Rewind and explore alternative paths

**Result:** A support chatbot that can:
- Answer questions by searching the web
- Maintain conversation state
- Route complex queries to humans
- Use custom state
- Rewind and explore alternatives

---

## Next Steps

1. Read "Workflows & Agents" concept
2. Read "Agent Architectures" concept
3. Complete the 6 tutorial series
4. Study multi-agent patterns
5. Study checkpointing and persistence

---

## Installation

```bash
pip install -U langgraph
```

## Basic Example

```python
from langgraph.prebuilt import create_react_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_weather],
    prompt="You are a helpful assistant"
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
```

---

## Key Takeaways for DentalAI

1. **Perfect for our use case:** Long-running, stateful agents (Dana, Michal, Yosef, Sarah)
2. **Durable execution:** Agents can handle failures and resume
3. **Human-in-the-loop:** Critical for medical/billing decisions
4. **Memory:** Short-term (conversation) + Long-term (patient history)
5. **Multi-agent:** Each agent has a specific role (receptionist, medical, billing, scheduling)
6. **Streaming:** Real-time updates to users
7. **Low-level control:** We can customize everything for our specific needs

---

**Status:** Initial concepts learned ✅  
**Next:** Deep dive into tutorials and multi-agent patterns
