# Harper - HIPAA Compliance Agent

## Overview

Harper is DentaFlow's AI-powered HIPAA Compliance Agent, designed to provide real-time compliance monitoring, guidance, and proactive alerts for dental clinics. Built with LangGraph V4 and powered by GPT-4.1-mini, Harper helps clinic administrators maintain HIPAA compliance through intelligent automation and expert guidance.

## Features

### 🤖 AI-Powered Compliance Guidance
- **RAG-Powered Knowledge Base**: 33 comprehensive HIPAA documents stored in Pinecone vector database
- **Real-time Q&A**: Instant answers to HIPAA compliance questions
- **Contextual Recommendations**: Tailored advice based on your clinic's specific situation
- **Suggested Actions**: Proactive suggestions for compliance improvements

### 🛡️ 10 Specialized Compliance Tools

1. **search_hipaa_knowledge**: Search the comprehensive HIPAA knowledge base
2. **check_phi_compliance**: Validate PHI handling and security measures
3. **validate_baa**: Verify Business Associate Agreements
4. **assess_security_controls**: Evaluate technical, administrative, and physical safeguards
5. **generate_breach_report**: Create breach notification reports
6. **audit_access_logs**: Review PHI access patterns and detect anomalies
7. **check_patient_rights**: Verify compliance with patient rights requests
8. **evaluate_risk**: Perform HIPAA risk assessments
9. **generate_compliance_report**: Create comprehensive compliance reports
10. **recommend_remediation**: Provide actionable remediation plans

### 📊 Proactive Monitoring System

Harper automatically monitors your clinic's compliance status and generates alerts for:

- **BAA Expirations**: Alerts 30 days before BAA expiration
- **PHI Compliance Issues**: Detects encryption, access control, and storage violations
- **Security Gaps**: Identifies missing or inadequate security controls
- **Access Anomalies**: Flags suspicious PHI access patterns
- **Risk Threshold Violations**: Monitors overall risk levels
- **Breach Detection**: Identifies potential HIPAA breaches
- **Patient Rights Violations**: Tracks compliance with patient requests
- **Audit Findings**: Documents compliance gaps discovered during audits

### 📈 Compliance Dashboard

- **Real-time Compliance Score**: Overall, PHI, and Security scores
- **Alert Management**: Track and resolve compliance issues
- **Trend Analysis**: Historical compliance metrics and trends
- **Quick Actions**: One-click access to common compliance tasks

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Harper Agent                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  LangGraph V4 State Machine                       │ │
│  │  ├─ Input Node: Process user queries              │ │
│  │  ├─ Tool Node: Execute compliance tools           │ │
│  │  └─ Output Node: Generate responses               │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  10 Specialized Tools                             │ │
│  │  ├─ search_hipaa_knowledge (RAG)                  │ │
│  │  ├─ check_phi_compliance                          │ │
│  │  ├─ validate_baa                                  │ │
│  │  ├─ assess_security_controls                      │ │
│  │  ├─ generate_breach_report                        │ │
│  │  ├─ audit_access_logs                             │ │
│  │  ├─ check_patient_rights                          │ │
│  │  ├─ evaluate_risk                                 │ │
│  │  ├─ generate_compliance_report                    │ │
│  │  └─ recommend_remediation                         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Knowledge Base (Pinecone)                        │ │
│  │  ├─ 4 Regulation Summaries                        │ │
│  │  ├─ 5 FAQ Documents (100 Q&A)                     │ │
│  │  ├─ 3 Best Practice Guides                        │ │
│  │  └─ 7 Policy Templates                            │ │
│  │  Total: 33 documents, 2,430+ lines                │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Proactive Monitoring Service               │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Daily Checks (Every 24h)                         │ │
│  │  ├─ BAA expiration monitoring                     │ │
│  │  ├─ PHI compliance verification                   │ │
│  │  ├─ Access anomaly detection                      │ │
│  │  └─ Risk level assessment                         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Weekly Checks (Every 7 days)                     │ │
│  │  ├─ Security controls assessment                  │ │
│  │  ├─ Compliance score calculation                  │ │
│  │  └─ Weekly summary generation                     │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Monthly Checks (Every 30 days)                   │ │
│  │  ├─ Comprehensive compliance report               │ │
│  │  ├─ Trend analysis                                │ │
│  │  └─ Risk assessment summary                       │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### Chat with Harper

```http
POST /api/v1/compliance/chat
```

**Request:**
```json
{
  "message": "What are the requirements for PHI encryption?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous message...",
      "timestamp": "2025-01-19T10:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "response": "Under HIPAA Security Rule, PHI encryption is addressable...",
  "suggested_actions": [
    {
      "label": "Check current encryption status",
      "action": "check_phi_compliance"
    }
  ]
}
```

### Get Compliance Score

```http
GET /api/v1/compliance/score
```

**Response:**
```json
{
  "overall": 87,
  "phi": 90,
  "security": 85,
  "phi_findings": 3,
  "security_gaps": 5
}
```

### Get Compliance Alerts

```http
GET /api/v1/compliance/alerts?status=open&severity=critical
```

**Response:**
```json
[
  {
    "id": 1,
    "organization_id": 123,
    "alert_type": "baa_expired",
    "severity": "critical",
    "status": "open",
    "title": "Business Associate Agreement Expired",
    "description": "BAA with XYZ Vendor expired on 2025-01-15",
    "action_required": "Renew BAA immediately or cease data sharing",
    "deadline": "IMMEDIATE",
    "created_at": "2025-01-16T08:00:00Z"
  }
]
```

### Manage Alerts

```http
POST /api/v1/compliance/alerts/{alert_id}/acknowledge
POST /api/v1/compliance/alerts/{alert_id}/start_progress
POST /api/v1/compliance/alerts/{alert_id}/resolve
POST /api/v1/compliance/alerts/{alert_id}/dismiss
```

**Request:**
```json
{
  "notes": "Contacted vendor, renewal in progress"
}
```

### Get Compliance Metrics

```http
GET /api/v1/compliance/metrics
```

**Response:**
```json
{
  "overall_score": 87,
  "overall_trend": 5,
  "overall_last_month": 82,
  "phi_score": 90,
  "phi_trend": 3,
  "security_score": 85,
  "risk_level": "medium",
  "total_risks": 8,
  "critical_risks": 1,
  "high_risks": 2,
  "recent_activity": [
    {
      "description": "BAA renewed with Vendor X",
      "timestamp": "2025-01-18T14:30:00Z"
    }
  ]
}
```

### Run Compliance Checks (Super Admin Only)

```http
POST /api/v1/compliance/monitoring/run-checks?check_type=daily
```

## Database Schema

### compliance_alerts

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| organization_id | Integer | Organization FK |
| alert_type | Enum | Type of alert |
| severity | Enum | critical, high, medium, low, info |
| status | Enum | open, acknowledged, in_progress, resolved, dismissed |
| title | String | Alert title |
| description | Text | Detailed description |
| action_required | Text | Required actions |
| deadline | String | Deadline description |
| deadline_date | DateTime | Parsed deadline |
| metadata | JSON | Additional context |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update |
| acknowledged_at | DateTime | Acknowledgment time |
| acknowledged_by | Integer | User FK |
| resolved_at | DateTime | Resolution time |
| resolved_by | Integer | User FK |
| resolution_notes | Text | Resolution details |

### compliance_metrics

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| organization_id | Integer | Organization FK |
| recorded_at | DateTime | Recording timestamp |
| metric_type | String | Type of metric |
| value | Integer | Score (0-100) |
| details | JSON | Detailed breakdown |
| period_type | String | daily, weekly, monthly |
| period_start | DateTime | Period start |
| period_end | DateTime | Period end |

## Role-Based Access Control

Harper is accessible to the following roles:

| Role | Access Level |
|------|-------------|
| **super_admin** | Full access to all Harper features |
| **clinic_admin** | Full access to organization's compliance data |
| **doctor** | Read-only access to general HIPAA guidance |
| **patient** | No access |

## Frontend Components

### HarperDashboard.jsx
Main compliance dashboard with:
- Compliance score overview
- Active alerts summary
- Quick actions
- Metrics visualization

### HarperChat.jsx
Interactive chat interface for:
- Real-time Q&A with Harper
- Suggested actions
- Conversation history

### ComplianceAlerts.jsx
Alert management interface with:
- Tabbed view (Open, Acknowledged, In Progress, Resolved)
- Status tracking
- Action buttons
- Resolution notes

### ComplianceMetrics.jsx
Metrics visualization with:
- Trend indicators
- Historical comparisons
- Recent activity feed

## Deployment

### 1. Database Migration

```bash
cd backend
alembic upgrade head
```

### 2. Upload Knowledge Base to Pinecone

```bash
cd backend
python scripts/upload_hipaa_knowledge.py
```

### 3. Configure Environment Variables

```bash
# .env
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

### 6. Access Harper

Navigate to: `http://localhost:3000/compliance`

## Testing

### Manual Testing

1. **Test Harper Chat:**
   - Navigate to `/compliance`
   - Click "Ask Harper"
   - Ask: "What are the requirements for PHI encryption?"
   - Verify response and suggested actions

2. **Test Alert Management:**
   - Navigate to `/compliance`
   - View active alerts
   - Acknowledge an alert
   - Mark as resolved with notes

3. **Test Compliance Score:**
   - Navigate to `/compliance`
   - Verify compliance score displays
   - Check trend indicators

### API Testing

```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/compliance/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "What is PHI?"}'

# Test compliance score
curl http://localhost:8000/api/v1/compliance/score \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test alerts
curl http://localhost:8000/api/v1/compliance/alerts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Monitoring

### Scheduled Checks

Harper automatically runs compliance checks:

- **Daily (00:00 UTC)**: BAA expirations, PHI compliance, access anomalies
- **Weekly (Monday 00:00 UTC)**: Security controls, compliance score
- **Monthly (1st of month 00:00 UTC)**: Comprehensive report, trend analysis

### Alert Notifications

Alerts are sent via:
- Email (to clinic admins)
- Dashboard notifications
- SMS (for critical alerts)

## Troubleshooting

### Harper Not Responding

1. Check OpenAI API key is valid
2. Verify Pinecone index exists and has data
3. Check backend logs for errors

### Alerts Not Generating

1. Verify monitoring service is running
2. Check scheduled tasks are configured
3. Review database for existing alerts

### Compliance Score Not Updating

1. Run manual compliance check
2. Verify metrics are being recorded
3. Check database for recent metrics

## Support

For issues or questions:
- Email: support@dentaflow.com
- Documentation: https://docs.dentaflow.com/harper
- GitHub Issues: https://github.com/dentaflow/issues

## License

Copyright © 2025 DentaFlow. All rights reserved.

