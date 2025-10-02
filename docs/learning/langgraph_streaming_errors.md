# LangGraph Streaming & Error Handling - Learning Notes

**Date:** 2025-10-02  
**Epic:** L - Deep Learning Phase  
**User Story:** L.1 - Master LangGraph and LangChain

---

## Streaming in LangGraph

LangGraph implements a streaming system to surface **real-time updates**, allowing for responsive and transparent user experiences.

### Three Main Categories of Data You Can Stream:

1. **Workflow progress** — Get state updates after each graph node is executed
2. **LLM tokens** — Stream language model tokens as they're generated
3. **Custom updates** — Emit user-defined signals (e.g., "Fetched 10/100 records")

---

## What's Possible with LangGraph Streaming

### 1. **Stream LLM Tokens**
Capture token streams from anywhere: inside nodes, subgraphs, or tools.

### 2. **Emit Progress Notifications from Tools**
Send custom updates or progress signals directly from tool functions.

### 3. **Stream from Subgraphs**
Include outputs from both the parent graph and any nested subgraphs.

### 4. **Use Any LLM**
Stream tokens from any LLM, even if it's not a LangChain model using the `custom` streaming mode.

### 5. **Use Multiple Streaming Modes**
Choose from:
- `values` — Full state after each node
- `updates` — State deltas (only what changed)
- `messages` — LLM tokens + metadata
- `custom` — Arbitrary user data
- `debug` — Detailed traces

---

## Streaming Modes

### 1. **values** Mode
Stream full state after each node execution.

```python
for chunk in graph.stream({"messages": [("user", "Hello")]}, stream_mode="values"):
    print(chunk)
```

**Output:**
```python
{'messages': [('user', 'Hello')]}
{'messages': [('user', 'Hello'), ('assistant', 'Hi there!')]}
```

### 2. **updates** Mode
Stream only state deltas (what changed).

```python
for chunk in graph.stream({"messages": [("user", "Hello")]}, stream_mode="updates"):
    print(chunk)
```

**Output:**
```python
{'node_a': {'messages': [('assistant', 'Hi there!')]}}
```

### 3. **messages** Mode
Stream LLM tokens + metadata.

```python
for chunk in graph.stream({"messages": [("user", "Hello")]}, stream_mode="messages"):
    print(chunk)
```

**Output:**
```python
('node_a', {'content': 'Hi', 'type': 'AIMessageChunk'})
('node_a', {'content': ' there', 'type': 'AIMessageChunk'})
('node_a', {'content': '!', 'type': 'AIMessageChunk'})
```

### 4. **custom** Mode
Stream arbitrary user-defined data.

```python
from langgraph.streaming import get_stream_writer

def my_node(state):
    writer = get_stream_writer()
    writer("Processing step 1...")
    # ... do work ...
    writer("Processing step 2...")
    return state

for chunk in graph.stream({"messages": [("user", "Hello")]}, stream_mode="custom"):
    print(chunk)
```

**Output:**
```
Processing step 1...
Processing step 2...
```

### 5. **debug** Mode
Stream detailed traces for debugging.

```python
for chunk in graph.stream({"messages": [("user", "Hello")]}, stream_mode="debug"):
    print(chunk)
```

---

## Streaming LLM Tokens

### From a Node

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(streaming=True)

def my_node(state):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Stream tokens
for chunk in graph.stream({"messages": [("user", "Hello")]}, stream_mode="messages"):
    print(chunk[1]["content"], end="", flush=True)
```

### From a Tool

```python
from langchain_core.tools import tool
from langgraph.streaming import get_stream_writer

@tool
def my_tool(query: str):
    """Search for information."""
    writer = get_stream_writer()
    writer("Searching...")
    # ... do search ...
    writer(f"Found {len(results)} results")
    return results

# Stream custom updates from tool
for chunk in graph.stream({"messages": [("user", "Search for X")]}, stream_mode="custom"):
    print(chunk)
```

---

## Error Handling in LangGraph

### 1. **Error Collection in State**

Add error tracking to your state:

```python
from typing import TypedDict, List

class State(TypedDict):
    messages: List[str]
    errors: List[dict]  # Track errors

def my_node(state):
    try:
        # ... do work ...
        return {"messages": ["Success"]}
    except Exception as e:
        return {
            "errors": [{
                "node": "my_node",
                "error": str(e),
                "type": type(e).__name__
            }]
        }
```

### 2. **Error Categorization**

Categorize errors for targeted handling:

```python
class ErrorCategory:
    RETRYABLE = "retryable"  # Network errors, timeouts
    FATAL = "fatal"  # Invalid input, auth errors
    VALIDATION = "validation"  # Data validation errors

def categorize_error(error: Exception) -> str:
    if isinstance(error, (ConnectionError, TimeoutError)):
        return ErrorCategory.RETRYABLE
    elif isinstance(error, (ValueError, KeyError)):
        return ErrorCategory.VALIDATION
    else:
        return ErrorCategory.FATAL

def my_node(state):
    try:
        # ... do work ...
        return {"messages": ["Success"]}
    except Exception as e:
        return {
            "errors": [{
                "node": "my_node",
                "error": str(e),
                "category": categorize_error(e)
            }]
        }
```

### 3. **Error Routing**

Route to different nodes based on error category:

```python
from langgraph.graph import StateGraph, END

def route_on_error(state):
    if not state.get("errors"):
        return "success_node"
    
    error = state["errors"][-1]
    if error["category"] == ErrorCategory.RETRYABLE:
        return "retry_node"
    elif error["category"] == ErrorCategory.VALIDATION:
        return "validation_node"
    else:
        return END

workflow = StateGraph(State)
workflow.add_node("my_node", my_node)
workflow.add_node("retry_node", retry_node)
workflow.add_node("validation_node", validation_node)
workflow.add_node("success_node", success_node)

workflow.add_conditional_edges(
    "my_node",
    route_on_error,
    {
        "success_node": "success_node",
        "retry_node": "retry_node",
        "validation_node": "validation_node",
        END: END
    }
)
```

### 4. **Retry with Exponential Backoff**

```python
import time

def retry_node(state):
    max_retries = 3
    retry_count = state.get("retry_count", 0)
    
    if retry_count >= max_retries:
        return {"errors": [{"node": "retry_node", "error": "Max retries exceeded"}]}
    
    try:
        # Wait with exponential backoff
        wait_time = 2 ** retry_count
        time.sleep(wait_time)
        
        # Retry the operation
        result = risky_operation()
        return {"messages": [result], "retry_count": 0}
    except Exception as e:
        return {
            "retry_count": retry_count + 1,
            "errors": [{
                "node": "retry_node",
                "error": str(e),
                "retry_count": retry_count + 1
            }]
        }
```

### 5. **LLM-Powered Error Summarization**

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI()

def error_summary_node(state):
    errors = state.get("errors", [])
    if not errors:
        return state
    
    # Use LLM to summarize errors
    error_text = "\n".join([f"{e['node']}: {e['error']}" for e in errors])
    prompt = f"Summarize these errors for the user:\n{error_text}"
    
    summary = model.invoke(prompt)
    return {"messages": [summary.content]}
```

---

## Key Takeaways for DentalAI

### Streaming:
1. **Use `messages` mode** for token-by-token streaming to users
2. **Use `custom` mode** for progress updates (e.g., "Searching Odoo...")
3. **Stream from tools** to show progress (e.g., "Found 5 appointments")
4. **Stream from subgraphs** to show nested agent progress

### Error Handling:
1. **Collect errors in state** for tracking and debugging
2. **Categorize errors** (retryable, fatal, validation)
3. **Route based on error category** to specialized handlers
4. **Retry with exponential backoff** for network/API errors
5. **LLM-powered error summaries** for user-friendly messages
6. **Log all errors** for audit trails and debugging

---

**Status:** Streaming and error handling learned ✅  
**Next:** Complete User Story L.1 and move to L.2 (Odoo Integration)
