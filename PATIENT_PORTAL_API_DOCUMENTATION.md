# Patient Portal API Documentation

**Date:** October 11, 2025  
**Backend URL:** http://localhost:8002  
**API Version:** 14.0.0  
**Source:** OpenAPI Specification

---

## Overview

This document provides comprehensive documentation for all Patient Portal API endpoints extracted from the running backend server. All endpoints marked with 🔒 require authentication.

**Total Patient Portal Endpoints:** 17

---

## Authentication

All patient portal endpoints require authentication using JWT tokens. The authentication flow is:

1. **Register or Login**
   - `POST /api/v1/auth/register` - Register new user
   - `POST /api/v1/auth/login` - Login existing user
   
2. **Get Token**
   - Response includes `access_token` and `refresh_token`
   
3. **Use Token**
   - Include in header: `Authorization: Bearer <access_token>`
   
4. **Refresh Token**
   - `POST /api/v1/auth/refresh` - Get new access token

---

## Core Patient Portal Endpoints

### 1. Patient Profile

#### GET `/api/v1/patient/profile` 🔒

**Description:** Get current patient profile from Odoo

**Authentication:** Required

**Response (200):**
```json
{
  "id": 1,
  "name": "Shane גבע",
  "email": "shane.גבע@gmail.com",
  "phone": "+972521481915",
  "birth_date": "1979-10-14",
  "registration_date": "2021-06-18",
  "address": "השדות 89, שיטים, 2784351",
  "insurance_provider": "Meuhedet",
  "insurance_number": "IL422626472",
  "emergency_contact": "+972525467745",
  "allergies": "None",
  "medical_conditions": "None",
  "last_visit": "2024-11-25",
  "total_visits": 10,
  "outstanding_balance": 0
}
```

---

### 2. Health Score

#### GET `/api/v1/patient/health-score` 🔒

**Description:** Get patient's dental health score calculated based on:
- Appointment frequency
- Treatment completion
- Preventive care adherence

**Authentication:** Required

**Response (200):**
```json
{
  "score": 85,
  "message": "Your dental health is in great shape!",
  "factors": [
    {
      "label": "Regular checkups",
      "status": "good",
      "value": 95
    },
    {
      "label": "Good oral hygiene",
      "status": "good",
      "value": 90
    },
    {
      "label": "Next cleaning due soon",
      "status": "warning",
      "value": 70
    }
  ],
  "recommendations": [
    "Schedule your next cleaning appointment",
    "Continue brushing twice daily"
  ],
  "last_updated": "2025-10-11T10:00:00"
}
```

---

## Appointments

### 3. Get Appointments

#### GET `/api/v1/appointments` 🔒

**Description:** Get patient's appointments from Odoo

**Authentication:** Required

**Query Parameters:**
- `status` (optional): Filter by status - `upcoming`, `past`, `cancelled`, `all`
- `limit` (optional): Number of results (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "appointments": [
    {
      "id": 1,
      "patient_id": 1,
      "patient_name": "Shane גבע",
      "date": "2025-01-15",
      "time": "17:15",
      "datetime": "2025-01-15T17:15:49",
      "treatment_type": "Root Canal",
      "duration_minutes": 90,
      "dentist": "Dr. Smith",
      "status": "completed",
      "notes": "Previous root canal on tooth #14",
      "created_at": "2024-12-26T17:15:49"
    }
  ],
  "total": 10,
  "limit": 10,
  "offset": 0
}
```

---

### 4. Create Appointment

#### POST `/api/v1/appointments` 🔒

**Description:** Create a new appointment

**Authentication:** Required

**Request Body:**
```json
{
  "doctor_id": 1,
  "date": "2025-11-15",
  "time": "14:00",
  "treatment_type": "Routine Cleaning",
  "notes": "Optional notes"
}
```

**Response (200):**
```json
{
  "id": 123,
  "patient_id": 1,
  "doctor_id": 1,
  "date": "2025-11-15",
  "time": "14:00",
  "treatment_type": "Routine Cleaning",
  "status": "scheduled",
  "created_at": "2025-10-11T10:00:00"
}
```

---

### 5. Get Available Slots

#### GET `/api/v1/appointments/available-slots` 🔒

**Description:** Get available time slots for a doctor on a specific date. Considers:
1. Doctor's working hours
2. Existing appointments
3. Appointment duration
4. Breaks and holidays

**Authentication:** Required

**Query Parameters:**
- `doctor_id` (required): Doctor ID
- `date` (required): Date in YYYY-MM-DD format

**Response (200):**
```json
{
  "date": "2025-11-15",
  "doctor_id": 1,
  "doctor_name": "Dr. Sarah Goldstein",
  "available_slots": [
    {
      "time": "09:00",
      "duration_minutes": 45,
      "available": true
    },
    {
      "time": "10:00",
      "duration_minutes": 45,
      "available": true
    },
    {
      "time": "14:00",
      "duration_minutes": 45,
      "available": false,
      "reason": "Already booked"
    }
  ]
}
```

---

### 6. Cancel Appointment

#### PUT `/api/v1/appointments/{appointment_id}/cancel` 🔒

**Description:** Cancel an existing appointment

**Authentication:** Required

**Path Parameters:**
- `appointment_id` (required): ID of appointment to cancel

**Response (200):**
```json
{
  "id": 123,
  "status": "cancelled",
  "cancelled_at": "2025-10-11T10:00:00",
  "message": "Appointment cancelled successfully"
}
```

---

### 7. Get Doctors

#### GET `/api/v1/doctors` 🔒

**Description:** Get list of available doctors

**Authentication:** Required

**Response (200):**
```json
{
  "doctors": [
    {
      "id": 1,
      "name": "Dr. Sarah Goldstein",
      "specialization": "General Dentistry",
      "available": true
    },
    {
      "id": 2,
      "name": "Dr. David Cohen",
      "specialization": "Orthodontics",
      "available": true
    }
  ]
}
```

---

## Medical Records

### 8. Get Medical Records

#### GET `/api/v1/records` 🔒

**Description:** Get patient's medical records

**Authentication:** Required

**Query Parameters:**
- `record_type` (optional): Filter by type - `xray`, `report`, `treatment`, `all`
- `limit` (optional): Number of results (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "records": [
    {
      "id": 1,
      "patient_id": 1,
      "appointment_id": 1,
      "date": "2024-09-17",
      "treatment_type": "X-Ray",
      "tooth_number": "#5",
      "diagnosis": "Gingivitis",
      "procedure_notes": "Patient wears night guard",
      "dentist": "Dr. Cohen",
      "follow_up_required": false,
      "follow_up_date": null,
      "attachments": [
        {
          "type": "xray",
          "url": "/files/xray_123.jpg",
          "description": "Panoramic X-ray"
        }
      ]
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

---

### 9. Get Record Detail

#### GET `/api/v1/records/{record_id}` 🔒

**Description:** Get detailed information for a specific medical record

**Authentication:** Required

**Path Parameters:**
- `record_id` (required): ID of the medical record

**Response (200):**
```json
{
  "id": 1,
  "patient_id": 1,
  "appointment_id": 1,
  "date": "2024-09-17",
  "treatment_type": "X-Ray",
  "tooth_number": "#5",
  "diagnosis": "Gingivitis",
  "procedure_notes": "Patient wears night guard",
  "dentist": "Dr. Cohen",
  "follow_up_required": false,
  "follow_up_date": null,
  "attachments": [],
  "created_at": "2024-09-17T10:00:00",
  "updated_at": "2024-09-17T10:00:00"
}
```

---

## Billing

### 10. Get Billing Overview

#### GET `/api/v1/billing/overview` 🔒

**Description:** Get billing overview for patient

**Authentication:** Required

**Response (200):**
```json
{
  "outstanding_balance": 500.00,
  "total_paid": 2500.00,
  "pending_invoices": 2,
  "last_payment": {
    "date": "2025-09-15",
    "amount": 150.00,
    "method": "Credit Card"
  },
  "payment_history": [
    {
      "date": "2025-09-15",
      "amount": 150.00,
      "method": "Credit Card",
      "status": "completed"
    }
  ]
}
```

---

### 11. Get Invoices

#### GET `/api/v1/billing/invoices` 🔒

**Description:** Get patient's invoices

**Authentication:** Required

**Query Parameters:**
- `status` (optional): Filter by status - `paid`, `unpaid`, `overdue`, `all`
- `limit` (optional): Number of results (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "invoices": [
    {
      "id": 1,
      "patient_id": 1,
      "patient_name": "Shane גבע",
      "appointment_id": 1,
      "issue_date": "2025-07-25",
      "due_date": "2025-08-24",
      "treatment": "X-Ray",
      "total_amount": 277,
      "insurance_amount": 221,
      "patient_amount": 56,
      "paid_amount": 56,
      "outstanding_amount": 0,
      "status": "paid",
      "payment_method": "Credit Card",
      "invoice_number": "INV-2025-00001",
      "items": [
        {
          "description": "Routine Cleaning",
          "quantity": 1,
          "price": 150.00
        }
      ]
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

---

## Additional Endpoints

### 12. Get Today's Appointments

#### GET `/api/v1/appointments/today`

**Description:** Get appointments scheduled for today

**Authentication:** Not required (but should be for production)

**Response (200):**
```json
{
  "date": "2025-10-11",
  "appointments": [
    {
      "id": 1,
      "patient_name": "Shane גבע",
      "time": "14:00",
      "treatment_type": "Routine Cleaning",
      "dentist": "Dr. Sarah Goldstein",
      "status": "scheduled"
    }
  ],
  "total": 5
}
```

---

### 13. Get Appointment Detail

#### GET `/api/v1/appointments/{appointment_id}`

**Description:** Get details of a specific appointment

**Authentication:** Not required (but should be for production)

**Path Parameters:**
- `appointment_id` (required): ID of the appointment

**Response (200):**
```json
{
  "id": 1,
  "patient_id": 1,
  "patient_name": "Shane גבע",
  "date": "2025-01-15",
  "time": "17:15",
  "treatment_type": "Root Canal",
  "duration_minutes": 90,
  "dentist": "Dr. Smith",
  "status": "completed",
  "notes": "Previous root canal on tooth #14"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "status"],
      "msg": "Invalid status value",
      "type": "value_error"
    }
  ]
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Frontend Integration Checklist

### Priority 1: Critical
- [ ] Implement authentication flow (login/register)
- [ ] Store and manage JWT tokens
- [ ] Implement token refresh mechanism
- [ ] Create API client service with auth headers
- [ ] Implement user-patient mapping

### Priority 2: Dashboard
- [ ] Connect to `/api/v1/patient/profile`
- [ ] Connect to `/api/v1/patient/health-score`
- [ ] Connect to `/api/v1/appointments?status=upcoming&limit=3`
- [ ] Connect to `/api/v1/billing/overview`

### Priority 3: Appointments Page
- [ ] Connect to `/api/v1/appointments`
- [ ] Connect to `/api/v1/doctors`
- [ ] Connect to `/api/v1/appointments/available-slots`
- [ ] Implement appointment booking with `POST /api/v1/appointments`
- [ ] Implement appointment cancellation with `PUT /api/v1/appointments/{id}/cancel`

### Priority 4: Medical Records Page
- [ ] Connect to `/api/v1/records`
- [ ] Connect to `/api/v1/records/{id}`
- [ ] Implement record filtering by type

### Priority 5: Billing Page
- [ ] Connect to `/api/v1/billing/overview`
- [ ] Connect to `/api/v1/billing/invoices`
- [ ] Implement invoice filtering by status

### Priority 6: Profile Page
- [ ] Connect to `/api/v1/patient/profile`
- [ ] Implement profile update (if endpoint exists)

---

## Testing Strategy

### Unit Tests
- Test API client functions
- Test authentication flow
- Test data transformation
- Test error handling

### Integration Tests
- Test complete user journeys
- Test with Mock Odoo data
- Test error scenarios
- Test loading states

### E2E Tests
- Test full patient portal workflow
- Test with real backend
- Test Hebrew/RTL support

---

## Notes

1. **Authentication:** All patient portal endpoints require authentication except for a few public endpoints
2. **User-Patient Mapping:** Need to implement mapping between authenticated users and Odoo patients
3. **Mock Odoo Data:** Backend is using Mock Odoo Dental with 1,500 patients
4. **Hebrew Support:** All responses support Hebrew text with RTL
5. **Pagination:** Most list endpoints support `limit` and `offset` parameters
6. **Filtering:** Appointments, records, and invoices support status/type filtering

---

**Status:** Ready for frontend integration! 🚀

