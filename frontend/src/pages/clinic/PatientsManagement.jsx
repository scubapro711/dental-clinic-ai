import React, { useState } from 'react';
import { 
  Users, Search, Filter, Plus, Eye, Edit, MessageCircle,
  Phone, Mail, Calendar, FileText, DollarSign, AlertCircle,
  CheckCircle, Clock, Sparkles, ChevronRight
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useNavigate } from 'react-router-dom';

/**
 * Patients Management Page - Clinic Portal
 * 
 * Features:
 * - Search and filter patients
 * - View patient details
 * - Quick actions (call, email, chat with Alex)
 * - Patient status indicators
 * - Alex & Sarah suggestions
 */
export default function PatientsManagement() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedPatient, setSelectedPatient] = useState(null);

  // Mock patients data
  const patients = [
    {
      id: 1,
      name: 'שרה כהן',
      phone: '+972-50-123-4567',
      email: 'sarah.cohen@example.com',
      lastVisit: '2025-10-05',
      nextAppointment: '2025-10-12',
      balance: 0,
      status: 'active',
      visits: 12,
      kupat: 'מכבי',
      healthScore: 85
    },
    {
      id: 2,
      name: 'יוסי לוי',
      phone: '+972-52-987-6543',
      email: 'yossi.levi@example.com',
      lastVisit: '2025-09-20',
      nextAppointment: null,
      balance: 850,
      status: 'overdue',
      visits: 8,
      kupat: 'כללית',
      healthScore: 72
    },
    {
      id: 3,
      name: 'רחל אברהם',
      phone: '+972-54-555-1234',
      email: 'rachel.a@example.com',
      lastVisit: '2025-10-01',
      nextAppointment: '2025-11-15',
      status: 'active',
      visits: 15,
      kupat: 'מאוחדת',
      healthScore: 92
    },
  ];

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/clinic/dashboard')}>
                <ChevronRight className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ניהול מטופלים</h1>
                <p className="text-sm text-gray-500">צפה ונהל את כל המטופלים במרפאה</p>
              </div>
            </div>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
              <Plus className="h-4 w-4 ml-1" />
              מטופל חדש
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alex Suggestion */}
        <Card className="mb-6 border-blue-200 bg-gradient-to-r from-blue-50 to-blue-100/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge className="bg-blue-600 hover:bg-blue-600 text-white">Alex</Badge>
                  <Badge variant="outline" className="text-xs">Reception</Badge>
                  <span className="text-xs text-gray-500">לפני 5 דקות</span>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  3 מטופלים צריכים תור המשך 📅
                </h3>
                <p className="text-gray-700 mb-3">
                  זיהיתי 3 מטופלים שלא קבעו תור המשך. האם לשלוח להם תזכורת?
                </p>
                <div className="flex gap-2">
                  <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                    שלח תזכורות
                  </Button>
                  <Button size="sm" variant="outline">
                    צפה ברשימה
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">סה"כ מטופלים</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,500</div>
              <p className="text-xs text-gray-500">+12 החודש</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">פעילים</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,234</div>
              <p className="text-xs text-gray-500">82%</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">עם חוב</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">45</div>
              <p className="text-xs text-gray-500">₪38,500</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">תורים היום</CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">18</div>
              <p className="text-xs text-gray-500">3 ממתינים</p>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="חפש לפי שם, טלפון או אימייל..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pr-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="סטטוס" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">הכל</SelectItem>
                  <SelectItem value="active">פעילים</SelectItem>
                  <SelectItem value="overdue">עם חוב</SelectItem>
                  <SelectItem value="inactive">לא פעילים</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                <Filter className="h-4 w-4 ml-1" />
                סינון מתקדם
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Patients List */}
        <div className="space-y-4">
          {(patients || []).map((patient) => (
            <Card key={patient.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
                      {patient.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold">{patient.name}</h3>
                        {getStatusBadge(patient.status)}
                        <Badge variant="outline" className="text-xs">{patient.kupat}</Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4 text-gray-400" />
                          <span>{patient.phone}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4 text-gray-400" />
                          <span className="text-xs">{patient.email}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          <span>ביקור אחרון: {new Date(patient.lastVisit).toLocaleDateString('he-IL')}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-gray-400" />
                          <span>{patient.visits} ביקורים</span>
                        </div>
                      </div>

                      {patient.balance > 0 && (
                        <div className="p-3 bg-red-50 rounded-lg text-sm mb-3">
                          <span className="text-red-800 font-semibold">
                            חוב: ₪{patient.balance}
                          </span>
                        </div>
                      )}

                      {patient.nextAppointment && (
                        <div className="p-3 bg-green-50 rounded-lg text-sm">
                          <span className="text-green-800">
                            תור הבא: {new Date(patient.nextAppointment).toLocaleDateString('he-IL')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => navigate(`/clinic/patients/${patient.id}`)}
                    >
                      <Eye className="h-4 w-4 ml-1" />
                      צפה
                    </Button>
                    <Button size="sm" variant="outline">
                      <Edit className="h-4 w-4 ml-1" />
                      ערוך
                    </Button>
                    <Button size="sm" variant="outline">
                      <MessageCircle className="h-4 w-4 ml-1" />
                      צ'אט
                    </Button>
                    <Button size="sm" variant="outline">
                      <Phone className="h-4 w-4 ml-1" />
                      התקשר
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>

      {/* Floating Chat Button */}
      <Button
        size="lg"
        className="fixed bottom-6 left-6 w-16 h-16 rounded-full shadow-2xl bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 z-50"
        onClick={() => navigate('/clinic/dashboard')}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    </div>
  );
}

