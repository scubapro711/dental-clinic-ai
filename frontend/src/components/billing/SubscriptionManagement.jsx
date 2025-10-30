import React, { useState, useEffect } from 'react';
import { 
  CreditCard, Calendar, AlertCircle, CheckCircle, Clock,
  TrendingUp, Users, FileText, Settings, RefreshCw,
  ArrowLeft, Download, Sparkles, Shield, Crown
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';
import PaymentMethodForm from './PaymentMethodForm';

/**
 * Subscription Management Component
 * 
 * Allows clinics to view and manage their subscription.
 * Features:
 * - Current plan details
 * - Usage statistics
 * - Payment method management
 * - Upgrade/downgrade options
 * - Cancel subscription
 * - Invoice history
 */
export default function SubscriptionManagement() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [paymentMethod, setPaymentMethod] = useState(null);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      
      // Fetch subscription
      const subResponse = await fetch(`${API_BASE_URL}/api/v1/subscriptions/current`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (subResponse.ok) {
        const subData = await subResponse.json();
        setSubscription(subData);
      }

      // Fetch invoices
      const invResponse = await fetch(`${API_BASE_URL}/api/v1/subscriptions/invoices`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (invResponse.ok) {
        const invData = await invResponse.json();
        setInvoices(invData.invoices || []);
      }

      // Fetch payment method
      const pmResponse = await fetch(`${API_BASE_URL}/api/v1/subscriptions/payment-method`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (pmResponse.ok) {
        const pmData = await pmResponse.json();
        setPaymentMethod(pmData);
      }

    } catch (error) {
      console.error('Error fetching subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    setCancelling(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        alert('המנוי בוטל בהצלחה. תוכל להמשיך להשתמש במערכת עד סוף תקופת החיוב.');
        fetchSubscriptionData();
        setShowCancelDialog(false);
      } else {
        const error = await response.json();
        alert(`שגיאה בביטול המנוי: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      alert('שגיאה בביטול המנוי. אנא נסה שוב.');
    } finally {
      setCancelling(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { label: 'פעיל', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      trialing: { label: 'ניסיון', className: 'bg-blue-100 text-blue-800', icon: Clock },
      past_due: { label: 'באיחור', className: 'bg-red-100 text-red-800', icon: AlertCircle },
      canceled: { label: 'מבוטל', className: 'bg-gray-100 text-gray-800', icon: AlertCircle },
      incomplete: { label: 'לא הושלם', className: 'bg-yellow-100 text-yellow-800', icon: Clock },
    };
    const config = statusConfig[status] || statusConfig.active;
    const Icon = config.icon;
    return (
      <Badge className={`${config.className} hover:${config.className}`}>
        <Icon className="h-3 w-3 ml-1" />
        {config.label}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('he-IL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      minimumFractionDigits: 0
    }).format(price);
  };

  const calculateUsagePercentage = (current, max) => {
    return Math.round((current / max) * 100);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">טוען נתוני מנוי...</p>
        </div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ניהול מנוי</h1>
              </div>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <Card>
            <CardContent className="p-12 text-center">
              <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">אין לך מנוי פעיל</h2>
              <p className="text-gray-600 mb-6">התחל עם ניסיון חינם ל-30 יום</p>
              <Button onClick={() => navigate('/pricing')}>
                בחר תוכנית
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const usagePercentage = {
    users: calculateUsagePercentage(subscription.current_users || 0, subscription.plan?.max_users || 1),
    patients: calculateUsagePercentage(subscription.current_patients || 0, subscription.plan?.max_patients || 1)
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ניהול מנוי</h1>
                <p className="text-sm text-gray-500">נהל את המנוי והתשלומים שלך</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Trial Alert */}
        {subscription.status === 'trialing' && (
          <Alert className="border-blue-200 bg-gradient-to-r from-blue-50 to-blue-100/50">
            <Clock className="h-5 w-5 text-blue-600" />
            <AlertDescription className="text-blue-900">
              <strong>אתה בתקופת ניסיון!</strong> תקופת הניסיון שלך מסתיימת ב-{formatDate(subscription.trial_end)}.
              {!paymentMethod && ' אנא הוסף אמצעי תשלום כדי להמשיך את השירות לאחר תום תקופת הניסיון.'}
            </AlertDescription>
          </Alert>
        )}

        {/* Past Due Alert */}
        {subscription.status === 'past_due' && (
          <Alert className="border-red-200 bg-gradient-to-r from-red-50 to-red-100/50">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <AlertDescription className="text-red-900">
              <strong>התשלום שלך באיחור!</strong> אנא עדכן את אמצעי התשלום שלך כדי להמשיך להשתמש בשירות.
            </AlertDescription>
          </Alert>
        )}

        {/* Current Plan Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                  <Crown className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle className="text-2xl">{subscription.plan?.name}</CardTitle>
                  <CardDescription>תוכנית נוכחית</CardDescription>
                </div>
              </div>
              {getStatusBadge(subscription.status)}
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="text-sm text-gray-500 mb-1">מחיר חודשי</div>
                <div className="text-2xl font-bold">{formatPrice(subscription.plan?.monthly_price || 0)}</div>
                {subscription.discount_percentage > 0 && (
                  <Badge className="mt-1 bg-green-100 text-green-800 hover:bg-green-100">
                    {subscription.discount_percentage}% הנחה
                  </Badge>
                )}
              </div>
              <div>
                <div className="text-sm text-gray-500 mb-1">תאריך חידוש</div>
                <div className="text-lg font-semibold">
                  {subscription.current_period_end ? formatDate(subscription.current_period_end) : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500 mb-1">תאריך התחלה</div>
                <div className="text-lg font-semibold">
                  {subscription.start_date ? formatDate(subscription.start_date) : 'N/A'}
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button onClick={() => navigate('/pricing')} variant="outline">
                <TrendingUp className="h-4 w-4 ml-2" />
                שדרג תוכנית
              </Button>
              <Dialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="text-red-600 hover:text-red-700">
                    ביטול מנוי
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>האם אתה בטוח?</DialogTitle>
                    <DialogDescription>
                      ביטול המנוי יגרום לאובדן גישה למערכת בסוף תקופת החיוב הנוכחית.
                      תוכל להמשיך להשתמש במערכת עד {subscription.current_period_end ? formatDate(subscription.current_period_end) : 'סוף התקופה'}.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex gap-3 justify-end">
                    <Button variant="outline" onClick={() => setShowCancelDialog(false)}>
                      ביטול
                    </Button>
                    <Button 
                      variant="destructive" 
                      onClick={handleCancelSubscription}
                      disabled={cancelling}
                    >
                      {cancelling ? 'מבטל...' : 'אישור ביטול'}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardContent>
        </Card>

        {/* Usage Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>שימוש נוכחי</CardTitle>
            <CardDescription>מעקב אחר השימוש שלך בתוכנית</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">משתמשים</span>
                </div>
                <span className="text-sm text-gray-600">
                  {subscription.current_users || 0} / {subscription.plan?.max_users || 0}
                </span>
              </div>
              <Progress value={usagePercentage.users} className="h-2" />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium">מטופלים</span>
                </div>
                <span className="text-sm text-gray-600">
                  {subscription.current_patients || 0} / {subscription.plan?.max_patients || 0}
                </span>
              </div>
              <Progress value={usagePercentage.patients} className="h-2" />
            </div>

            {(usagePercentage.users > 80 || usagePercentage.patients > 80) && (
              <Alert className="border-yellow-200 bg-yellow-50">
                <AlertCircle className="h-4 w-4 text-yellow-600" />
                <AlertDescription className="text-yellow-900 text-sm">
                  אתה מתקרב למגבלת התוכנית שלך. שקול לשדרג לתוכנית גבוהה יותר.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Payment Method */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>אמצעי תשלום</CardTitle>
                <CardDescription>נהל את אמצעי התשלום שלך</CardDescription>
              </div>
              <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 ml-2" />
                    {paymentMethod ? 'עדכן' : 'הוסף'}
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>עדכון אמצעי תשלום</DialogTitle>
                    <DialogDescription>
                      עדכן את פרטי כרטיס האשראי שלך
                    </DialogDescription>
                  </DialogHeader>
                  <PaymentMethodForm 
                    onSuccess={() => {
                      setShowPaymentDialog(false);
                      fetchSubscriptionData();
                    }}
                  />
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {paymentMethod ? (
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center">
                  <CreditCard className="h-6 w-6 text-gray-600" />
                </div>
                <div>
                  <div className="font-medium">
                    {paymentMethod.brand} •••• {paymentMethod.last4}
                  </div>
                  <div className="text-sm text-gray-500">
                    תוקף: {paymentMethod.exp_month}/{paymentMethod.exp_year}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600 mb-4">לא הוגדר אמצעי תשלום</p>
                <Button onClick={() => setShowPaymentDialog(true)}>
                  הוסף אמצעי תשלום
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Invoice History */}
        <Card>
          <CardHeader>
            <CardTitle>היסטוריית חשבוניות</CardTitle>
            <CardDescription>כל החשבוניות שלך במקום אחד</CardDescription>
          </CardHeader>
          <CardContent>
            {(invoices || []).length > 0 ? (
              <div className="space-y-3">
                {(invoices || []).map((invoice) => (
                  <div 
                    key={invoice.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="font-medium">{invoice.number}</div>
                        <div className="text-sm text-gray-500">
                          {formatDate(invoice.created_at)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-left">
                        <div className="font-semibold">{formatPrice(invoice.amount)}</div>
                        {getStatusBadge(invoice.status)}
                      </div>
                      {invoice.pdf_url && (
                        <Button variant="ghost" size="sm" asChild>
                          <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                            <Download className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-gray-500">
                אין חשבוניות עדיין
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

