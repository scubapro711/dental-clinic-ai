import React, { useState, useEffect } from 'react';
import { 
  FileText, Image, Pill, Activity, Heart, TrendingUp,
  ChevronRight, Download, Eye, MessageCircle, Sparkles,
  Calendar, User, Stethoscope, AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';

/**
 * Patient Medical Records Page - Hebrew version
 * 
 * Features:
 * - Treatment history
 * - Dental chart (32 teeth)
 * - X-rays viewer
 * - Prescriptions
 * - Health score
 * - Sarah insights
 */
export default function PatientMedicalRecords() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('treatments');

  // Mock dental chart data (32 teeth)
  const dentalChart = Array.from({ length: 32 }, (_, i) => ({
    number: i + 1,
    status: ['healthy', 'filled', 'cavity', 'missing'][Math.floor(Math.random() * 4)],
    treatments: []
  }));

  // Mock treatment records
  const treatments = [
    {
      id: 1,
      date: '2025-10-05',
      treatment: 'ניקוי שיניים',
      tooth: null,
      doctor: 'ד"ר כהן',
      diagnosis: 'חניכיים בריאות',
      notes: 'הניקוי עבר בהצלחה. חניכיים בריאות, אין אבנית.',
      followUp: false
    },
    {
      id: 2,
      date: '2025-09-20',
      treatment: 'סתימה',
      tooth: '#14',
      doctor: 'ד"ר לוי',
      diagnosis: 'עששת',
      notes: 'סתימה לבנה בשן 14. המטופל דיווח על רגישות קלה.',
      followUp: true
    },
    {
      id: 3,
      date: '2025-08-10',
      treatment: 'צילום פנורמי',
      tooth: null,
      doctor: 'ד"ר כהן',
      diagnosis: 'בדיקה שגרתית',
      notes: 'צילום פנורמי תקין. אין ממצאים חריגים.',
      followUp: false
    },
  ];

  // Mock X-rays
  const xrays = [
    { id: 1, date: '2025-08-10', type: 'פנורמי', url: '/xrays/panoramic.jpg' },
    { id: 2, date: '2025-06-15', type: 'Bitewing', url: '/xrays/bitewing.jpg' },
  ];

  // Mock prescriptions
  const prescriptions = [
    {
      id: 1,
      date: '2025-09-20',
      medication: 'Amoxicillin 500mg',
      dosage: '3 פעמים ביום',
      duration: '7 ימים',
      doctor: 'ד"ר לוי',
      notes: 'לקחת עם אוכל'
    },
  ];

  const getToothStatusColor = (status) => {
    const colors = {
      healthy: 'bg-green-500',
      filled: 'bg-blue-500',
      cavity: 'bg-red-500',
      missing: 'bg-gray-300'
    };
    return colors[status] || colors.healthy;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/patient/dashboard')}>
                <ChevronRight className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">רשומות רפואיות</h1>
                <p className="text-sm text-gray-500">ההיסטוריה הרפואית שלך</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Health Score Card */}
        <Card className="mb-6 border-purple-200 bg-gradient-to-r from-purple-50 to-purple-100/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                <Heart className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-purple-600 hover:bg-purple-600 text-white">Sarah</Badge>
                  <Badge variant="outline" className="text-xs">עוזרת קלינית</Badge>
                  <span className="text-xs text-gray-500">לפני 3 שעות</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  ציון בריאות השיניים שלך: 85/100 🎉
                </h3>
                <p className="text-gray-700 mb-3">
                  מצוין! השיניים והחניכיים שלך במצב טוב. המשך לצחצח פעמיים ביום ולהשתמש בחוט דנטלי.
                </p>
                <div className="flex items-center gap-2 mb-3">
                  <Progress value={85} className="flex-1 h-3 bg-purple-200" />
                  <span className="text-sm font-semibold">85/100</span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-purple-600">28</p>
                    <p className="text-xs text-gray-600">שיניים בריאות</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-600">3</p>
                    <p className="text-xs text-gray-600">סתימות</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-600">1</p>
                    <p className="text-xs text-gray-600">טיפול נדרש</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">שיניים</CardTitle>
              <Activity className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">28/32</div>
              <p className="text-xs text-gray-500">שיניים בריאות</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">רשומות</CardTitle>
              <FileText className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-gray-500">רשומות טיפול</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">צילומים</CardTitle>
              <Image className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-gray-500">צילומי רנטגן</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">מרשמים</CardTitle>
              <Pill className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-gray-500">מרשמים פעילים</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="treatments">טיפולים</TabsTrigger>
            <TabsTrigger value="dental-chart">מפת שיניים</TabsTrigger>
            <TabsTrigger value="xrays">צילומים</TabsTrigger>
            <TabsTrigger value="prescriptions">מרשמים</TabsTrigger>
          </TabsList>

          {/* Treatments Tab */}
          <TabsContent value="treatments" className="space-y-4">
            {(treatments || []).map((treatment) => (
              <Card key={treatment.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-white flex-shrink-0">
                        <FileText className="h-6 w-6" />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold">{treatment.treatment}</h3>
                          {treatment.tooth && (
                            <Badge variant="outline">{treatment.tooth}</Badge>
                          )}
                          {treatment.followUp && (
                            <Badge className="bg-orange-100 text-orange-800 hover:bg-orange-100">
                              <AlertCircle className="h-3 w-3 ml-1" />
                              נדרש מעקב
                            </Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600 mb-3">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <span>{new Date(treatment.date).toLocaleDateString('he-IL')}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4" />
                            <span>{treatment.doctor}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Stethoscope className="h-4 w-4" />
                            <span>{treatment.diagnosis}</span>
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                          {treatment.notes}
                        </p>
                      </div>
                    </div>
                    
                    <Button size="sm" variant="outline">
                      <Eye className="h-4 w-4 ml-1" />
                      פרטים
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Dental Chart Tab */}
          <TabsContent value="dental-chart">
            <Card>
              <CardHeader>
                <CardTitle>מפת שיניים</CardTitle>
                <CardDescription>מצב כל שן בפה</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-8">
                  {/* Upper Teeth */}
                  <div>
                    <h4 className="text-sm font-semibold mb-4 text-center">לסת עליונה</h4>
                    <div className="grid grid-cols-16 gap-2">
                      {dentalChart.slice(0, 16).reverse().map((tooth) => (
                        <div key={tooth.number} className="flex flex-col items-center">
                          <div
                            className={`w-8 h-12 rounded-t-full ${getToothStatusColor(tooth.status)} cursor-pointer hover:opacity-80 transition-opacity`}
                            title={`שן ${tooth.number} - ${tooth.status}`}
                          />
                          <span className="text-xs text-gray-600 mt-1">{tooth.number}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Lower Teeth */}
                  <div>
                    <h4 className="text-sm font-semibold mb-4 text-center">לסת תחתונה</h4>
                    <div className="grid grid-cols-16 gap-2">
                      {dentalChart.slice(16, 32).reverse().map((tooth) => (
                        <div key={tooth.number} className="flex flex-col items-center">
                          <span className="text-xs text-gray-600 mb-1">{tooth.number}</span>
                          <div
                            className={`w-8 h-12 rounded-b-full ${getToothStatusColor(tooth.status)} cursor-pointer hover:opacity-80 transition-opacity`}
                            title={`שן ${tooth.number} - ${tooth.status}`}
                          />
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="flex justify-center gap-6 pt-4 border-t">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-green-500" />
                      <span className="text-sm">בריא</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-blue-500" />
                      <span className="text-sm">סתימה</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-red-500" />
                      <span className="text-sm">עששת</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-gray-300" />
                      <span className="text-sm">חסר</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* X-rays Tab */}
          <TabsContent value="xrays" className="space-y-4">
            {xrays.map((xray) => (
              <Card key={xray.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                        <Image className="h-8 w-8 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{xray.type}</h3>
                        <p className="text-sm text-gray-600">
                          {new Date(xray.date).toLocaleDateString('he-IL')}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 ml-1" />
                        צפה
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4 ml-1" />
                        הורד
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Prescriptions Tab */}
          <TabsContent value="prescriptions" className="space-y-4">
            {prescriptions.map((prescription) => (
              <Card key={prescription.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-600 to-red-600 flex items-center justify-center flex-shrink-0">
                      <Pill className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-2">{prescription.medication}</h3>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">מינון:</span>
                          <span className="font-medium mr-2">{prescription.dosage}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">משך:</span>
                          <span className="font-medium mr-2">{prescription.duration}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">רופא:</span>
                          <span className="font-medium mr-2">{prescription.doctor}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">תאריך:</span>
                          <span className="font-medium mr-2">
                            {new Date(prescription.date).toLocaleDateString('he-IL')}
                          </span>
                        </div>
                      </div>
                      {prescription.notes && (
                        <p className="text-sm text-gray-600 mt-3 bg-orange-50 p-3 rounded-lg">
                          💡 {prescription.notes}
                        </p>
                      )}
                    </div>
                    <Button size="sm" variant="outline">
                      <Download className="h-4 w-4 ml-1" />
                      הורד
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      </main>

      {/* Floating Chat Button */}
      <Button
        size="lg"
        className="fixed bottom-6 left-6 w-16 h-16 rounded-full shadow-2xl bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 z-50"
        onClick={() => navigate('/patient/dashboard')}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    </div>
  );
}

