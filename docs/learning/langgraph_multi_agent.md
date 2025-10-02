# LangGraph Multi-Agent Systems - Learning Notes

**Date:** 2025-10-02  
**Epic:** L - Deep Learning Phase  
**User Story:** L.1 - Master LangGraph and LangChain

---

## What is a Multi-Agent System?

Breaking your application into **multiple smaller, independent agents** and composing them into a multi-agent system.

**When to use:**
- Agent has too many tools and makes poor decisions
- Context grows too complex for a single agent
- Need for multiple specialization areas (planner, researcher, math expert, etc.)

---

## Primary Benefits

1. **Modularity** - Easier to develop, test, and maintain
2. **Specialization** - Expert agents focused on specific domains
3. **Control** - Explicitly control how agents communicate

---

## Multi-Agent Architectures

### 1. **Network**
- Each agent can communicate with every other agent (many-to-many)
- Any agent can decide which agent to call next
- **Good for:** Problems without clear hierarchy

### 2. **Supervisor**
- Each agent communicates with a single supervisor agent
- Supervisor decides which agent should be called next
- **Good for:** Centralized control

### 3. **Supervisor (Tool-Calling)**
- Special case: agents represented as tools
- Supervisor uses tool-calling LLM to decide which agent to call
- **Good for:** Leveraging LLM's tool-calling capabilities

### 4. **Hierarchical**
- Supervisor of supervisors
- Generalization of supervisor architecture
- **Good for:** Complex control flows

### 5. **Custom Multi-Agent Workflow**
- Each agent communicates with only a subset of agents
- Parts of flow are deterministic
- **Good for:** Specific, well-defined workflows

---

## Handoffs

**Handoffs** = One agent hands off control to another

**Components:**
- **Destination:** Target agent to navigate to
- **Payload:** Information to pass to that agent

**Implementation with Command:**

```python
from langgraph.types import Command

def agent(state) -> Command[Literal["agent", "another_agent"]]:
    goto = get_next_agent(...)
    return Command(
        goto=goto,  # Which agent to call next
        update={"my_state_key": "my_state_value"}  # Update state
    )
```

**For subgraphs:**

```python
def some_node_inside_alice(state):
    return Command(
        goto="bob",
        update={"my_state_key": "my_state_value"},
        graph=Command.PARENT  # Navigate to parent graph
    )
```

---

## Handoffs as Tools

Common pattern for tool-calling agents:

```python
from langchain_core.tools import tool

@tool
def transfer_to_bob():
    """Transfer to bob."""
    return Command(
        goto="bob",
        update={"my_state_key": "my_state_value"},
        graph=Command.PARENT
    )
```

---

## Communication and State Management

### Message Passing Between Agents

**Two approaches:**

1. **Sharing full thought process** - All intermediate steps visible
2. **Sharing only final results** - Only final output visible

### Indicating Agent Name in Messages

Add agent name to messages for clarity:

```python
update={"messages": [{"role": "assistant", "content": "...", "name": "agent_1"}]}
```

### State Management for Subagents

**Options:**
- **Same state schema** - All agents share the same state
- **Different state schemas** - Each agent has its own state

---

## Architecture Decision for DentalAI

**Chosen Architecture:** **Supervisor (Tool-Calling)**

**Why:**
1. **Clear hierarchy:** Dana (receptionist) is the supervisor
2. **Specialization:** Each agent (Michal, Yosef, Sarah) has a specific role
3. **Tool-calling:** Dana can call other agents as tools
4. **Control:** Dana decides which agent to call based on user intent

**Agent Structure:**

```
Dana (Supervisor/Receptionist)
├── Tool: transfer_to_michal (Medical Info)
├── Tool: transfer_to_yosef (Billing)
└── Tool: transfer_to_sarah (Scheduling)
```

**State Sharing:**
- **Full thought process** for transparency
- **Agent name in messages** for clarity
- **Same state schema** (MessagesState + custom fields)

---

## Key Takeaways for DentalAI

1. **Use Supervisor (Tool-Calling)** - Dana is the supervisor
2. **Each agent is a tool** - transfer_to_michal, transfer_to_yosef, transfer_to_sarah
3. **Command for handoffs** - Clean navigation between agents
4. **Shared state** - All agents see conversation history
5. **Agent names in messages** - Users know who they're talking to
6. **Modularity** - Each agent can be developed/tested independently

---

**Status:** Multi-agent architecture learned ✅  
**Next:** Study persistence and checkpointing
