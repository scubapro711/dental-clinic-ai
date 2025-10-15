// Test user credentials
export const testUsers = {
  patient: {
    email: process.env.TEST_PATIENT_EMAIL || 'test.patient@example.com',
    password: process.env.TEST_PATIENT_PASSWORD || 'TestPassword123!',
    firstName: 'Test',
    lastName: 'Patient'
  },
  clinicAdmin: {
    email: process.env.TEST_CLINIC_ADMIN_EMAIL || 'admin@clinic.example.com',
    password: process.env.TEST_CLINIC_ADMIN_PASSWORD || 'AdminPassword123!',
    firstName: 'Clinic',
    lastName: 'Admin'
  }
};

// Test appointment data
export const testAppointment = {
  date: '2025-10-20',
  time: '14:00',
  type: 'checkup',
  notes: 'Regular checkup appointment - E2E test'
};

// Test patient data
export const testPatient = {
  firstName: 'John',
  lastName: 'Doe',
  email: `test.patient.${Date.now()}@example.com`,
  phone: '+1234567890',
  dateOfBirth: '1990-01-15'
};

// Test Telegram invite data
export const testTelegramInvite = {
  notes: 'E2E test invite code',
  expiresIn: 7 // days
};

// API endpoints
export const apiEndpoints = {
  login: '/api/v1/auth/login',
  logout: '/api/v1/auth/logout',
  dashboard: '/api/v1/dashboard',
  patients: '/api/v1/patients',
  appointments: '/api/v1/appointments',
  telegram: {
    invites: '/api/v1/telegram-admin/invite-codes',
    users: '/api/v1/telegram-admin/users',
    conversations: '/api/v1/telegram-admin/conversations'
  }
};

// Test timeouts
export const timeouts = {
  short: 5000,
  medium: 10000,
  long: 15000,
  veryLong: 30000
};

// Test viewport sizes
export const viewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1920, height: 1080 }
};

