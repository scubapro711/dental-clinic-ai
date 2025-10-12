/**
 * Financial Dashboard Component
 * 
 * Displays comprehensive financial overview for clinic owners/admins.
 * Integrates with Marcus (CFO Agent) for AI-powered insights.
 * 
 * Reference: Phase 3 - Marcus Expansion
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Receipt,
  Warning,
  Refresh,
  Chat,
  Download,
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

interface FinancialSummary {
  period: {
    from: string;
    to: string;
  };
  revenue: {
    total_revenue: number;
    invoice_count: number;
    average_invoice: number;
  };
  outstanding: {
    total: number;
    invoice_count: number;
  };
  payments: {
    total_collected: number;
    payment_count: number;
  };
  top_treatments: Array<{
    product_name: string;
    revenue: number;
    quantity: number;
  }>;
}

export const FinancialDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [period, setPeriod] = useState<'week' | 'month' | 'quarter' | 'year'>('month');
  const [showMarcusChat, setShowMarcusChat] = useState(false);

  useEffect(() => {
    fetchFinancialSummary();
  }, [period]);

  const fetchFinancialSummary = async () => {
    setLoading(true);
    setError(null);

    try {
      // Calculate date range based on period
      const to = new Date().toISOString().split('T')[0];
      const from = new Date();
      
      switch (period) {
        case 'week':
          from.setDate(from.getDate() - 7);
          break;
        case 'month':
          from.setMonth(from.getMonth() - 1);
          break;
        case 'quarter':
          from.setMonth(from.getMonth() - 3);
          break;
        case 'year':
          from.setFullYear(from.getFullYear() - 1);
          break;
      }

      const fromStr = from.toISOString().split('T')[0];

      // Call backend API
      const response = await fetch(
        `/api/v1/financial/summary?date_from=${fromStr}&date_to=${to}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch financial summary');
      }

      const data = await response.json();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
    }).format(amount);
  };

  const calculateCollectionRate = () => {
    if (!summary) return 0;
    const total = summary.revenue.total_revenue + summary.outstanding.total;
    if (total === 0) return 0;
    return (summary.revenue.total_revenue / total) * 100;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={fetchFinancialSummary}>
          נסה שוב
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  if (!summary) {
    return <Alert severity="info">אין נתונים פיננסיים להצגה</Alert>;
  }

  const collectionRate = calculateCollectionRate();

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          💰 דשבורד פיננסי
        </Typography>
        <Box display="flex" gap={2}>
          <Tooltip title="רענן נתונים">
            <IconButton onClick={fetchFinancialSummary}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="שוחח עם Marcus (CFO)">
            <Button
              variant="contained"
              startIcon={<Chat />}
              onClick={() => setShowMarcusChat(true)}
            >
              שאל את Marcus
            </Button>
          </Tooltip>
        </Box>
      </Box>

      {/* Period Selector */}
      <Box mb={3} display="flex" gap={1}>
        {(['week', 'month', 'quarter', 'year'] as const).map((p) => (
          <Chip
            key={p}
            label={
              p === 'week' ? 'שבוע' :
              p === 'month' ? 'חודש' :
              p === 'quarter' ? 'רבעון' :
              'שנה'
            }
            color={period === p ? 'primary' : 'default'}
            onClick={() => setPeriod(p)}
          />
        ))}
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        {/* Revenue */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    הכנסות
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(summary.revenue.total_revenue)}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {summary.revenue.invoice_count} חשבוניות
                  </Typography>
                </Box>
                <TrendingUp color="success" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Collected */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    נגבה
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(summary.payments.total_collected)}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {summary.payments.payment_count} תשלומים
                  </Typography>
                </Box>
                <AttachMoney color="primary" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Outstanding */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    חובות
                  </Typography>
                  <Typography variant="h5" color="warning.main">
                    {formatCurrency(summary.outstanding.total)}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {summary.outstanding.invoice_count} חשבוניות
                  </Typography>
                </Box>
                <Warning color="warning" fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Collection Rate */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    אחוז גבייה
                  </Typography>
                  <Typography variant="h5">
                    {collectionRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    מתוך סה"כ חשבוניות
                  </Typography>
                </Box>
                <Receipt color={collectionRate > 80 ? 'success' : 'warning'} fontSize="large" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Top Treatments */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🏆 טיפולים מובילים
          </Typography>
          <Divider sx={{ mb: 2 }} />
          {summary.top_treatments.length > 0 ? (
            <Grid container spacing={2}>
              {summary.top_treatments.map((treatment, index) => (
                <Grid item xs={12} key={index}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="body1">
                        {index + 1}. {treatment.product_name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        כמות: {treatment.quantity}
                      </Typography>
                    </Box>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(treatment.revenue)}
                    </Typography>
                  </Box>
                  {index < summary.top_treatments.length - 1 && <Divider sx={{ mt: 1 }} />}
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography color="textSecondary">אין נתונים על טיפולים</Typography>
          )}
        </CardContent>
      </Card>

      {/* Marcus Chat Modal - Placeholder */}
      {showMarcusChat && (
        <Box
          position="fixed"
          bottom={20}
          right={20}
          width={400}
          height={500}
          bgcolor="background.paper"
          boxShadow={3}
          borderRadius={2}
          p={2}
          zIndex={1000}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">💼 Marcus - CFO</Typography>
            <Button size="small" onClick={() => setShowMarcusChat(false)}>
              סגור
            </Button>
          </Box>
          <Typography color="textSecondary">
            צ'אט עם Marcus יהיה זמין בקרוב...
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default FinancialDashboard;

