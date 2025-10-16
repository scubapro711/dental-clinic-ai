import React, { useState, useEffect } from 'react';
import { 
  DollarSign, TrendingUp, Users, Building2, Calendar,
  CheckCircle, Clock, AlertCircle, Search, Filter,
  Download, Eye, ArrowLeft, Sparkles, Crown, RefreshCw
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';

/**
 * Billing Dashboard Component (Super Admin)
 * 
 * Comprehensive view of all clinic subscriptions and billing.
 * Features:
 * - Revenue overview
 * - Active subscriptions
 * - Trial conversions
 * - Churn rate
 * - Subscription list with filters
 * - Individual clinic details
 * - Invoice management
 */
export default function BillingDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [filteredSubscriptions, setFilteredSubscriptions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [planFilter, setPlanFilter] = useState('all');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    filterSubscriptions();
  }, [searchTerm, statusFilter, planFilter, subscriptions]);

  const fetchDashboardData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      // Fetch stats
      const statsResponse = await fetch(`${API_BASE_URL}/api/v1/admin/billing/stats`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch all subscriptions
      const subsResponse = await fetch(`${API_BASE_URL}/api/v1/admin/billing/subscriptions`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (subsResponse.ok) {
        const subsData = await subsResponse.json();
        setSubscriptions(subsData.subscriptions || []);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const filterSubscriptions = () => {
    let filtered = [...subscriptions];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(sub => 
        sub.organization_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sub.organization_id?.toString().includes(searchTerm)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(sub => sub.status === statusFilter);
    }

    // Plan filter
    if (planFilter !== 'all') {
      filtered = filtered.filter(sub => sub.plan_id?.toString() === planFilter);
    }

    setFilteredSubscriptions(filtered);
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
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('he-IL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      minimumFractionDigits: 0
    }).format(price || 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">טוען נתוני חיוב...</p>
        </div>
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
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">לוח בקרת חיוב</h1>
                <p className="text-sm text-gray-500">ניהול מנויים והכנסות</p>
              </div>
            </div>
            <Button 
              onClick={() => fetchDashboardData(true)} 
              disabled={refreshing}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 ml-2 ${refreshing ? 'animate-spin' : ''}`} />
              רענן
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">הכנסה חודשית</CardTitle>
              <DollarSign className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatPrice(stats?.monthly_revenue || 0)}</div>
              <p className="text-xs text-gray-500">
                <TrendingUp className="h-3 w-3 inline ml-1" />
                +{stats?.revenue_growth || 0}% מהחודש שעבר
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">מנויים פעילים</CardTitle>
              <CheckCircle className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.active_subscriptions || 0}</div>
              <p className="text-xs text-gray-500">
                {stats?.trial_subscriptions || 0} בניסיון
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">שיעור המרה</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.conversion_rate || 0}%</div>
              <p className="text-xs text-gray-500">מניסיון לתשלום</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">נטישה חודשית</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.churn_rate || 0}%</div>
              <p className="text-xs text-gray-500">
                {stats?.canceled_this_month || 0} ביטולים החודש
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Revenue Chart Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>מגמת הכנסות</CardTitle>
            <CardDescription>הכנסה חודשית ב-6 החודשים האחרונים</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <p className="text-gray-500">תרשים הכנסות (יישום עתידי)</p>
            </div>
          </CardContent>
        </Card>

        {/* Subscriptions Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>מנויים</CardTitle>
                <CardDescription>כל המנויים במערכת</CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 ml-2" />
                ייצוא
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Filters */}
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="חפש מרפאה..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pr-10"
                  />
                </div>
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="סטטוס" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">כל הסטטוסים</SelectItem>
                  <SelectItem value="active">פעיל</SelectItem>
                  <SelectItem value="trialing">ניסיון</SelectItem>
                  <SelectItem value="past_due">באיחור</SelectItem>
                  <SelectItem value="canceled">מבוטל</SelectItem>
                </SelectContent>
              </Select>
              <Select value={planFilter} onValueChange={setPlanFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="תוכנית" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">כל התוכניות</SelectItem>
                  {stats?.plans?.map(plan => (
                    <SelectItem key={plan.id} value={plan.id.toString()}>
                      {plan.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Table */}
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">מרפאה</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">תוכנית</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">סטטוס</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">מחיר</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">תאריך התחלה</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">חידוש</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">פעולות</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredSubscriptions.length > 0 ? (
                    filteredSubscriptions.map((sub) => (
                      <tr key={sub.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Building2 className="h-4 w-4 text-gray-400" />
                            <div>
                              <div className="font-medium">{sub.organization_name || 'Unknown'}</div>
                              <div className="text-xs text-gray-500">ID: {sub.organization_id}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {sub.plan_name?.toLowerCase().includes('enterprise') && (
                              <Crown className="h-4 w-4 text-purple-600" />
                            )}
                            <span className="text-sm">{sub.plan_name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {getStatusBadge(sub.status)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium">{formatPrice(sub.monthly_price)}</div>
                          {sub.discount_percentage > 0 && (
                            <div className="text-xs text-green-600">
                              -{sub.discount_percentage}% הנחה
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {formatDate(sub.start_date)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {formatDate(sub.current_period_end)}
                        </td>
                        <td className="px-4 py-3">
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => navigate(`/admin/billing/subscription/${sub.id}`)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                        לא נמצאו מנויים
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Placeholder */}
            {filteredSubscriptions.length > 0 && (
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-500">
                  מציג {filteredSubscriptions.length} מתוך {subscriptions.length} מנויים
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

