import React, { useState, useEffect } from 'react';
import { 
  CreditCard, DollarSign, FileText, Download, Eye,
  CheckCircle, Clock, AlertCircle, ChevronRight,
  MessageCircle, Sparkles, Calendar, Receipt
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';

/**
 * Patient Billing Page - Hebrew/Israeli version
 * 
 * Features:
 * - Invoices list
 * - Payment history
 * - Outstanding balance
 * - Israeli payment methods (Bit, PayBox, Credit Card)
 * - Kupat Cholim info (not insurance claims)
 * - Marcus reminders
 * - Israeli tax invoice format
 */
export default function PatientBilling() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('invoices');
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  // Mock invoices
  const invoices = [
    {
      id: 1,
      number: 'INV-2025-001',
      date: '2025-10-05',
      dueDate: '2025-10-20',
      treatment: 'ניקוי שיניים',
      amount: 450,
      paid: 450,
      status: 'paid',
      paymentMethod: 'אשראי',
      paymentDate: '2025-10-06'
    },
    {
      id: 2,
      number: 'INV-2025-002',
      date: '2025-09-20',
      dueDate: '2025-10-05',
      treatment: 'סתימה',
      amount: 850,
      paid: 0,
      status: 'overdue',
      paymentMethod: null,
      paymentDate: null
    },
    {
      id: 3,
      number: 'INV-2025-003',
      date: '2025-08-10',
      dueDate: '2025-08-25',
      treatment: 'צילום פנורמי',
      amount: 350,
      paid: 350,
      status: 'paid',
      paymentMethod: 'Bit',
      paymentDate: '2025-08-12'
    },
  ];

  // Mock payment history
  const payments = [
    {
      id: 1,
      date: '2025-10-06',
      amount: 450,
      method: 'אשראי',
      invoice: 'INV-2025-001',
      status: 'completed'
    },
    {
      id: 2,
      date: '2025-08-12',
      amount: 350,
      method: 'Bit',
      invoice: 'INV-2025-003',
      status: 'completed'
    },
  ];

  const getStatusBadge = (status) => {
    const statusConfig = {
      paid: { label: 'שולם', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      pending: { label: 'ממתין', className: 'bg-yellow-100 text-yellow-800', icon: Clock },
      overdue: { label: 'באיחור', className: 'bg-red-100 text-red-800', icon: AlertCircle },
    };
    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;
    return (
      <Badge className={`${config.className} hover:${config.className}`}>
        <Icon className="h-3 w-3 ml-1" />
        {config.label}
      </Badge>
    );
  };

  const totalBalance = (invoices || []).reduce((sum, inv) => sum + (inv.amount - inv.paid), 0);
  const totalPaid = (invoices || []).reduce((sum, inv) => sum + inv.paid, 0);
  const overdueAmount = invoices
    .filter(inv => inv.status === 'overdue')
    .reduce((sum, inv) => sum + (inv.amount - inv.paid), 0);

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
                <h1 className="text-2xl font-bold text-gray-900">חשבוניות ותשלומים</h1>
                <p className="text-sm text-gray-500">נהל את החשבוניות והתשלומים שלך</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Marcus Alert - Overdue Payment */}
        {overdueAmount > 0 && (
          <Card className="mb-6 border-red-200 bg-gradient-to-r from-red-50 to-red-100/50">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center flex-shrink-0">
                  <AlertCircle className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className="bg-red-600 hover:bg-red-600 text-white">Marcus</Badge>
                    <Badge variant="outline" className="text-xs">CFO</Badge>
                    <span className="text-xs text-gray-500">לפני שעה</span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    יש לך חשבונית באיחור 💳
                  </h3>
                  <p className="text-gray-700 mb-3">
                    חשבונית INV-2025-002 בסכום ₪{overdueAmount} באיחור. אנא שלם בהקדם האפשרי.
                  </p>
                  <div className="flex items-center gap-2 mb-3">
                    <Progress value={95} className="flex-1 h-2 bg-red-200" />
                    <span className="text-xs text-gray-600">95% ביטחון</span>
                  </div>
                  <Button size="sm" className="bg-red-600 hover:bg-red-700" onClick={() => {
                    setSelectedInvoice(invoices.find(inv => inv.status === 'overdue'));
                    setPaymentDialogOpen(true);
                  }}>
                    <CreditCard className="h-4 w-4 ml-1" />
                    שלם עכשיו
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">יתרה</CardTitle>
              <DollarSign className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₪{totalBalance}</div>
              <p className="text-xs text-gray-500">לתשלום</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">שולם</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₪{totalPaid}</div>
              <p className="text-xs text-gray-500">החודש</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">חשבוניות</CardTitle>
              <FileText className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(invoices || []).length}</div>
              <p className="text-xs text-gray-500">סה"כ</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">תשלום אחרון</CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">06/10</div>
              <p className="text-xs text-gray-500">₪450</p>
            </CardContent>
          </Card>
        </div>

        {/* Kupat Cholim Info */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>קופת חולים</CardTitle>
            <CardDescription>מידע על קופת החולים והביטוח המשלים שלך</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">קופת חולים</h4>
                <p className="text-sm text-gray-600">מכבי</p>
                <p className="text-xs text-gray-500 mt-1">מספר חבר: 12345678</p>
              </div>
              <div>
                <h4 className="font-semibold mb-2">ביטוח משלים</h4>
                <p className="text-sm text-gray-600">מכבי שלי זהב</p>
                <p className="text-xs text-gray-500 mt-1">כיסוי: 80% מרפאת שיניים</p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-900">
                💡 <strong>טיפ:</strong> שמור את החשבוניות והקבלות להגשה לביטוח המשלים שלך. 
                אתה יכול להוריד את כל החשבוניות בפורמט PDF.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="invoices">חשבוניות</TabsTrigger>
            <TabsTrigger value="payments">היסטוריית תשלומים</TabsTrigger>
          </TabsList>

          {/* Invoices Tab */}
          <TabsContent value="invoices" className="space-y-4">
            {(invoices || []).map((invoice) => (
              <Card key={invoice.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex flex-col items-center justify-center text-white flex-shrink-0">
                        <Receipt className="h-6 w-6 mb-1" />
                        <span className="text-xs">חשבונית</span>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold">{invoice.number}</h3>
                          {getStatusBadge(invoice.status)}
                        </div>
                        
                        <p className="text-gray-700 mb-3">{invoice.treatment}</p>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">תאריך הנפקה:</span>
                            <span className="font-medium mr-2">
                              {new Date(invoice.date).toLocaleDateString('he-IL')}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">תאריך פירעון:</span>
                            <span className="font-medium mr-2">
                              {new Date(invoice.dueDate).toLocaleDateString('he-IL')}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">סכום:</span>
                            <span className="font-bold text-lg mr-2">₪{invoice.amount}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">שולם:</span>
                            <span className="font-medium mr-2">₪{invoice.paid}</span>
                          </div>
                        </div>

                        {invoice.status === 'paid' && invoice.paymentMethod && (
                          <div className="mt-3 p-3 bg-green-50 rounded-lg text-sm">
                            <span className="text-green-800">
                              ✓ שולם ב-{new Date(invoice.paymentDate).toLocaleDateString('he-IL')} 
                              באמצעות {invoice.paymentMethod}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex flex-col gap-2">
                      {invoice.status !== 'paid' && (
                        <Button 
                          size="sm" 
                          className="bg-gradient-to-r from-blue-600 to-purple-600"
                          onClick={() => {
                            setSelectedInvoice(invoice);
                            setPaymentDialogOpen(true);
                          }}
                        >
                          <CreditCard className="h-4 w-4 ml-1" />
                          שלם
                        </Button>
                      )}
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4 ml-1" />
                        הורד PDF
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 ml-1" />
                        צפה
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Payments Tab */}
          <TabsContent value="payments" className="space-y-4">
            {payments.map((payment) => (
              <Card key={payment.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-600 to-emerald-600 flex items-center justify-center">
                        <CheckCircle className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">₪{payment.amount}</h3>
                        <p className="text-sm text-gray-600">
                          {new Date(payment.date).toLocaleDateString('he-IL')} • {payment.method}
                        </p>
                        <p className="text-xs text-gray-500">חשבונית: {payment.invoice}</p>
                      </div>
                    </div>
                    <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                      הושלם
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      </main>

      {/* Payment Dialog */}
      <Dialog open={paymentDialogOpen} onOpenChange={setPaymentDialogOpen}>
        <DialogContent className="sm:max-w-[500px]" dir="rtl">
          <DialogHeader>
            <DialogTitle>תשלום חשבונית</DialogTitle>
            <DialogDescription>
              בחר אמצעי תשלום לסגירת החשבונית
            </DialogDescription>
          </DialogHeader>
          {selectedInvoice && (
            <div className="space-y-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600">חשבונית:</span>
                    <span className="font-semibold">{selectedInvoice.number}</span>
                  </div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600">טיפול:</span>
                    <span className="font-semibold">{selectedInvoice.treatment}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">סכום לתשלום:</span>
                    <span className="font-bold text-xl text-blue-600">
                      ₪{selectedInvoice.amount - selectedInvoice.paid}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <div className="space-y-3">
                <h4 className="font-semibold">בחר אמצעי תשלום:</h4>
                
                {/* Bit */}
                <Button 
                  variant="outline" 
                  className="w-full h-16 justify-start text-right"
                  onClick={() => {
                    alert('מפנה ל-Bit...');
                    setPaymentDialogOpen(false);
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
                      <span className="text-white font-bold">Bit</span>
                    </div>
                    <div>
                      <p className="font-semibold">Bit</p>
                      <p className="text-xs text-gray-500">תשלום מהיר דרך האפליקציה</p>
                    </div>
                  </div>
                </Button>

                {/* PayBox */}
                <Button 
                  variant="outline" 
                  className="w-full h-16 justify-start text-right"
                  onClick={() => {
                    alert('מפנה ל-PayBox...');
                    setPaymentDialogOpen(false);
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-orange-600 flex items-center justify-center">
                      <CreditCard className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold">PayBox</p>
                      <p className="text-xs text-gray-500">תשלום בכרטיס אשראי</p>
                    </div>
                  </div>
                </Button>

                {/* Credit Card */}
                <Button 
                  variant="outline" 
                  className="w-full h-16 justify-start text-right"
                  onClick={() => {
                    alert('מפנה לתשלום בכרטיס אשראי...');
                    setPaymentDialogOpen(false);
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-purple-600 flex items-center justify-center">
                      <CreditCard className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold">כרטיס אשראי</p>
                      <p className="text-xs text-gray-500">תשלום רגיל או בתשלומים</p>
                    </div>
                  </div>
                </Button>

                {/* Bank Transfer */}
                <Button 
                  variant="outline" 
                  className="w-full h-16 justify-start text-right"
                  onClick={() => {
                    alert('מציג פרטי העברה בנקאית...');
                    setPaymentDialogOpen(false);
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-green-600 flex items-center justify-center">
                      <DollarSign className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold">העברה בנקאית</p>
                      <p className="text-xs text-gray-500">העברה ישירה מהבנק</p>
                    </div>
                  </div>
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

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

