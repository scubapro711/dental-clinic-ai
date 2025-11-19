// Constants and mock data for Agentic Dashboard

// FILE 1: CONSTANTS & MOCKS (src/data/mocks.js)
// ==========================================

// משתמשי דמו מתוך מסמך האימות (Flow 2)
const MOCK_USERS = {
    'rachel@dentaflow.ai': {
        id: 'usr_demo_admin',
        email: 'rachel@dentaflow.ai',
        full_name: 'Dr. Rachel Cohen',
        role: 'CLINIC_ADMIN',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rachel'
    },
    'sarah@example.com': {
        id: 'usr_demo_patient',
        email: 'sarah@example.com',
        full_name: 'Sarah Johnson',
        role: 'PATIENT',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah'
    }
};

const MOCK_ORG = {
  id: 'org_denta_flow_01',
  name: 'מרפאת שניידר - תל אביב',
  plan: 'professional'
};

const SUBSCRIPTION_PLANS = {
  starter: { name: 'Starter', price: 1633, features: ['basic_ai', 'patient_portal'], color: 'bg-slate-500' },
  professional: { name: 'Professional', price: 3070, features: ['basic_ai', 'patient_portal', 'advanced_ai', 'sms', 'analytics'], color: 'bg-blue-600' },
  enterprise: { name: 'Enterprise', price: 6141, features: ['all'], color: 'bg-amber-500' }
};

const AGENTS_ROSTER = {
  ALEX: { id: 'alex', name: 'Alex', role: 'Patient Coordinator', color: 'blue' },
  SARAH: { id: 'sarah', name: 'Sarah', role: 'Clinical Operations', color: 'purple' },
  MARCUS: { id: 'marcus', name: 'Marcus', role: 'CFO', color: 'emerald' },
  SOPHIA: { id: 'sophia', name: 'Sophia', role: 'Practice Admin', color: 'orange' },
  HARPER: { id: 'harper', name: 'Harper', role: 'HIPAA Specialist', color: 'red' }
};

const MOCK_PATIENTS_DB = [
  { 
    id: 1, 
    name: 'ישראל ישראלי', 
    email: 'israel@example.com', 
    phone: '050-1234567', 
    birth_date: '1980-01-01', 
    last_visit: '2025-11-19', 
    total_visits: 12, 
    outstanding_balance: 0.00, 
    insurance_provider: 'הראל', 
    status: 'active',
    address: 'רחוב הרצל 10, תל אביב',
    medical_history: {
      allergies: ['פניצילין', 'אגוזים'],
      conditions: ['סוכרת סוג 2'],
      medications: ['מטפורמין 500mg']
    },
    dental_chart: [
      { code: '18', status: 'missing' },
      { code: '16', status: 'filled', material: 'composite', date: '2023-05-10' },
      { code: '24', status: 'healthy' },
      { code: '36', status: 'root_canal', condition: 'good', date: '2024-01-15' },
      { code: '46', status: 'crown', material: 'zirconia' }
    ],
    treatments: [
      { id: 2001, date: '2025-11-19', type: 'root_canal', tooth: '36', desc: 'טיפול שורש - תעלה אחת', doctor: 'ד"ר רון כהן', cost: 1500, status: 'completed' },
      { id: 1998, date: '2025-06-10', type: 'cleaning', tooth: '', desc: 'הסרת אבנית', doctor: 'מיכל לוי (שיננית)', cost: 250, status: 'completed' }
    ],
    documents: [
       { id: 8001, name: 'צילום רנטגן - שן 36', type: 'xray', date: '2025-11-15', url: 'https://placehold.co/150x150/000000/FFF?text=XRAY-36' },
       { id: 8002, name: 'טופס הסכמה לטיפול', type: 'form', date: '2025-11-19', url: '#' }
    ]
  },
  { id: 2, name: 'רבקה מיכאלי', email: 'rivka@example.com', phone: '052-9876543', birth_date: '1992-05-15', last_visit: '2025-10-10', total_visits: 5, outstanding_balance: 450.00, insurance_provider: 'הפניקס', status: 'debt' },
  { id: 3, name: 'דנה רון', email: 'dana@example.com', phone: '054-3334444', birth_date: '1995-11-20', last_visit: '2025-11-01', total_visits: 2, outstanding_balance: 0.00, insurance_provider: 'מכבי שלי', status: 'active' }
];


export { MOCK_USERS, MOCK_ORG, SUBSCRIPTION_PLANS, AGENTS_ROSTER, MOCK_PATIENTS_DB };
