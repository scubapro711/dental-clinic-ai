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
  CloudQueue,
  Storage,
  Computer,
  Memory,
  AttachMoney,
} from '@mui/icons-material';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || API_CONFIG.BASE_URL;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

/**
 * Cost Dashboard - Track Infrastructure Costs
 * 
 * Features:
 * - GCP cost tracking
 * - Cost breakdown by service
 * - Cost per organization
 * - Cost trends
 * - Unit economics (cost per user, per conversation, etc.)
 */
const CostDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [costSummary, setCostSummary] = useState({
    total_cost: 0,
    by_service: [],
    by_organization: [],
    trends: [],
  });

  useEffect(() => {
    fetchCostData();
  }, []);

  const fetchCostData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Note: This is a placeholder implementation
      // In production, this would integrate with GCP Billing API
      // For now, we'll use mock data to demonstrate the UI

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock data
      const mockData = {
        total_cost: 4250.75,
        by_service: [
          { service: 'Cloud Run', cost: 1200.50, percentage: 28.2 },
          { service: 'Cloud SQL', cost: 950.25, percentage: 22.4 },
          { service: 'Cloud Storage', cost: 450.00, percentage: 10.6 },
          { service: 'Cloud Functions', cost: 380.00, percentage: 8.9 },
          { service: 'Vertex AI', cost: 720.00, percentage: 16.9 },
          { service: 'Other Services', cost: 550.00, percentage: 12.9 },
        ],
        by_organization: [
          { name: 'Dental Clinic A', cost: 450.00, users: 12, cost_per_user: 37.50 },
          { name: 'Dental Clinic B', cost: 380.00, users: 8, cost_per_user: 47.50 },
          { name: 'Dental Clinic C', cost: 320.00, users: 10, cost_per_user: 32.00 },
          { name: 'Dental Clinic D', cost: 290.00, users: 6, cost_per_user: 48.33 },
          { name: 'Dental Clinic E', cost: 250.00, users: 7, cost_per_user: 35.71 },
        ],
        trends: [
          { month: 'Jan', cost: 3200 },
          { month: 'Feb', cost: 3450 },
          { month: 'Mar', cost: 3680 },
          { month: 'Apr', cost: 3890 },
          { month: 'May', cost: 4050 },
          { month: 'Jun', cost: 4250 },
        ],
      };

      setCostSummary(mockData);

    } catch (err) {
      console.error('Error fetching cost data:', err);
      setError(err.response?.data?.detail || 'Failed to load cost data');
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

  // Calculate unit economics
  const totalOrgs = costSummary.by_organization.length;
  const totalUsers = costSummary.by_organization.reduce((sum, org) => sum + org.users, 0);
  const costPerOrg = totalOrgs > 0 ? costSummary.total_cost / totalOrgs : 0;
  const costPerUser = totalUsers > 0 ? costSummary.total_cost / totalUsers : 0;

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cost Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track infrastructure costs and unit economics
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          Note: Cost tracking integration with GCP Billing API is pending. Data shown is for demonstration purposes.
        </Alert>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AttachMoney color="primary" />
                <Typography variant="h6" ml={1}>
                  Total Cost
                </Typography>
              </Box>
              <Typography variant="h4">
                ${costSummary.total_cost.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                This month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <CloudQueue color="primary" />
                <Typography variant="h6" ml={1}>
                  Cost per Org
                </Typography>
              </Box>
              <Typography variant="h4">
                ${costPerOrg.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average per organization
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Computer color="primary" />
                <Typography variant="h6" ml={1}>
                  Cost per User
                </Typography>
              </Box>
              <Typography variant="h4">
                ${costPerUser.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average per user
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Memory color="primary" />
                <Typography variant="h6" ml={1}>
                  Growth
                </Typography>
              </Box>
              <Typography variant="h4" color="error.main">
                +32.8%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                vs last month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cost Trends */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cost Trends (Last 6 Months)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={costSummary.trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="cost"
                  stroke="#8884d8"
                  name="Total Cost"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Cost Breakdown */}
      <Grid container spacing={3} mb={3}>
        {/* By Service */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cost by Service
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={costSummary.by_service}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ service, percentage }) => `${service}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="cost"
                >
                  {costSummary.by_service.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Service Breakdown Table */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Service Breakdown
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Service</TableCell>
                    <TableCell align="right">Cost</TableCell>
                    <TableCell align="right">%</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {costSummary.by_service.map((service, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              borderRadius: '50%',
                              backgroundColor: COLORS[index % COLORS.length],
                              mr: 1,
                            }}
                          />
                          {service.service}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          ${service.cost.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label={`${service.percentage}%`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Cost by Organization */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Cost by Organization
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Organization</TableCell>
                <TableCell align="right">Total Cost</TableCell>
                <TableCell align="right">Users</TableCell>
                <TableCell align="right">Cost per User</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {costSummary.by_organization.map((org, index) => (
                <TableRow key={index}>
                  <TableCell>{org.name}</TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="medium">
                      ${org.cost.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{org.users}</TableCell>
                  <TableCell align="right">
                    <Chip
                      label={`$${org.cost_per_user.toFixed(2)}`}
                      size="small"
                      color={org.cost_per_user > 40 ? 'error' : 'success'}
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Unit Economics */}
      <Grid container spacing={3} mt={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Unit Economics
            </Typography>
            <Grid container spacing={3} mt={1}>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Cost per Organization
                  </Typography>
                  <Typography variant="h5">
                    ${costPerOrg.toFixed(2)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Cost per User
                  </Typography>
                  <Typography variant="h5">
                    ${costPerUser.toFixed(2)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Cost per Conversation (Est.)
                  </Typography>
                  <Typography variant="h5">
                    $0.15
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Gross Margin
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    68%
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CostDashboard;

