# DentaFlow API Reference

**Status:** ✅ Current | **Last Updated:** November 21, 2025

This document provides a comprehensive reference for the DentaFlow backend API. It is optimized for AI development agents.

**Base URL (Staging):** `https://dentaflow-backend-staging-688311017213.us-central1.run.app`
**API Docs (Swagger):** [Staging Backend /docs](https://dentaflow-backend-staging-688311017213.us-central1.run.app/docs)

---

## 1. Authentication

- **Type:** JWT (JSON Web Tokens)
- **Header:** `Authorization: Bearer <token>`
- **Token Endpoint:** `POST /api/v1/auth/login`
- **Token Payload:** Includes `user_id`, `organization_id`, `role`.

---

## 2. API Endpoints

### 2.1. Auth (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/login` | Authenticate user and get JWT | ❌ No |
| `POST` | `/register` | Register a new user and organization | ❌ No |
| `GET` | `/me` | Get current user profile | ✅ Yes |

### 2.2. Demo (`/api/v1/demo`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/session/create` | Create a new interactive demo session | ❌ No |
| `POST` | `/chat` | Send a message in a demo session | ❌ No |
| `GET` | `/session/{session_id}/status` | Get status of a demo session | ❌ No |
| `DELETE` | `/session/{session_id}` | End a demo session | ❌ No |

### 2.3. Patients (`/api/v1/patients`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | Get a list of all patients for the organization | ✅ Yes |
| `POST` | `/` | Create a new patient | ✅ Yes |
| `GET` | `/{patient_id}` | Get details for a specific patient | ✅ Yes |
| `PUT` | `/{patient_id}` | Update a patient's details | ✅ Yes |
| `GET` | `/{patient_id}/appointments` | Get all appointments for a patient | ✅ Yes |
| `GET` | `/{patient_id}/medical-records` | Get medical records for a patient | ✅ Yes |

### 2.4. Appointments (`/api/v1/appointments`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | Get all appointments for the organization | ✅ Yes |
| `POST` | `/` | Create a new appointment | ✅ Yes |
| `GET` | `/{appointment_id}` | Get details for a specific appointment | ✅ Yes |
| `PUT` | `/{appointment_id}` | Update an appointment | ✅ Yes |
| `POST` | `/{appointment_id}/cancel` | Cancel an appointment | ✅ Yes |

### 2.5. AI Agent (`/api/v1/agent`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/chat` | Send a message to the AI agent system | ✅ Yes |
| `GET` | `/conversation/{convo_id}` | Get history of a conversation | ✅ Yes |

### 2.6. Odoo (`/api/v1/odoo`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/sync-status` | Get the status of the last Odoo sync | ✅ Yes (Admin) |
| `POST` | `/trigger-sync` | Manually trigger a full sync with Odoo | ✅ Yes (Admin) |

---

## 3. Common Schemas

### Patient

```json
{
  "id": "integer",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "date",
  "email": "string",
  "phone_number": "string",
  "address": "string"
}
```

### Appointment

```json
{
  "id": "integer",
  "patient_id": "integer",
  "start_time": "datetime",
  "end_time": "datetime",
  "status": "string (e.g., confirmed, cancelled)",
  "reason": "string",
  "notes": "string"
}
```

---

## 4. Related Documents

- **[ARCHITECTURE.md](ARCHITECTURE.md):** System architecture overview.
- **[DEVELOPMENT.md](DEVELOPMENT.md):** How to set up and run the project locally.
- **[Swagger API Docs](https://dentaflow-backend-staging-688311017213.us-central1.run.app/docs):** Interactive API documentation.
