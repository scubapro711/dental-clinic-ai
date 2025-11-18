import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Phone, Mail, MessageCircle, Calendar, Download, Share2,
  User, Activity, FileText, Image, Pill, DollarSign, Brain, Clock,
  MapPin, Heart, AlertCircle, CheckCircle, TrendingUp, Edit
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import API_CONFIG from '@/config/api';

/**
 * Patient Detail Page - Comprehensive Patient View
 * 
 * Professional SaaS-grade patient management interface with:
 * - Complete patient information from Odoo
 * - Interactive tooth chart
 * - X-ray gallery and viewer
 * - Medical history and questionnaire
 * - Appointments timeline
 * - Treatment history and plans
 * - Billing and invoices
 * - AI insights from Sarah
 * 
 * UX/UI Features:
 * - Clean, modern medical interface
 * - Tab-based organization
 * - Quick actions bar
 * - Responsive design
 * - Loading states
 * - Error handling
 * - Breadcrumb navigation
 */
export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [patient, setPatient] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchPatientDetails();
  }, [id]);

  const fetchPatientDetails = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        API_CONFIG.endpoint(`dashboard/patients/${id}`),
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
            'X-Organization-ID': localStorage.getItem('organization_id') || '1'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch patient details');
      }

      const data = await response.json();
      setPatient(data);
    } catch (err) {
      console.error('Error fetching patient:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCall = () => {
    if (patient?.patient?.phone) {
      window.location.href = `tel:${patient.patient.phone}`;
    }
  };

  const handleEmail = () => {
    if (patient?.patient?.email) {
      window.location.href = `mailto:${patient.patient.email}`;
    }
  };

  const handleChat = () => {
    // TODO: Open AI chat with patient context
    console.log('Open chat with patient:', patient?.patient?.name);
  };

  const handleSchedule = () => {
    navigate(`/clinic/schedule?patient=${id}`);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Patient: ${patient?.patient?.name}`,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      // TODO: Show toast notification
    }
  };

  const calculateAge = (birthdate) => {
    if (!birthdate) return null;
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <Skeleton className="h-12 w-64" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 text-red-800">
                <AlertCircle className="h-6 w-6" />
                <div>
                  <h3 className="font-semibold">שגיאה בטעינת פרטי המטופל</h3>
                  <p className="text-sm">{error || 'מטופל לא נמצא'}</p>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => navigate('/clinic/patients')}
              >
                <ArrowLeft className="h-4 w-4 ml-2" />
                חזרה לרשימת מטופלים
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const patientData = patient.patient;
  const age = calculateAge(patientData.birthdate_date);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
            <button 
              onClick={() => navigate('/clinic/dashboard')}
              className="hover:text-gray-900"
            >
              Dashboard
            </button>
            <span>/</span>
            <button 
              onClick={() => navigate('/clinic/patients')}
              className="hover:text-gray-900"
            >
              מטופלים
            </button>
            <span>/</span>
            <span className="text-gray-900 font-medium">{patientData.name}</span>
          </div>

          {/* Patient Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              {/* Avatar */}
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">
                {patientData.name.split(' ').map(n => n[0]).join('')}
              </div>

              {/* Info */}
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold text-gray-900">
                    {patientData.name}
                  </h1>
                  <Badge variant="outline" className="text-sm">
                    ID: {id}
                  </Badge>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {age && (
                    <div className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      <span>גיל {age}</span>
                    </div>
                  )}
                  {patientData.phone && (
                    <div className="flex items-center gap-1">
                      <Phone className="h-4 w-4" />
                      <span>{patientData.phone}</span>
                    </div>
                  )}
                  {patientData.email && (
                    <div className="flex items-center gap-1">
                      <Mail className="h-4 w-4" />
                      <span className="text-xs">{patientData.email}</span>
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="flex items-center gap-6 mt-3">
                  <div className="text-sm">
                    <span className="text-gray-600">תורים: </span>
                    <span className="font-semibold">{patient.total_appointments || 0}</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-600">הכנסות: </span>
                    <span className="font-semibold">₪{(patient.total_revenue || 0).toLocaleString()}</span>
                  </div>
                  {patient.outstanding_balance > 0 && (
                    <div className="text-sm">
                      <span className="text-red-600">יתרה: </span>
                      <span className="font-semibold text-red-600">
                        ₪{patient.outstanding_balance.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={handleCall}
                disabled={!patientData.phone}
              >
                <Phone className="h-4 w-4 ml-1" />
                התקשר
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleEmail}
                disabled={!patientData.email}
              >
                <Mail className="h-4 w-4 ml-1" />
                אימייל
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleChat}
              >
                <MessageCircle className="h-4 w-4 ml-1" />
                צ'אט
              </Button>
              <Button
                size="sm"
                onClick={handleSchedule}
              >
                <Calendar className="h-4 w-4 ml-1" />
                קבע תור
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleShare}
              >
                <Share2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-8 mb-6">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              <span className="hidden md:inline">סקירה</span>
            </TabsTrigger>
            <TabsTrigger value="appointments" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span className="hidden md:inline">תורים</span>
            </TabsTrigger>
            <TabsTrigger value="tooth-chart" className="flex items-center gap-2">
              <Heart className="h-4 w-4" />
              <span className="hidden md:inline">מפת שיניים</span>
            </TabsTrigger>
            <TabsTrigger value="xrays" className="flex items-center gap-2">
              <Image className="h-4 w-4" />
              <span className="hidden md:inline">צילומים</span>
            </TabsTrigger>
            <TabsTrigger value="medical" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span className="hidden md:inline">היסטוריה</span>
            </TabsTrigger>
            <TabsTrigger value="treatments" className="flex items-center gap-2">
              <Pill className="h-4 w-4" />
              <span className="hidden md:inline">טיפולים</span>
            </TabsTrigger>
            <TabsTrigger value="invoices" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              <span className="hidden md:inline">חשבוניות</span>
            </TabsTrigger>
            <TabsTrigger value="ai-insights" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              <span className="hidden md:inline">AI</span>
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Stats Cards */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    סה"כ תורים
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{patient.total_appointments || 0}</div>
                  <p className="text-xs text-gray-500 mt-1">כל הזמנים</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    סה"כ הכנסות
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    ₪{(patient.total_revenue || 0).toLocaleString()}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">מכל הטיפולים</p>
                </CardContent>
              </Card>

              <Card className={cn(
                patient.outstanding_balance > 0 ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'
              )}>
                <CardHeader className="pb-3">
                  <CardTitle className={cn(
                    "text-sm font-medium",
                    patient.outstanding_balance > 0 ? 'text-red-600' : 'text-green-600'
                  )}>
                    יתרה לתשלום
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className={cn(
                    "text-3xl font-bold",
                    patient.outstanding_balance > 0 ? 'text-red-600' : 'text-green-600'
                  )}>
                    ₪{(patient.outstanding_balance || 0).toLocaleString()}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {patient.outstanding_balance > 0 ? 'דורש תשלום' : 'אין חובות'}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>פעילות אחרונה</CardTitle>
                <CardDescription>תורים וטיפולים אחרונים</CardDescription>
              </CardHeader>
              <CardContent>
                {patient.appointments && patient.appointments.length > 0 ? (
                  <div className="space-y-4">
                    {patient.appointments.slice(0, 5).map((apt) => (
                      <div key={apt.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            "w-2 h-2 rounded-full",
                            apt.state === 'done' ? 'bg-green-500' :
                            apt.state === 'confirmed' ? 'bg-blue-500' :
                            'bg-gray-400'
                          )} />
                          <div>
                            <div className="font-medium">
                              {new Date(apt.start).toLocaleDateString('he-IL', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </div>
                            <div className="text-sm text-gray-600">
                              {new Date(apt.start).toLocaleTimeString('he-IL', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          </div>
                        </div>
                        <Badge variant={
                          apt.state === 'done' ? 'default' :
                          apt.state === 'confirmed' ? 'secondary' :
                          'outline'
                        }>
                          {apt.state === 'done' ? 'הושלם' :
                           apt.state === 'confirmed' ? 'מאושר' :
                           apt.state}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Calendar className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                    <p>אין תורים רשומים</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Appointments Tab */}
          <TabsContent value="appointments">
            <Card>
              <CardHeader>
                <CardTitle>תורים</CardTitle>
                <CardDescription>כל התורים של המטופל</CardDescription>
              </CardHeader>
              <CardContent>
                {patient.appointments && patient.appointments.length > 0 ? (
                  <div className="space-y-3">
                    {patient.appointments.map((apt) => (
                      <div key={apt.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-semibold text-lg">
                              {new Date(apt.start).toLocaleDateString('he-IL', {
                                weekday: 'long',
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </div>
                            <div className="text-gray-600 mt-1">
                              {new Date(apt.start).toLocaleTimeString('he-IL', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                              {' - '}
                              {new Date(apt.stop).toLocaleTimeString('he-IL', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          </div>
                          <Badge variant={
                            apt.state === 'done' ? 'default' :
                            apt.state === 'confirmed' ? 'secondary' :
                            'outline'
                          }>
                            {apt.state === 'done' ? 'הושלם' :
                             apt.state === 'confirmed' ? 'מאושר' :
                             apt.state}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Calendar className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                    <p className="text-lg">אין תורים רשומים</p>
                    <Button className="mt-4" onClick={handleSchedule}>
                      <Calendar className="h-4 w-4 ml-2" />
                      קבע תור ראשון
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Other tabs - placeholder for now */}
          <TabsContent value="tooth-chart">
            <Card>
              <CardHeader>
                <CardTitle>מפת שיניים</CardTitle>
                <CardDescription>מצב שיניים ומפת טיפולים</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12 text-gray-500">
                <Heart className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p>מפת שיניים תתווסף בקרוב</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="xrays">
            <Card>
              <CardHeader>
                <CardTitle>צילומי רנטגן</CardTitle>
                <CardDescription>כל הצילומים של המטופל</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12 text-gray-500">
                <Image className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p>גלריית צילומים תתווסף בקרוב</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="medical">
            <Card>
              <CardHeader>
                <CardTitle>היסטוריה רפואית</CardTitle>
                <CardDescription>שאלון רפואי ומצבים רפואיים</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12 text-gray-500">
                <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p>היסטוריה רפואית תתווסף בקרוב</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="treatments">
            <Card>
              <CardHeader>
                <CardTitle>טיפולים</CardTitle>
                <CardDescription>היסטוריית טיפולים ותוכניות עתידיות</CardDescription>
              </CardHeader>
              <CardContent>
                {patient.treatments && patient.treatments.length > 0 ? (
                  <div className="space-y-3">
                    {patient.treatments.map((treatment) => (
                      <div key={treatment.id} className="p-4 border rounded-lg">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-semibold">
                              {new Date(treatment.start).toLocaleDateString('he-IL')}
                            </div>
                            {treatment.comments && (
                              <p className="text-sm text-gray-600 mt-1">{treatment.comments}</p>
                            )}
                          </div>
                          <Badge variant="default">הושלם</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Pill className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                    <p>אין טיפולים רשומים</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="invoices">
            <Card>
              <CardHeader>
                <CardTitle>חשבוניות</CardTitle>
                <CardDescription>היסטוריית חיובים ותשלומים</CardDescription>
              </CardHeader>
              <CardContent>
                {patient.invoices && patient.invoices.length > 0 ? (
                  <div className="space-y-3">
                    {patient.invoices.map((invoice) => (
                      <div key={invoice.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-semibold">{invoice.name}</div>
                            <div className="text-sm text-gray-600 mt-1">
                              {new Date(invoice.invoice_date).toLocaleDateString('he-IL')}
                            </div>
                          </div>
                          <div className="text-left">
                            <div className="font-bold text-lg">
                              ₪{invoice.amount_total.toLocaleString()}
                            </div>
                            {invoice.amount_residual > 0 && (
                              <div className="text-sm text-red-600">
                                נותר: ₪{invoice.amount_residual.toLocaleString()}
                              </div>
                            )}
                            <Badge 
                              variant={invoice.payment_state === 'paid' ? 'default' : 'destructive'}
                              className="mt-1"
                            >
                              {invoice.payment_state === 'paid' ? 'שולם' : 
                               invoice.payment_state === 'partial' ? 'חלקי' : 
                               'לא שולם'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <DollarSign className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                    <p>אין חשבוניות רשומות</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai-insights">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  תובנות AI - Sarah
                </CardTitle>
                <CardDescription>ניתוח והמלצות מבוססות בינה מלאכותית</CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12 text-gray-500">
                <Brain className="h-16 w-16 mx-auto mb-4 text-purple-400" />
                <p>תובנות AI יתווספו בקרוב</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
