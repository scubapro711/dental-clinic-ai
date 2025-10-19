import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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
} from '@mui/material';
import {
  TrendingUp,
  Business,
  AttachMoney,
  People,
  Assessment,
  CloudQueue,
} from '@mui/icons-material';
import SecurityIncidentsWidget from '../../components/super-admin/SecurityIncidentsWidget';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Super Admin Dashboard - Main Overview
 * 
 * Provides a high-level overview of the entire platform:
 * - Revenue metrics (MRR, ARR, growth)
 * - Organization stats
 * - Usage metrics
 * - Cost tracking
 * - Quick actions
 */
const SuperAdminDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [revenueSummary, setRevenueSummary] = useState(null);
  const [subscriptionsSummary, setSubscriptionsSummary] = useState(null);
  const [usageSummary, setUsageSummary] = useState(null);

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
      const revenueResponse = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/revenue/summary`,
        { headers }
      );
      setRevenueSummary(revenueResponse.data);

      // Fetch subscriptions summary
      const subscriptionsResponse = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/subscriptions/summary`,
        { headers }
      );
      setSubscriptionsSummary(subscriptionsResponse.data);

      // Fetch usage summary
      const usageResponse = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/usage/summary`,
        { headers }
      );
      setUsageSummary(usageResponse.data);

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
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Super Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Platform overview and management
        </Typography>
      </Box>

      {/* Revenue Metrics */}
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
              <Typography variant="body2" color="text.secondary">
                Monthly Recurring Revenue
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <TrendingUp
                  fontSize="small"
                  color={revenueSummary?.growth_rate >= 0 ? 'success' : 'error'}
                />
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
              <Typography variant="body2" color="text.secondary">
                Annual Recurring Revenue
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Business color="primary" />
                <Typography variant="h6" ml={1}>
                  Active Clinics
                </Typography>
              </Box>
              <Typography variant="h4">
                {subscriptionsSummary?.active || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {subscriptionsSummary?.trial || 0} in trial
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Assessment color="primary" />
                <Typography variant="h6" ml={1}>
                  Churn Rate
                </Typography>
              </Box>
              <Typography variant="h4">
                {revenueSummary?.churn_rate?.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monthly churn
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Usage Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Platform Usage (Last 30 Days)
            </Typography>
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    AI Conversations
                  </Typography>
                  <Typography variant="h5">
                    {usageSummary?.total_conversations?.toLocaleString() || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Appointments Booked
                  </Typography>
                  <Typography variant="h5">
                    {usageSummary?.total_appointments?.toLocaleString() || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Patients Added
                  </Typography>
                  <Typography variant="h5">
                    {usageSummary?.total_patients?.toLocaleString() || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Active Users
                  </Typography>
                  <Typography variant="h5">
                    {usageSummary?.total_users?.toLocaleString() || 0}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Subscriptions Breakdown
            </Typography>
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Active
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {subscriptionsSummary?.active || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Trial
                  </Typography>
                  <Typography variant="h5" color="info.main">
                    {subscriptionsSummary?.trial || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Past Due
                  </Typography>
                  <Typography variant="h5" color="warning.main">
                    {subscriptionsSummary?.past_due || 0}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Canceled
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    {subscriptionsSummary?.canceled || 0}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Security Incidents Widget */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <SecurityIncidentsWidget />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/organizations" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Business color="primary" fontSize="large" />
                  <Typography variant="h6" ml={2}>
                    Manage Organizations
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  View and manage all clinics
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/revenue" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <TrendingUp color="primary" fontSize="large" />
                  <Typography variant="h6" ml={2}>
                    Revenue Analytics
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Track revenue and growth
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/usage" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <People color="primary" fontSize="large" />
                  <Typography variant="h6" ml={2}>
                    Usage Tracking
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Monitor platform usage
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/costs" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <CloudQueue color="primary" fontSize="large" />
                  <Typography variant="h6" ml={2}>
                    Cost Tracking
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Monitor infrastructure costs
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/pilot-applications" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="h3" component="span">🚀</Typography>
                  <Typography variant="h6" ml={2}>
                    Pilot Applications
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Review and manage pilot requests
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/analytics" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Assessment color="primary" fontSize="large" />
                  <Typography variant="h6" ml={2}>
                    Analytics & Insights
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Cohort analysis and predictions
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/compliance" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="h3" component="span">🛡️</Typography>
                  <Typography variant="h6" ml={2}>
                    HIPAA Compliance
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Monitor compliance and ask Harper
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/hipaa/baa-management" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="h3" component="span">🔒</Typography>
                  <Typography variant="h6" ml={2}>
                    BAA Management
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Manage Business Associate Agreements
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Link to="/super-admin/hipaa/data-retention" style={{ textDecoration: 'none' }}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 6 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Typography variant="h3" component="span">🗄️</Typography>
                  <Typography variant="h6" ml={2}>
                    Data Retention
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Monitor data retention compliance
                </Typography>
              </CardContent>
            </Card>
          </Link>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SuperAdminDashboard;

