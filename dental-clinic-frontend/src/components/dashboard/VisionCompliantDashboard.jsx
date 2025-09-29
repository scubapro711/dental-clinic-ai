import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Activity, 
  Users, 
  Calendar, 
  MessageSquare, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Brain,
  Shield,
  Zap
} from 'lucide-react';
import SimulationControlPanel from './SimulationControlPanel';

const VisionCompliantDashboard = () => {
  const [agentStatus, setAgentStatus] = useState('active');
  const [showSimulation, setShowSimulation] = useState(false);
  const [currentTasks, setCurrentTasks] = useState([
    { id: 1, type: 'scheduling', description: 'מזמן תור למטופל חדש', time: '14:32', status: 'active' },
    { id: 2, type: 'update', description: 'מעדכן יומן רופא - תור בוטל', time: '14:30', status: 'completed' },
    { id: 3, type: 'reminder', description: 'שולח תזכורת SMS', time: '14:28', status: 'completed' },
    { id: 4, type: 'analysis', description: 'מנתח נתוני ביצועים', time: '14:25', status: 'completed' }
  ]);

  const [metrics, setMetrics] = useState({
    todayAppointments: 23,
    activeCalls: 5,
    completionRate: 95,
    responseTime: 12,
    patientSatisfaction: 92
  });

  const [alerts, setAlerts] = useState([
    { id: 1, type: 'intervention', message: 'מטופל מבקש שינוי מורכב בתור', priority: 'high' },
    { id: 2, type: 'system', message: 'זיהוי מקרה חירום - הופנה לטיפול מיידי', priority: 'critical' }
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6" dir="rtl">
      {/* Header - מרכז הפיקוד והשליטה */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center mb-2">
              <Brain className="w-10 h-10 text-blue-600 ml-3" />
              <h1 className="text-4xl font-bold text-gray-900">
                מרכז הפיקוד והשליטה AI
              </h1>
            </div>
            <p className="text-lg text-gray-600 mb-3">
              מערכת AI מתקדמת לניהול מרפאת שיניים - פעילה 24/7
            </p>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full ml-2 animate-pulse"></div>
              <span className="text-sm font-medium text-green-700">מערכת פעילה ומחוברת</span>
              <Badge variant="secondary" className="mr-3">גרסה 2.1.0</Badge>
            </div>
          </div>
          <div className="flex items-center space-x-4 space-x-reverse">
            <Badge variant={agentStatus === 'active' ? 'default' : 'secondary'} className="text-lg px-4 py-2">
              <Activity className="w-4 h-4 ml-2" />
              {agentStatus === 'active' ? 'פעיל' : 'לא פעיל'}
            </Badge>
            <Button variant="outline" size="lg">
              <Shield className="w-4 h-4 ml-2" />
              הגדרות אבטחה
            </Button>
          </div>
        </div>

        {/* Agent Status Card */}
        <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center ml-4">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">הסוכן האוטונומי פעיל</h3>
                  <p className="text-gray-600">מנהל כרגע 5 שיחות במקביל ומעבד בקשות חדשות</p>
                </div>
              </div>
              <Button variant="outline">
                <Zap className="w-4 h-4 ml-2" />
                שלח הוראה
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700">תורים היום</p>
                <p className="text-3xl font-bold text-blue-800">{metrics.todayAppointments}</p>
                <p className="text-xs text-blue-600">+12% מאתמול</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700">שיחות פעילות</p>
                <p className="text-3xl font-bold text-green-800">{metrics.activeCalls}</p>
                <p className="text-xs text-green-600">זמן אמת</p>
              </div>
              <MessageSquare className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-700">שיעור השלמה</p>
                <p className="text-3xl font-bold text-purple-800">{metrics.completionRate}%</p>
                <p className="text-xs text-purple-600">יעד: 90%</p>
              </div>
              <CheckCircle className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-700">זמן תגובה</p>
                <p className="text-3xl font-bold text-orange-800">{metrics.responseTime}s</p>
                <p className="text-xs text-orange-600">מהיר מ-95% מהמתחרים</p>
              </div>
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-pink-50 to-pink-100 border-pink-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-pink-700">שביעות רצון</p>
                <p className="text-3xl font-bold text-pink-800">{metrics.patientSatisfaction}%</p>
                <p className="text-xs text-pink-600">+8% מהחודש הקודם</p>
              </div>
              <Users className="w-8 h-8 text-pink-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Current Tasks */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 ml-2" />
              פעילות הסוכן בזמן אמת
            </CardTitle>
            <CardDescription>
              משימות שהסוכן מבצע כרגע ופעילות אחרונה
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {currentTasks.map((task) => (
                <div key={task.id} className={`p-4 rounded-lg border-r-4 ${
                  task.status === 'active' ? 'bg-blue-50 border-blue-500' : 'bg-gray-50 border-gray-300'
                }`}>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      {task.status === 'active' ? (
                        <div className="w-3 h-3 bg-blue-500 rounded-full ml-3 animate-pulse"></div>
                      ) : (
                        <CheckCircle className="w-4 h-4 text-green-600 ml-3" />
                      )}
                      <span className="font-medium text-gray-900">{task.description}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-sm text-gray-500 ml-3">{task.time}</span>
                      <Badge variant={task.status === 'active' ? 'default' : 'secondary'}>
                        {task.status === 'active' ? 'פעיל' : 'הושלם'}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Alerts and Interventions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="w-5 h-5 ml-2" />
              התראות ודרושה התערבות
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className={`p-4 rounded-lg border-r-4 ${
                  alert.priority === 'critical' ? 'bg-red-50 border-red-500' : 
                  alert.priority === 'high' ? 'bg-yellow-50 border-yellow-500' : 
                  'bg-blue-50 border-blue-500'
                }`}>
                  <p className="font-medium text-gray-900">{alert.message}</p>
                  <div className="flex justify-between items-center mt-2">
                    <Badge variant={alert.priority === 'critical' ? 'destructive' : 'secondary'}>
                      {alert.priority === 'critical' ? 'קריטי' : 'דרושה התערבות'}
                    </Badge>
                    <Button size="sm" variant="outline">
                      טפל
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CheckCircle className="w-5 h-5 ml-2" />
              משימות שהושלמו היום
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm">47 שיחות מנוהלות</span>
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm">23 תורים נקבעו</span>
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm">15 תזכורות נשלחו</span>
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm">3 מקרי חירום זוהו</span>
                <CheckCircle className="w-4 h-4 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Explanation */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>הסבר הסוכן לפעילות הנוכחית</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-blue-50 p-4 rounded-lg border-r-4 border-blue-500">
            <p className="text-gray-900">
              <strong>הסוכן מזמן תור כי:</strong> זיהיתי פנייה חדשה דרך WhatsApp ממטופל שמבקש ניקוי שיניים. 
              מצאתי זמינות מתאימה ביומן של ד"ר כהן ביום רביעי בשעה 10:00. 
              המטופל אישר את הזמן והתור נקבע במערכת.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Simulation Control Panel - Moved to bottom for investor demo */}
      <div className="mt-12 border-t-2 border-gray-200 pt-8">
        <div className="mb-4">
          <Button 
            variant="outline" 
            onClick={() => setShowSimulation(!showSimulation)}
            className="w-full"
          >
            {showSimulation ? 'הסתר' : 'הצג'} פאנל הדגמה למשקיעים
          </Button>
        </div>
        {showSimulation && <SimulationControlPanel />}
      </div>
    </div>
  );
};

export default VisionCompliantDashboard;
