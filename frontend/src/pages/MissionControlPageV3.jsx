import React, { useState, useEffect } from 'react';
import { MissionControlLayoutV2 } from '../components/layout/MissionControlLayoutV2';
import { AgentStatusCardV2 } from '../components/dashboard/AgentStatusCardV2';
import { PriorityCard } from '../components/dashboard/PriorityCard';
import { AgentChatModal } from '../components/dashboard/AgentChatModal';
import { PatientActions, AppointmentActions, FinancialActions, ActionToast } from '../components/dashboard/EmbeddedActions';
import { ProactiveSuggestionsPanel } from '../components/dashboard/ProactiveSuggestionsPanel';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Skeleton } from '../components/ui/Skeleton';
import { dataService } from '../services/dataService';
import { 
  MessageCircle, 
  Calendar, 
  DollarSign,
  TrendingUp,
  Clock,
  AlertCircle,
  Users,
  Sparkles
} from 'lucide-react';

const MissionControlPageV3 = () => {
  // State
  const [agents, setAgents] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Agent chat modal
  const [chatModalOpen, setChatModalOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [chatContext, setChatContext] = useState(null);
  
  // Action toast
  const [actionToast, setActionToast] = useState(null);
  
  // Active tab
  const [activeTab, setActiveTab] = useState('suggestions');

  // Fetch data
  useEffect(() => {
    fetchAllData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      const [
        agentsData,
        conversationsData,
        appointmentsData,
        patientsData,
        metricsData,
        logsData,
        alertsData,
      ] = await Promise.all([
        dataService.getAgents(),
        dataService.getConversations(),
        dataService.getAppointments(),
        dataService.getPatients(),
        dataService.getMetrics(),
        dataService.getLogs(),
        dataService.getAlerts(),
      ]);

      setAgents(agentsData);
      setConversations(conversationsData);
      setAppointments(appointmentsData.slice(0, 10));
      setPatients(patientsData);
      setMetrics(metricsData);
      setLogs(logsData);
      setAlerts(alertsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handlers
  const handleAgentChat = (agent, context = null) => {
    setSelectedAgent(agent);
    setChatContext(context);
    setChatModalOpen(true);
  };

  const handlePatientAction = async (actionType, data) => {
    const agentMap = {
      call: 'Alex',
      schedule: 'Alex',
      payment_reminder: 'Marcus',
    };

    const agent = agentMap[actionType];
    
    setActionToast({
      agent,
      message: `${agent} is ${actionType.replace('_', ' ')}ing ${data.patient.name}...`,
      estimatedTime: '2 minutes',
    });

    // TODO: Call backend API
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setActionToast(null);
  };

  const handleAppointmentAction = async (actionType, data) => {
    const agentMap = {
      confirm: 'Alex',
      reminder: 'Alex',
      reschedule: 'Sophia',
    };

    const agent = agentMap[actionType];
    
    setActionToast({
      agent,
      message: `${agent} is handling appointment ${actionType}...`,
      estimatedTime: '1 minute',
    });

    await new Promise(resolve => setTimeout(resolve, 2000));
    setActionToast(null);
  };

  const handleFinancialAction = async (actionType, data) => {
    setActionToast({
      agent: 'Marcus',
      message: `Marcus is ${actionType}ing financial data...`,
      estimatedTime: '3 minutes',
    });

    await new Promise(resolve => setTimeout(resolve, 2000));
    setActionToast(null);
  };

  // Render tabs
  const renderTabContent = () => {
    switch (activeTab) {
      case 'suggestions':
        return <ProactiveSuggestionsPanel />;
      
      case 'conversations':
        return (
          <div className="space-y-3">
            {conversations.slice(0, 5).map((conv) => (
              <PriorityCard
                key={conv.id}
                priority={conv.priority}
                title={conv.patient_name}
                description={conv.message}
                time={conv.waiting_time}
                agent={conv.handled_by}
                onTakeOver={() => handleAgentChat(
                  agents.find(a => a.name === conv.handled_by),
                  { type: 'conversation', data: conv }
                )}
                onViewDetails={() => {}}
              />
            ))}
          </div>
        );
      
      case 'patients':
        return (
          <div className="space-y-3">
            {patients.slice(0, 10).map((patient) => (
              <Card key={patient.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{patient.name}</h4>
                    <p className="text-sm text-gray-600">{patient.phone}</p>
                    <p className="text-xs text-gray-500">{patient.visits} visits</p>
                  </div>
                  <Badge variant="default" size="sm">
                    {patient.status}
                  </Badge>
                </div>
                <PatientActions 
                  patient={patient}
                  onAction={handlePatientAction}
                />
              </Card>
            ))}
          </div>
        );
      
      case 'logs':
        return (
          <div className="space-y-2">
            {(logs || []).map((log, index) => (
              <Card key={index} className="p-3">
                <div className="flex items-start gap-3">
                  <Badge 
                    variant={
                      log.level === 'ERROR' ? 'destructive' :
                      log.level === 'WARN' ? 'warning' : 'default'
                    }
                    size="sm"
                  >
                    {log.level}
                  </Badge>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {log.agent}
                    </p>
                    <p className="text-sm text-gray-600">{log.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{log.time}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        );
      
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <MissionControlLayoutV2>
        <div className="space-y-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </MissionControlLayoutV2>
    );
  }

  return (
    <>
      <MissionControlLayoutV2>
        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Agents & Overview */}
          <div className="col-span-3 space-y-4">
            {/* Today's Overview */}
            <Card className="p-4">
              <h3 className="text-sm font-semibold text-gray-600 mb-3">
                Today's Overview
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>Appointments</span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">
                    {metrics?.appointments_today || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <DollarSign className="w-4 h-4" />
                    <span>Revenue</span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">
                    ₪{metrics?.revenue_today || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MessageCircle className="w-4 h-4" />
                    <span>Active Chats</span>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">
                    {metrics?.active_conversations || 0}
                  </span>
                </div>
              </div>
            </Card>

            {/* Agent Cards */}
            <div className="space-y-3">
              {agents.map((agent) => (
                <AgentStatusCardV2
                  key={agent.name}
                  {...agent}
                  onChatClick={() => handleAgentChat(agent)}
                />
              ))}
            </div>
          </div>

          {/* Center Stage - Main Content */}
          <div className="col-span-6 space-y-4">
            {/* Tabs */}
            <Card className="p-1">
              <div className="flex gap-1">
                {[
                  { id: 'suggestions', label: 'Smart Suggestions', icon: Sparkles, count: 5 },
                  { id: 'conversations', label: 'Priority Queue', icon: MessageCircle, count: 3 },
                  { id: 'patients', label: 'Patients', icon: Users, count: (patients || []).length },
                  { id: 'logs', label: 'System Logs', icon: Clock, count: (logs || []).length },
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                      {tab.count > 0 && (
                        <Badge 
                          variant={activeTab === tab.id ? 'default' : 'secondary'}
                          size="sm"
                          className={activeTab === tab.id ? 'bg-white/20 text-white' : ''}
                        >
                          {tab.count}
                        </Badge>
                      )}
                    </button>
                  );
                })}
              </div>
            </Card>

            {/* Tab Content */}
            <div className="min-h-[600px]">
              {renderTabContent()}
            </div>
          </div>

          {/* Right Sidebar - Context & Actions */}
          <div className="col-span-3 space-y-4">
            {/* Today's Appointments */}
            <Card className="p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Today's Appointments
              </h3>
              <div className="space-y-2">
                {(appointments || []).map((apt, index) => (
                  <div key={index} className="p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">
                        {apt.time}
                      </span>
                      <Badge variant="default" size="sm">
                        {apt.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{apt.patient_name}</p>
                    <AppointmentActions
                      appointment={apt}
                      onAction={handleAppointmentAction}
                    />
                  </div>
                ))}
              </div>
            </Card>

            {/* Financial Summary */}
            <Card className="p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                Financial Summary
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-600">Payment Success Rate</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {metrics?.payment_success_rate || 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${metrics?.payment_success_rate || 0}%` }}
                    />
                  </div>
                </div>
                <FinancialActions
                  data={metrics}
                  onAction={handleFinancialAction}
                />
              </div>
            </Card>

            {/* Alerts */}
            {(alerts || []).length > 0 && (
              <Card className="p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  Alerts
                </h3>
                <div className="space-y-2">
                  {alerts.slice(0, 3).map((alert, index) => (
                    <div key={index} className="p-2 bg-red-50 rounded-lg border border-red-200">
                      <p className="text-sm font-medium text-red-900">{alert.title}</p>
                      <p className="text-xs text-red-700 mt-1">{alert.message}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </MissionControlLayoutV2>

      {/* Agent Chat Modal */}
      {chatModalOpen && selectedAgent && (
        <AgentChatModal
          isOpen={chatModalOpen}
          onClose={() => {
            setChatModalOpen(false);
            setSelectedAgent(null);
            setChatContext(null);
          }}
          agent={selectedAgent}
          initialContext={chatContext}
        />
      )}

      {/* Action Toast */}
      {actionToast && (
        <ActionToast
          action={actionToast}
          agent={actionToast.agent}
          onClose={() => setActionToast(null)}
        />
      )}
    </>
  );
};

export default MissionControlPageV3;
