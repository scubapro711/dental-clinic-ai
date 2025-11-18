import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowRight, Phone, Mail, Calendar, FileText, DollarSign, 
  AlertCircle, CheckCircle, Clock, Sparkles, ChevronRight,
  User, MapPin, CreditCard, Activity, MessageCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';

/**
 * Patient Detail Page - Clinic Portal
 * 
 * Features:
 * - View comprehensive patient information
 * - Medical history and visits
 * - Appointments and billing
 * - Quick actions (call, email, chat)
 * - AI insights from Sarah & Alex
 */
export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPatientDetails();
  }, [id]);

  const fetchPatientDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with real API call
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/patients/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch patient details');
      }

      const data = await response.json();
      setPatient(data);
    } catch (err) {
      console.error('Error fetching patient:', err);
      setError(err.message);
      toast.error('שגיאה בטעינת פרטי המטופל', {
        description: err.message
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const config = {
      active: { label: 'פעיל', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      overdue: { label: 'חוב', className: 'bg-red-100 text-red-800', icon: AlertCircle },
      inactive: { label: 'לא פעיל', className: 'bg-gray-100 text-gray-800', icon: Clock },
    };
    const statusConfig = config[status] || config.active;
    const Icon = statusConfig.icon;
    return (
      <Badge className={`${statusConfig.className} hover:${statusConfig.className}`}>
        <Icon className="h-3 w-3 ml-1" />
        {statusConfig.label}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center" dir="rtl">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">טוען פרטי מטופל...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center" dir="rtl">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">שגיאה בטעינת פרטי המטופל</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <Button onClick={() => navigate('/clinic/patients')}>
              <ArrowRight className="h-4 w-4 ml-1" />
              חזרה לרשימת מטופלים
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center" dir="rtl">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <User className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">מטופל לא נמצא</h2>
            <p className="text-gray-600 mb-6">המטופל שחיפשת לא קיים במערכת</p>
            <Button onClick={() => navigate('/clinic/patients')}>
              <ArrowRight className="h-4 w-4 ml-1" />
              חזרה לרשימת מטופלים
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/clinic/patients')}>
                <ArrowRight className="h-5 w-5" />
              </Button>
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-xl font-bold">
                {patient.name?.split(' ').map(n => n[0]).join('') || 'N/A'}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold text-gray-900">{patient.name || 'ללא שם'}</h1>
                  {patient.status && getStatusBadge(patient.status)}
                </div>
                <p className="text-sm text-gray-500">מזהה: {patient.id}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Phone className="h-4 w-4 ml-1" />
                התקשר
              </Button>
              <Button variant="outline" size="sm">
                <Mail className="h-4 w-4 ml-1" />
                שלח אימייל
              </Button>
              <Button variant="outline" size="sm">
                <MessageCircle className="h-4 w-4 ml-1" />
                צ'אט
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ביקורים</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{patient.visits || 0}</div>
              <p className="text-xs text-gray-500">סה"כ ביקורים</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">יתרה</CardTitle>
              <DollarSign className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₪{patient.balance || 0}</div>
              <p className="text-xs text-gray-500">{patient.balance > 0 ? 'חוב' : 'אין חובות'}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ביקור אחרון</CardTitle>
              <Clock className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {patient.lastVisit ? new Date(patient.lastVisit).toLocaleDateString('he-IL') : 'אין מידע'}
              </div>
              <p className="text-xs text-gray-500">תאריך</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ציון בריאות</CardTitle>
              <Activity className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{patient.healthScore || 'N/A'}/100</div>
              <p className="text-xs text-gray-500">מצב כללי</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">סקירה</TabsTrigger>
            <TabsTrigger value="medical">היסטוריה רפואית</TabsTrigger>
            <TabsTrigger value="appointments">תורים</TabsTrigger>
            <TabsTrigger value="billing">חיובים</TabsTrigger>
            <TabsTrigger value="documents">מסמכים</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle>פרטי קשר</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-3">
                    <Phone className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">טלפון</p>
                      <p className="font-medium">{patient.phone || 'לא זמין'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">אימייל</p>
                      <p className="font-medium">{patient.email || 'לא זמין'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <MapPin className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">כתובת</p>
                      <p className="font-medium">{patient.address || 'לא זמין'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <CreditCard className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">קופת חולים</p>
                      <p className="font-medium">{patient.kupat || 'לא זמין'}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Insights */}
            {patient.aiInsights && (
              <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-blue-100/50">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                      <Sparkles className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className="bg-blue-600 hover:bg-blue-600 text-white">Sarah AI</Badge>
                        <span className="text-xs text-gray-500">לפני 2 שעות</span>
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {patient.aiInsights.title}
                      </h3>
                      <p className="text-gray-700">
                        {patient.aiInsights.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="medical">
            <Card>
              <CardHeader>
                <CardTitle>היסטוריה רפואית</CardTitle>
                <CardDescription>רשומות רפואיות וטיפולים קודמים</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">בקרוב - היסטוריה רפואית מפורטת</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appointments">
            <Card>
              <CardHeader>
                <CardTitle>תורים</CardTitle>
                <CardDescription>תורים עתידיים ועבר</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">בקרוב - רשימת תורים</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="billing">
            <Card>
              <CardHeader>
                <CardTitle>חיובים</CardTitle>
                <CardDescription>היסטוריית תשלומים וחובות</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">בקרוב - פרטי חיובים</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documents">
            <Card>
              <CardHeader>
                <CardTitle>מסמכים</CardTitle>
                <CardDescription>מסמכים וקבצים של המטופל</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500">בקרוב - מסמכים</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
