/**
 * Constants for Agentic Dashboard
 */

export const SUBSCRIPTION_PLANS = {
  starter: {
    name: 'Starter',
    price: 1633,
    features: ['basic_ai', 'patient_portal'],
    color: 'bg-slate-500'
  },
  professional: {
    name: 'Professional',
    price: 3070,
    features: ['basic_ai', 'patient_portal', 'advanced_ai', 'sms', 'analytics'],
    color: 'bg-blue-600'
  },
  enterprise: {
    name: 'Enterprise',
    price: 6141,
    features: ['all'],
    color: 'bg-amber-500'
  }
};

export const AGENTS_ROSTER = {
  ALEX: { id: 'alex', name: 'Alex', role: 'Patient Coordinator', color: 'blue' },
  SARAH: { id: 'sarah', name: 'Sarah', role: 'Clinical Operations', color: 'purple' },
  MARCUS: { id: 'marcus', name: 'Marcus', role: 'CFO', color: 'emerald' },
  SOPHIA: { id: 'sophia', name: 'Sophia', role: 'Practice Admin', color: 'orange' },
  HARPER: { id: 'harper', name: 'Harper', role: 'HIPAA Specialist', color: 'red' }
};

export const PRIORITY_COLORS = {
  low: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400',
  medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400',
  high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400',
  critical: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
};

export const STATUS_COLORS = {
  active: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400',
  inactive: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
  debt: 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400'
};

export const AGENT_COLORS = {
  alex: 'bg-blue-500',
  sarah: 'bg-purple-500',
  marcus: 'bg-emerald-500',
  sophia: 'bg-orange-500',
  harper: 'bg-red-500'
};
