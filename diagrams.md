# תרשימי מערכת - AI Dental Clinic Management System

## תרשים ארכיטקטורה כללי

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Interface<br/>React + TypeScript]
        MOBILE[Mobile App<br/>Future Phase]
        WHATSAPP[WhatsApp<br/>Business API]
        TELEGRAM[Telegram<br/>Bot API]
    end
    
    subgraph "API Gateway Layer"
        GATEWAY[Gateway Service<br/>FastAPI - Port 8000]
        WEBHOOKS[Webhook Endpoints<br/>WhatsApp, Telegram]
        HEALTH[Health Check<br/>/health]
        DOCS[API Documentation<br/>/docs]
    end
    
    subgraph "Message Processing Layer"
        REDIS[Redis Queue<br/>Message Broker<br/>Port 6379]
        PROCESSOR[Enhanced Message Processor<br/>OpenManus Engine]
        ROUTER[Message Router<br/>Intent Analysis]
    end
    
    subgraph "AI Agents Layer"
        RECEPTIONIST[Receptionist Agent<br/>General Inquiries<br/>Emergency Detection]
        SCHEDULER[Scheduler Agent<br/>Appointment Management<br/>Availability Check]
        CONFIRMATION[Confirmation Agent<br/>Reminders & Confirmations<br/>Cancellations]
    end
    
    subgraph "Tools & Integration Layer"
        MOCK_TOOL[Enhanced Mock Dental Tool<br/>20 Patients, 4 Doctors<br/>Development Data]
        ADVANCED_TOOL[Advanced Dental Tool<br/>Production Ready<br/>MySQL Integration]
        OPEN_DENTAL[Open Dental API<br/>Awaiting Access<br/>PMS Integration]
    end
    
    subgraph "Data Layer"
        MYSQL[MySQL Database<br/>Patient Data<br/>Port 3306]
        DEMO_DATA[Demo Data<br/>Israeli Patients<br/>Realistic Scenarios]
    end
    
    subgraph "Infrastructure Layer"
        DOCKER[Docker Containers<br/>Microservices]
        MONITORING[Monitoring<br/>Health Checks]
        LOGGING[Centralized Logging<br/>Application Logs]
    end
    
    %% Client connections
    WEB --> GATEWAY
    MOBILE --> GATEWAY
    WHATSAPP --> WEBHOOKS
    TELEGRAM --> WEBHOOKS
    
    %% Gateway layer
    GATEWAY --> REDIS
    WEBHOOKS --> REDIS
    GATEWAY --> HEALTH
    GATEWAY --> DOCS
    
    %% Message processing
    REDIS --> PROCESSOR
    PROCESSOR --> ROUTER
    ROUTER --> RECEPTIONIST
    ROUTER --> SCHEDULER
    ROUTER --> CONFIRMATION
    
    %% Agent tools
    RECEPTIONIST --> MOCK_TOOL
    SCHEDULER --> MOCK_TOOL
    CONFIRMATION --> MOCK_TOOL
    ADVANCED_TOOL --> MYSQL
    MOCK_TOOL --> DEMO_DATA
    OPEN_DENTAL -.-> ADVANCED_TOOL
    
    %% Infrastructure
    DOCKER --> GATEWAY
    DOCKER --> REDIS
    DOCKER --> MYSQL
    MONITORING --> GATEWAY
    MONITORING --> REDIS
    MONITORING --> MYSQL
    LOGGING --> GATEWAY
    LOGGING --> PROCESSOR
    
    %% Styling
    classDef clientLayer fill:#e1f5fe
    classDef gatewayLayer fill:#f3e5f5
    classDef processingLayer fill:#e8f5e8
    classDef agentLayer fill:#fff3e0
    classDef toolLayer fill:#fce4ec
    classDef dataLayer fill:#e0f2f1
    classDef infraLayer fill:#f5f5f5
    
    class WEB,MOBILE,WHATSAPP,TELEGRAM clientLayer
    class GATEWAY,WEBHOOKS,HEALTH,DOCS gatewayLayer
    class REDIS,PROCESSOR,ROUTER processingLayer
    class RECEPTIONIST,SCHEDULER,CONFIRMATION agentLayer
    class MOCK_TOOL,ADVANCED_TOOL,OPEN_DENTAL toolLayer
    class MYSQL,DEMO_DATA dataLayer
    class DOCKER,MONITORING,LOGGING infraLayer
```

## תרשים רצף: קביעת תור

```mermaid
sequenceDiagram
    participant Patient as מטופל
    participant Gateway as Gateway Service
    participant Queue as Redis Queue
    participant Processor as Message Processor
    participant Router as Intent Router
    participant Scheduler as Scheduler Agent
    participant Tool as Enhanced Mock Tool
    participant Data as Demo Data
    
    Patient->>Gateway: POST /api/queue/process-async<br/>{"text": "אני רוצה לקבוע תור", "sender_id": "123"}
    Gateway->>Queue: enqueue message
    Queue-->>Gateway: message queued
    Gateway-->>Patient: {"status": "queued"}
    
    Queue->>Processor: dequeue message
    Processor->>Processor: analyze_intent_advanced()
    Note over Processor: Intent: appointment_scheduling<br/>Confidence: 0.8<br/>Language: Hebrew
    
    Processor->>Router: route_to_agent("appointment_scheduling")
    Router-->>Processor: agent="scheduler"
    
    Processor->>Scheduler: process_message(text, sender_id, context)
    Scheduler->>Scheduler: _handle_scheduler_task()
    
    Scheduler->>Tool: get_available_slots(start_date, end_date)
    Tool->>Data: query available appointments
    Data-->>Tool: available_slots[]
    Tool-->>Scheduler: slots with dates and times
    
    Scheduler->>Scheduler: format_response_hebrew()
    Scheduler-->>Processor: {"response": "זמנים פנויים:\n1. 2025-12-30 09:00\n2. 2025-12-30 10:00", "intent": "appointment_scheduling"}
    
    Processor-->>Queue: response ready
    Queue-->>Gateway: response available
    Gateway-->>Patient: {"success": true, "response": "זמנים פנויים...", "agent": "scheduler"}
    
    Note over Patient,Data: Patient can now select preferred time slot
```

## תרשים רצף: זיהוי חירום

```mermaid
sequenceDiagram
    participant Patient as מטופל
    participant Gateway as Gateway Service
    participant Processor as Message Processor
    participant Receptionist as Receptionist Agent
    participant Emergency as Emergency Protocol
    
    Patient->>Gateway: "יש לי כאב שיניים דחוף!"
    Gateway->>Processor: process emergency message
    
    Processor->>Processor: analyze_intent_advanced()
    Note over Processor: Emergency keywords detected:<br/>["כאב", "דחוף"]<br/>Emergency score: 0.7
    
    alt Emergency Detected (score > 0.3)
        Processor->>Receptionist: handle_emergency_task()
        Receptionist->>Emergency: activate_emergency_protocol()
        Emergency-->>Receptionist: emergency_response_template
        
        Receptionist-->>Processor: {<br/>"response": "🚨 חירום - התקשר: 03-555-0123",<br/>"priority": "critical",<br/>"intent": "emergency"<br/>}
        
        Processor-->>Gateway: emergency response
        Gateway-->>Patient: "🚨 אני מבין שזה דחוף...<br/>התקשר מיד: 03-555-0123"
        
        Note over Emergency: Emergency logged<br/>Priority: CRITICAL<br/>Response time: <2 seconds
    else Normal Processing
        Processor->>Receptionist: handle_general_inquiry()
        Receptionist-->>Processor: standard_response
        Processor-->>Gateway: normal response
        Gateway-->>Patient: standard response
    end
```

## תרשים תלויות בין מודולים

```mermaid
graph LR
    subgraph "Core Services"
        GATEWAY[Gateway Service]
        PROCESSOR[Message Processor]
        AGENTS[AI Agents]
    end
    
    subgraph "AI Engine"
        OPENMANUS[OpenManus Engine]
        FACTORY[AI Engine Factory]
        WRAPPER[Agent Wrapper]
    end
    
    subgraph "Data Tools"
        MOCK[Enhanced Mock Tool]
        ADVANCED[Advanced Dental Tool]
        ADAPTER[Open Dental Adapter]
    end
    
    subgraph "Infrastructure"
        REDIS[Redis Queue]
        MYSQL[MySQL Database]
        I18N[i18n Solution]
    end
    
    subgraph "External APIs"
        OPENAI[OpenAI API]
        OPENDENTAL[Open Dental API]
        WHATSAPP_API[WhatsApp API]
    end
    
    %% Dependencies
    GATEWAY --> REDIS
    GATEWAY --> PROCESSOR
    PROCESSOR --> FACTORY
    FACTORY --> OPENMANUS
    OPENMANUS --> WRAPPER
    WRAPPER --> AGENTS
    AGENTS --> MOCK
    AGENTS --> ADVANCED
    ADVANCED --> MYSQL
    ADVANCED --> ADAPTER
    ADAPTER --> OPENDENTAL
    PROCESSOR --> I18N
    OPENMANUS --> OPENAI
    GATEWAY --> WHATSAPP_API
    
    %% Styling
    classDef coreService fill:#e3f2fd
    classDef aiEngine fill:#f1f8e9
    classDef dataTools fill:#fff8e1
    classDef infrastructure fill:#fce4ec
    classDef externalApi fill:#f3e5f5
    
    class GATEWAY,PROCESSOR,AGENTS coreService
    class OPENMANUS,FACTORY,WRAPPER aiEngine
    class MOCK,ADVANCED,ADAPTER dataTools
    class REDIS,MYSQL,I18N infrastructure
    class OPENAI,OPENDENTAL,WHATSAPP_API externalApi
```

## תרשים מצבי סוכן (Agent State Machine)

```mermaid
stateDiagram-v2
    [*] --> Initializing
    
    Initializing --> Ready: initialize() success
    Initializing --> Error: initialize() failed
    
    Ready --> Processing: receive_message()
    Ready --> Idle: no messages
    
    Processing --> AnalyzingIntent: analyze_intent()
    AnalyzingIntent --> Emergency: emergency detected
    AnalyzingIntent --> Scheduling: appointment intent
    AnalyzingIntent --> Confirmation: confirmation intent
    AnalyzingIntent --> General: general inquiry
    
    Emergency --> ResponseReady: emergency_response()
    Scheduling --> CheckingAvailability: get_available_slots()
    CheckingAvailability --> ResponseReady: slots found
    CheckingAvailability --> NoAvailability: no slots
    NoAvailability --> ResponseReady: alternative_response()
    
    Confirmation --> CheckingAppointments: get_appointments()
    CheckingAppointments --> ResponseReady: appointments found
    CheckingAppointments --> NoAppointments: no appointments
    NoAppointments --> ResponseReady: no_appointments_response()
    
    General --> ResponseReady: general_response()
    
    ResponseReady --> Ready: response_sent()
    ResponseReady --> Error: response_failed()
    
    Error --> Ready: retry_successful()
    Error --> [*]: shutdown()
    
    Idle --> Ready: health_check()
    Ready --> [*]: shutdown()
```

## תרשים זרימת נתונים (Data Flow)

```mermaid
flowchart TD
    subgraph "Input Sources"
        USER_INPUT[User Input<br/>Text Message]
        WEBHOOK_INPUT[Webhook Input<br/>WhatsApp/Telegram]
        API_INPUT[Direct API Call<br/>REST Endpoint]
    end
    
    subgraph "Processing Pipeline"
        VALIDATION[Input Validation<br/>Security Check]
        QUEUE[Redis Queue<br/>Message Buffering]
        PROCESSOR[Message Processor<br/>OpenManus Engine]
        INTENT[Intent Analysis<br/>Confidence Scoring]
        ROUTING[Agent Routing<br/>Specialized Handling]
    end
    
    subgraph "Agent Processing"
        RECEPTIONIST_PROC[Receptionist Processing<br/>General + Emergency]
        SCHEDULER_PROC[Scheduler Processing<br/>Appointments]
        CONFIRMATION_PROC[Confirmation Processing<br/>Reminders]
    end
    
    subgraph "Data Access"
        MOCK_DATA[Mock Data Access<br/>Development]
        DB_ACCESS[Database Access<br/>Production]
        API_ACCESS[External API<br/>Open Dental]
    end
    
    subgraph "Response Generation"
        RESPONSE_FORMAT[Response Formatting<br/>Hebrew/English]
        RESPONSE_VALIDATE[Response Validation<br/>Quality Check]
        RESPONSE_SEND[Response Delivery<br/>Multiple Channels]
    end
    
    %% Flow connections
    USER_INPUT --> VALIDATION
    WEBHOOK_INPUT --> VALIDATION
    API_INPUT --> VALIDATION
    
    VALIDATION --> QUEUE
    QUEUE --> PROCESSOR
    PROCESSOR --> INTENT
    INTENT --> ROUTING
    
    ROUTING --> RECEPTIONIST_PROC
    ROUTING --> SCHEDULER_PROC
    ROUTING --> CONFIRMATION_PROC
    
    RECEPTIONIST_PROC --> MOCK_DATA
    SCHEDULER_PROC --> MOCK_DATA
    CONFIRMATION_PROC --> MOCK_DATA
    
    MOCK_DATA --> RESPONSE_FORMAT
    DB_ACCESS --> RESPONSE_FORMAT
    API_ACCESS --> RESPONSE_FORMAT
    
    RESPONSE_FORMAT --> RESPONSE_VALIDATE
    RESPONSE_VALIDATE --> RESPONSE_SEND
    
    %% Styling
    classDef inputStyle fill:#e8f5e8
    classDef processStyle fill:#e3f2fd
    classDef agentStyle fill:#fff3e0
    classDef dataStyle fill:#fce4ec
    classDef responseStyle fill:#f1f8e9
    
    class USER_INPUT,WEBHOOK_INPUT,API_INPUT inputStyle
    class VALIDATION,QUEUE,PROCESSOR,INTENT,ROUTING processStyle
    class RECEPTIONIST_PROC,SCHEDULER_PROC,CONFIRMATION_PROC agentStyle
    class MOCK_DATA,DB_ACCESS,API_ACCESS dataStyle
    class RESPONSE_FORMAT,RESPONSE_VALIDATE,RESPONSE_SEND responseStyle
```

---

**תרשימים אלו מספקים מבט מקיף על ארכיטקטורת המערכת, זרימות העבודה והתלויות בין הרכיבים השונים.**
