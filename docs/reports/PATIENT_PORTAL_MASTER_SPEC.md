# DentaFlow Patient Portal - Master Specification
## Complete Feature Set & Implementation Guide

**Version:** 2.0  
**Date:** October 11, 2025  
**Status:** Ready for Development

---

## 🎯 Vision

Create the most intuitive, proactive, and comprehensive dental patient portal that seamlessly integrates traditional UI with AI-powered assistance, making dental care management effortless for patients.

---

## 📊 Complete Data Model (from Odoo Dental)

### Patient Data
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

### Appointment Data
```json
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
```

### Invoice Data
```json
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
  "invoice_number": "INV-2025-00001"
}
```

### Treatment Record Data
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
  "follow_up_date": null
}
```

---

## 🎨 Design System

### Layout Structure (3-Column Hybrid)

**All pages follow this structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: Logo | Navigation | User Menu | Notifications      │
├──────────┬──────────────────────────────────┬────────────────┤
│          │                                  │                │
│  Left    │         Center Panel            │  Right Panel   │
│  Panel   │       (Main Content)            │  (Chat &       │
│  (Quick  │                                  │   Suggestions) │
│  Actions │                                  │                │
│  &       │                                  │                │
│  Widgets)│                                  │                │
│          │                                  │                │
│  20%     │          55%                     │      25%       │
│  width   │          width                   │      width     │
│          │                                  │                │
└──────────┴──────────────────────────────────┴────────────────┘
                                              │
                                              └─ Floating Chat Button
```

### Color Palette
- **Primary Gradient:** `from-blue-600 to-purple-600`
- **Background Gradient:** `from-blue-50 via-purple-50 to-pink-50`
- **Success:** `green-500`
- **Warning:** `yellow-500`
- **Error:** `red-500`
- **Info:** `blue-500`
- **Text Primary:** `gray-900`
- **Text Secondary:** `gray-600`

### Typography
- **Headings:** Inter, bold, sizes 24px-48px
- **Body:** Inter, regular, 16px
- **Small:** Inter, regular, 14px
- **Tiny:** Inter, regular, 12px

### Components
- **Cards:** White background, rounded-xl, shadow-lg, hover:shadow-xl
- **Buttons:** Gradient background, rounded-lg, px-6 py-3
- **Inputs:** Border gray-300, rounded-lg, focus:ring-2 focus:ring-blue-500
- **Badges:** Rounded-full, px-3 py-1, text-sm
- **Icons:** Lucide React, 20px-24px

---

## 📄 Page 1: Dashboard

### Purpose
Provide an at-a-glance overview of the patient's dental health, upcoming appointments, and proactive AI suggestions.

### Layout

**Left Panel (20%):**
- Quick Actions Widget
  - Book Appointment (primary button)
  - View Medical Records (secondary button)
  - Pay Bill (secondary button)
  - Chat with Alex (tertiary button)
- Health Score Widget
  - Large circular progress (0-100)
  - Color-coded (red < 60, yellow 60-80, green > 80)
  - Trend indicator (↑ ↓ →)
  - "How to improve" link

**Center Panel (55%):**
- Welcome Banner
  - "Welcome back, [Name]!"
  - Last visit date
  - Next appointment countdown
- 4 Stats Cards (grid 2x2)
  - Next Appointment (date, time, dentist, treatment)
  - Total Visits (number, trend)
  - Outstanding Balance (amount, "Pay Now" button)
  - Health Score (number, visual indicator)
- Upcoming Appointments Section
  - Title: "Your Upcoming Appointments"
  - List of next 3 appointments
  - Each appointment card shows:
    - Date & time
    - Dentist name with avatar
    - Treatment type badge
    - Duration
    - Action buttons (Reschedule, Cancel, Details)
  - "View All" link
- Recent Medical Records Section
  - Title: "Recent Medical Records"
  - List of last 3 treatment records
  - Each record card shows:
    - Date
    - Treatment type
    - Tooth number (if applicable)
    - Dentist name
    - "View Details" button
  - "View All Records" link

**Right Panel (25%):**
- Proactive AI Suggestions (2-3 cards)
  - Alex Suggestion Card
    - Agent avatar and name
    - Suggestion text (e.g., "Your next cleaning is due in 2 weeks!")
    - Confidence indicator (85%)
    - Action buttons (Book Now, Remind Me Later, Dismiss)
    - "Why am I seeing this?" tooltip
  - Sarah Insight Card
    - Agent avatar and name
    - Health insight (e.g., "Your dental health score improved to 92!")
    - Confidence indicator (90%)
    - "Learn More" button
  - Marcus Reminder Card (if applicable)
    - Agent avatar and name
    - Payment reminder (e.g., "You have an outstanding balance of ₪450")
    - "Pay Now" button
- Chat Panel (collapsible)
  - "Chat with Alex" header
  - Recent conversation preview
  - "Open Chat" button

**Floating Chat Button:**
- Fixed position (bottom right)
- Purple gradient background
- Chat icon
- Badge with unread count (if any)
- Hover effect (scale 1.1)
- Click opens chat panel

### API Endpoints Used
- `GET /api/v1/patient/profile` - Patient info
- `GET /api/v1/patient/health-score` - Health score
- `GET /api/v1/appointments?patient_id={id}&status=scheduled&limit=3` - Upcoming appointments
- `GET /api/v1/medical-records?patient_id={id}&limit=3` - Recent records
- `GET /api/v1/invoices?patient_id={id}&status=unpaid` - Outstanding balance
- `GET /api/v1/ai/suggestions?patient_id={id}&context=dashboard` - AI suggestions

### Proactive AI Logic

**Alex Suggestions:**
- If last cleaning > 6 months ago → "Time for your cleaning!"
- If no upcoming appointment → "Would you like to book an appointment?"
- If appointment tomorrow → "Reminder: Your appointment is tomorrow!"
- If dentist has cancellation → "Dr. Cohen has a slot available tomorrow at 2 PM"

**Sarah Insights:**
- If health score improved → "Great job! Your health score is up!"
- If health score declined → "Your health score dropped. Let's talk about it."
- If treatment follow-up due → "Follow-up for your root canal is due"
- If X-ray older than 1 year → "Time for your annual X-ray"

**Marcus Reminders:**
- If outstanding balance > 0 → "You have an unpaid invoice of ₪{amount}"
- If payment plan available → "Payment plan available: ₪{amount}/month"
- If insurance claim pending → "Your insurance claim is being processed"

---

## 📄 Page 2: Appointments

### Purpose
View, book, reschedule, and cancel appointments with ease.

### Layout

**Left Panel (20%):**
- Calendar Widget (month view)
  - Highlight dates with appointments
  - Click date to filter
- Filter Widget
  - Status filter (All, Scheduled, Completed, Cancelled, No-show)
  - Dentist filter (All, Dr. Cohen, Dr. Smith, Dr. Levi)
  - Treatment type filter (All, Cleaning, X-Ray, Root Canal, etc.)
  - Date range picker
- Quick Book Widget
  - "Book New Appointment" button (primary)
  - Shows next available slot
  - One-click booking

**Center Panel (55%):**
- Page Header
  - Title: "My Appointments"
  - Subtitle: "Manage your dental appointments"
  - "Book New Appointment" button (primary)
- Tabs
  - Upcoming (default)
  - Past
  - Cancelled
- Upcoming Appointments List
  - Sorted by date (nearest first)
  - Each appointment card shows:
    - Date & time (large, prominent)
    - Countdown (e.g., "in 2 days")
    - Dentist name with avatar
    - Treatment type badge
    - Duration
    - Status badge (Scheduled, Confirmed)
    - Notes (if any)
    - Action buttons:
      - Reschedule (secondary)
      - Cancel (tertiary, red)
      - Add to Calendar (tertiary)
      - Get Directions (tertiary)
  - Empty state: "No upcoming appointments. Book one now!"
- Past Appointments List
  - Sorted by date (most recent first)
  - Each appointment card shows:
    - Date & time
    - Dentist name
    - Treatment type
    - Status badge (Completed, No-show)
    - "View Details" button
    - "Book Follow-up" button (if follow-up required)
  - Pagination (10 per page)

**Right Panel (25%):**
- Alex Suggestion Card
  - "Best times for you: Mornings"
  - "Dr. Cohen is available next week"
  - "Cleaning due in 2 weeks"
- Appointment Stats Widget
  - Total appointments this year
  - Completed appointments
  - No-show rate
  - Average time between visits
- Chat Panel

**Floating Chat Button:**
- Context-aware: "Ask Alex about appointments"

### Booking Flow (Modal/Wizard)

**Step 1: Select Treatment Type**
- Grid of treatment types (cards with icons)
  - Cleaning
  - X-Ray
  - Root Canal
  - Filling
  - Extraction
  - Crown
  - Implant
  - Whitening
  - Braces Consultation
  - Emergency Visit
- Each card shows:
  - Icon
  - Name
  - Typical duration
  - Estimated cost
- "Not sure? Chat with Alex" button

**Step 2: Select Dentist**
- List of dentists (cards with photos)
  - Dr. Cohen
  - Dr. Smith
  - Dr. Levi
- Each card shows:
  - Photo
  - Name
  - Specialization
  - Rating (stars)
  - Next available slot
  - "Select" button
- "No preference" option (Alex will suggest)

**Step 3: Select Date & Time**
- Calendar view (week view)
- Available time slots (green)
- Unavailable slots (gray)
- Suggested slots (highlighted by Alex)
- "Show more dates" button

**Step 4: Confirm Details**
- Summary card:
  - Treatment type
  - Dentist
  - Date & time
  - Duration
  - Estimated cost
  - Insurance coverage (if applicable)
- "Add notes" textarea
- "Confirm Booking" button (primary)
- "Back" button (secondary)

**Step 5: Confirmation**
- Success message
- Appointment details
- "Add to Calendar" button
- "Get Directions" button
- "Done" button

### API Endpoints Used
- `GET /api/v1/appointments?patient_id={id}` - All appointments
- `GET /api/v1/appointments/available-slots?treatment_type={type}&dentist={dentist}&date={date}` - Available slots
- `POST /api/v1/appointments` - Book appointment
- `PUT /api/v1/appointments/{id}` - Reschedule appointment
- `DELETE /api/v1/appointments/{id}` - Cancel appointment
- `GET /api/v1/ai/suggestions?context=appointments` - Alex suggestions

---

## 📄 Page 3: Medical Records

### Purpose
View comprehensive dental health information including treatment history, X-rays, dental chart, and health insights.

### Layout

**Left Panel (20%):**
- Health Score Widget (same as dashboard)
- Quick Filters Widget
  - Date range
  - Treatment type
  - Dentist
  - Tooth number
- Download Options Widget
  - "Download All Records" (PDF)
  - "Download X-Rays" (ZIP)
  - "Download Prescriptions" (PDF)
  - "Request Records Transfer" button

**Center Panel (55%):**
- Page Header
  - Title: "My Medical Records"
  - Subtitle: "Your complete dental health history"
- Tabs
  - Overview (default)
  - Treatments
  - X-Rays
  - Prescriptions
  - Lab Results

**Tab 1: Overview**
- Dental Chart (Interactive 32-tooth diagram)
  - Visual representation of all 32 teeth
  - Color-coded by status:
    - Green: Healthy
    - Yellow: Watch/Monitor
    - Orange: Needs treatment
    - Red: Urgent/Cavity
    - Blue: Filled/Treated
    - Gray: Missing/Extracted
  - Click tooth to see:
    - Tooth number
    - Status
    - Treatment history for that tooth
    - Planned treatments
  - Legend explaining colors
- Health Summary Cards (4 cards)
  - Total Teeth Healthy (number, percentage)
  - Treatments This Year (number)
  - X-Rays on File (number)
  - Prescriptions Active (number)
- Recent Activity Timeline
  - Last 5 treatments/events
  - Date, treatment type, dentist, outcome

**Tab 2: Treatments**
- Treatment Records List
  - Sorted by date (most recent first)
  - Each treatment card shows:
    - Date
    - Treatment type badge
    - Tooth number (if applicable)
    - Diagnosis
    - Dentist name with avatar
    - Procedure notes (collapsible)
    - Follow-up required badge (if applicable)
    - Follow-up date (if applicable)
    - "View Full Details" button
  - Filters: Date, Treatment type, Dentist, Tooth
  - Search bar
  - Pagination (20 per page)

**Tab 3: X-Rays**
- X-Ray Gallery (grid view)
  - Each X-ray card shows:
    - Thumbnail image
    - Date taken
    - Type (Panoramic, Periapical, Bitewing)
    - Dentist who ordered
    - "View" button (opens lightbox)
    - "Download" button
  - Lightbox viewer features:
    - Full-size image
    - Zoom in/out
    - Pan
    - Rotate
    - Compare mode (side-by-side)
    - Annotations (if any)
    - Download button
    - Close button
  - Filters: Date, Type
  - Grid/List view toggle

**Tab 4: Prescriptions**
- Prescriptions List
  - Active prescriptions (top)
  - Past prescriptions (below)
  - Each prescription card shows:
    - Medication name
    - Dosage
    - Frequency
    - Start date
    - End date (if applicable)
    - Prescribing dentist
    - Pharmacy
    - Refills remaining
    - "Request Refill" button (if refillable)
    - "View Details" button
  - Filters: Active/Past, Date, Dentist

**Tab 5: Lab Results**
- Lab Results List
  - Each result card shows:
    - Test name
    - Date
    - Ordering dentist
    - Status badge (Pending, Ready, Reviewed)
    - "View Results" button
    - "Download PDF" button
  - Filters: Date, Status

**Right Panel (25%):**
- Sarah Insight Cards
  - "Your dental health score is excellent!"
  - "Consider fluoride treatment for tooth #14"
  - "Your last X-ray was 8 months ago"
- Health Trends Widget
  - Chart showing health score over time
  - Trend line
  - Notable events marked
- Chat Panel (with Sarah)

**Floating Chat Button:**
- Context-aware: "Ask Sarah about your records"

### API Endpoints Used
- `GET /api/v1/medical-records?patient_id={id}` - All treatment records
- `GET /api/v1/medical-records/{id}` - Single treatment record
- `GET /api/v1/patient/dental-chart?patient_id={id}` - Dental chart data
- `GET /api/v1/xrays?patient_id={id}` - X-rays
- `GET /api/v1/prescriptions?patient_id={id}` - Prescriptions
- `GET /api/v1/lab-results?patient_id={id}` - Lab results
- `GET /api/v1/patient/health-score?patient_id={id}&history=true` - Health score history
- `GET /api/v1/ai/insights?patient_id={id}&context=medical-records` - Sarah insights

---

## 📄 Page 4: Billing

### Purpose
View invoices, make payments, manage payment plans, and track insurance claims.

### Layout

**Left Panel (20%):**
- Payment Quick Actions Widget
  - "Pay Outstanding Balance" button (primary, if balance > 0)
  - Amount due (large, prominent)
  - "Set up Payment Plan" button (secondary)
  - "Update Payment Method" button (tertiary)
- Payment Methods Widget
  - Saved credit cards (last 4 digits)
  - "Add New Card" button
  - Default payment method indicator
- Insurance Info Widget
  - Provider name
  - Policy number
  - Coverage details
  - "Update Insurance" button

**Center Panel (55%):**
- Page Header
  - Title: "Billing & Payments"
  - Subtitle: "Manage your payments and invoices"
- 4 Stats Cards (grid 2x2)
  - Outstanding Balance (amount, "Pay Now" button)
  - Paid This Year (amount, trend)
  - Open Invoices (count)
  - Last Payment (date, amount, method)
- Tabs
  - Invoices (default)
  - Payment History
  - Payment Plans
  - Insurance Claims

**Tab 1: Invoices**
- Invoices List
  - Unpaid invoices (top, highlighted)
  - Paid invoices (below)
  - Each invoice card shows:
    - Invoice number
    - Issue date
    - Due date (if unpaid)
    - Treatment description
    - Total amount
    - Insurance amount (if applicable)
    - Patient amount
    - Paid amount
    - Outstanding amount
    - Status badge (Paid, Unpaid, Overdue, Partial)
    - Payment method (if paid)
    - Action buttons:
      - "Pay Now" (if unpaid, primary button)
      - "View Details" (secondary)
      - "Download PDF" (tertiary)
      - "Dispute" (tertiary, red)
  - Filters: Status, Date range, Amount range
  - Search by invoice number
  - Pagination (20 per page)

**Tab 2: Payment History**
- Payments List (timeline view)
  - Sorted by date (most recent first)
  - Each payment card shows:
    - Date
    - Amount
    - Payment method (card icon + last 4 digits)
    - Invoice number(s) paid
    - Status badge (Completed, Pending, Failed)
    - "View Receipt" button
    - "Download Receipt" button
  - Filters: Date range, Payment method, Amount range
  - Total paid this year (summary at top)

**Tab 3: Payment Plans**
- Active Payment Plans (if any)
  - Each plan card shows:
    - Plan name
    - Total amount
    - Amount paid
    - Amount remaining
    - Monthly payment
    - Next payment date
    - Progress bar
    - "View Details" button
    - "Make Payment" button
- Available Payment Plans (if balance > threshold)
  - "Set up a payment plan" section
  - Options:
    - 3 months (amount per month)
    - 6 months (amount per month)
    - 12 months (amount per month)
  - "Apply Now" buttons

**Tab 4: Insurance Claims**
- Claims List
  - Each claim card shows:
    - Claim number
    - Submission date
    - Treatment
    - Claim amount
    - Approved amount
    - Status badge (Submitted, Approved, Denied, Pending)
    - "View Details" button
  - Filters: Status, Date
  - "Submit New Claim" button (if applicable)

**Right Panel (25%):**
- Marcus Insight Cards
  - "All invoices are paid! Great job!"
  - "Your insurance covers 80% of preventive care"
  - "Payment plan available: ₪150/month for 6 months"
- Spending Trends Widget
  - Chart showing spending over time
  - Average per visit
  - Total this year vs last year
- Chat Panel (with Marcus)

**Floating Chat Button:**
- Context-aware: "Ask Marcus about billing"

### Payment Flow (Modal)

**Step 1: Select Invoices**
- List of unpaid invoices with checkboxes
- Select all / Select none buttons
- Total amount to pay (updates as you select)
- "Continue" button

**Step 2: Select Payment Method**
- Saved payment methods (radio buttons)
  - Credit card (last 4 digits, expiry)
  - Bank transfer
- "Add New Payment Method" button
- "Continue" button

**Step 3: Confirm Payment**
- Summary:
  - Invoices being paid (list)
  - Total amount
  - Payment method
  - Payment date (today)
- "Confirm Payment" button (primary)
- "Back" button (secondary)

**Step 4: Processing**
- Loading spinner
- "Processing your payment..."
- Do not close this window

**Step 5: Confirmation**
- Success message
- Payment confirmation number
- Receipt (downloadable)
- "View Receipt" button
- "Done" button

### API Endpoints Used
- `GET /api/v1/invoices?patient_id={id}` - All invoices
- `GET /api/v1/invoices/{id}` - Single invoice
- `POST /api/v1/payments` - Make payment
- `GET /api/v1/payments?patient_id={id}` - Payment history
- `GET /api/v1/payment-plans?patient_id={id}` - Payment plans
- `POST /api/v1/payment-plans` - Set up payment plan
- `GET /api/v1/insurance-claims?patient_id={id}` - Insurance claims
- `POST /api/v1/insurance-claims` - Submit claim
- `GET /api/v1/ai/insights?context=billing` - Marcus insights

---

## 📄 Page 5: Profile

### Purpose
View and edit personal information, medical history, insurance details, and account settings.

### Layout

**Left Panel (20%):**
- Profile Summary Widget
  - Profile photo (editable)
  - Name
  - Patient ID
  - Member since date
  - "Edit Profile" button
- Quick Links Widget
  - Change Password
  - Update Insurance
  - Communication Preferences
  - Privacy Settings
  - Download My Data
  - Delete Account

**Center Panel (55%):**
- Page Header
  - Title: "My Profile"
  - Subtitle: "Manage your personal information"
- Tabs
  - Personal Info (default)
  - Medical History
  - Insurance
  - Settings

**Tab 1: Personal Info**
- Sections (each with "Edit" button):
  
  **Basic Information**
  - Full Name (editable)
  - Date of Birth (editable)
  - Email (editable)
  - Phone (editable)
  - Address (editable)
  - Emergency Contact (editable)
  
  **Account Information**
  - Patient ID (read-only)
  - Registration Date (read-only)
  - Last Login (read-only)
  - Account Status (read-only)

**Tab 2: Medical History**
- Sections (each with "Edit" button):
  
  **Allergies**
  - List of allergies (editable)
  - "Add Allergy" button
  - Severity indicators
  
  **Medical Conditions**
  - List of conditions (editable)
  - "Add Condition" button
  - Active/Past toggle
  
  **Current Medications**
  - List of medications (editable)
  - "Add Medication" button
  - Dosage and frequency
  
  **Family History**
  - Dental conditions in family
  - "Add Family History" button
  
  **Lifestyle**
  - Smoking status
  - Alcohol consumption
  - Oral hygiene habits
  - Diet preferences

**Tab 3: Insurance**
- Sections (each with "Edit" button):
  
  **Primary Insurance**
  - Provider name
  - Policy number
  - Group number
  - Coverage start date
  - Coverage end date
  - Coverage details
  - "Upload Insurance Card" button
  
  **Secondary Insurance** (if applicable)
  - Same fields as primary
  
  **Coverage Summary**
  - Preventive care coverage (percentage)
  - Basic procedures coverage (percentage)
  - Major procedures coverage (percentage)
  - Annual maximum
  - Deductible
  - Deductible met this year

**Tab 4: Settings**
- Sections:
  
  **Communication Preferences**
  - Email notifications (toggle)
  - SMS notifications (toggle)
  - Push notifications (toggle)
  - Appointment reminders (toggle)
  - Marketing emails (toggle)
  - Preferred contact method (dropdown)
  - Preferred language (dropdown)
  
  **Notification Settings**
  - Appointment reminders (toggle, timing)
  - Lab results ready (toggle)
  - Prescription ready (toggle)
  - Payment due (toggle)
  - Health insights (toggle)
  - Clinic announcements (toggle)
  
  **Privacy Settings**
  - Share data with dentist (toggle)
  - Share data for research (toggle)
  - Allow marketing communications (toggle)
  - "View Privacy Policy" link
  - "View Terms of Service" link
  
  **Security Settings**
  - Change Password button
  - Enable Two-Factor Authentication (toggle)
  - Active Sessions (list)
  - "Log Out All Devices" button
  
  **Account Management**
  - "Download My Data" button (GDPR)
  - "Delete My Account" button (red, with confirmation)

**Right Panel (25%):**
- Profile Completion Widget
  - Progress bar (percentage)
  - Checklist of missing information
  - "Complete Your Profile" CTA
- Alex Suggestion Card
  - "Add your allergies for safer treatment"
  - "Update your insurance information"
- Chat Panel

**Floating Chat Button:**
- Context-aware: "Ask Alex about your profile"

### Edit Mode (Inline Editing)
- Click "Edit" button on any section
- Fields become editable
- "Save" and "Cancel" buttons appear
- Validation on save
- Success/error messages

### API Endpoints Used
- `GET /api/v1/patient/profile?patient_id={id}` - Patient profile
- `PUT /api/v1/patient/profile` - Update profile
- `PUT /api/v1/patient/medical-history` - Update medical history
- `PUT /api/v1/patient/insurance` - Update insurance
- `PUT /api/v1/patient/settings` - Update settings
- `POST /api/v1/patient/profile-photo` - Upload photo
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/enable-2fa` - Enable 2FA
- `GET /api/v1/auth/sessions` - Active sessions
- `DELETE /api/v1/auth/sessions` - Log out all devices
- `GET /api/v1/patient/data-export` - Download data
- `DELETE /api/v1/patient/account` - Delete account

---

## 💬 Floating Chat Component (Global)

### Purpose
Provide instant access to AI agents from any page for questions, assistance, and actions.

### Design
- **Position:** Fixed, bottom right, 24px from edges
- **Size:** 64px x 64px circle
- **Color:** Purple gradient (`from-purple-600 to-pink-600`)
- **Icon:** Chat bubble icon (white)
- **Badge:** Unread count (if any), red circle, top right
- **Hover:** Scale 1.1, shadow-2xl
- **Click:** Opens chat panel

### Chat Panel (Slide-in)
- **Position:** Fixed, right side, full height
- **Width:** 35% of viewport (min 400px, max 600px)
- **Animation:** Slide in from right (300ms ease-out)
- **Background:** White with backdrop blur
- **Shadow:** shadow-2xl

**Panel Structure:**
```
┌────────────────────────────────┐
│  Header                        │
│  - "Chat with DentaFlow"       │
│  - Agent selector dropdown     │
│  - Close button                │
├────────────────────────────────┤
│                                │
│  Messages Area                 │
│  (scrollable)                  │
│                                │
│  - User messages (right)       │
│  - Agent messages (left)       │
│  - Typing indicator            │
│  - Timestamps                  │
│                                │
├────────────────────────────────┤
│  Input Area                    │
│  - Text input                  │
│  - Send button                 │
│  - Attachment button           │
│  - Voice input button          │
└────────────────────────────────┘
```

### Agent Selector
- Dropdown in header
- Options:
  - Alex (Reception & Patient Relations) - Default
  - Sarah (Clinical Assistant)
  - Marcus (CFO)
  - Sophia (Practice Administrator)
- Each option shows:
  - Agent avatar
  - Agent name
  - Agent role
  - Online status indicator

### Message Types

**User Message:**
- Alignment: Right
- Background: Gradient (`from-blue-600 to-purple-600`)
- Text color: White
- Border radius: rounded-2xl (top-left, bottom-left, top-right), rounded-sm (bottom-right)
- Max width: 80%
- Padding: 12px 16px
- Timestamp below (small, gray)

**Agent Message:**
- Alignment: Left
- Background: White
- Text color: Gray-900
- Border: 1px solid gray-200
- Border radius: rounded-2xl (top-right, bottom-right, top-left), rounded-sm (bottom-left)
- Max width: 80%
- Padding: 12px 16px
- Agent avatar (left)
- Agent name above (small, bold)
- Timestamp below (small, gray)
- Confidence indicator (if suggestion)
- Action buttons (if applicable)

**Rich Message Types:**
- Text message
- Card message (with image, title, description, buttons)
- List message (multiple items)
- Quick replies (chips/buttons)
- Form message (input fields)
- Confirmation message (yes/no buttons)
- Loading message (typing indicator)

### Context Awareness
The chat knows which page the user is on and can:
- Suggest relevant actions
- Answer page-specific questions
- Perform actions on behalf of the user

**Examples:**
- On Dashboard: "Would you like to book an appointment?"
- On Appointments: "I can help you reschedule your appointment"
- On Medical Records: "I can explain your treatment history"
- On Billing: "I can help you pay your invoice"
- On Profile: "I can help you update your information"

### Actions from Chat
Agents can perform actions:
- Book appointment
- Reschedule appointment
- Cancel appointment
- Pay invoice
- Request prescription refill
- Download records
- Update profile
- And more...

### API Endpoints Used
- `POST /api/v1/chat/message` - Send message
- `GET /api/v1/chat/history?patient_id={id}` - Chat history
- `POST /api/v1/chat/action` - Perform action
- `GET /api/v1/chat/suggestions?context={page}` - Get suggestions

---

## 🤖 AI Agent Behaviors

### Alex (Reception & Patient Relations)
**Personality:** Friendly, helpful, proactive  
**Primary Role:** Appointments, general questions, navigation  
**Confidence Threshold:** 80%

**Proactive Triggers:**
- Last cleaning > 6 months → Suggest cleaning appointment
- No upcoming appointment → Suggest booking
- Appointment tomorrow → Send reminder
- Dentist has cancellation → Offer earlier slot
- User on appointments page → "Need help booking?"

**Can Perform:**
- Book appointment
- Reschedule appointment
- Cancel appointment
- Answer general questions
- Navigate user to pages
- Explain features

### Sarah (Clinical Assistant)
**Personality:** Professional, caring, knowledgeable  
**Primary Role:** Medical records, health insights, treatment questions  
**Confidence Threshold:** 85%

**Proactive Triggers:**
- Health score improved → Congratulate
- Health score declined → Offer advice
- Treatment follow-up due → Remind
- X-ray older than 1 year → Suggest new X-ray
- User viewing dental chart → Offer explanation

**Can Perform:**
- Explain treatment records
- Provide health insights
- Answer medical questions
- Explain dental chart
- Suggest preventive care
- Explain X-rays

### Marcus (CFO)
**Personality:** Professional, clear, helpful  
**Primary Role:** Billing, payments, insurance  
**Confidence Threshold:** 90%

**Proactive Triggers:**
- Outstanding balance > 0 → Remind to pay
- Invoice overdue → Send urgent reminder
- Payment plan available → Offer plan
- Insurance claim approved → Notify
- User on billing page → "Need help paying?"

**Can Perform:**
- Explain invoices
- Process payments
- Set up payment plans
- Answer insurance questions
- Explain coverage
- Download receipts

### Sophia (Practice Administrator)
**Personality:** Efficient, solution-oriented, empathetic  
**Primary Role:** Feedback, complaints, suggestions, operations  
**Confidence Threshold:** 85%

**Proactive Triggers:**
- User had bad experience → Offer to help
- User frequently reschedules → Suggest better times
- User prefers certain dentist → Note preference
- Clinic announcement → Notify user

**Can Perform:**
- Collect feedback
- Handle complaints
- Suggest improvements
- Answer operational questions
- Explain policies
- Escalate issues

---

## 🔒 Security & Compliance

### Authentication
- Email + password login
- Two-factor authentication (optional)
- Social login (Google, Apple) (optional)
- Session management (30 min timeout)
- Remember me (30 days)
- Password reset via email

### Authorization
- Role-based access control (RBAC)
- Patient can only see their own data
- Parent can see child's data (if linked)
- Dentist can see patient data (with consent)
- Admin can see all data (audit logged)

### Data Protection
- All data encrypted at rest (AES-256)
- All data encrypted in transit (TLS 1.3)
- PII (Personally Identifiable Information) masked in logs
- Audit logging for all access
- Data backup (daily)
- Data retention policy (7 years)

### Compliance
- HIPAA compliance (US)
- GDPR compliance (EU)
- Israeli privacy laws
- PCI DSS compliance (payments)
- SOC 2 Type II (in progress)

---

## 📊 Analytics & Monitoring

### User Analytics
- Page views
- Session duration
- Feature usage
- Conversion rates (booking, payment)
- Drop-off points
- User flows

### Performance Monitoring
- Page load times
- API response times
- Error rates
- Uptime
- Resource usage

### Business Metrics
- Active users (DAU, MAU)
- Appointment booking rate
- Online payment rate
- No-show rate
- Patient satisfaction (NPS)
- Support ticket volume

---

## 🚀 Implementation Plan

### Phase 1: MVP (2-3 weeks)
**Goal:** Launch basic functional portal

**Features:**
- Dashboard (basic)
- Appointments (view, book, cancel)
- Medical Records (view only)
- Billing (view, pay)
- Profile (view, edit basic info)
- Basic chat with Alex
- Authentication & authorization
- Responsive design

**Deliverables:**
- 5 pages (basic versions)
- API integration
- Payment integration
- Deployment to staging

### Phase 2: Enhanced (1-2 weeks)
**Goal:** Add AI features and polish

**Features:**
- Proactive AI suggestions (all agents)
- Full chat functionality (all agents)
- Dental chart (interactive)
- X-ray viewer
- Notifications system
- Document management
- Advanced filters & search
- Mobile optimization

**Deliverables:**
- AI integration
- Enhanced UI/UX
- Notification system
- Deployment to production (beta)

### Phase 3: Advanced (1-2 weeks)
**Goal:** Add advanced features

**Features:**
- Telemedicine integration
- Health score & gamification
- Treatment plans
- Advanced analytics
- Mobile app (React Native)
- Offline support
- Push notifications

**Deliverables:**
- Telemedicine platform
- Mobile app (iOS, Android)
- Advanced features
- Full production launch

---

## 📚 Technical Stack

### Frontend
- **Framework:** React 18
- **Language:** JavaScript (ES6+)
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **State Management:** React Context API
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Forms:** React Hook Form
- **Validation:** Zod
- **Date Handling:** date-fns
- **Charts:** Recharts
- **Image Viewer:** React Image Lightbox
- **PDF Viewer:** React-PDF
- **Payment:** Stripe React

### Backend (Already Built)
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **API Docs:** Swagger/OpenAPI
- **File Storage:** S3
- **Email:** SendGrid
- **SMS:** Twilio
- **Payment:** Stripe
- **AI:** OpenAI GPT-4

### DevOps
- **Hosting:** AWS / Vercel
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry
- **Analytics:** Google Analytics
- **CDN:** CloudFront

---

## ✅ Definition of Done

### For Each Page:
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] All API endpoints integrated
- [ ] Loading states implemented
- [ ] Error states implemented
- [ ] Empty states implemented
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Cross-browser tested
- [ ] Performance optimized (< 2s load)
- [ ] Security review passed
- [ ] User testing completed
- [ ] Documentation written

### For Entire Portal:
- [ ] All 5 pages completed
- [ ] Chat functionality working
- [ ] AI suggestions working
- [ ] Payment flow working
- [ ] Authentication working
- [ ] Authorization working
- [ ] Notifications working
- [ ] Analytics integrated
- [ ] Monitoring set up
- [ ] Compliance audit passed
- [ ] User acceptance testing passed
- [ ] Production deployment successful

---

## 📞 Support & Maintenance

### Support Channels
- In-app chat (with agents)
- Email: support@dentaflow.com
- Phone: 1-800-DENTAFLOW
- Help center (FAQ, tutorials)

### Maintenance Schedule
- **Daily:** Backups, monitoring
- **Weekly:** Security updates, bug fixes
- **Monthly:** Feature releases, performance optimization
- **Quarterly:** Compliance audits, user surveys

---

**Document Owner:** AI Development Team  
**Approved By:** Product Manager  
**Last Updated:** October 11, 2025  
**Version:** 2.0  
**Status:** ✅ Ready for Development

