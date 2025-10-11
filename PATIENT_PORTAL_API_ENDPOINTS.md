# Patient Portal API Endpoints

**תאריך:** 11 באוקטובר 2025  
**Backend URL:** http://localhost:8002  
**Swagger UI:** http://localhost:8002/docs

---

## 📊 סיכום

**סה"כ endpoints במערכת:** 105  
**Patient Portal related:** 21 endpoints

---

## 🏥 Patient Profile & Health

### GET `/api/v1/patient/profile`
**תיאור:** קבלת פרופיל מטופל  
**Authentication:** Required  
**Response:**
```json
{
  "id": 1,
  "name": "Sarah Johnson",
  "email": "sarah@example.com",
  "phone": "+1 (555) 123-4567",
  "date_of_birth": "1985-03-15",
  "address": "123 Main St, New York, NY 10001",
  "insurance": {
    "provider": "HealthCare Plus",
    "policy_number": "HC123456789",
    "group_number": "GRP001"
  }
}
```

### GET `/api/v1/patient/health-score`
**תיאור:** קבלת ציון בריאות שיניים  
**Authentication:** Required  
**Response:**
```json
{
  "score": 85,
  "message": "Your dental health is in great shape!",
  "factors": [
    {"label": "Regular checkups", "status": "good", "value": 95},
    {"label": "Good oral hygiene", "status": "good", "value": 90},
    {"label": "Next cleaning due soon", "status": "warning", "value": 70}
  ],
  "recommendations": [
    "Schedule your next cleaning appointment",
    "Continue brushing twice daily"
  ],
  "last_updated": "2025-10-11T10:00:00"
}
```

---

## 📅 Appointments

### GET `/api/v1/appointments`
**תיאור:** קבלת רשימת תורים  
**Authentication:** Required  
**Query Parameters:**
- `status` (optional): upcoming, past, cancelled, all
- `limit` (optional): 1-100, default 10
- `offset` (optional): pagination offset

**Response:**
```json
{
  "appointments": [
    {
      "id": 1,
      "date": "2025-10-15",
      "time": "14:00",
      "doctor": "Dr. Sarah Goldstein",
      "type": "Routine Cleaning",
      "duration": "45 min",
      "status": "confirmed",
      "location": "Main Clinic"
    }
  ],
  "total": 10,
  "limit": 10,
  "offset": 0
}
```

### GET `/api/v1/appointments/today`
**תיאור:** תורים להיום  
**Authentication:** Required

### GET `/api/v1/appointments/available-slots`
**תיאור:** חריצי זמן פנויים  
**Authentication:** Required  
**Query Parameters:**
- `date` (required): YYYY-MM-DD
- `doctor_id` (optional): filter by doctor
- `appointment_type` (optional): filter by type

### GET `/api/v1/appointments/{appointment_id}`
**תיאור:** פרטי תור ספציפי  
**Authentication:** Required

### POST `/api/v1/appointments/{appointment_id}/cancel`
**תיאור:** ביטול תור  
**Authentication:** Required

---

## 💰 Billing & Payments

### GET `/api/v1/billing/overview`
**תיאור:** סקירת חיובים  
**Authentication:** Required  
**Response:**
```json
{
  "outstanding_balance": 500.00,
  "total_paid": 2500.00,
  "pending_invoices": 2,
  "last_payment": {
    "date": "2025-09-15",
    "amount": 150.00,
    "method": "Credit Card"
  }
}
```

### GET `/api/v1/billing/invoices`
**תיאור:** רשימת חשבוניות  
**Authentication:** Required  
**Query Parameters:**
- `status` (optional): paid, pending, overdue, all
- `limit` (optional): 1-100
- `offset` (optional): pagination

**Response:**
```json
{
  "invoices": [
    {
      "id": 1,
      "invoice_number": "INV-2025-001",
      "date": "2025-09-15",
      "due_date": "2025-10-15",
      "amount": 150.00,
      "status": "paid",
      "items": [
        {
          "description": "Routine Cleaning",
          "quantity": 1,
          "price": 150.00
        }
      ]
    }
  ],
  "total": 10
}
```

---

## 📋 Medical Records

### GET `/api/v1/records`
**תיאור:** רשימת רשומות רפואיות  
**Authentication:** Required  
**Query Parameters:**
- `type` (optional): checkup, treatment, xray, prescription
- `limit` (optional): 1-100
- `offset` (optional): pagination

### GET `/api/v1/records/{record_id}`
**תיאור:** רשומה רפואית ספציפית  
**Authentication:** Required

---

## 🦷 Treatments

### GET `/api/v1/financial/treatments`
**תיאור:** רשימת טיפולים  
**Authentication:** Required

### GET `/api/v1/treatment-prices/organizations/{org_id}/treatments`
**תיאור:** מחירון טיפולים לארגון  
**Authentication:** Required (Admin/Staff only)

---

## 📊 Statistics (For Clinic Staff)

### GET `/api/v1/statistics/appointments`
**תיאור:** סטטיסטיקות תורים  
**Authentication:** Required (Staff only)

### GET `/api/v1/statistics/patients`
**תיאור:** סטטיסטיקות מטופלים  
**Authentication:** Required (Staff only)

### GET `/api/v1/statistics/top-patients`
**תיאור:** מטופלים מובילים  
**Authentication:** Required (Staff only)

---

## 🔐 Audit Logs (For Compliance)

### GET `/api/v1/audit-logs/audit-logs/patients/{patient_id}/phi-access`
**תיאור:** לוג גישה למידע רפואי (PHI)  
**Authentication:** Required (Admin only)

---

## 📝 Frontend Pages to Build

### ✅ PatientDashboard
**Path:** `/patient/dashboard`  
**APIs Used:**
- `/api/v1/patient/profile`
- `/api/v1/patient/health-score`
- `/api/v1/appointments` (upcoming)
- `/api/v1/records` (recent)
- `/api/v1/billing/overview`

### ⏳ PatientAppointments
**Path:** `/patient/appointments`  
**APIs Used:**
- `/api/v1/appointments` (all)
- `/api/v1/appointments/{id}`
- `/api/v1/appointments/available-slots`
- `/api/v1/appointments/{id}/cancel`

### ⏳ PatientMedicalRecords
**Path:** `/patient/medical-records`  
**APIs Used:**
- `/api/v1/records`
- `/api/v1/records/{id}`

### ⏳ PatientBilling
**Path:** `/patient/billing`  
**APIs Used:**
- `/api/v1/billing/overview`
- `/api/v1/billing/invoices`

### ⏳ PatientProfile
**Path:** `/patient/profile`  
**APIs Used:**
- `/api/v1/patient/profile` (GET/PUT)

### ✅ PatientChat
**Path:** `/patient/chat`  
**APIs Used:**
- `/api/v1/chat/` (existing)
- Websocket connection

---

## 🎨 Agentic UX Integration

### Layer 1: Traditional UI
- ✅ All endpoints work with standard REST calls
- ✅ Forms, tables, cards
- ✅ Clear navigation

### Layer 2: AI-Enhanced UI
- 🔄 Smart suggestions based on health score
- 🔄 Proactive notifications for upcoming appointments
- 🔄 Quick actions with AI pre-fill
- 🔄 Contextual help tooltips

### Layer 3: Conversational UI
- ✅ Chat with Alex (existing)
- 🔄 Rich message components
- 🔄 Context-aware responses
- 🔄 Multi-turn conversations

---

## 🚀 Next Steps

1. ✅ PatientDashboard - Created
2. ⏳ PatientAppointments - Create with booking flow
3. ⏳ PatientMedicalRecords - Create with document viewer
4. ⏳ PatientBilling - Create with payment integration
5. ⏳ PatientProfile - Create with edit functionality
6. ⏳ Integrate Layer 2 (AI-Enhanced) features
7. ⏳ Add floating chat button (Layer 3)
8. ⏳ Connect all pages to real APIs
9. ⏳ Add loading states and error handling
10. ⏳ Add tests

---

**Total Endpoints Available:** 105  
**Patient Portal Coverage:** 21 endpoints  
**Ready to use!** 🎉

