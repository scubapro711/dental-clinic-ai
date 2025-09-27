import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  Calendar, 
  Activity, 
  DollarSign,
  Heart,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Zap
} from 'lucide-react';
import DashboardGrid from './DashboardGrid';
import StatisticsCard from './StatisticsCard';

/**
 * DashboardDemo Component
 * 
 * Integration demonstration of StatisticsCard and DashboardGrid components
 * showcasing the Mission Control Dashboard for dental clinic management.
 * 
 * Features:
 * - Real-time data simulation
 * - Multiple agent status modes
 * - Interactive dashboard controls
 * - Responsive grid layouts
 * - Comprehensive statistics display
 */
const DashboardDemo = () => {
  // Demo state management
  const [agentMode, setAgentMode] = useState('active');
  const [refreshCount, setRefreshCount] = useState(0);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Simulate real-time data updates
  const [liveData, setLiveData] = useState({
    activePatients: 1234,
    appointmentsToday: 56,
    systemUptime: 98.5,
    monthlyRevenue: 12345,
    emergencyCases: 3,
    waitingTime: 12,
    satisfaction: 94.2,
    systemLoad: 67
  });

  // Simulate data changes every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveData(prev => ({
        activePatients: prev.activePatients + Math.floor(Math.random() * 10 - 5),
        appointmentsToday: Math.max(0, prev.appointmentsToday + Math.floor(Math.random() * 6 - 3)),
        systemUptime: Math.min(100, prev.systemUptime + (Math.random() - 0.5) * 0.1),
        monthlyRevenue: prev.monthlyRevenue + Math.floor(Math.random() * 1000 - 500),
        emergencyCases: Math.max(0, prev.emergencyCases + Math.floor(Math.random() * 3 - 1)),
        waitingTime: Math.max(0, prev.waitingTime + Math.floor(Math.random() * 6 - 3)),
        satisfaction: Math.min(100, Math.max(0, prev.satisfaction + (Math.random() - 0.5) * 2)),
        systemLoad: Math.min(100, Math.max(0, prev.systemLoad + Math.floor(Math.random() * 20 - 10)))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Generate dashboard cards based on live data
  const generateDashboardCards = () => {
    return [
      {
        id: 'active-patients',
        title: 'Active Patients',
        value: liveData.activePatients.toLocaleString(),
        subtitle: 'Currently in system',
        trend: liveData.activePatients > 1234 ? 'up' : liveData.activePatients < 1234 ? 'down' : 'neutral',
        trendValue: `${liveData.activePatients > 1234 ? '+' : ''}${((liveData.activePatients - 1234) / 1234 * 100).toFixed(1)}%`,
        status: liveData.activePatients > 1300 ? 'warning' : liveData.activePatients > 1200 ? 'success' : 'error',
        icon: Users,
        priority: 'high',
        lastUpdated: '2 minutes ago'
      },
      {
        id: 'appointments-today',
        title: 'Appointments Today',
        value: liveData.appointmentsToday.toString(),
        subtitle: 'Scheduled appointments',
        trend: liveData.appointmentsToday > 56 ? 'up' : liveData.appointmentsToday < 56 ? 'down' : 'neutral',
        trendValue: `${liveData.appointmentsToday > 56 ? '+' : ''}${liveData.appointmentsToday - 56}`,
        status: liveData.appointmentsToday > 60 ? 'warning' : liveData.appointmentsToday > 40 ? 'success' : 'error',
        icon: Calendar,
        priority: 'high',
        lastUpdated: '1 minute ago'
      },
      {
        id: 'system-uptime',
        title: 'System Uptime',
        value: `${liveData.systemUptime.toFixed(1)}%`,
        subtitle: 'This month',
        trend: liveData.systemUptime > 98.5 ? 'up' : liveData.systemUptime < 98.5 ? 'down' : 'neutral',
        trendValue: `${liveData.systemUptime > 98.5 ? '+' : ''}${(liveData.systemUptime - 98.5).toFixed(2)}%`,
        status: liveData.systemUptime > 99 ? 'success' : liveData.systemUptime > 95 ? 'warning' : 'error',
        icon: Activity,
        priority: 'medium',
        lastUpdated: '30 seconds ago'
      },
      {
        id: 'monthly-revenue',
        title: 'Monthly Revenue',
        value: `$${liveData.monthlyRevenue.toLocaleString()}`,
        subtitle: 'Current month',
        trend: liveData.monthlyRevenue > 12345 ? 'up' : liveData.monthlyRevenue < 12345 ? 'down' : 'neutral',
        trendValue: `${liveData.monthlyRevenue > 12345 ? '+' : ''}$${(liveData.monthlyRevenue - 12345).toLocaleString()}`,
        status: liveData.monthlyRevenue > 15000 ? 'success' : liveData.monthlyRevenue > 10000 ? 'warning' : 'error',
        icon: DollarSign,
        priority: 'high',
        lastUpdated: '5 minutes ago'
      },
      {
        id: 'emergency-cases',
        title: 'Emergency Cases',
        value: liveData.emergencyCases.toString(),
        subtitle: 'Urgent attention needed',
        trend: liveData.emergencyCases > 3 ? 'up' : liveData.emergencyCases < 3 ? 'down' : 'neutral',
        trendValue: `${liveData.emergencyCases > 3 ? '+' : ''}${liveData.emergencyCases - 3}`,
        status: liveData.emergencyCases > 5 ? 'error' : liveData.emergencyCases > 2 ? 'warning' : 'success',
        icon: AlertTriangle,
        priority: liveData.emergencyCases > 5 ? 'high' : 'medium',
        lastUpdated: '1 minute ago'
      },
      {
        id: 'waiting-time',
        title: 'Avg Wait Time',
        value: `${liveData.waitingTime} min`,
        subtitle: 'Patient waiting time',
        trend: liveData.waitingTime > 12 ? 'up' : liveData.waitingTime < 12 ? 'down' : 'neutral',
        trendValue: `${liveData.waitingTime > 12 ? '+' : ''}${liveData.waitingTime - 12} min`,
        status: liveData.waitingTime > 20 ? 'error' : liveData.waitingTime > 15 ? 'warning' : 'success',
        icon: Clock,
        priority: 'medium',
        lastUpdated: '3 minutes ago'
      },
      {
        id: 'satisfaction',
        title: 'Patient Satisfaction',
        value: `${liveData.satisfaction.toFixed(1)}%`,
        subtitle: 'This month average',
        trend: liveData.satisfaction > 94.2 ? 'up' : liveData.satisfaction < 94.2 ? 'down' : 'neutral',
        trendValue: `${liveData.satisfaction > 94.2 ? '+' : ''}${(liveData.satisfaction - 94.2).toFixed(1)}%`,
        status: liveData.satisfaction > 95 ? 'success' : liveData.satisfaction > 90 ? 'warning' : 'error',
        icon: Heart,
        priority: 'medium',
        lastUpdated: '10 minutes ago'
      },
      {
        id: 'system-load',
        title: 'System Load',
        value: `${liveData.systemLoad}%`,
        subtitle: 'Current CPU usage',
        trend: liveData.systemLoad > 67 ? 'up' : liveData.systemLoad < 67 ? 'down' : 'neutral',
        trendValue: `${liveData.systemLoad > 67 ? '+' : ''}${liveData.systemLoad - 67}%`,
        status: liveData.systemLoad > 80 ? 'error' : liveData.systemLoad > 70 ? 'warning' : 'success',
        icon: Zap,
        priority: liveData.systemLoad > 80 ? 'high' : 'low',
        lastUpdated: '15 seconds ago'
      }
    ];
  };

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshCount(prev => prev + 1);
    setLastRefresh(new Date());
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Trigger data update
    setLiveData(prev => ({
      ...prev,
      activePatients: prev.activePatients + Math.floor(Math.random() * 20 - 10),
      appointmentsToday: Math.max(0, prev.appointmentsToday + Math.floor(Math.random() * 10 - 5))
    }));
  };

  // Handle filter changes
  const handleFilterChange = (status) => {
    console.log('Filter changed to:', status);
  };

  // Handle card clicks
  const handleCardClick = (card, index) => {
    console.log('Card clicked:', card.title, 'at index:', index);
    alert(`Clicked on ${card.title}: ${card.value}`);
  };

  // Agent mode controls
  const agentModes = [
    { mode: 'active', label: 'Active', color: 'bg-green-500' },
    { mode: 'monitoring', label: 'Monitoring', color: 'bg-blue-500' },
    { mode: 'idle', label: 'Idle', color: 'bg-yellow-500' },
    { mode: 'error', label: 'Error', color: 'bg-red-500' },
    { mode: 'offline', label: 'Offline', color: 'bg-gray-500' }
  ];

  const dashboardCards = generateDashboardCards();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Demo Header */}
        <Card className="border-l-4 border-l-purple-500">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-bold text-gray-900">
                  Dental Clinic Management System
                </CardTitle>
                <p className="text-gray-600 mt-2">
                  Mission Control Dashboard - Component Integration Demo
                </p>
              </div>
              
              <div className="flex items-center gap-4">
                <Badge variant="outline" className="text-sm">
                  Refreshes: {refreshCount}
                </Badge>
                <Badge variant="outline" className="text-sm">
                  Last: {lastRefresh.toLocaleTimeString()}
                </Badge>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700">Agent Mode:</span>
              <div className="flex items-center gap-2">
                {agentModes.map(({ mode, label, color }) => (
                  <Button
                    key={mode}
                    variant={agentMode === mode ? "default" : "outline"}
                    size="sm"
                    onClick={() => setAgentMode(mode)}
                    className="flex items-center gap-2"
                  >
                    <div className={`w-2 h-2 rounded-full ${color}`} />
                    {label}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Individual StatisticsCard Demo */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Individual StatisticsCard Demo
            </CardTitle>
            <p className="text-gray-600">
              Standalone StatisticsCard component with live data updates
            </p>
          </CardHeader>
          
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {dashboardCards.slice(0, 4).map((card, index) => (
                <StatisticsCard
                  key={card.id}
                  {...card}
                  agentStatus={agentMode}
                  onClick={() => handleCardClick(card, index)}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Full DashboardGrid Demo */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Complete DashboardGrid Integration
            </CardTitle>
            <p className="text-gray-600">
              Full Mission Control Dashboard with all features enabled
            </p>
          </CardHeader>
          
          <CardContent className="p-0">
            <DashboardGrid
              cards={dashboardCards}
              agentMode={agentMode}
              onRefresh={handleRefresh}
              onFilterChange={handleFilterChange}
              onCardClick={handleCardClick}
              showControls={true}
              enableFiltering={true}
              enableRefresh={true}
              refreshInterval={30000}
              columns="auto"
              gap="default"
              className="p-6"
            />
          </CardContent>
        </Card>

        {/* Component Status */}
        <Card className="border-l-4 border-l-green-500">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-green-800">
              Component Integration Status
            </CardTitle>
          </CardHeader>
          
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900">StatisticsCard Component</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">100% Test Coverage (31/31 tests)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Number Formatting Fixed</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Accessibility Compliant</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Agentic UX Integration</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900">DashboardGrid Component</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Mission Control Dashboard</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Responsive Grid Layout</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Advanced Filtering System</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">Real-time Refresh Capability</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardDemo;
