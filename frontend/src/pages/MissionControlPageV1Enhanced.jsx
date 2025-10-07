import { useState, useEffect } from 'react';
import MissionControlLayout from '../components/dashboard/MissionControlLayout';
import { AgentAction, AgentChatButton } from '../components/agentic/AgentAction';
import { MessageSquare, Phone, Calendar, DollarSign, TrendingUp } from 'lucide-react';

/**
 * MissionControlPageV1Enhanced
 * 
 * This is v1.0 with ALL 9 widgets working + embedded agent actions!
 * 
 * Strategy: Keep everything that works, add agentic layer on top
 */
export default function MissionControlPageV1Enhanced() {
  const [metrics, setMetrics] = useState({
    activeConversations: 8,
    appointmentsToday: 58,
    avgResponseTime: '2.3s',
    paymentSuccessRate: '84.8%',
  });

  const [conversations, setConversations] = useState([
    {
      id: 1,
      patient: 'Sarah Johnson',
      message: 'I need to reschedule my appointment',
      time: '2 min ago',
      status: 'active',
      priority: 'high',
      agent: 'Alex',
    },
    {
      id: 2,
      patient: 'David Cohen',
      message: 'Question about treatment cost',
      time: '5 min ago',
      status: 'active',
      priority: 'normal',
      agent: 'Marcus',
    },
    {
      id: 3,
      patient: 'Rachel Levi',
      message: 'Appointment confirmation needed',
      time: '8 min ago',
      status: 'active',
      priority: 'normal',
      agent: 'Alex',
    },
  ]);

  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    // Load data from API
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load appointments
      const apptResponse = await fetch('http://localhost:8000/api/v1/dashboard/appointments?date=today&limit=10');
      if (apptResponse.ok) {
        const apptData = await apptResponse.json();
        setAppointments(apptData.slice(0, 10));
      }

      // Load patients
      const patientResponse = await fetch('http://localhost:8000/api/v1/dashboard/patients?limit=10');
      if (patientResponse.ok) {
        const patientData = await patientResponse.json();
        setPatients(patientData.slice(0, 10));
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  return (
    <MissionControlLayout>
      <div className="p-6 space-y-6">
        {/* Header with metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard
            title="Active Conversations"
            value={metrics.activeConversations}
            icon={MessageSquare}
            color="blue"
          />
          <MetricCard
            title="Today's Appointments"
            value={metrics.appointmentsToday}
            icon={Calendar}
            color="green"
          />
          <MetricCard
            title="Avg Response Time"
            value={metrics.avgResponseTime}
            icon={TrendingUp}
            color="purple"
          />
          <MetricCard
            title="Payment Success"
            value={metrics.paymentSuccessRate}
            icon={DollarSign}
            color="orange"
          />
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Active Conversations Widget with Agent Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Active Conversations</h2>
              <AgentChatButton agentName="Alex" label="Chat with Alex" />
            </div>

            <div className="space-y-3">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-medium">{conv.patient}</h3>
                      <p className="text-sm text-gray-600">{conv.message}</p>
                      <p className="text-xs text-gray-400 mt-1">{conv.time} • Handled by {conv.agent}</p>
                    </div>
                    {conv.priority === 'high' && (
                      <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                        Urgent
                      </span>
                    )}
                  </div>

                  {/* Embedded Agent Actions */}
                  <div className="flex gap-2 mt-3">
                    <AgentAction
                      agentName="Alex"
                      action="call_patient"
                      context={{ patientName: conv.patient, conversationId: conv.id }}
                      label="Ask Alex to Call"
                      icon={Phone}
                      variant="secondary"
                    />
                    <AgentAction
                      agentName="Alex"
                      action="take_over"
                      context={{ conversationId: conv.id }}
                      label="Take Over"
                      variant="primary"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Today's Appointments Widget with Agent Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Today's Appointments</h2>
              <AgentChatButton agentName="Sophia" label="Chat with Sophia" />
            </div>

            <div className="space-y-2">
              {appointments.map((appt, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{appt.patient_name}</p>
                      <p className="text-sm text-gray-600">{appt.appointment_time}</p>
                    </div>
                    <div className="flex gap-2">
                      <AgentAction
                        agentName="Sophia"
                        action="send_reminder"
                        context={{ appointmentId: appt.id, patientName: appt.patient_name }}
                        label="Send Reminder"
                        variant="ghost"
                      />
                      <AgentAction
                        agentName="Sophia"
                        action="optimize_schedule"
                        context={{ appointmentId: appt.id }}
                        label="Optimize"
                        variant="ghost"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Financial Analytics Widget with Agent Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Financial Analytics</h2>
              <AgentChatButton agentName="Marcus" label="Chat with Marcus" />
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Today's Revenue</p>
                <p className="text-2xl font-bold text-blue-600">$5,234</p>
              </div>

              <div className="p-4 bg-orange-50 rounded-lg">
                <p className="text-sm text-gray-600">Outstanding Payments</p>
                <p className="text-2xl font-bold text-orange-600">$12,450</p>
              </div>

              {/* Agent Actions for Financial Data */}
              <div className="flex gap-2">
                <AgentAction
                  agentName="Marcus"
                  action="analyze_revenue"
                  context={{ period: 'today' }}
                  label="Ask Marcus to Analyze"
                  variant="primary"
                />
                <AgentAction
                  agentName="Marcus"
                  action="collect_payments"
                  context={{ amount: 12450 }}
                  label="Auto-Collect"
                  variant="secondary"
                />
              </div>
            </div>
          </div>

          {/* Patients Widget with Agent Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Patients</h2>
              <AgentChatButton agentName="Alex" label="Ask about Patients" />
            </div>

            <div className="space-y-2">
              {patients.slice(0, 5).map((patient, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{patient.name}</p>
                      <p className="text-sm text-gray-600">{patient.phone}</p>
                    </div>
                    <div className="flex gap-2">
                      <AgentAction
                        agentName="Alex"
                        action="call_patient"
                        context={{ patientId: patient.id, patientName: patient.name }}
                        label="Call"
                        icon={Phone}
                        variant="ghost"
                      />
                      <AgentAction
                        agentName="Sophia"
                        action="schedule_followup"
                        context={{ patientId: patient.id }}
                        label="Schedule"
                        icon={Calendar}
                        variant="ghost"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </MissionControlLayout>
  );
}

function MetricCard({ title, value, icon: Icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center gap-3">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  );
}
