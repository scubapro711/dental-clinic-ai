# תוכנית עבודה מעודכנת V18.2 - Agentic UX Dashboard

**תאריך:** 8 באוקטובר 2025  
**גרסה:** 18.2.0  
**מבוסס על:** תוכנית אב לממשק סוכן אוטונומי (PDF) + ניתוח פרויקט מקיף

---

## 🎯 חזון: Agentic Experience (AX)

### עקרונות מנחים (מתוך ה-PDF)

1. **Mission Control** - המשתמש "מפעיל" את המערכת, לא "מאזר" אותה
2. **שקיפות ובחירת אמון** - המשתמש חייב להבין מה הסוכן עושה
3. **שליטה אנושית ונ יהול כשלים** - האדם תמיד יכול להתערב
4. **המעבר ב"תהליך אינטראקציה"** - מפיקוד מסוכן לארכיטקטורה של מערכת

---

## 📊 Phase 1: Enhanced Agentic Dashboard (Weeks 1-2)

### Week 1: Mission Control Dashboard

**מטרה:** ליצור Dashboard שמתאים לעקרונות Agentic UX

#### Day 1-2: סקירה כללית (Overview)

**Layout (מתוך PDF):**
```
┌─────────────────────────────────────────────────────────┐
│  Header: "מרכז פיקוד DentaFlow"                         │
│  סרגל ניווט צדדי (#001529) + סרגל עליון (#f0f0f0)      │
└─────────────────────────────────────────────────────────┘
│                                                         │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │  סרגל ניווט צדדי  │  │  אזור תוכן מרכזי          │   │
│  │  (24 פיקסלים)    │  │                          │   │
│  │                  │  │  ┌────────────────────┐  │   │
│  │  • לוח מחוונים    │  │  │  KPIs (3 כרטיסים) │  │   │
│  │  • שיחות          │  │  └────────────────────┘  │   │
│  │  • ניתוח ביצועים  │  │                          │   │
│  │  • ניהול ידע      │  │  ┌────────────────────┐  │   │
│  │                  │  │  │  עומדת ימינית (65%) │  │   │
│  └──────────────────┘  │  │  - שיחות פתוחות     │  │   │
│                        │  │  - היסטוריית שיחות  │  │   │
│                        │  └────────────────────┘  │   │
│                        │                          │   │
│                        │  ┌────────────────────┐  │   │
│                        │  │  עומדת שמאלית (35%) │  │   │
│                        │  │  - משימות בביצועים  │  │   │
│                        │  │  - ניתוח ביצועים    │  │   │
│                        │  └────────────────────┘  │   │
│                        └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**KPIs (3 כרטיסים):**
1. **תורים שנקבעו היום** - מספר גדול (פונט 30), ומתחתיו טקסט קטן יותר
2. **שיעור הצלחה (24 שעות)** - אחוז גדול, ומתחתיו טקסט "X" פתוח
3. **זמן טיפול ממוצע** - MM:SS, ומתחתיו טקסט הממוצע השבועי

**Implementation:**
```jsx
// frontend/src/pages/MissionControlDashboard.jsx
import { KPICard } from '../components/dashboard/KPICard';
import { ConversationMonitor } from '../components/dashboard/ConversationMonitor';
import { TaskQueue } from '../components/dashboard/TaskQueue';

export function MissionControlDashboard() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <Sidebar width="24px" bgColor="#001529" />
      
      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Header */}
        <Header title="מרכז פיקוד DentaFlow" />
        
        {/* KPIs */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <KPICard
            title="תורים שנקבעו היום"
            value={14}
            subtitle="(גדול פונט 30), ומתחתיו טקסט קטן יותר"
            trend="+2 מאתמול"
          />
          <KPICard
            title="שיעור הצלחה (24 שעות)"
            value="87%"
            subtitle="X פתוח"
          />
          <KPICard
            title="זמן טיפול ממוצע"
            value="03:45"
            subtitle="ממוצע השבועי: 04:12"
          />
        </div>
        
        {/* Two Columns */}
        <div className="grid grid-cols-[65%_35%] gap-4">
          {/* Right Column (65%) */}
          <div>
            <ConversationMonitor />
          </div>
          
          {/* Left Column (35%) */}
          <div>
            <TaskQueue />
          </div>
        </div>
      </div>
    </div>
  );
}
```

**API Integration:**
```javascript
// Connect to real data
const { data: kpis } = useQuery('/api/v1/dashboard-metrics', {
  refetchInterval: 5000 // Update every 5 seconds
});
```

---

#### Day 3-4: מסך שיחות ובקרה (Conversations)

**Layout (מתוך PDF):**
```
┌─────────────────────────────────────────────────────────┐
│  עומדת סיכון ורשימה (ימין)                              │
│  ┌────────────────────────────────────────────────┐     │
│  │  חלק עליון - שדה חיפוש טקסט                    │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  🔍 חיפוש שיחות...                       │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │  חלק תחתון - רשימת נגלית של כרטיסי שיחות קטנים│     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  📞 יוסי כהן - 14:23                     │  │     │
│  │  │  "רוצה לקבוע תור לניקוי"                 │  │     │
│  │  │  סטטוס: פתוח | אמון: גבוה                │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  📞 שרה לוי - 13:45                       │  │     │
│  │  │  "שאלה על מחיר כתר"                      │  │     │
│  │  │  סטטוס: ממתין | אמון: בינוני             │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  אזור תוכן מרכזי - תצוגת שיחה והשתלטות                  │
│  ┌────────────────────────────────────────────────┐     │
│  │  כותרת: שם המטופל + עריכה מרכזי               │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  יוסי כהן | ערוך                         │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │  מיקום: חופס את 100 הפיקסלים התחתונים של אזור│     │
│  │  התוכן, מופרד מהתחלולול בקו אופקי             │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  💬 הקלד את תגובת האנושית...             │  │     │
│  │  │  [שלח] [העבר לאנושי]                     │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**
```jsx
// frontend/src/components/dashboard/ConversationMonitor.jsx
export function ConversationMonitor() {
  const [conversations, setConversations] = useState([]);
  const [selectedConv, setSelectedConv] = useState(null);
  
  useEffect(() => {
    // Real-time updates via WebSocket
    const ws = new WebSocket('ws://localhost:8000/api/v1/websocket');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'conversation_update') {
        setConversations(prev => updateConversation(prev, data.conversation));
      }
    };
  }, []);
  
  return (
    <div className="grid grid-cols-[30%_70%]">
      {/* Left: Conversation List */}
      <div className="border-r">
        <input
          type="text"
          placeholder="🔍 חיפוש שיחות..."
          className="w-full p-2 border-b"
        />
        <div className="overflow-y-auto">
          {conversations.map(conv => (
            <ConversationCard
              key={conv.id}
              conversation={conv}
              onClick={() => setSelectedConv(conv)}
              selected={selectedConv?.id === conv.id}
            />
          ))}
        </div>
      </div>
      
      {/* Right: Conversation Detail */}
      <div className="flex flex-col">
        {selectedConv && (
          <>
            <ConversationHeader conversation={selectedConv} />
            <ConversationMessages messages={selectedConv.messages} />
            <HumanHandoffInput conversationId={selectedConv.id} />
          </>
        )}
      </div>
    </div>
  );
}
```

---

#### Day 5: מסך ניתוח ביצועים (Performance)

**Layout (מתוך PDF):**
```
┌─────────────────────────────────────────────────────────┐
│  סרגל פילטרים עליון ורשת של כרטיסי גרפים                │
│  ┌────────────────────────────────────────────────┐     │
│  │  🗓️ בחר טווח תאריכים | 📊 בחר מטריקה          │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────────────┐      │
│  │  גרף משפך       │  │  נפח שיחות לפי ערוץ     │      │
│  │  (Funnel)       │  │  (Stacked Bar Chart)    │      │
│  └─────────────────┘  └─────────────────────────┘      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  גרף עומדות אופקי המציג את השאלות הנפוצות      │   │
│  │  (RAG - Retrieval Augmented Generation)        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**
```jsx
// frontend/src/components/dashboard/PerformanceAnalytics.jsx
import { FunnelChart } from '../charts/FunnelChart';
import { StackedBarChart } from '../charts/StackedBarChart';
import { RAGQuestionsChart } from '../charts/RAGQuestionsChart';

export function PerformanceAnalytics() {
  const [dateRange, setDateRange] = useState('last_7_days');
  const [metric, setMetric] = useState('appointments');
  
  const { data: analytics } = useQuery(
    `/api/v1/dashboard/analytics?range=${dateRange}&metric=${metric}`
  );
  
  return (
    <div>
      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <DateRangePicker value={dateRange} onChange={setDateRange} />
        <MetricSelector value={metric} onChange={setMetric} />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <FunnelChart data={analytics?.funnel} />
        <StackedBarChart data={analytics?.channels} />
      </div>
      
      <div>
        <RAGQuestionsChart data={analytics?.rag_questions} />
      </div>
    </div>
  );
}
```

---

### Week 2: ניהול ידע (Knowledge Management)

#### Day 1-2: עמודת ניווט (עם קבצים)

**Layout (מתוך PDF):**
```
┌─────────────────────────────────────────────────────────┐
│  להציג על קובץ טוענת את המשק agent_kb                   │
│  ┌────────────────────────────────────────────────┐     │
│  │  📁 בסיס ידע                                   │     │
│  │  ├── 📄 מדריך טיפולים.pdf                     │     │
│  │  ├── 📄 מחירון 2025.xlsx                       │     │
│  │  ├── 📄 שאלות נפוצות.md                        │     │
│  │  └── 📄 הנחיות HIPAA.pdf                       │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  אזור עריכה מרכזי (משאבה לפי סוג הקובץ)                │
│  ┌────────────────────────────────────────────────┐     │
│  │  עבור קובץ .yaml:                              │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  משקל: לוח שנה שבועי ויזואלי               │     │
│  │  │  עבודה                                    │     │
│  │  └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │  עבור קובץ שיחות:                              │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  כל תא הוכר לשדה קלט (EditableTable)     │     │
│  │  │  בהזמאה                                   │     │
│  │  └──────────────────────────────────────────┘  │     │
│  │                                                │     │
│  │  עבור קובץ שאלות נפוצות:                       │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  כל פריט הוא שאלה, והציצה מהריבה אותו     │     │
│  │  │  (Collapse). והוספת תיבת טקסט לעריכת התשובה│     │
│  │  └──────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**
```jsx
// frontend/src/components/dashboard/KnowledgeManagement.jsx
export function KnowledgeManagement() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  
  useEffect(() => {
    // Load knowledge base files
    fetch('/api/v1/knowledge-base/files')
      .then(res => res.json())
      .then(setFiles);
  }, []);
  
  return (
    <div className="grid grid-cols-[25%_75%]">
      {/* File Tree */}
      <div className="border-r p-4">
        <h3>📁 בסיס ידע</h3>
        <FileTree
          files={files}
          onSelect={setSelectedFile}
          selected={selectedFile}
        />
      </div>
      
      {/* Editor */}
      <div className="p-4">
        {selectedFile && (
          <FileEditor
            file={selectedFile}
            onSave={(content) => saveFile(selectedFile.id, content)}
          />
        )}
      </div>
    </div>
  );
}

// Different editors based on file type
function FileEditor({ file, onSave }) {
  switch (file.type) {
    case 'yaml':
      return <ScheduleEditor file={file} onSave={onSave} />;
    case 'csv':
      return <EditableTable file={file} onSave={onSave} />;
    case 'faq':
      return <FAQEditor file={file} onSave={onSave} />;
    default:
      return <TextEditor file={file} onSave={onSave} />;
  }
}
```

---

#### Day 3-5: ממשק השתלטות ו-Human Handoff

**Layout (מתוך PDF):**
```
┌─────────────────────────────────────────────────────────┐
│  מיקום: חופס את 100 הפיקסלים התחתונים של אזור התוכן     │
│  ┌────────────────────────────────────────────────┐     │
│  │  💬 הקלד את תגובת האנושית...                   │     │
│  │  ┌──────────────────────────────────────────┐  │     │
│  │  │  [שלח] [העבר לאנושי] [סגור שיחה]         │  │     │
│  │  └──────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  כפתור שליחה: כמו ראשי עם איקון "שאול" ושמאל            │     │
│  כפתור שליחת: כפתור כחול ראשי עם איקון "טוסט ניירי"    │     │
│  והקטסט "שלח"                                           │     │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**
```jsx
// frontend/src/components/dashboard/HumanHandoff.jsx
export function HumanHandoffInput({ conversationId }) {
  const [message, setMessage] = useState('');
  const [isHandoff, setIsHandoff] = useState(false);
  
  const handleSend = async () => {
    if (isHandoff) {
      // Transfer to human
      await fetch(`/api/v1/handoff/${conversationId}`, {
        method: 'POST',
        body: JSON.stringify({ message })
      });
    } else {
      // Send message as human
      await fetch(`/api/v1/conversations/${conversationId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content: message, from: 'human' })
      });
    }
    setMessage('');
  };
  
  return (
    <div className="border-t p-4 h-[100px]">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="💬 הקלד את תגובת האנושית..."
        className="w-full h-12 p-2 border rounded"
      />
      <div className="flex gap-2 mt-2">
        <button
          onClick={handleSend}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          📤 שלח
        </button>
        <button
          onClick={() => setIsHandoff(true)}
          className="bg-orange-500 text-white px-4 py-2 rounded"
        >
          🙋 העבר לאנושי
        </button>
        <button
          onClick={() => closeConversation(conversationId)}
          className="bg-gray-500 text-white px-4 py-2 rounded"
        >
          ❌ סגור שיחה
        </button>
      </div>
    </div>
  );
}
```

---

## 📊 Phase 2: Backend Enhancements (Weeks 3-4)

### Week 3: Real-time Updates & WebSocket

**Goal:** הוסף real-time updates לכל ה-Dashboard

**Implementation:**
```python
# backend/app/api/v1/endpoints/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, organization_id: str):
        await websocket.accept()
        if organization_id not in self.active_connections:
            self.active_connections[organization_id] = set()
        self.active_connections[organization_id].add(websocket)
    
    async def broadcast(self, organization_id: str, message: dict):
        if organization_id in self.active_connections:
            for connection in self.active_connections[organization_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/api/v1/ws/{organization_id}")
async def websocket_endpoint(websocket: WebSocket, organization_id: str):
    await manager.connect(websocket, organization_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
    except WebSocketDisconnect:
        manager.disconnect(websocket, organization_id)
```

**Events to broadcast:**
```python
# When new conversation starts
await manager.broadcast(org_id, {
    "type": "conversation_started",
    "conversation": conversation_dict
})

# When agent takes action
await manager.broadcast(org_id, {
    "type": "agent_action",
    "action": action_dict
})

# When metrics update
await manager.broadcast(org_id, {
    "type": "metrics_update",
    "metrics": metrics_dict
})
```

---

### Week 4: Knowledge Base API

**Goal:** API לניהול בסיס ידע

**Implementation:**
```python
# backend/app/api/v1/endpoints/knowledge_base.py
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.get("/api/v1/knowledge-base/files")
async def list_files(organization_id: str):
    """List all knowledge base files."""
    files = await get_kb_files(organization_id)
    return files

@router.post("/api/v1/knowledge-base/files")
async def upload_file(
    organization_id: str,
    file: UploadFile = File(...)
):
    """Upload a new file to knowledge base."""
    # Save file
    file_path = await save_file(organization_id, file)
    
    # Index file for RAG
    await index_file_for_rag(file_path)
    
    return {"file_id": file_path, "status": "indexed"}

@router.put("/api/v1/knowledge-base/files/{file_id}")
async def update_file(file_id: str, content: str):
    """Update file content."""
    await update_kb_file(file_id, content)
    
    # Re-index for RAG
    await reindex_file(file_id)
    
    return {"status": "updated"}

@router.delete("/api/v1/knowledge-base/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file from knowledge base."""
    await delete_kb_file(file_id)
    return {"status": "deleted"}
```

---

## 📊 סיכום תוכנית העבודה

### Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 0** | ✅ 1 day | Odoo fixed, data populated |
| **Phase 1** | 2 weeks | Agentic Dashboard (Mission Control, Conversations, Performance, Knowledge) |
| **Phase 2** | 2 weeks | Real-time updates, Knowledge Base API |
| **Phase 3** | 2 weeks | Onboarding integration, Landing page |
| **Phase 4** | 2 weeks | AWS deployment, CI/CD, Monitoring |
| **Total** | **8 weeks** | Production-ready Agentic UX system |

---

### עקרונות מנחים לכל הפיתוח

1. **Mission Control** - המשתמש תמיד בשליטה
2. **Transparency** - תמיד להראות מה הסוכן עושה
3. **Human Handoff** - תמיד אפשרות להתערבות אנושית
4. **Real-time** - עדכונים בזמן אמת
5. **Agentic UX** - ממשק שמתאים לעידן הסוכנים

---

**הפרויקט מוכן להמשך פיתוח לפי עקרונות Agentic UX! 🚀**

