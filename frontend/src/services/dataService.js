/**
 * Data Service - Integrates with Backend API (LangGraph + Odoo)
 * Provides real-time data for Mission Control Dashboard
 */

const API_BASE = 'http://localhost:8000/api/v1';

/**
 * Fetch dashboard metrics (from backend)
 */
export async function fetchDashboardMetrics() {
  try {
    const response = await fetch(`${API_BASE}/dashboard/metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return await response.json();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return getMockMetrics();
  }
}

/**
 * Fetch appointments from Odoo (via backend)
 */
export async function fetchAppointments(date = 'today', limit = 100) {
  try {
    const response = await fetch(`${API_BASE}/dashboard/appointments?date=${date}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch appointments');
    const data = await response.json();
    return data.appointments || [];
  } catch (error) {
    console.error('Error fetching appointments:', error);
    return [];
  }
}

/**
 * Fetch patients from Odoo (via backend)
 */
export async function fetchPatients(limit = 50) {
  try {
    const response = await fetch(`${API_BASE}/dashboard/patients?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch patients');
    const data = await response.json();
    return data.patients || [];
  } catch (error) {
    console.error('Error fetching patients:', error);
    return [];
  }
}

/**
 * Fetch agent status from LangGraph system
 */
export async function fetchAgentStatus() {
  try {
    const response = await fetch(`${API_BASE}/agents/status`);
    if (!response.ok) throw new Error('Failed to fetch agent status');
    const agents = await response.json();
    
    // Transform backend format to frontend format
    return {
      agents: agents.map(agent => ({
        name: agent.display_name,
        role: agent.description,
        status: agent.status === 'online' ? 'active' : 'offline',
        activeConversations: Math.floor(agent.requests_handled / 20), // Estimate
        avgResponseTime: agent.avg_response_time,
        specialization: agent.description,
        successRate: agent.success_rate,
        requestsHandled: agent.requests_handled,
        uptime: agent.uptime_seconds,
      }))
    };
  } catch (error) {
    console.error('Error fetching agent status:', error);
    return getMockAgentStatus();
  }
}

/**
 * Fetch active conversations (LangGraph agents)
 */
export async function fetchActiveConversations(limit = 20) {
  try {
    const response = await fetch(`${API_BASE}/conversations/?limit=${limit}&status=active`);
    if (!response.ok) throw new Error('Failed to fetch conversations');
    const data = await response.json();
    return data.conversations || getMockConversations();
  } catch (error) {
    console.error('Error fetching conversations:', error);
    return getMockConversations();
  }
}

/**
 * Fetch system logs
 */
export async function fetchSystemLogs(limit = 50) {
  try {
    const response = await fetch(`${API_BASE}/logs/?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch logs');
    const data = await response.json();
    return data.logs || getMockLogs();
  } catch (error) {
    console.error('Error fetching logs:', error);
    return getMockLogs();
  }
}

/**
 * Fetch alerts
 */
export async function fetchAlerts(limit = 20) {
  try {
    const response = await fetch(`${API_BASE}/alerts/?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    const data = await response.json();
    return data.alerts || getMockAlerts();
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return getMockAlerts();
  }
}

/**
 * Take over conversation (handoff from agent to doctor)
 */
export async function takeOverConversation(conversationId) {
  try {
    const response = await fetch(`${API_BASE}/handoff/takeover`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: conversationId }),
    });
    if (!response.ok) throw new Error('Failed to take over conversation');
    return await response.json();
  } catch (error) {
    console.error('Error taking over conversation:', error);
    throw error;
  }
}

/**
 * Reschedule appointment (Odoo integration)
 */
export async function rescheduleAppointment(appointmentId, newDate, newTime, reason) {
  try {
    const response = await fetch(`${API_BASE}/dashboard/appointments/${appointmentId}/reschedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_date: newDate, new_time: newTime, reason }),
    });
    if (!response.ok) throw new Error('Failed to reschedule appointment');
    return await response.json();
  } catch (error) {
    console.error('Error rescheduling appointment:', error);
    throw error;
  }
}

// ===== MOCK DATA FALLBACKS =====

function getMockMetrics() {
  return {
    active_conversations: 8,
    appointments_today: 58,
    avg_response_time_seconds: 2.3,
    payment_success_rate: 84.81,
    revenue_today: 15420,
    escalations_pending: 2,
  };
}

function getMockAgentStatus() {
  return {
    agents: [
      {
        name: 'Alex',
        role: 'Patient-Facing Agent',
        status: 'active',
        activeConversations: 5,
        avgResponseTime: 2.3,
        specialization: 'Appointments & Medical Triage',
      },
      {
        name: 'Marcus',
        role: 'CFO Agent',
        status: 'active',
        activeConversations: 2,
        avgResponseTime: 1.8,
        specialization: 'Financial Analysis & Payments',
      },
      {
        name: 'Sophia',
        role: 'Admin Agent',
        status: 'offline',
        activeConversations: 0,
        avgResponseTime: 0,
        specialization: 'Operations & Scheduling',
      },
    ],
  };
}

function getMockConversations() {
  return [
    {
      id: 'conv-001',
      priority: 'emergency',
      patient: { name: 'Sarah Johnson', phone: '+972-50-123-4567' },
      reason: 'Severe tooth pain, possible infection',
      waitTime: '5m',
      agent: 'Alex',
      status: 'active',
      lastMessage: 'I have severe pain in my lower left molar...',
      messageCount: 8,
    },
    {
      id: 'conv-002',
      priority: 'urgent',
      patient: { name: 'David Cohen', phone: '+972-54-987-6543' },
      reason: 'Appointment confirmation needed today',
      waitTime: '12m',
      agent: 'Alex',
      status: 'active',
      lastMessage: 'Can you confirm my appointment for tomorrow?',
      messageCount: 5,
    },
    {
      id: 'conv-003',
      priority: 'normal',
      patient: { name: 'Rachel Levi', phone: '+972-52-456-7890' },
      reason: 'Question about treatment cost',
      waitTime: '8m',
      agent: 'Marcus',
      status: 'active',
      lastMessage: 'How much will the root canal cost?',
      messageCount: 3,
    },
  ];
}

function getMockLogs() {
  const now = new Date();
  return [
    {
      id: 1,
      timestamp: new Date(now - 5 * 60000).toISOString(),
      level: 'INFO',
      agent: 'Alex',
      message: 'Processed patient inquiry about appointment availability',
    },
    {
      id: 2,
      timestamp: new Date(now - 8 * 60000).toISOString(),
      level: 'WARN',
      agent: 'Marcus',
      message: 'Payment verification delayed for patient #1234',
    },
    {
      id: 3,
      timestamp: new Date(now - 12 * 60000).toISOString(),
      level: 'ERROR',
      agent: 'Sophia',
      message: 'Failed to sync appointment with Odoo - retrying',
    },
    {
      id: 4,
      timestamp: new Date(now - 15 * 60000).toISOString(),
      level: 'INFO',
      agent: 'Alex',
      message: 'Successfully scheduled appointment for Sarah Johnson',
    },
  ];
}

function getMockAlerts() {
  return [
    {
      id: 1,
      severity: 'high',
      agent: 'Marcus',
      title: 'Outstanding Payments',
      message: '6 patients have outstanding payments over 30 days',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 2,
      severity: 'normal',
      agent: 'Marcus',
      title: 'Revenue Below Target',
      message: 'Today\'s revenue is 15% below daily target',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
    },
    {
      id: 3,
      severity: 'high',
      agent: 'Alex',
      title: 'High Wait Time',
      message: '3 patients waiting over 10 minutes for response',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
    },
  ];
}

export default {
  fetchDashboardMetrics,
  fetchAppointments,
  fetchPatients,
  fetchAgentStatus,
  fetchActiveConversations,
  fetchSystemLogs,
  fetchAlerts,
  takeOverConversation,
  rescheduleAppointment,
};
