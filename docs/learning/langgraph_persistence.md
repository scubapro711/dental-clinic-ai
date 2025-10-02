# LangGraph Persistence & Checkpointing - Learning Notes

**Date:** 2025-10-02  
**Epic:** L - Deep Learning Phase  
**User Story:** L.1 - Master LangGraph and LangChain

---

## What is Persistence?

LangGraph has a **built-in persistence layer** implemented through **checkpointers**.

When you compile a graph with a checkpointer, it saves a `checkpoint` of the graph state at every super-step. Checkpoints are saved to a `thread`.

---

## Key Concepts

### 1. **Threads**

A **thread** is a unique ID assigned to each checkpoint saved by a checkpointer.

- Contains the accumulated state of a sequence of runs
- Must be specified when invoking a graph with a checkpointer

```python
config = {"configurable": {"thread_id": "1"}}
graph.invoke({"foo": ""}, config)
```

### 2. **Checkpoints**

A **checkpoint** is a snapshot of the graph state saved at each super-step.

**StateSnapshot properties:**
- `config`: Config associated with this checkpoint
- `metadata`: Metadata associated with this checkpoint
- `values`: Values of the state channels at this point in time
- `next`: Tuple of node names to execute next
- `tasks`: Tuple of PregelTask objects with next tasks to be executed

---

## Checkpoint Example

Simple graph with 2 nodes:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

def node_a(state):
    return {"foo": "a", "bar": ["a"]}

def node_b(state):
    return {"foo": "b", "bar": ["b"]}

workflow = StateGraph(State)
workflow.add_node(node_a)
workflow.add_node(node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
graph.invoke({"foo": ""}, config)
```

**Checkpoints created:**
1. Empty checkpoint with `START` as next node
2. Checkpoint with user input `{'foo': '', 'bar': []}` and `node_a` as next node
3. Checkpoint with outputs of `node_a` `{'foo': 'a', 'bar': ['a']}` and `node_b` as next node
4. Checkpoint with outputs of `node_b` `{'foo': 'b', 'bar': ['a', 'b']}` and no next nodes

---

## Working with State

### Get Latest State

```python
config = {"configurable": {"thread_id": "1"}}
graph.get_state(config)
```

Returns `StateSnapshot` with latest checkpoint.

### Get State for Specific Checkpoint

```python
config = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": "1ef663ba-28fe-6528-8002-5a559208592c"
    }
}
graph.get_state(config)
```

### Get State History

```python
config = {"configurable": {"thread_id": "1"}}
list(graph.get_state_history(config))
```

Returns list of `StateSnapshot` objects ordered chronologically (most recent first).

---

## Replay

Replay a prior graph execution:

```python
# Get a specific checkpoint config
checkpoint_config = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": "1ef663ba-28f9-6ec4-8001-31981c2c39f8"
    }
}

# Replay from that checkpoint
graph.invoke(None, checkpoint_config)
```

---

## Update State

Manually update the state:

```python
graph.update_state(
    config={"configurable": {"thread_id": "1"}},
    values={"foo": "updated_value"},
    as_node="node_a"  # Optional: act as if this node made the update
)
```

**Parameters:**
- `config`: Thread config
- `values`: State updates
- `as_node`: (Optional) Which node made the update

---

## Memory Store

LangGraph provides a **Memory Store** for long-term memory across sessions.

**Basic Usage:**

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Put memory
store.put(
    namespace=("user", "123"),
    key="preferences",
    value={"language": "en", "theme": "dark"}
)

# Get memory
memory = store.get(namespace=("user", "123"), key="preferences")

# Search memory
results = store.search(namespace=("user", "123"))
```

**Semantic Search:**

```python
# Search by semantic similarity
results = store.search(
    namespace=("user", "123"),
    query="What are my preferences?",
    limit=5
)
```

---

## Checkpointer Libraries

### 1. **InMemorySaver** (Development)

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
```

### 2. **PostgresSaver** (Production)

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgresql://...")
graph = workflow.compile(checkpointer=checkpointer)
```

### 3. **AsyncPostgresSaver** (Production, Async)

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = await AsyncPostgresSaver.from_conn_string("postgresql://...")
graph = workflow.compile(checkpointer=checkpointer)
```

---

## Capabilities Enabled by Persistence

### 1. **Human-in-the-Loop**
- Pause execution
- Inspect state
- Modify state
- Resume execution

### 2. **Memory**
- Short-term: Conversation history within a session
- Long-term: User preferences, past interactions across sessions

### 3. **Time Travel**
- Replay past executions
- Branch from any checkpoint
- Explore alternative paths

### 4. **Fault-Tolerance**
- Automatic recovery from failures
- Resume from last checkpoint
- No data loss

---

## Serialization

**Default:** Uses `pickle` for serialization

**Custom Serializer:**

```python
from langgraph.checkpoint.serde.base import SerializerProtocol

class MySerializer(SerializerProtocol):
    def dumps(self, obj):
        # Custom serialization
        pass
    
    def loads(self, data):
        # Custom deserialization
        pass

checkpointer = PostgresSaver(
    conn_string="postgresql://...",
    serde=MySerializer()
)
```

---

## Encryption

Encrypt sensitive data in checkpoints:

```python
from langgraph.checkpoint.postgres import PostgresSaver
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

checkpointer = PostgresSaver(
    conn_string="postgresql://...",
    serde=EncryptedSerializer(cipher)
)
```

---

## Key Takeaways for DentalAI

1. **Use PostgresSaver** for production (not InMemorySaver)
2. **Thread ID = Conversation ID** - Each patient conversation gets a unique thread
3. **Checkpoints** enable:
   - Resume interrupted conversations
   - Review conversation history
   - Human-in-the-loop for sensitive decisions
   - Time travel for debugging
4. **Memory Store** for:
   - Patient preferences (language, communication style)
   - Past interactions across sessions
   - Knowledge cards
5. **Encryption** for GDPR compliance
6. **State history** for audit trails

---

**Status:** Persistence and checkpointing learned ✅  
**Next:** Study streaming and error handling
