import React, { useState, useEffect } from 'react';
import { 
  MissionControlLayoutV2, 
  LeftPanel, 
  CenterStage, 
  RightSidebar 
} from '../components/layout/MissionControlLayoutV2';
import { AgentStatusCardV2 } from '../components/dashboard/AgentStatusCardV2';
import { PriorityCard } from '../components/dashboard/PriorityCard';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { SkeletonCard } from '../components/ui/Skeleton';
import { 
  TrendingUp, 
  Calendar, 
  DollarSign, 
  Activity,
  AlertTriangle,
  FileText,
  Users,
  Settings as SettingsIcon
} from 'lucide-react';
import { formatNumber, formatCurrency, timeAgo } from '../lib/utils';
import * as dataService from '../services/dataService';

const MissionControlPageV2 = () => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [agents, setAgents] = useState([]);
  const [priorityQueue, setPriorityQueue] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [logs, setLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [activeTab, setActiveTab] = useState('priority'); // 'priority', 'logs', 'alerts', 'patients'

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [
        metricsData,
        agentStatusData,
        conversationsData,
        appointmentsData,
        patientsData,
        logsData,
        alertsData,
      ] = await Promise.all([
        dataService.fetchDashboardMetrics(),
        dataService.fetchAgentStatus(),
        dataService.fetchActiveConversations(),
        dataService.fetchAppointments('today', 10),
        dataService.fetchPatients(50),
        dataService.fetchSystemLogs(50),
        dataService.fetchAlerts(20),
      ]);

      setMetrics(metricsData);
      setAgents(agentStatusData.agents || []);
      setPriorityQueue(conversationsData);
      setAppointments(appointmentsData);
      setPatients(patientsData);
      setLogs(logsData);
      setAlerts(alertsData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const handleTakeOver = async (conversationId) => {
    try {
      await dataService.takeOverConversation(conversationId);
      // Refresh data
      await fetchAllData();
      alert('Successfully took over conversation!');
    } catch (error) {
      console.error('Error taking over:', error);
      alert('Failed to take over conversation. Please try again.');
    }
  };

  const handleViewDetails = (id) => {
    console.log('Viewing details for:', id);
    // TODO: Open modal with full conversation details
  };

  if (loading) {
    return (
      <MissionControlLayoutV2>
        <LeftPanel>
          <SkeletonCard />
          <SkeletonCard />
        </LeftPanel>
        <CenterStage>
          <SkeletonCard />
          <SkeletonCard />
        </CenterStage>
        <RightSidebar>
          <SkeletonCard />
        </RightSidebar>
      </MissionControlLayoutV2>
    );
  }

  return (
    <MissionControlLayoutV2>
      {/* Left Panel: Agent Status & Quick Metrics */}
      <LeftPanel>
        {/* Agent Status Cards */}
        <div className="space-y-3">
          {agents.map((agent) => (
            <AgentStatusCardV2 key={agent.name} {...agent} />
          ))}
        </div>

        {/* Quick Metrics */}
        <Card className="bg-gradient-to-br from-blue-50 to-cyan-50">
          <CardHeader>
            <CardTitle className="text-base">Today's Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Calendar className="w-4 h-4" />
                <span>Appointments</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-2xl font-bold text-gray-900">
                  {metrics?.appointments_today || 0}
                </span>
                <TrendingUp className="w-4 h-4 text-green-600" />
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <DollarSign className="w-4 h-4" />
                <span>Revenue</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-xl font-bold text-gray-900">
                  {formatCurrency(metrics?.revenue_today || 0)}
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Activity className="w-4 h-4" />
                <span>Active Chats</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-2xl font-bold text-gray-900">
                  {metrics?.active_conversations || 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </LeftPanel>

      {/* Center Stage: Tabbed Content */}
      <CenterStage>
        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mb-4">
          <Button
            variant={activeTab === 'priority' ? 'primary' : 'ghost'}
            size="md"
            onClick={() => setActiveTab('priority')}
          >
            <AlertTriangle className="w-4 h-4" />
            Priority Queue ({priorityQueue.length})
          </Button>
          <Button
            variant={activeTab === 'logs' ? 'primary' : 'ghost'}
            size="md"
            onClick={() => setActiveTab('logs')}
          >
            <FileText className="w-4 h-4" />
            System Logs
          </Button>
          <Button
            variant={activeTab === 'alerts' ? 'primary' : 'ghost'}
            size="md"
            onClick={() => setActiveTab('alerts')}
          >
            <AlertTriangle className="w-4 h-4" />
            Alerts ({alerts.length})
          </Button>
          <Button
            variant={activeTab === 'patients' ? 'primary' : 'ghost'}
            size="md"
            onClick={() => setActiveTab('patients')}
          >
            <Users className="w-4 h-4" />
            Patients
          </Button>
        </div>

        {/* Priority Queue Tab */}
        {activeTab === 'priority' && (
          <div className="space-y-4 stagger-children">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Priority Queue</h2>
                <p className="text-sm text-gray-600">Items requiring immediate attention</p>
              </div>
              <Badge variant="info" size="lg">
                {priorityQueue.length} items
              </Badge>
            </div>

            {priorityQueue.map((item) => (
              <PriorityCard
                key={item.id}
                {...item}
                onTakeOver={() => handleTakeOver(item.id)}
                onViewDetails={() => handleViewDetails(item.id)}
              />
            ))}

            {priorityQueue.length === 0 && (
              <Card>
                <CardContent className="text-center py-12">
                  <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    All Clear!
                  </p>
                  <p className="text-sm text-gray-600">
                    No conversations require immediate attention
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* System Logs Tab */}
        {activeTab === 'logs' && (
          <Card>
            <CardHeader>
              <CardTitle>System Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {logs.map((log) => (
                  <div 
                    key={log.id}
                    className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Badge 
                      variant={
                        log.level === 'ERROR' ? 'error' :
                        log.level === 'WARN' ? 'warning' :
                        'info'
                      }
                      size="sm"
                    >
                      {log.level}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-gray-900">
                          {log.agent}
                        </span>
                        <span className="text-xs text-gray-500">
                          {timeAgo(log.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{log.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <Card>
            <CardHeader>
              <CardTitle>System Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div 
                    key={alert.id}
                    className={`p-4 border-l-4 rounded-lg ${
                      alert.severity === 'high' 
                        ? 'bg-red-50 border-red-500' 
                        : 'bg-orange-50 border-orange-500'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className={`w-5 h-5 ${
                          alert.severity === 'high' ? 'text-red-600' : 'text-orange-600'
                        }`} />
                        <h4 className="font-semibold text-gray-900">
                          {alert.title}
                        </h4>
                      </div>
                      <Badge variant={alert.agent.toLowerCase()} size="sm">
                        {alert.agent}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
                    <p className="text-xs text-gray-500">
                      {timeAgo(alert.timestamp)}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Patients Tab */}
        {activeTab === 'patients' && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Patients</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {patients.slice(0, 20).map((patient, idx) => (
                  <div 
                    key={idx}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900 truncate">
                        {patient.name}
                      </p>
                      <p className="text-xs text-gray-600 truncate">
                        {patient.phone} • {patient.email}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {patient.total_visits || 0} visits
                      </p>
                      <Badge 
                        variant={patient.status === 'active' ? 'success' : 'default'}
                        size="sm"
                      >
                        {patient.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </CenterStage>

      {/* Right Sidebar: Today's Appointments & Financial Summary */}
      <RightSidebar>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Today's Appointments</CardTitle>
              <Badge variant="info">{appointments.length}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {appointments.map((apt, idx) => (
                <div 
                  key={idx}
                  className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-gray-900 truncate">
                        {apt.patient_name}
                      </p>
                      <p className="text-xs text-gray-600 truncate">
                        {apt.patient_phone}
                      </p>
                    </div>
                    <Badge 
                      variant={apt.status === 'confirmed' ? 'success' : 'warning'}
                      size="sm"
                    >
                      {apt.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-3 h-3" />
                    <span>{apt.appointment_time}</span>
                  </div>
                  {apt.treatment_type && (
                    <p className="text-xs text-gray-500 mt-1">
                      {apt.treatment_type}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Financial Summary */}
        {metrics && (
          <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
            <CardHeader>
              <CardTitle className="text-base">Financial Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Payment Success Rate</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 rounded-full transition-all"
                        style={{ width: `${metrics.payment_success_rate || 0}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-gray-900">
                      {(metrics.payment_success_rate || 0).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div>
                  <p className="text-sm text-gray-600 mb-1">Avg Response Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {(metrics.avg_response_time_seconds || 0).toFixed(1)}s
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </RightSidebar>
    </MissionControlLayoutV2>
  );
};

export default MissionControlPageV2;
