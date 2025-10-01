import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { 
  Activity,
  MessageSquare,
  BarChart3,
  Brain,
  Users,
  Calendar,
  DollarSign,
  Clock,
  AlertTriangle,
  CheckCircle,
  Zap,
  Phone,
  MessageCircle,
  TrendingUp,
  TrendingDown,
  Pause,
  Play,
  Settings,
  Bell,
  User,
  LogOut,
  Eye,
  EyeOff,
  RefreshCw,
  Download,
  Filter,
  Search,
  MoreVertical,
  ArrowRight,
  Shield,
  Cpu,
  Database,
  Wifi,
  WifiOff
} from 'lucide-react';
import DashboardGrid from './DashboardGrid';
import StatisticsCard from './StatisticsCard';
import RealTimeAlerts from './RealTimeAlerts';

/**
 * MissionControlDashboard Component
 * 
 * The complete Mission Control Dashboard implementing the Agentic UX vision
 * from the master plan document. Features all four main screens:
 * 1. General Overview (Dashboard)
 * 2. Chat History & Control
 * 3. Performance Analytics  
 * 4. Knowledge Management
 * 
 * Design follows exact specifications:
 * - Colors: #001529, #220, #f5f5f5
 * - Agentic UX principles
 * - Mission Control paradigm
 * - Human Handoff capabilities
 */
const MissionControlDashboard = () => {
  // Agent status management
  const [agentStatus, setAgentStatus] = useState('active');
  const [agentMode, setAgentMode] = useState('autonomous');
  const [lastActivity, setLastActivity] = useState(new Date());
  const [activeTab, setActiveTab] = useState('overview');
  
  // Real-time data simulation
  const [liveData, setLiveData] = useState({
    activePatients: 1234,
    appointmentsToday: 56,
    systemUptime: 98.5,
    monthlyRevenue: 12345,
    emergencyCases: 3,
    avgWaitTime: 12,
    satisfaction: 94.2,
    systemLoad: 67,
    activeChats: 8,
    successfulConversations: 142,
    avgHandlingTime: 185, // seconds
    handoffRate: 12.5
  });

  // Agent activity log
  const [agentActivities, setAgentActivities] = useState([
    {
      id: 1,
      time: '14:32',
      action: 'שיחה עם מטופל - דוד כהן',
      status: 'completed',
      channel: 'whatsapp',
      result: 'תור נקבע ל-15/10'
    },
    {
      id: 2,
      time: '14:28',
      action: 'עדכון יומן - ביטול תור',
      status: 'completed',
      channel: 'system',
      result: 'תור 16:00 בוטל, מטופל הוזמן'
    },
    {
      id: 3,
      time: '14:25',
      action: 'תקשורת עם מטופל - שרה לוי',
      status: 'needs_handoff',
      channel: 'phone',
      result: 'דרושה התערבות אנושית'
    }
  ]);

  // Performance data
  const [performanceData, setPerformanceData] = useState({
    conversionFunnel: [
      { stage: 'פניות ראשוניות', value: 245, percentage: 100 },
      { stage: 'שיחות מוצלחות', value: 198, percentage: 81 },
      { stage: 'תורים שנקבעו', value: 156, percentage: 64 },
      { stage: 'תורים שהתקיימו', value: 142, percentage: 58 }
    ],
    channelPerformance: [
      { channel: 'WhatsApp', conversations: 89, success: 94, handoff: 8 },
      { channel: 'טלפון', conversations: 67, success: 87, handoff: 18 },
      { channel: 'SMS', conversations: 34, success: 76, handoff: 15 }
    ]
  });

  // Knowledge base structure
  const [knowledgeBase, setKnowledgeBase] = useState({
    schedules: {
      name: 'לוחות זמנים',
      files: ['dr_cohen_schedule.yaml', 'clinic_hours.yaml'],
      lastUpdated: '2 שעות'
    },
    services: {
      name: 'שירותים ומחירים', 
      files: ['pricelist.yaml', 'treatments.yaml'],
      lastUpdated: '1 יום'
    },
    faq: {
      name: 'שאלות נפוצות',
      files: ['common_questions.yaml', 'emergency_protocols.yaml'],
      lastUpdated: '3 ימים'
    }
  });

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLastActivity(new Date());
      
      // Simulate agent activity
      if (Math.random() > 0.7) {
        const newActivity = {
          id: Date.now(),
          time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' }),
          action: 'פעילות חדשה של הסוכן',
          status: Math.random() > 0.8 ? 'needs_handoff' : 'completed',
          channel: ['whatsapp', 'phone', 'system'][Math.floor(Math.random() * 3)],
          result: 'תוצאה אוטומטית'
        };
        
        setAgentActivities(prev => [newActivity, ...prev.slice(0, 9)]);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Generate dashboard cards
  const generateDashboardCards = () => [
    {
      id: 'appointments-today',
      title: 'תורים שנקבעו היום',
      value: liveData.appointmentsToday.toString(),
      subtitle: 'תורים מתוכננים',
      trend: 'up',
      trendValue: '+12%',
      status: 'success',
      icon: Calendar,
      priority: 'high'
    },
    {
      id: 'success-rate',
      title: 'שיעור הצלחה (24 שעות)',
      value: `${liveData.systemUptime.toFixed(1)}%`,
      subtitle: `${liveData.successfulConversations} שיחות מוצלחות מתוך ${Math.round(liveData.successfulConversations / (liveData.systemUptime/100))}`,
      trend: 'up',
      trendValue: '+0.2%',
      status: 'success',
      icon: CheckCircle,
      priority: 'high'
    },
    {
      id: 'avg-handling-time',
      title: 'זמן טיפול ממוצע',
      value: `${Math.floor(liveData.avgHandlingTime / 60)}:${(liveData.avgHandlingTime % 60).toString().padStart(2, '0')}`,
      subtitle: 'דקות',
      trend: 'down',
      trendValue: '-15 שניות',
      status: 'success',
      icon: Clock,
      priority: 'medium'
    }
  ];

  // Agent status indicator
  const getAgentStatusConfig = () => {
    const configs = {
      active: { color: 'bg-green-500', text: 'פעיל', pulse: true },
      monitoring: { color: 'bg-blue-500', text: 'במעקב', pulse: false },
      idle: { color: 'bg-yellow-500', text: 'במנוחה', pulse: false },
      error: { color: 'bg-red-500', text: 'שגיאה', pulse: true },
      offline: { color: 'bg-gray-500', text: 'לא מחובר', pulse: false }
    };
    return configs[agentStatus] || configs.offline;
  };

  const statusConfig = getAgentStatusConfig();

  return (
    <div className="min-h-screen bg-[#f5f5f5]" dir="rtl">
      {/* Top Header - Mission Control Style */}
      <header className="bg-white border-b border-[#f0f0f0] h-16 px-6 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#001529] rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-[#001529]">מרכז השליטה והבקרה</h1>
          </div>
          
          {/* Agent Status */}
          <div className="flex items-center gap-2 bg-[#f5f5f5] px-3 py-1 rounded-full">
            <div className={cn(
              "w-3 h-3 rounded-full",
              statusConfig.color,
              statusConfig.pulse && "animate-pulse"
            )} />
            <span className="text-sm font-medium text-[#001529]">
              סוכן {statusConfig.text}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm">
            <Bell className="w-4 h-4" />
          </Button>
          <div className="w-8 h-8 bg-[#001529] rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar Navigation */}
        <aside className="w-64 bg-[#001529] text-white flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-[#220]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <Cpu className="w-5 h-5 text-[#001529]" />
              </div>
              <span className="font-bold">DentalAI</span>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="flex-1 p-4">
            <div className="space-y-2">
              <Button
                variant={activeTab === 'overview' ? 'secondary' : 'ghost'}
                className={cn(
                  "w-full justify-start h-10 text-right",
                  activeTab === 'overview' && "bg-[#e6f7ff] text-[#001529] border-r-4 border-r-blue-500"
                )}
                onClick={() => setActiveTab('overview')}
              >
                <Activity className="w-5 h-5 ml-3" />
                סקירה כללית
              </Button>
              
              <Button
                variant={activeTab === 'chat' ? 'secondary' : 'ghost'}
                className={cn(
                  "w-full justify-start h-10 text-right",
                  activeTab === 'chat' && "bg-[#e6f7ff] text-[#001529] border-r-4 border-r-blue-500"
                )}
                onClick={() => setActiveTab('chat')}
              >
                <MessageSquare className="w-5 h-5 ml-3" />
                היסטוריית שיחות
              </Button>
              
              <Button
                variant={activeTab === 'chat' ? 'secondary' : 'ghost'}
                className={cn(
                  "w-full justify-start h-10 text-right",
                  activeTab === 'chat' && "bg-[#e6f7ff] text-[#001529] border-r-4 border-r-blue-500"
                )}
                onClick={() => setActiveTab('chat')}
              >
                <MessageSquare className="w-5 h-5 ml-3" />
                צ'אט עם דנה
              </Button>
              
              <Button
                variant={activeTab === 'knowledge' ? 'secondary' : 'ghost'}
                className={cn(
                  "w-full justify-start h-10 text-right",
                  activeTab === 'knowledge' && "bg-[#e6f7ff] text-[#001529] border-r-4 border-r-blue-500"
                )}
                onClick={() => setActiveTab('knowledge')}
              >
                <Brain className="w-5 h-5 ml-3" />
                ניהול ידע
              </Button>
            </div>
          </nav>

          {/* Bottom Actions */}
          <div className="p-4 border-t border-[#220] space-y-2">
            <Button variant="ghost" className="w-full justify-start h-10 text-right">
              <Settings className="w-5 h-5 ml-3" />
              הגדרות
            </Button>
            <Button variant="ghost" className="w-full justify-start h-10 text-right">
              <LogOut className="w-5 h-5 ml-3" />
              יציאה
            </Button>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="p-6 space-y-6">
              {/* KPI Cards Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {generateDashboardCards().map((card, index) => (
                  <StatisticsCard
                    key={card.id}
                    {...card}
                    agentStatus={agentStatus}
                  />
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Live Monitoring - 65% width */}
                <div className="lg:col-span-2 space-y-6">
                  <RealTimeAlerts />
                  <Card className="border-r-4 border-r-green-500">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                          מעקב חי
                        </CardTitle>
                        <Badge variant="outline" className="text-green-600">
                          {agentActivities.filter(a => a.status === 'completed').length} פעולות הושלמו
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {agentActivities.slice(0, 5).map((activity) => (
                          <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="flex items-center gap-2">
                                {activity.channel === 'whatsapp' && <MessageCircle className="w-4 h-4 text-green-600" />}
                                {activity.channel === 'phone' && <Phone className="w-4 h-4 text-blue-600" />}
                                {activity.channel === 'system' && <Cpu className="w-4 h-4 text-gray-600" />}
                                <span className="text-sm font-medium">{activity.action}</span>
                              </div>
                              <Badge 
                                variant={activity.status === 'completed' ? 'default' : 'destructive'}
                                className="text-xs"
                              >
                                {activity.status === 'completed' ? 'הושלם' : 'דרושה התערבות'}
                              </Badge>
                            </div>
                            <div className="text-left">
                              <div className="text-sm text-gray-600">{activity.time}</div>
                              <div className="text-xs text-gray-500">{activity.result}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>היסטוריית שיחות אחרונות</CardTitle>
                      <Button variant="ghost" size="sm" className="text-blue-600">
                        הצג הכל
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {[
                          { patient: 'דוד כהן', channel: 'WhatsApp', time: '14:32', result: 'תור נקבע', status: 'success' },
                          { patient: 'שרה לוי', channel: 'טלפון', time: '14:28', result: 'דרושה התערבות', status: 'handoff' },
                          { patient: 'מיכל ברק', channel: 'SMS', time: '14:25', result: 'תזכורת נשלחה', status: 'success' }
                        ].map((chat, index) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-[#001529] rounded-full flex items-center justify-center text-white text-sm">
                                {chat.patient.charAt(0)}
                              </div>
                              <div>
                                <div className="font-medium">{chat.patient}</div>
                                <div className="text-sm text-gray-600">{chat.channel}</div>
                              </div>
                            </div>
                            <div className="text-left">
                              <div className="text-sm">{chat.time}</div>
                              <Badge 
                                variant={chat.status === 'success' ? 'default' : 'destructive'}
                                className="text-xs"
                              >
                                {chat.result}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Right Column - 35% width */}
                <div className="space-y-6">
                  <Card className="border-r-4 border-r-red-500">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-red-600">
                        <AlertTriangle className="w-5 h-5" />
                        דרושה התערבות
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {agentActivities.filter(a => a.status === 'needs_handoff').map((activity) => (
                          <div key={activity.id} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                            <div className="font-medium text-red-800">{activity.action}</div>
                            <div className="text-sm text-red-600 mt-1">{activity.result}</div>
                            <Button size="sm" className="mt-2 bg-blue-600 hover:bg-blue-700">
                              קח שליטה על השיחה
                            </Button>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>ביצועים יומיים (7 ימים)</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">תורים שנקבעו</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-gray-200 rounded-full">
                              <div className="w-16 h-2 bg-green-500 rounded-full"></div>
                            </div>
                            <span className="text-sm font-medium">80%</span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">שביעות רצון</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-gray-200 rounded-full">
                              <div className="w-19 h-2 bg-blue-500 rounded-full"></div>
                            </div>
                            <span className="text-sm font-medium">94%</span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">זמן תגובה</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-gray-200 rounded-full">
                              <div className="w-14 h-2 bg-yellow-500 rounded-full"></div>
                            </div>
                            <span className="text-sm font-medium">12 שניות</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {/* Chat History Tab */}
          {activeTab === 'chat' && (
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-8rem)]">
                {/* Chat List - 30% */}
                <div className="lg:col-span-1">
                  <Card className="h-full">
                    <CardHeader>
                      <div className="space-y-4">
                        <div className="flex items-center gap-2">
                          <Search className="w-4 h-4 text-gray-500" />
                          <input 
                            type="text" 
                            placeholder="חיפוש שיחות..."
                            className="flex-1 px-3 py-2 border rounded-lg text-sm"
                          />
                        </div>
                        <div className="flex gap-2">
                          <select className="flex-1 px-3 py-2 border rounded-lg text-sm">
                            <option>כל הערוצים</option>
                            <option>WhatsApp</option>
                            <option>טלפון</option>
                            <option>SMS</option>
                          </select>
                          <select className="flex-1 px-3 py-2 border rounded-lg text-sm">
                            <option>כל התוצאות</option>
                            <option>מוצלח</option>
                            <option>דרושה התערבות</option>
                          </select>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="space-y-1 max-h-96 overflow-y-auto">
                        {[
                          { id: 1, name: 'דוד כהן', phone: '050-1234567', time: '14:32', selected: true },
                          { id: 2, name: 'שרה לוי', phone: '052-9876543', time: '14:28', selected: false },
                          { id: 3, name: 'מיכל ברק', phone: '054-5555555', time: '14:25', selected: false }
                        ].map((chat) => (
                          <div 
                            key={chat.id}
                            className={cn(
                              "p-3 cursor-pointer hover:bg-gray-50",
                              chat.selected && "bg-blue-50 border-r-4 border-r-blue-500"
                            )}
                          >
                            <div className="font-medium">{chat.name}</div>
                            <div className="text-sm text-gray-600">{chat.phone}</div>
                            <div className="text-xs text-gray-500">{chat.time}</div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Chat Display & Control - 70% */}
                <div className="lg:col-span-3">
                  <Card className="h-full flex flex-col">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-bold">דוד כהן</h3>
                          <p className="text-sm text-gray-600">050-1234567 • 15/10/2024</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-green-600">WhatsApp</Badge>
                          <Badge variant="default">הושלם</Badge>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="flex-1 flex flex-col">
                      {/* Chat Messages */}
                      <div className="flex-1 space-y-4 mb-4 overflow-y-auto">
                        <div className="flex justify-end">
                          <div className="bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                            שלום! אני הסוכן הדיגיטלי של מרפאת השיניים. איך אוכל לעזור?
                          </div>
                        </div>
                        <div className="flex justify-start">
                          <div className="bg-gray-200 p-3 rounded-lg max-w-xs">
                            היי, אני צריך לקבוע תור לטיפול שורש
                          </div>
                        </div>
                        <div className="flex justify-end">
                          <div className="bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                            בוודאי! אני יכול לעזור לך לקבוע תור. מתי נוח לך להגיע?
                          </div>
                        </div>
                        <div className="flex justify-start">
                          <div className="bg-gray-200 p-3 rounded-lg max-w-xs">
                            מחר אחר הצהריים אם אפשר
                          </div>
                        </div>
                        <div className="flex justify-end">
                          <div className="bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                            מצוין! יש לי זמינות מחר ב-15:00. האם זה מתאים?
                          </div>
                        </div>
                      </div>

                      {/* Human Handoff Control */}
                      <div className="border-t pt-4">
                        <div className="bg-[#f5f5f5] p-4 rounded-lg">
                          <div className="flex items-center gap-2 mb-3">
                            <Shield className="w-5 h-5 text-blue-600" />
                            <span className="font-medium">התערבות אנושית</span>
                          </div>
                          <textarea 
                            placeholder="הקלד כאן את תגובתך כדי להשתלט על השיחה..."
                            className="w-full p-3 border rounded-lg resize-none"
                            rows={3}
                          />
                          <div className="flex justify-between items-center mt-3">
                            <Button variant="outline" size="sm">
                              <Eye className="w-4 h-4 ml-2" />
                              צפה בלבד
                            </Button>
                            <Button className="bg-blue-600 hover:bg-blue-700">
                              <ArrowRight className="w-4 h-4 ml-2" />
                              שלח
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {/* Dana Chat Tab */}
          {activeTab === 'chat' && (
            <div className="p-6 space-y-6">
              {/* Dana Chat Header */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    צ'אט עם דנה - הסוכנת הראשית
                  </CardTitle>
                  <p className="text-sm text-gray-600">
                    דנה היא הסוכנת הראשית שלכם לניהול המרפאה. היא יכולה לעזור עם תיאום תורים, מידע על מטופלים, וניהול כללי של המרפאה.
                  </p>
                </CardHeader>
              </Card>

              {/* Chat Interface */}
              <Card className="h-96">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>שיחה עם דנה</CardTitle>
                    <Badge className="bg-green-100 text-green-800">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
                      פעילה
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col h-full">
                  {/* Chat Messages */}
                  <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                        ד
                      </div>
                      <div className="bg-white p-3 rounded-lg shadow-sm max-w-xs">
                        <p className="text-sm">שלום! אני דנה, הסוכנת הראשית של המרפאה. איך אני יכולה לעזור לך היום?</p>
                        <span className="text-xs text-gray-500 mt-1 block">עכשיו</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Chat Input */}
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      placeholder="הקלד הודעה לדנה..."
                      className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <Button className="bg-blue-600 hover:bg-blue-700">
                      <MessageCircle className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Dana's Capabilities */}
              <Card>
                <CardHeader>
                  <CardTitle>יכולות דנה</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-4 h-4 text-blue-500" />
                        <span className="font-medium">ניהול תורים</span>
                      </div>
                      <p className="text-sm text-gray-600">קביעת תורים, ביטולים ושינויים</p>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Users className="w-4 h-4 text-green-500" />
                        <span className="font-medium">מידע על מטופלים</span>
                      </div>
                      <p className="text-sm text-gray-600">היסטוריה רפואית ופרטי קשר</p>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="w-4 h-4 text-yellow-500" />
                        <span className="font-medium">מידע כלכלי</span>
                      </div>
                      <p className="text-sm text-gray-600">עלויות טיפולים ותשלומים</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Knowledge Management Tab */}
          {activeTab === 'knowledge' && (
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-8rem)]">
                {/* Knowledge Tree - 25% */}
                <div className="lg:col-span-1">
                  <Card className="h-full">
                    <CardHeader>
                      <CardTitle className="text-lg">בסיס הידע</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="space-y-1">
                        {Object.entries(knowledgeBase).map(([key, section]) => (
                          <div key={key} className="p-3 hover:bg-gray-50 cursor-pointer border-r-4 border-r-transparent hover:border-r-blue-500">
                            <div className="font-medium">{section.name}</div>
                            <div className="text-sm text-gray-600">{section.files.length} קבצים</div>
                            <div className="text-xs text-gray-500">עודכן לפני {section.lastUpdated}</div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Knowledge Editor - 75% */}
                <div className="lg:col-span-3">
                  <Card className="h-full">
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle>עריכת לוח זמנים - dr_cohen_schedule.yaml</CardTitle>
                        <div className="flex gap-2">
                          <Button variant="outline" className="text-gray-600">
                            בטל שינויים
                          </Button>
                          <Button className="bg-green-600 hover:bg-green-700">
                            שמור שינויים
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Visual Weekly Schedule */}
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h4 className="font-medium mb-4">לוח שבועי ויזואלי</h4>
                          <div className="grid grid-cols-8 gap-2 text-sm">
                            <div className="font-medium">שעה</div>
                            {['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ש'].map(day => (
                              <div key={day} className="font-medium text-center">{day}</div>
                            ))}
                            
                            {[9, 10, 11, 12, 13, 14, 15, 16, 17].map(hour => (
                              <React.Fragment key={hour}>
                                <div className="py-2">{hour}:00</div>
                                {[1, 2, 3, 4, 5, 6, 7].map(day => (
                                  <div 
                                    key={`${hour}-${day}`}
                                    className={cn(
                                      "h-8 border rounded cursor-pointer hover:bg-blue-100",
                                      (hour >= 9 && hour <= 17 && day <= 5) ? "bg-green-100 border-green-300" : "bg-gray-100"
                                    )}
                                    title={`${hour}:00 - ${day <= 5 ? 'זמין' : 'סגור'}`}
                                  />
                                ))}
                              </React.Fragment>
                            ))}
                          </div>
                        </div>

                        {/* YAML Editor */}
                        <div>
                          <h4 className="font-medium mb-2">עריכת YAML</h4>
                          <textarea 
                            className="w-full h-64 p-4 border rounded-lg font-mono text-sm bg-gray-50"
                            defaultValue={`# לוח זמנים של ד"ר כהן
schedule:
  sunday:
    start: "09:00"
    end: "17:00"
    breaks:
      - start: "13:00"
        end: "14:00"
  monday:
    start: "09:00" 
    end: "17:00"
    breaks:
      - start: "13:00"
        end: "14:00"
  tuesday:
    start: "09:00"
    end: "17:00"
  # המשך הגדרות...`}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default MissionControlDashboard;
