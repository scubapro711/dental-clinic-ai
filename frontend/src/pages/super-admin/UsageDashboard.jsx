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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import API_CONFIG from '@/config/api';
import {
  Chat,
  Event,
  People,
  Storage,
  Api,
  Telegram,
  Sms,
  Email,
} from '@mui/icons-material';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || API_CONFIG.BASE_URL;

/**
 * Usage Dashboard - Track Platform Usage
 * 
 * Features:
 * - Overall usage summary
 * - Usage by organization
 * - Usage trends
 * - Metric type filtering
 */
const UsageDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usageSummary, setUsageSummary] = useState(null);
  const [usageByOrg, setUsageByOrg] = useState([]);
  const [usageTrends, setUsageTrends] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('ai_conversations');

  const metricTypes = [
    { value: 'ai_conversations', label: 'AI Conversations', icon: Chat },
    { value: 'appointments_booked', label: 'Appointments Booked', icon: Event },
    { value: 'patients_added', label: 'Patients Added', icon: People },
    { value: 'active_users', label: 'Active Users', icon: People },
    { value: 'storage_used_mb', label: 'Storage Used (MB)', icon: Storage },
    { value: 'api_calls', label: 'API Calls', icon: Api },
    { value: 'telegram_messages', label: 'Telegram Messages', icon: Telegram },
    { value: 'sms_sent', label: 'SMS Sent', icon: Sms },
    { value: 'emails_sent', label: 'Emails Sent', icon: Email },
  ];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (selectedMetric) {
      fetchUsageTrends();
      fetchUsageByOrg();
    }
  }, [selectedMetric]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch usage summary
      const summaryRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/usage/summary`,
        { headers }
      );
      setUsageSummary(summaryRes.data);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageTrends = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const trendsRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/usage/trends`,
        {
          headers,
          params: { metric_type: selectedMetric },
        }
      );
      setUsageTrends(trendsRes.data.trends || []);
    } catch (err) {
      console.error('Error fetching usage trends:', err);
    }
  };

  const fetchUsageByOrg = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const byOrgRes = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/usage/by-organization`,
        {
          headers,
          params: { metric_type: selectedMetric, limit: 10 },
        }
      );
      setUsageByOrg(byOrgRes.data || []);
    } catch (err) {
      console.error('Error fetching usage by organization:', err);
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

  const getMetricIcon = (metricType) => {
    const metric = metricTypes.find((m) => m.value === metricType);
    if (!metric) return null;
    const IconComponent = metric.icon;
    return <IconComponent />;
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Usage Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor platform usage across all organizations
        </Typography>
      </Box>

      {/* Overall Usage Summary */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Chat color="primary" />
                <Typography variant="h6" ml={1}>
                  AI Conversations
                </Typography>
              </Box>
              <Typography variant="h4">
                {usageSummary?.total_conversations?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Event color="primary" />
                <Typography variant="h6" ml={1}>
                  Appointments
                </Typography>
              </Box>
              <Typography variant="h4">
                {usageSummary?.total_appointments?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <People color="primary" />
                <Typography variant="h6" ml={1}>
                  Patients Added
                </Typography>
              </Box>
              <Typography variant="h4">
                {usageSummary?.total_patients?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Storage color="primary" />
                <Typography variant="h6" ml={1}>
                  Storage Used
                </Typography>
              </Box>
              <Typography variant="h4">
                {(usageSummary?.total_storage_mb / 1024)?.toFixed(1) || 0} GB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total across all orgs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metric Selector */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <FormControl fullWidth>
          <InputLabel>Select Metric</InputLabel>
          <Select
            value={selectedMetric}
            label="Select Metric"
            onChange={(e) => setSelectedMetric(e.target.value)}
          >
            {metricTypes.map((metric) => (
              <MenuItem key={metric.value} value={metric.value}>
                <Box display="flex" alignItems="center">
                  <Box component={metric.icon} sx={{ mr: 1 }} />
                  {metric.label}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Paper>

      {/* Usage Trends Chart */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Usage Trends - {metricTypes.find((m) => m.value === selectedMetric)?.label}
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={usageTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  name={metricTypes.find((m) => m.value === selectedMetric)?.label}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Top Organizations by Usage */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Organizations - {metricTypes.find((m) => m.value === selectedMetric)?.label}
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={usageByOrg.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="organization_name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Usage by Organization
            </Typography>
            <TableContainer sx={{ maxHeight: 300 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Organization</TableCell>
                    <TableCell align="right">Usage</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {usageByOrg.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={2} align="center">
                        No usage data available
                      </TableCell>
                    </TableRow>
                  ) : (
                    usageByOrg.map((org, index) => (
                      <TableRow key={index}>
                        <TableCell>{org.organization_name}</TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight="medium">
                            {org.value.toLocaleString()}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Communication Metrics */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Telegram color="primary" />
                <Typography variant="h6" ml={1}>
                  Telegram Messages
                </Typography>
              </Box>
              <Typography variant="h4">
                {usageSummary?.total_telegram_messages?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Sms color="primary" />
                <Typography variant="h6" ml={1}>
                  SMS Sent
                </Typography>
              </Box>
              <Typography variant="h4">
                {usageSummary?.total_sms_sent?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Email color="primary" />
                <Typography variant="h6" ml={1}>
                  Emails Sent
                </Typography>
              </Box>
              <Typography variant="h4">
                {usageSummary?.total_emails_sent?.toLocaleString() || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default UsageDashboard;

