import React, { useState, useEffect } from 'react';
import { 
  Calendar, FileText, CreditCard, User, MessageCircle, 
  Bell, Phone, Send, CheckCircle, Clock, AlertCircle,
  TrendingUp, Activity, Heart, Sparkles
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Progress } from '@/components/ui/progress';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';

/**
 * Patient Dashboard - Hebrew version with Twilio SMS + Telegram
 * 
 * Features:
 * - Health overview with AI insights from agents
 * - Upcoming appointments
 * - Recent medical records  
 * - Billing summary
 * - Proactive AI suggestions (Alex, Marcus, Sarah, Sophia)
 * - SMS status (Twilio)
 * - Telegram integration status
 * - Quick actions
 * - Floating chat button
 */
export default function PatientDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/patient/dashboard`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">🦷</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  DentaFlow
                </h1>
                <p className="text-sm text-gray-500">פורטל מטופלים</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
              </Button>
              
              <div className="flex items-center gap-2">
                <Avatar>
                  <AvatarImage src={user?.avatar} />
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                    {user?.name?.charAt(0) || 'מ'}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium">{user?.name || 'מטופל'}</p>
                  <p className="text-xs text-gray-500">פורטל מטופלים</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            שלום, {user?.name?.split(' ')[0] || 'מטופל יקר'}! 👋
          </h2>
          <p className="text-gray-600">
            הנה סקירה של המצב הרפואי שלך ותורים קרובים
          </p>
        </div>

        {/* AI Alert - Alex */}
        <Card className="mb-6 border-blue-200 bg-gradient-to-r from-blue-50 to-blue-100/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-blue-600 hover:bg-blue-600 text-white">Alex</Badge>
                  <span className="text-xs text-gray-500">לפני 2 שעות</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  תזכורת: התור הבא שלך מחר! 📅
                </h3>
                <p className="text-gray-700 mb-3">
                  שלום! רציתי להזכיר לך שיש לך תור מחר (12 באוקטובר) בשעה 10:00 עם ד"ר כהן לניקוי שיניים.
                </p>
                <div className="flex items-center gap-2 mb-3">
                  <Progress value={95} className="flex-1 h-2" />
                  <span className="text-xs text-gray-600">95% ביטחון</span>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                    <CheckCircle className="h-4 w-4 ml-1" />
                    צפה בפרטי התור
                  </Button>
                  <Button size="sm" variant="outline">
                    <Bell className="h-4 w-4 ml-1" />
                    הגדר תזכורת
                  </Button>
                  <Button size="sm" variant="ghost" className="text-blue-600">
                    <MessageCircle className="h-4 w-4 ml-1" />
                    שאל את Alex
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/patient/appointments')}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">התור הבא</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">מחר</div>
              <p className="text-xs text-gray-500">12 אוקטובר, 10:00</p>
              <Badge className="mt-2 bg-green-100 text-green-800 hover:bg-green-100">
                מאושר
              </Badge>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/patient/medical-records')}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ביקורים</CardTitle>
              <Activity className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-gray-500">סה"כ ביקורים</p>
              <p className="text-xs text-green-600 mt-2">+2 החודש</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/patient/billing')}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">יתרה</CardTitle>
              <CreditCard className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₪0</div>
              <p className="text-xs text-gray-500">אין חובות</p>
              <Badge className="mt-2 bg-green-100 text-green-800 hover:bg-green-100">
                <CheckCircle className="h-3 w-3 ml-1" />
                מעולה!
              </Badge>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ציון בריאות</CardTitle>
              <Heart className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">85/100</div>
              <p className="text-xs text-gray-500">מצוין!</p>
              <Progress value={85} className="mt-2 h-2" />
            </CardContent>
          </Card>
        </div>

        {/* Communication Status - SMS + Telegram */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>ערוצי תקשורת</CardTitle>
            <CardDescription>נהל את ההתראות וההודעות שלך</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* SMS Status (Twilio) */}
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-green-600 flex items-center justify-center">
                    <Phone className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold">SMS (Twilio)</h4>
                    <p className="text-sm text-gray-600">+972-50-123-4567</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className="bg-green-600 hover:bg-green-600">
                    <CheckCircle className="h-3 w-3 ml-1" />
                    פעיל
                  </Badge>
                  <Button size="sm" variant="outline" onClick={() => navigate('/patient/profile')}>
                    הגדרות
                  </Button>
                </div>
              </div>

              {/* Telegram Status */}
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                    <Send className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold">Telegram</h4>
                    <p className="text-sm text-gray-600">@username</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className="bg-blue-600 hover:bg-blue-600">
                    <CheckCircle className="h-3 w-3 ml-1" />
                    מקושר
                  </Badge>
                  <Button size="sm" variant="outline" onClick={() => window.open('https://t.me/DentaFlowBot', '_blank')}>
                    פתח צ'אט
                  </Button>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 pt-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">5</p>
                  <p className="text-xs text-gray-500">SMS החודש</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">12</p>
                  <p className="text-xs text-gray-500">הודעות Telegram</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">100%</p>
                  <p className="text-xs text-gray-500">נמסרו בהצלחה</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="hover:shadow-xl transition-all cursor-pointer group" onClick={() => navigate('/patient/appointments')}>
            <CardContent className="p-6">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Calendar className="h-8 w-8 text-white" />
                </div>
                <h3 className="font-semibold text-lg mb-2">קביעת תור</h3>
                <p className="text-sm text-gray-600">קבע תור חדש במהירות</p>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-xl transition-all cursor-pointer group" onClick={() => setChatOpen(true)}>
            <CardContent className="p-6">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-600 to-purple-700 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <h3 className="font-semibold text-lg mb-2">צ'אט עם Alex</h3>
                <p className="text-sm text-gray-600">שאל שאלות ותקבל מענה מיידי</p>
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-xl transition-all cursor-pointer group" onClick={() => navigate('/patient/medical-records')}>
            <CardContent className="p-6">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-600 to-green-700 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <h3 className="font-semibold text-lg mb-2">רשומות רפואיות</h3>
                <p className="text-sm text-gray-600">צפה בהיסטוריה הרפואית שלך</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Floating Chat Button */}
      <Button
        size="lg"
        className="fixed bottom-6 left-6 w-16 h-16 rounded-full shadow-2xl bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 z-50"
        onClick={() => setChatOpen(!chatOpen)}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Chat Panel */}
      {chatOpen && (
        <div className="fixed bottom-24 left-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col border border-gray-200">
          <div className="p-4 border-b bg-gradient-to-r from-purple-600 to-pink-600 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">צ'אט עם Alex</h3>
                  <p className="text-xs text-purple-100">פעיל עכשיו</p>
                </div>
              </div>
              <Button size="sm" variant="ghost" className="text-white hover:bg-white/20" onClick={() => setChatOpen(false)}>
                ✕
              </Button>
            </div>
          </div>
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-4">
              <div className="flex gap-2">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="bg-purple-600 text-white text-xs">A</AvatarFallback>
                </Avatar>
                <div className="bg-gray-100 rounded-2xl rounded-tr-none p-3 max-w-[80%]">
                  <p className="text-sm">שלום! אני Alex, איך אני יכול לעזור לך היום? 😊</p>
                </div>
              </div>
            </div>
          </div>
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="הקלד הודעה..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-600"
              />
              <Button size="icon" className="rounded-full bg-purple-600 hover:bg-purple-700">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

