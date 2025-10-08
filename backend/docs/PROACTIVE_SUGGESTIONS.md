# Proactive Suggestions Guide

Complete guide for implementing proactive, intelligent suggestions in conversations.

## 📋 Overview

Proactive suggestions allow the system to:
- **Anticipate** user needs before they ask
- **Remind** users of upcoming appointments
- **Suggest** relevant actions based on context
- **Engage** users at the right time
- **Improve** user experience and satisfaction

---

## 🎯 Suggestion Types

### 1. Appointment Reminders
**When:** User has appointment in next 24 hours  
**Example:** "יש לך תור מחר בשעה 10:00. האם תרצה תזכורת נוספת?"

### 2. Checkup Reminders
**When:** 6+ months since last checkup  
**Example:** "עברו 6 חודשים מהבדיקה האחרונה. מומלץ לקבוע תור."

### 3. Treatment Plan Review
**When:** New treatment plan created  
**Example:** "תוכנית הטיפול שלך מוכנה. האם תרצה לעבור עליה?"

### 4. Payment Reminders
**When:** Unpaid invoices exist  
**Example:** "יש לך חשבונית פתוחה בסך 500 ₪. האם תרצה לשלם עכשיו?"

### 5. Follow-up After Treatment
**When:** 3-7 days after treatment  
**Example:** "איך אתה מרגיש אחרי הטיפול? יש כאבים או אי נוחות?"

### 6. Feedback Requests
**When:** After completed conversation  
**Example:** "איך היתה החוויה שלך? נשמח לקבל משוב קצר."

### 7. Contextual Suggestions
**When:** Based on conversation keywords  
**Examples:**
- User mentions "תור" → "מצאתי כמה תורים פנויים השבוע"
- User mentions "כאב" → "נשמע דחוף. תור בהקדם?"
- User mentions "מחיר" → "רוצה לראות מחירון מלא?"

---

## 🚀 Usage Examples

### Example 1: Get Suggestions

```python
from app.services.proactive_suggestions import get_proactive_suggestions_service

# Get suggestions for conversation
service = get_proactive_suggestions_service(db)

suggestions = service.get_suggestions(
    conversation_id=conversation_id,
    limit=3
)

for suggestion in suggestions:
    print(f"[{suggestion['type']}] {suggestion['title']}")
    print(f"  {suggestion['message']}")
    for action in suggestion['actions']:
        print(f"  - {action['label']}")
```

**Output:**
```
[appointment_reminder] תזכורת לתור מחר
  יש לך תור מחר בשעה 10:00. האם תרצה תזכורת נוספת?
  - כן, שלח תזכורת
  - לא צריך

[schedule_checkup] הגיע הזמן לבדיקה
  עברו 6 חודשים מהבדיקה האחרונה. מומלץ לקבוע תור.
  - קבע תור עכשיו
  - הזכר לי בעוד שבוע
```

---

### Example 2: API Request

```bash
# Get suggestions
curl -X GET "https://dentaflow.ai/api/v1/proactive-suggestions/conversations/{conversation_id}/suggestions?limit=3"
```

**Response:**
```json
[
  {
    "type": "appointment_reminder",
    "priority": 10,
    "title": "תזכורת לתור מחר",
    "message": "יש לך תור מחר בשעה 10:00. האם תרצה תזכורת נוספת?",
    "actions": [
      {
        "label": "כן, שלח תזכורת",
        "action": "send_reminder",
        "data": {"appointment_id": 123}
      },
      {
        "label": "לא צריך",
        "action": "dismiss"
      }
    ],
    "metadata": {
      "appointment_date": "2025-10-09",
      "appointment_time": "10:00"
    }
  }
]
```

---

### Example 3: Execute Action

```python
# User clicked "כן, שלח תזכורת"
result = service.execute_suggestion_action(
    conversation_id=conversation_id,
    action="send_reminder",
    data={"appointment_id": 123}
)

print(result["message"])
# Output: "תזכורת נשלחה! תקבל הודעה 2 שעות לפני התור."
```

---

### Example 4: Dismiss Suggestion

```python
# User clicked "לא צריך"
service.dismiss_suggestion(
    conversation_id=conversation_id,
    suggestion_type="appointment_reminder"
)

# This suggestion won't appear again for this conversation
```

---

### Example 5: Frontend Integration (React)

```jsx
import { useState, useEffect } from 'react';

function ProactiveSuggestions({ conversationId }) {
  const [suggestions, setSuggestions] = useState([]);
  
  useEffect(() => {
    // Fetch suggestions
    fetch(`/api/v1/proactive-suggestions/conversations/${conversationId}/suggestions`)
      .then(res => res.json())
      .then(data => setSuggestions(data));
  }, [conversationId]);
  
  const handleAction = async (action, data) => {
    const response = await fetch(
      `/api/v1/proactive-suggestions/conversations/${conversationId}/suggestions/execute`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, data })
      }
    );
    
    const result = await response.json();
    alert(result.message);
  };
  
  return (
    <div className="suggestions">
      {suggestions.map((suggestion, index) => (
        <div key={index} className="suggestion-card">
          <h3>{suggestion.title}</h3>
          <p>{suggestion.message}</p>
          <div className="actions">
            {suggestion.actions.map((action, i) => (
              <button
                key={i}
                onClick={() => handleAction(action.action, action.data)}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 🧠 How It Works

### 1. Context Analysis

```python
def _get_contextual_suggestions(conversation):
    """Analyze conversation for context."""
    
    # Get recent messages
    messages = get_recent_messages(conversation.id, limit=5)
    
    # Extract keywords
    content = " ".join([m.content.lower() for m in messages])
    
    # Check for patterns
    if "תור" in content or "appointment" in content:
        return appointment_suggestions()
    elif "כאב" in content or "pain" in content:
        return urgent_suggestions()
    elif "מחיר" in content or "price" in content:
        return pricing_suggestions()
```

### 2. Data-Driven Suggestions

```python
def _get_appointment_reminders(conversation):
    """Get reminders based on Odoo data."""
    
    # Query Odoo for upcoming appointments
    appointments = odoo_client.get_patient_appointments(
        patient_phone=conversation.patient_phone,
        date_from=datetime.now(),
        date_to=datetime.now() + timedelta(days=1)
    )
    
    if appointments:
        return [{
            "type": "appointment_reminder",
            "priority": 10,
            "message": f"יש לך תור מחר בשעה {appointment.time}"
        }]
```

### 3. Priority Sorting

```python
# Suggestions are sorted by priority
suggestions.sort(key=lambda x: x["priority"], reverse=True)

# Priority levels:
# 10 = Critical (urgent appointment, payment overdue)
# 8-9 = High (checkup reminder, treatment plan)
# 5-7 = Medium (follow-up, contextual)
# 1-4 = Low (feedback, special offers)
```

---

## 📊 Suggestion Structure

```python
{
    "type": str,  # Suggestion type (e.g., "appointment_reminder")
    "priority": int,  # 1-10 (higher = more important)
    "title": str,  # Short title (Hebrew)
    "message": str,  # Full message (Hebrew)
    "actions": [  # List of possible actions
        {
            "label": str,  # Button label (Hebrew)
            "action": str,  # Action name
            "data": dict  # Action data
        }
    ],
    "metadata": dict  # Additional data
}
```

---

## 🎨 UI/UX Best Practices

### 1. Timing

**✅ DO:**
- Show suggestions after user sends message
- Show reminders at appropriate times (morning for appointments)
- Limit to 1-3 suggestions at a time

**❌ DON'T:**
- Interrupt user while typing
- Show too many suggestions at once
- Show same suggestion repeatedly

### 2. Presentation

**✅ DO:**
- Use cards or bubbles for suggestions
- Make actions clear with buttons
- Use Hebrew for Israeli users
- Show priority visually (colors, icons)

**❌ DON'T:**
- Hide suggestions in menus
- Use confusing labels
- Mix languages

### 3. Dismissal

**✅ DO:**
- Allow easy dismissal (X button)
- Remember dismissed suggestions
- Provide "remind me later" option

**❌ DON'T:**
- Force user to act
- Show dismissed suggestions again
- Make dismissal difficult

---

## 🔧 Configuration

### Enable/Disable Suggestion Types

```python
# In settings
PROACTIVE_SUGGESTIONS_CONFIG = {
    "appointment_reminder": {
        "enabled": True,
        "hours_before": 24,
        "max_reminders": 2
    },
    "checkup_reminder": {
        "enabled": True,
        "months_since_last": 6
    },
    "payment_reminder": {
        "enabled": True,
        "days_overdue": 7
    },
    "feedback_request": {
        "enabled": True,
        "delay_after_completion": 24  # hours
    }
}
```

---

## 📈 Analytics

### Track Suggestion Performance

```python
def track_suggestion_metrics(suggestion_type: str, action: str):
    """Track suggestion engagement."""
    
    metrics = {
        "suggestion_type": suggestion_type,
        "action": action,  # "clicked", "dismissed", "ignored"
        "timestamp": datetime.now(),
        "conversation_id": conversation_id
    }
    
    # Save to analytics database
    analytics_db.save(metrics)
```

### Metrics to Track

- **Impression rate**: How often suggestions are shown
- **Click rate**: How often users click actions
- **Dismissal rate**: How often users dismiss
- **Conversion rate**: How often actions complete successfully
- **Time to action**: How long until user acts

---

## 🧪 Testing

### Test 1: Context Detection

```python
def test_context_detection():
    """Test that context is detected correctly."""
    
    # Create conversation with "תור" keyword
    conversation = create_test_conversation()
    add_message(conversation.id, "אני רוצה לקבוע תור")
    
    # Get suggestions
    suggestions = service.get_suggestions(conversation.id)
    
    # Should include appointment-related suggestion
    assert any(s["type"] == "contextual" for s in suggestions)
    assert "תורים פנויים" in suggestions[0]["message"]
```

### Test 2: Priority Sorting

```python
def test_priority_sorting():
    """Test that suggestions are sorted by priority."""
    
    suggestions = [
        {"type": "feedback", "priority": 3},
        {"type": "urgent", "priority": 10},
        {"type": "checkup", "priority": 8}
    ]
    
    suggestions.sort(key=lambda x: x["priority"], reverse=True)
    
    assert suggestions[0]["priority"] == 10  # Urgent first
    assert suggestions[-1]["priority"] == 3  # Feedback last
```

### Test 3: Action Execution

```python
def test_action_execution():
    """Test that actions execute correctly."""
    
    result = service.execute_suggestion_action(
        conversation_id=conversation_id,
        action="send_reminder",
        data={"appointment_id": 123}
    )
    
    assert result["success"] == True
    assert "תזכורת נשלחה" in result["message"]
```

---

## 🐛 Troubleshooting

### Issue: No suggestions appearing

**Cause:** No data or context available

**Solution:**
```python
# Check if conversation has messages
messages = get_conversation_history(conversation_id)
print(f"Message count: {len(messages)}")

# Check if patient data exists
patient = get_patient_by_phone(conversation.patient_phone)
print(f"Patient: {patient}")
```

---

### Issue: Wrong suggestions showing

**Cause:** Context analysis incorrect

**Solution:**
```python
# Debug context analysis
messages = get_recent_messages(conversation_id)
content = " ".join([m.content for m in messages])
print(f"Content: {content}")

# Check keywords
if "תור" in content:
    print("Detected: appointment intent")
```

---

### Issue: Actions not working

**Cause:** Action handler not implemented

**Solution:**
```python
# Implement action handler
def _handle_custom_action(conversation_id, data):
    """Handle custom action."""
    # Your implementation here
    return {"success": True, "message": "Action completed"}
```

---

## 📚 Additional Resources

- [Proactive Engagement Best Practices](https://www.intercom.com/blog/proactive-support/)
- [Conversational UX Patterns](https://www.nngroup.com/articles/conversational-interfaces/)
- [Notification Timing Research](https://www.sciencedirect.com/science/article/pii/S0747563219303425)

---

**Last Updated:** October 8, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
