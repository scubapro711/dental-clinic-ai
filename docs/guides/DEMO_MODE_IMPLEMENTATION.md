# Demo Mode Implementation Guide

## Overview

This document describes the complete implementation of **Interactive Demo Mode** for DentaFlow, allowing potential customers to try the system without creating an account.

## Architecture

### Backend Components

#### 1. **State Management** (`backend/app/agents/graph_state.py`)
- Added `demo_mode: bool` field to `AgentState`
- Added `demo_session_id: Optional[str]` for session tracking

#### 2. **Demo Data Service** (`backend/app/services/demo_data.py`)
Provides realistic mock data:
- 5 demo patients (Sarah Johnson, David Cohen, Rachel Levi, Michael Green, Tamar Shapiro)
- 3 demo doctors (Dr. Rachel Cohen, Dr. Yossi Mizrahi, Dr. Maya Goldstein)
- 30 days of appointments
- Sample invoices
- Financial summary
- Clinic information

#### 3. **Demo Knowledge Base** (`backend/app/knowledge/demo_knowledge.json`)
12 knowledge documents covering:
- What is DentaFlow
- Why it's not a chatbot
- The 4 AI agents
- Multi-channel communication
- Odoo integration
- Pricing plans
- Implementation process
- ROI and time savings
- Security and compliance
- Free trial and pilot program

#### 4. **RAG Tools** (`backend/app/agents/tools/rag_tools.py`)
- `search_demo_knowledge_tool()` - Search product knowledge base

#### 5. **Demo Tools** (`backend/app/agents/tools/demo_tools.py`)
7 specialized tools for demo mode:
- `get_demo_patient_tool()` - Get patient information
- `get_demo_appointments_tool()` - Get appointments
- `get_demo_available_slots_tool()` - Get available time slots
- `get_demo_invoices_tool()` - Get billing information
- `get_demo_financial_summary_tool()` - Get financial metrics
- `get_demo_clinic_info_tool()` - Get clinic details
- `book_demo_appointment_tool()` - Simulate booking

#### 6. **Alex Demo Prompt** (`backend/app/agents/alex_demo_prompt.py`)
Comprehensive system prompt for demo mode:
- Product demonstration guidelines
- Feature guidance
- Sales-aware personality
- Conversion tactics
- Educational approach
- Example responses

#### 7. **Alex Agent** (`backend/app/agents/alex_v2.py`)
Updated to support demo mode:
- `__init__(demo_mode: bool = False)` parameter
- Selects appropriate system prompt based on mode
- Uses demo tools in demo mode, production tools otherwise

#### 8. **Agent Graph** (`backend/app/agents/agent_graph_v4.py`)
Updated to support demo mode:
- `__init__(memory=None, demo_mode: bool = False)` parameter
- Passes demo_mode to AlexAgent

#### 9. **Demo API Endpoints** (`backend/app/api/v1/endpoints/demo.py`)
RESTful API for demo sessions:
- `POST /api/v1/demo/session/create` - Create new demo session (30 min)
- `POST /api/v1/demo/chat` - Send message in demo mode
- `GET /api/v1/demo/session/{session_id}/status` - Get session status
- `DELETE /api/v1/demo/session/{session_id}` - End session
- `GET /api/v1/demo/stats` - Get demo usage statistics

### Frontend Components

#### 1. **InteractiveDemoChat** (`frontend/src/components/InteractiveDemoChat.jsx`)
Main chat component:
- Creates demo session on mount
- Sends/receives messages via API
- Displays conversation history
- Shows suggested actions
- Displays time remaining
- Auto-scrolls to latest message
- Handles session expiration

#### 2. **InteractiveDemoChat.css** (`frontend/src/components/InteractiveDemoChat.css`)
Styling for chat component:
- Modern, clean design
- Gradient header
- Smooth animations
- Typing indicator
- Mobile responsive
- Accessible

#### 3. **DemoChatButton** (`frontend/src/components/DemoChatButton.jsx`)
Floating action button:
- Opens/closes demo chat
- Pulsing animation
- Mobile responsive

#### 4. **DemoChatButton.css** (`frontend/src/components/DemoChatButton.css`)
Styling for FAB:
- Gradient background
- Pulse animation
- Hover effects
- Mobile responsive (shows only icon on small screens)

## Usage

### Backend

#### Starting Demo Mode

```python
from app.agents.agent_graph_v4 import AgentGraphV4

# Create demo graph
demo_graph = AgentGraphV4(demo_mode=True)

# Prepare demo state
state = {
    'messages': [HumanMessage(content="Hello!")],
    'demo_mode': True,
    'demo_session_id': 'demo_123',
    # ... other required fields
}

# Invoke
result = demo_graph.graph.invoke(state, config)
```

#### API Usage

```bash
# Create demo session
curl -X POST http://localhost:8000/api/v1/demo/session/create

# Response:
# {
#   "session_id": "demo_abc123",
#   "expires_at": "2025-10-16T15:30:00",
#   "message": "Welcome to DentaFlow Interactive Demo! ..."
# }

# Send message
curl -X POST http://localhost:8000/api/v1/demo/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_abc123",
    "message": "Can I schedule an appointment?"
  }'

# Response:
# {
#   "session_id": "demo_abc123",
#   "message": "Absolutely! Let me check our availability...",
#   "suggested_actions": ["Check patient info", "Ask about pricing"],
#   "session_active": true,
#   "time_remaining": 1750
# }
```

### Frontend

#### Integration with Landing Page

```jsx
import DemoChatButton from './components/DemoChatButton';

function LandingPage() {
  return (
    <div>
      {/* Your landing page content */}
      
      {/* Add demo chat button */}
      <DemoChatButton />
    </div>
  );
}
```

#### Standalone Usage

```jsx
import InteractiveDemoChat from './components/InteractiveDemoChat';

function DemoPage() {
  const [showChat, setShowChat] = useState(true);

  return (
    <div>
      {showChat && (
        <InteractiveDemoChat onClose={() => setShowChat(false)} />
      )}
    </div>
  );
}
```

## Features

### Demo Session Management
- **Duration:** 30 minutes per session
- **Message Limit:** 50 messages per session
- **Auto-Expiration:** Sessions automatically expire after 30 minutes
- **Cleanup:** Expired sessions are automatically removed
- **No Authentication:** No signup required

### Alex Capabilities in Demo Mode
1. **Product Knowledge**
   - Answers questions about DentaFlow features
   - Explains pricing and plans
   - Describes implementation process
   - Compares to chatbots

2. **Demo Data Operations**
   - Look up demo patients
   - Check appointments
   - Show available slots
   - Display invoices
   - Show financial summary
   - Simulate booking appointments

3. **Conversion Tactics**
   - Suggests free trial after demonstration
   - Mentions pilot program (6 months free)
   - Offers personalized demo call
   - Highlights time savings and ROI

### User Experience
- **Instant Access:** No signup required
- **Guided Exploration:** Suggested actions guide users
- **Time Awareness:** Timer shows remaining session time
- **Mobile Responsive:** Works on all devices
- **Accessible:** ARIA labels and keyboard navigation

## Deployment

### Backend Deployment

1. **Ensure all dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Demo knowledge base is loaded automatically** on module import

3. **API endpoints are registered** in `app/api/v1/__init__.py`

4. **No database required** - demo sessions stored in-memory (use Redis for production)

### Frontend Deployment

1. **Add components to your app:**
   ```bash
   # Components are already created in:
   # frontend/src/components/InteractiveDemoChat.jsx
   # frontend/src/components/InteractiveDemoChat.css
   # frontend/src/components/DemoChatButton.jsx
   # frontend/src/components/DemoChatButton.css
   ```

2. **Import and use in landing page:**
   ```jsx
   import DemoChatButton from './components/DemoChatButton';
   ```

3. **Set API URL in .env:**
   ```
   REACT_APP_API_URL=https://api.dentaflow.ai
   ```

## Production Considerations

### Session Storage
Currently using in-memory storage. For production:

```python
# Use Redis for session storage
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Store session
redis_client.setex(
    f"demo_session:{session_id}",
    1800,  # 30 minutes TTL
    json.dumps(session_data)
)
```

### Rate Limiting
Add rate limiting per IP:

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post("/chat", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def demo_chat(request: DemoChatMessage):
    # ...
```

### Analytics
Track demo usage:

```python
# Log demo events
logger.info(f"Demo event: {event_type}", extra={
    'session_id': session_id,
    'message_count': message_count,
    'duration': duration,
    'converted': converted_to_trial
})
```

### Security
- **Input Validation:** Validate all user inputs
- **XSS Protection:** Sanitize message content
- **CORS:** Configure CORS for production domain
- **Rate Limiting:** Prevent abuse

## Testing

### Backend Tests

```python
# Test demo session creation
def test_create_demo_session():
    response = client.post("/api/v1/demo/session/create")
    assert response.status_code == 200
    assert "session_id" in response.json()

# Test demo chat
def test_demo_chat():
    # Create session
    session = client.post("/api/v1/demo/session/create").json()
    
    # Send message
    response = client.post("/api/v1/demo/chat", json={
        "session_id": session["session_id"],
        "message": "Hello"
    })
    
    assert response.status_code == 200
    assert "message" in response.json()
```

### Frontend Tests

```jsx
// Test InteractiveDemoChat component
import { render, screen, fireEvent } from '@testing-library/react';
import InteractiveDemoChat from './InteractiveDemoChat';

test('creates demo session on mount', async () => {
  render(<InteractiveDemoChat onClose={() => {}} />);
  
  // Wait for welcome message
  const welcomeMessage = await screen.findByText(/Welcome to DentaFlow/i);
  expect(welcomeMessage).toBeInTheDocument();
});

test('sends message when user types and clicks send', async () => {
  render(<InteractiveDemoChat onClose={() => {}} />);
  
  const input = screen.getByPlaceholderText(/Type your message/i);
  const sendButton = screen.getByRole('button', { name: /send/i });
  
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.click(sendButton);
  
  // Check that message appears
  expect(await screen.findByText('Hello')).toBeInTheDocument();
});
```

## Monitoring

### Metrics to Track
- **Session Creation Rate:** Sessions created per hour/day
- **Average Session Duration:** How long users engage
- **Message Count:** Average messages per session
- **Conversion Rate:** Demo → Free Trial signup
- **Popular Questions:** Most asked questions in demo
- **Drop-off Points:** Where users leave the demo

### Dashboard Queries

```sql
-- Demo sessions created today
SELECT COUNT(*) FROM demo_sessions 
WHERE created_at >= CURRENT_DATE;

-- Average messages per session
SELECT AVG(message_count) FROM demo_sessions;

-- Conversion rate
SELECT 
  COUNT(*) as total_demos,
  SUM(CASE WHEN converted_to_trial THEN 1 ELSE 0 END) as conversions,
  (SUM(CASE WHEN converted_to_trial THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as conversion_rate
FROM demo_sessions;
```

## Future Enhancements

1. **Multi-Agent Demo**
   - Add demo modes for Sarah, Marcus, Sophia
   - Show agent handoffs in demo

2. **Guided Tours**
   - Step-by-step feature walkthrough
   - Interactive tutorials

3. **Personalization**
   - Collect clinic type (general, orthodontics, etc.)
   - Show relevant features based on clinic type

4. **Video Demos**
   - Embed video demonstrations
   - Screen recordings of features

5. **Lead Capture**
   - Optional email capture for follow-up
   - Send demo transcript via email

6. **A/B Testing**
   - Test different demo prompts
   - Optimize conversion tactics

## Support

For questions or issues:
- **Documentation:** See this file
- **Code:** Check inline comments in source files
- **API Docs:** Visit `/docs` endpoint when backend is running
- **Team:** Contact development team

## License

Internal use only. Not for redistribution.

---

**Last Updated:** October 16, 2025  
**Version:** 1.0.0  
**Author:** DentaFlow Development Team

