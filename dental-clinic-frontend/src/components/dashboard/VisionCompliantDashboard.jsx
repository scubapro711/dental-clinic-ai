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

const VisionCompliantDashboard = () => {
  const [agentStatus, setAgentStatus] = useState('active');
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
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              מרכז הפיקוד והשליטה
            </h1>
            <p className="text-lg text-gray-600">
              הסוכן האוטונומי שלכם פעיל ומנהל את המרפאה 24/7
            </p>
          </div>
          <div className="flex items-center space-x-4 space-x-reverse">
            <Badge variant={agentStatus === 'active' ? 'default' : 'secondary'} className="text-lg px-4 py-2">
              <Activity className="w-4 h-4 ml-2" />
              {agentStatus === 'active' ? 'פעיל' : 'לא פעיל'}
            </Badge>
            <Button variant="outline" size="lg">
              <Shield className="w-4 h-4 ml-2" />
              השתלט על הסוכן
            </Button>
          </div>
        </div>
      </div>

      {/* Real-time Agent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="w-5 h-5 ml-2" />
              פעילות הסוכן בזמן אמת
            </CardTitle>
            <CardDescription>
              מעקב אחר כל פעולה שהסוכן מבצע עם הסברים מפורטים
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {currentTasks.map((task) => (
                <div key={task.id} className="flex items-center justify-between p-4 bg-white rounded-lg border">
                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className={`w-3 h-3 rounded-full ${
                      task.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
                    }`} />
                    <div>
                      <p className="font-medium text-gray-900">{task.description}</p>
                      <p className="text-sm text-gray-500">
                        {task.status === 'active' ? 'מבצע כרגע...' : 'הושלם'}
                      </p>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">{task.time}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Agent Control Panel */}
        <Card>
          <CardHeader>
            <CardTitle>בקרת הסוכן</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">סטטוס</span>
                <Badge variant="default">פעיל</Badge>
              </div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm font-medium">מצב עבודה</span>
                <Badge variant="outline">אוטונומי</Badge>
              </div>
            </div>
            
            <div className="space-y-2">
              <Button className="w-full" variant="outline">
                <Zap className="w-4 h-4 ml-2" />
                עצור פעילות
              </Button>
              <Button className="w-full" variant="outline">
                <MessageSquare className="w-4 h-4 ml-2" />
                שלח הוראה
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">תורים היום</p>
                <p className="text-3xl font-bold text-gray-900">{metrics.todayAppointments}</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">שיחות פעילות</p>
                <p className="text-3xl font-bold text-gray-900">{metrics.activeCalls}</p>
              </div>
              <MessageSquare className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div>
              <p className="text-sm font-medium text-gray-600">שיעור השלמה</p>
              <p className="text-3xl font-bold text-gray-900">{metrics.completionRate}%</p>
              <Progress value={metrics.completionRate} className="mt-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div>
              <p className="text-sm font-medium text-gray-600">זמן תגובה ממוצע</p>
              <p className="text-3xl font-bold text-gray-900">{metrics.responseTime}ש'</p>
              <p className="text-sm text-green-600">מתחת ליעד</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div>
              <p className="text-sm font-medium text-gray-600">שביעות רצון</p>
              <p className="text-3xl font-bold text-gray-900">{metrics.patientSatisfaction}%</p>
              <Progress value={metrics.patientSatisfaction} className="mt-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts and Interventions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="w-5 h-5 ml-2" />
              התראות ודרושה התערבות
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
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
    </div>
  );
};

export default VisionCompliantDashboard;
