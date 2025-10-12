# Multi-Turn Conversations Guide

Complete guide for implementing multi-turn conversations with memory and context.

## 📋 Overview

Multi-turn conversations allow agents to:
- **Remember** previous messages
- **Maintain context** across turns
- **Provide continuity** in long conversations
- **Handle complex** multi-step tasks
- **Generate summaries** for handoffs

---

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Message                              │
│                         ↓                                    │
│              ConversationManager                             │
│                    ↓         ↓                               │
│         Load Conversation  Get History                       │
│                    ↓                                         │
│              Build Context Window                            │
│                    ↓                                         │
│                 AI Agent                                     │
│              (with memory)                                   │
│                    ↓                                         │
│              Generate Response                               │
│                    ↓                                         │
│         Save Message + Update State                          │
│                    ↓                                         │
│              Return Response                                 │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**Conversation Table:**
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    patient_name VARCHAR(255),
    patient_email VARCHAR(255),
    patient_phone VARCHAR(20),
    status VARCHAR(50) NOT NULL,  -- active, completed, escalated
    channel VARCHAR(50) NOT NULL,  -- web_chat, whatsapp, telegram
    primary_agent VARCHAR(50) NOT NULL,
    escalated_to_agent VARCHAR(50),
    langgraph_thread_id VARCHAR(255) UNIQUE NOT NULL,
    langgraph_state JSONB,
    summary TEXT,
    tags JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    deleted_at TIMESTAMP
);
```

**Message Table:**
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    agent_name VARCHAR(50),
    message_metadata JSONB,
    tokens_used INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMP NOT NULL
);
```

---

## 💬 Usage Examples

### Example 1: Create Conversation

```python
from app.services.conversation_manager import ConversationManager
from app.models.conversation import ConversationChannel

# Initialize manager
manager = ConversationManager(db)

# Create new conversation
conversation = manager.create_conversation(
    organization_id=org_id,
    channel=ConversationChannel.WEB_CHAT,
    primary_agent="alex",
    patient_name="דוד כהן",
    patient_phone="+972501234567",
    metadata={"source": "website", "page": "home"}
)

print(f"Created conversation: {conversation.id}")
print(f"Thread ID: {conversation.langgraph_thread_id}")
```

---

### Example 2: Add Messages

```python
from app.models.message import MessageRole

# User message
user_msg = manager.add_message(
    conversation_id=conversation.id,
    role=MessageRole.USER,
    content="שלום, אני רוצה לקבוע תור"
)

# Assistant response
assistant_msg = manager.add_message(
    conversation_id=conversation.id,
    role=MessageRole.ASSISTANT,
    content="שלום דוד! אשמח לעזור לך לקבוע תור. מתי נוח לך להגיע?",
    agent_name="alex",
    metadata={"intent": "schedule_appointment", "confidence": 0.95}
)
```

---

### Example 3: Get Conversation History

```python
# Get all messages
messages = manager.get_conversation_history(conversation.id)

for msg in messages:
    print(f"[{msg.role.value}] {msg.content}")

# Output:
# [user] שלום, אני רוצה לקבוע תור
# [assistant] שלום דוד! אשמח לעזור לך לקבוע תור. מתי נוח לך להגיע?
```

---

### Example 4: Get Context Window

```python
# Get last 10 messages for agent context
context = manager.get_context_window(
    conversation_id=conversation.id,
    window_size=10
)

# Pass to agent
response = agent.process_message(
    user_message="מחר בשעה 10:00",
    context=context
)
```

---

### Example 5: Continue Existing Conversation

```python
# For channels like Telegram/WhatsApp
conversation = manager.get_or_create_conversation(
    organization_id=org_id,
    patient_phone="+972501234567",
    channel=ConversationChannel.TELEGRAM
)

# This will:
# 1. Try to find active conversation for this phone
# 2. If found and recent (< 24h), continue it
# 3. Otherwise, create new conversation
```

---

### Example 6: Update Conversation State

```python
# Update LangGraph state
manager.update_conversation_state(
    conversation_id=conversation.id,
    state_update={
        "context": {
            "appointment_date": "2025-10-15",
            "appointment_time": "10:00",
            "doctor_id": 1
        },
        "step": "confirm_appointment"
    }
)
```

---

### Example 7: Generate Summary

```python
# Generate AI summary
summary = manager.generate_summary(conversation.id)

print(summary)
# Output: "Conversation with דוד כהן. 5 user messages, 5 assistant responses. 
#          Primary agent: alex. Status: active."
```

---

### Example 8: Complete Conversation

```python
# Mark as completed
manager.complete_conversation(
    conversation_id=conversation.id,
    reason="Appointment scheduled successfully"
)

# This will:
# 1. Set status to COMPLETED
# 2. Set completed_at timestamp
# 3. Generate final summary
# 4. Add completion reason to state
```

---

### Example 9: Escalate to Human

```python
# Escalate to human agent
manager.escalate_conversation(
    conversation_id=conversation.id,
    to_agent="human_receptionist",
    reason="Patient requested to speak with human"
)

# This will:
# 1. Set status to ESCALATED
# 2. Set escalated_to_agent
# 3. Add escalation info to state
# 4. Add system message
```

---

### Example 10: Proactive Suggestions

```python
# Get contextual suggestions
suggestions = manager.get_proactive_suggestions(conversation.id)

print("Suggestions:")
for suggestion in suggestions:
    print(f"  - {suggestion}")

# Output:
# Suggestions:
#   - האם תרצה לראות תורים פנויים?
#   - מתי נוח לך להגיע?
#   - האם תרצה תזכורת לפני התור?
```

---

## 🔄 Integration with AI Agents

### Example: Full Conversation Flow

```python
from app.services.conversation_manager import ConversationManager
from app.agents.alex import alex_agent
from app.models.message import MessageRole

def process_user_message(
    user_message: str,
    conversation_id: UUID,
    db: Session
) -> str:
    """
    Process user message with full conversation context.
    
    Args:
        user_message: User's message
        conversation_id: Conversation UUID
        db: Database session
    
    Returns:
        Agent's response
    """
    manager = ConversationManager(db)
    
    # 1. Save user message
    manager.add_message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=user_message
    )
    
    # 2. Get conversation context
    context = manager.get_context_window(
        conversation_id=conversation_id,
        window_size=10
    )
    
    # 3. Get conversation state
    conversation = manager.get_conversation(conversation_id)
    state = conversation.langgraph_state or {}
    
    # 4. Process with agent
    response = alex_agent.process(
        message=user_message,
        context=context,
        state=state
    )
    
    # 5. Save assistant response
    manager.add_message(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=response["content"],
        agent_name="alex",
        metadata={
            "tool_calls": response.get("tool_calls", []),
            "confidence": response.get("confidence", 0.0)
        }
    )
    
    # 6. Update conversation state
    if response.get("state_update"):
        manager.update_conversation_state(
            conversation_id=conversation_id,
            state_update=response["state_update"]
        )
    
    # 7. Check if conversation should be completed
    if response.get("should_complete"):
        manager.complete_conversation(
            conversation_id=conversation_id,
            reason=response.get("completion_reason")
        )
    
    return response["content"]
```

---

## 🧠 Memory Management

### Context Window Strategy

**Problem:** Long conversations exceed token limits

**Solution:** Use sliding window + summary

```python
def get_smart_context(conversation_id: UUID, max_tokens: int = 2000):
    """Get context that fits within token limit."""
    
    manager = ConversationManager(db)
    conversation = manager.get_conversation(conversation_id)
    
    # Start with recent messages
    recent_messages = manager.get_conversation_history(
        conversation_id=conversation_id,
        limit=10
    )
    
    # Calculate tokens
    tokens = sum(len(msg.content.split()) * 1.3 for msg in recent_messages)
    
    if tokens > max_tokens:
        # Use summary + recent messages
        summary = manager.generate_summary(conversation_id)
        recent_messages = recent_messages[-5:]  # Last 5 only
        
        context = [
            {"role": "system", "content": f"Previous conversation summary: {summary}"}
        ] + [
            {"role": msg.role.value, "content": msg.content}
            for msg in recent_messages
        ]
    else:
        # Use all recent messages
        context = [
            {"role": msg.role.value, "content": msg.content}
            for msg in recent_messages
        ]
    
    return context
```

---

### State Management

**Store important information in state:**

```python
# Example state structure
state = {
    "context": {
        "patient_name": "דוד כהן",
        "patient_phone": "+972501234567",
        "appointment_date": "2025-10-15",
        "appointment_time": "10:00",
        "doctor_id": 1,
        "treatment_type": "checkup"
    },
    "step": "confirm_appointment",  # Current step in flow
    "history_summary": "Patient wants to schedule checkup appointment",
    "metadata": {
        "source": "telegram",
        "language": "he"
    }
}
```

---

## 🎯 Best Practices

### 1. Always Save Messages

```python
# ✅ DO: Save both user and assistant messages
manager.add_message(conversation_id, MessageRole.USER, user_msg)
response = agent.process(user_msg, context)
manager.add_message(conversation_id, MessageRole.ASSISTANT, response)

# ❌ DON'T: Skip saving messages
response = agent.process(user_msg)  # Context lost!
```

---

### 2. Use Context Window

```python
# ✅ DO: Pass conversation context to agent
context = manager.get_context_window(conversation_id, window_size=10)
response = agent.process(user_msg, context=context)

# ❌ DON'T: Process without context
response = agent.process(user_msg)  # Agent has no memory!
```

---

### 3. Update State Regularly

```python
# ✅ DO: Update state after important events
manager.update_conversation_state(conversation_id, {
    "context": {"appointment_id": 123},
    "step": "appointment_confirmed"
})

# ❌ DON'T: Lose important information
# (No state update = information lost)
```

---

### 4. Generate Summaries

```python
# ✅ DO: Generate summaries for long conversations
if len(messages) > 50:
    summary = manager.generate_summary(conversation_id)

# ❌ DON'T: Let conversations grow unbounded
# (Will hit token limits)
```

---

### 5. Complete Conversations

```python
# ✅ DO: Mark conversations as completed
if task_done:
    manager.complete_conversation(conversation_id, reason="Task completed")

# ❌ DON'T: Leave conversations open forever
# (Wastes resources, confuses users)
```

---

## 📊 Monitoring

### Conversation Metrics

```python
def get_conversation_metrics(conversation_id: UUID):
    """Get metrics for conversation."""
    
    manager = ConversationManager(db)
    conversation = manager.get_conversation(conversation_id)
    messages = manager.get_conversation_history(conversation_id)
    
    user_messages = [m for m in messages if m.role == MessageRole.USER]
    assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
    
    return {
        "conversation_id": str(conversation_id),
        "status": conversation.status.value,
        "duration_minutes": (
            (conversation.updated_at - conversation.created_at).total_seconds() / 60
        ),
        "message_count": len(messages),
        "user_message_count": len(user_messages),
        "assistant_message_count": len(assistant_messages),
        "avg_response_time_ms": sum(
            m.latency_ms or 0 for m in assistant_messages
        ) / len(assistant_messages) if assistant_messages else 0,
        "total_tokens": sum(m.tokens_used or 0 for m in messages),
        "primary_agent": conversation.primary_agent,
        "escalated": conversation.status == ConversationStatus.ESCALATED
    }
```

---

## 🐛 Troubleshooting

### Issue: Agent doesn't remember previous messages

**Cause:** Not passing context to agent

**Solution:**
```python
# Get context before processing
context = manager.get_context_window(conversation_id)
response = agent.process(user_msg, context=context)
```

---

### Issue: Conversation not found

**Cause:** Using wrong conversation ID or deleted conversation

**Solution:**
```python
conversation = manager.get_conversation(conversation_id)
if not conversation:
    # Create new conversation
    conversation = manager.create_conversation(...)
```

---

### Issue: Token limit exceeded

**Cause:** Too many messages in context

**Solution:**
```python
# Use smart context with summary
context = get_smart_context(conversation_id, max_tokens=2000)
```

---

## 📚 Additional Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Conversation Design Best Practices](https://developers.google.com/assistant/conversation-design)
- [Multi-Turn Dialogue Systems](https://arxiv.org/abs/2004.13637)

---

**Last Updated:** October 8, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
