import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import API_CONFIG from '@/config/api';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  CreditCard,
  Cancel,
} from '@mui/icons-material';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || API_CONFIG.BASE_URL;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

/**
 * Revenue Dashboard - Track Revenue and Billing
 * 
 * Features:
 * - MRR/ARR tracking
 * - Revenue trends
 * - Subscriptions breakdown
 * - Payments summary
 * - Growth metrics
 */
const RevenueDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [revenueSummary, setRevenueSummary] = useState(null);
  const [revenueTrends, setRevenueTrends] = useState([]);
  const [subscriptionsSummary, setSubscriptionsSummary] = useState(null);
  const [paymentsSummary, setPaymentsSummary] = useState(null);
  const [recentPayments, setRecentPayments] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch revenue summary
      const revenueSummaryRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/revenue/summary`,
        { headers }
      );
      setRevenueSummary(revenueSummaryRes.data);

      // Fetch revenue trends (last 12 months)
      const trendsRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/revenue/trends`,
        {
          headers,
          params: { granularity: 'monthly' },
        }
      );
      setRevenueTrends(trendsRes.data);

      // Fetch subscriptions summary
      const subscriptionsRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/subscriptions/summary`,
        { headers }
      );
      setSubscriptionsSummary(subscriptionsRes.data);

      // Fetch payments summary
      const paymentsRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/payments/summary`,
        { headers }
      );
      setPaymentsSummary(paymentsRes.data);

      // Fetch recent payments
      const recentPaymentsRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/payments`,
        {
          headers,
          params: { limit: 10 },
        }
      );
      setRecentPayments(recentPaymentsRes.data.payments);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Prepare subscription breakdown data for pie chart
  const subscriptionData = subscriptionsSummary
    ? [
        { name: 'Active', value: subscriptionsSummary.active },
        { name: 'Trial', value: subscriptionsSummary.trial },
        { name: 'Past Due', value: subscriptionsSummary.past_due },
        { name: 'Canceled', value: subscriptionsSummary.canceled },
      ]
    : [];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Revenue Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track revenue, subscriptions, and payments
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AttachMoney color="primary" />
                <Typography variant="h6" ml={1}>
                  MRR
                </Typography>
              </Box>
              <Typography variant="h4">
                ${revenueSummary?.mrr?.toLocaleString() || '0'}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                {revenueSummary?.growth_rate >= 0 ? (
                  <TrendingUp fontSize="small" color="success" />
                ) : (
                  <TrendingDown fontSize="small" color="error" />
                )}
                <Typography
                  variant="body2"
                  color={revenueSummary?.growth_rate >= 0 ? 'success.main' : 'error.main'}
                  ml={0.5}
                >
                  {revenueSummary?.growth_rate >= 0 ? '+' : ''}
                  {revenueSummary?.growth_rate?.toFixed(1)}% vs last month
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp color="primary" />
                <Typography variant="h6" ml={1}>
                  ARR
                </Typography>
              </Box>
              <Typography variant="h4">
                ${revenueSummary?.arr?.toLocaleString() || '0'}
              </Typography>
              <Typography variant="body2" color="text.secondary" mt={1}>
                Annual Recurring Revenue
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <CreditCard color="primary" />
                <Typography variant="h6" ml={1}>
                  Successful Payments
                </Typography>
              </Box>
              <Typography variant="h4">
                {paymentsSummary?.successful_count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary" mt={1}>
                ${paymentsSummary?.total_amount?.toLocaleString() || '0'} total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Cancel color="error" />
                <Typography variant="h6" ml={1}>
                  Churn Rate
                </Typography>
              </Box>
              <Typography variant="h4">
                {revenueSummary?.churn_rate?.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary" mt={1}>
                Monthly churn
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Revenue Trends Chart */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Trends (Last 12 Months)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short' })}
                />
                <YAxis />
                <Tooltip
                  formatter={(value) => `$${value.toLocaleString()}`}
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <Legend />
                <Line type="monotone" dataKey="mrr" stroke="#8884d8" name="MRR" strokeWidth={2} />
                <Line type="monotone" dataKey="arr" stroke="#82ca9d" name="ARR" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Subscriptions and Payments */}
      <Grid container spacing={3} mb={3}>
        {/* Subscriptions Breakdown */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Subscriptions Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={subscriptionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {subscriptionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <Box mt={2}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Active
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {subscriptionsSummary?.active || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Trial
                  </Typography>
                  <Typography variant="h6" color="info.main">
                    {subscriptionsSummary?.trial || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Past Due
                  </Typography>
                  <Typography variant="h6" color="warning.main">
                    {subscriptionsSummary?.past_due || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Canceled
                  </Typography>
                  <Typography variant="h6" color="error.main">
                    {subscriptionsSummary?.canceled || 0}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>

        {/* Payments Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Payments Summary (This Month)
            </Typography>
            <Box mt={3}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      Total Amount
                    </Typography>
                    <Typography variant="h6">
                      ${paymentsSummary?.total_amount?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      Stripe Fees
                    </Typography>
                    <Typography variant="h6" color="error.main">
                      -${paymentsSummary?.stripe_fees?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      Net Revenue
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      ${paymentsSummary?.net_revenue?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                    <Typography variant="body2" color="text.secondary">
                      Successful
                    </Typography>
                    <Chip label={paymentsSummary?.successful_count || 0} color="success" size="small" />
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      Failed
                    </Typography>
                    <Chip label={paymentsSummary?.failed_count || 0} color="error" size="small" />
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      Refunded
                    </Typography>
                    <Chip label={paymentsSummary?.refunded_count || 0} color="warning" size="small" />
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Payments */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Payments
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Organization</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Stripe ID</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentPayments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No recent payments
                  </TableCell>
                </TableRow>
              ) : (
                recentPayments.map((payment) => (
                  <TableRow key={payment.id}>
                    <TableCell>{payment.organization_name}</TableCell>
                    <TableCell>
                      ${payment.amount} {payment.currency}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={payment.status}
                        color={
                          payment.status === 'succeeded'
                            ? 'success'
                            : payment.status === 'failed'
                            ? 'error'
                            : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(payment.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {payment.stripe_payment_intent_id?.substring(0, 20)}...
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default RevenueDashboard;

