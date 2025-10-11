import React, { useState, useEffect } from 'react';
import { 
  Calendar, Clock, User, MapPin, Phone, Mail, 
  CheckCircle, XCircle, AlertCircle, Plus, Filter,
  Search, ChevronRight, Video, MessageCircle, Sparkles
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';

/**
 * Patient Appointments Page - Hebrew version
 * 
 * Features:
 * - List of upcoming appointments
 * - List of past appointments
 * - Booking wizard (3 steps)
 * - Filters and search
 * - Reschedule/cancel actions
 * - Alex proactive suggestions
 * - SMS/Telegram reminders
 */
export default function PatientAppointments() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState([]);
  const [filter, setFilter] = useState('upcoming');
  const [searchTerm, setSearchTerm] = useState('');
  const [bookingOpen, setBookingOpen] = useState(false);
  const [bookingStep, setBookingStep] = useState(1);

  useEffect(() => {
    fetchAppointments();
  }, [filter]);

  const fetchAppointments = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/appointments?filter=${filter}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      const data = await response.json();
      setAppointments(data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      confirmed: { label: 'מאושר', className: 'bg-green-100 text-green-800' },
      scheduled: { label: 'מתוזמן', className: 'bg-blue-100 text-blue-800' },
      completed: { label: 'הושלם', className: 'bg-gray-100 text-gray-800' },
      cancelled: { label: 'בוטל', className: 'bg-red-100 text-red-800' },
      'no-show': { label: 'לא הגיע', className: 'bg-orange-100 text-orange-800' },
    };
    const config = statusConfig[status] || statusConfig.scheduled;
    return <Badge className={`${config.className} hover:${config.className}`}>{config.label}</Badge>;
  };

  // Mock data for demonstration
  const mockAppointments = [
    {
      id: 1,
      date: '2025-10-12',
      time: '10:00',
      doctor: 'ד"ר כהן',
      treatment: 'ניקוי שיניים',
      status: 'confirmed',
      duration: 30,
      room: 'חדר 2',
      notes: 'אנא הגיעו 10 דקות לפני'
    },
    {
      id: 2,
      date: '2025-11-15',
      time: '14:30',
      doctor: 'ד"ר לוי',
      treatment: 'בדיקה שגרתית',
      status: 'scheduled',
      duration: 20,
      room: 'חדר 1',
      notes: ''
    },
    {
      id: 3,
      date: '2025-09-20',
      time: '09:00',
      doctor: 'ד"ר כהן',
      treatment: 'סתימה',
      status: 'completed',
      duration: 45,
      room: 'חדר 2',
      notes: 'טיפול הושלם בהצלחה'
    },
  ];

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
                <h1 className="text-2xl font-bold text-gray-900">התורים שלי</h1>
                <p className="text-sm text-gray-500">נהל את התורים שלך</p>
              </div>
            </div>
            
            <Dialog open={bookingOpen} onOpenChange={setBookingOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Plus className="h-4 w-4 ml-1" />
                  קביעת תור חדש
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]" dir="rtl">
                <DialogHeader>
                  <DialogTitle>קביעת תור חדש</DialogTitle>
                  <DialogDescription>
                    בחר תאריך, שעה וסוג טיפול
                  </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <div className="space-y-4">
                    {/* Booking Wizard Steps */}
                    <div className="flex items-center justify-between mb-6">
                      {[1, 2, 3].map((step) => (
                        <div key={step} className="flex items-center">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            bookingStep >= step 
                              ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
                              : 'bg-gray-200 text-gray-500'
                          }`}>
                            {step}
                          </div>
                          {step < 3 && (
                            <div className={`w-20 h-1 ${
                              bookingStep > step ? 'bg-gradient-to-r from-blue-600 to-purple-600' : 'bg-gray-200'
                            }`} />
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Step 1: Treatment Type */}
                    {bookingStep === 1 && (
                      <div className="space-y-4">
                        <h3 className="font-semibold">בחר סוג טיפול</h3>
                        <div className="grid grid-cols-2 gap-3">
                          {['ניקוי שיניים', 'בדיקה שגרתית', 'סתימה', 'עקירה', 'שורש', 'הלבנה'].map((treatment) => (
                            <Button key={treatment} variant="outline" className="h-20">
                              {treatment}
                            </Button>
                          ))}
                        </div>
                        <Button className="w-full" onClick={() => setBookingStep(2)}>
                          המשך
                        </Button>
                      </div>
                    )}

                    {/* Step 2: Date & Time */}
                    {bookingStep === 2 && (
                      <div className="space-y-4">
                        <h3 className="font-semibold">בחר תאריך ושעה</h3>
                        <div className="grid grid-cols-1 gap-4">
                          <Input type="date" />
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="בחר שעה" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="09:00">09:00</SelectItem>
                              <SelectItem value="10:00">10:00</SelectItem>
                              <SelectItem value="11:00">11:00</SelectItem>
                              <SelectItem value="14:00">14:00</SelectItem>
                              <SelectItem value="15:00">15:00</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" className="flex-1" onClick={() => setBookingStep(1)}>
                            חזור
                          </Button>
                          <Button className="flex-1" onClick={() => setBookingStep(3)}>
                            המשך
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Step 3: Confirmation */}
                    {bookingStep === 3 && (
                      <div className="space-y-4">
                        <h3 className="font-semibold">אישור פרטים</h3>
                        <Card>
                          <CardContent className="p-4 space-y-2">
                            <div className="flex justify-between">
                              <span className="text-gray-600">טיפול:</span>
                              <span className="font-semibold">ניקוי שיניים</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">תאריך:</span>
                              <span className="font-semibold">15 נובמבר 2025</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">שעה:</span>
                              <span className="font-semibold">10:00</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">רופא:</span>
                              <span className="font-semibold">ד"ר כהן</span>
                            </div>
                          </CardContent>
                        </Card>
                        <div className="flex gap-2">
                          <Button variant="outline" className="flex-1" onClick={() => setBookingStep(2)}>
                            חזור
                          </Button>
                          <Button className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600">
                            אשר תור
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* AI Suggestion - Alex */}
        <Card className="mb-6 border-blue-200 bg-gradient-to-r from-blue-50 to-blue-100/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-blue-600 hover:bg-blue-600 text-white">Alex</Badge>
                  <span className="text-xs text-gray-500">לפני שעה</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  הגיע הזמן לניקוי שיניים! 🦷
                </h3>
                <p className="text-gray-700 mb-3">
                  עברו 6 חודשים מהניקוי האחרון שלך. אני ממליץ לקבוע תור לניקוי שיניים בשבועיים הקרובים.
                </p>
                <div className="flex items-center gap-2 mb-3">
                  <Progress value={92} className="flex-1 h-2" />
                  <span className="text-xs text-gray-600">92% ביטחון</span>
                </div>
                <Button size="sm" className="bg-blue-600 hover:bg-blue-700" onClick={() => setBookingOpen(true)}>
                  <Calendar className="h-4 w-4 ml-1" />
                  קבע תור עכשיו
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <Input
                placeholder="חפש תורים..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pr-10"
              />
            </div>
          </div>
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-full sm:w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="upcoming">תורים קרובים</SelectItem>
              <SelectItem value="past">תורים קודמים</SelectItem>
              <SelectItem value="cancelled">תורים מבוטלים</SelectItem>
              <SelectItem value="all">כל התורים</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Appointments List */}
        <div className="space-y-4">
          {mockAppointments
            .filter(apt => {
              if (filter === 'upcoming') return ['confirmed', 'scheduled'].includes(apt.status);
              if (filter === 'past') return apt.status === 'completed';
              if (filter === 'cancelled') return apt.status === 'cancelled';
              return true;
            })
            .map((apt) => (
              <Card key={apt.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex flex-col items-center justify-center text-white flex-shrink-0">
                        <span className="text-2xl font-bold">{apt.date.split('-')[2]}</span>
                        <span className="text-xs">
                          {new Date(apt.date).toLocaleDateString('he-IL', { month: 'short' })}
                        </span>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold">{apt.treatment}</h3>
                          {getStatusBadge(apt.status)}
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            <span>{apt.time} ({apt.duration} דקות)</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4" />
                            <span>{apt.doctor}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{apt.room}</span>
                          </div>
                        </div>
                        
                        {apt.notes && (
                          <p className="text-sm text-gray-500 mt-2">
                            💡 {apt.notes}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex flex-col gap-2">
                      {apt.status === 'confirmed' && (
                        <>
                          <Button size="sm" variant="outline">
                            <Calendar className="h-4 w-4 ml-1" />
                            שנה תאריך
                          </Button>
                          <Button size="sm" variant="outline" className="text-red-600 hover:text-red-700">
                            <XCircle className="h-4 w-4 ml-1" />
                            בטל תור
                          </Button>
                        </>
                      )}
                      {apt.status === 'completed' && (
                        <Button size="sm" variant="outline">
                          <CheckCircle className="h-4 w-4 ml-1" />
                          צפה ברשומה
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>

        {/* Empty State */}
        {mockAppointments.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                אין תורים
              </h3>
              <p className="text-gray-600 mb-4">
                עדיין לא קבעת תורים. קבע תור חדש עכשיו!
              </p>
              <Button onClick={() => setBookingOpen(true)}>
                <Plus className="h-4 w-4 ml-1" />
                קביעת תור חדש
              </Button>
            </CardContent>
          </Card>
        )}
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

