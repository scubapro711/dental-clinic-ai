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
  Tabs,
  Tab,
} from '@mui/material';
import {
  Security,
  Warning,
  CheckCircle,
  TrendingUp,
} from '@mui/icons-material';
import HarperDashboard from '../../components/compliance/HarperDashboard';
import ComplianceAlerts from '../../components/compliance/ComplianceAlerts';
import ComplianceMetrics from '../../components/compliance/ComplianceMetrics';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Super Admin Compliance Dashboard
 * 
 * Provides organization-wide compliance overview:
 * - Aggregate compliance scores across all clinics
 * - Critical alerts from all organizations
 * - Compliance trends
 * - Harper AI assistant for compliance questions
 */
const ComplianceDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [complianceScore, setComplianceScore] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch compliance score
      const scoreResponse = await axios.get(
        `${API_BASE_URL}/api/v1/compliance/score`,
        { headers }
      );
      setComplianceScore(scoreResponse.data);

      // Fetch alerts
      const alertsResponse = await axios.get(
        `${API_BASE_URL}/api/v1/compliance/alerts`,
        { headers, params: { status: 'open', limit: 10 } }
      );
      setAlerts(alertsResponse.data.alerts || []);

      // Fetch metrics
      const metricsResponse = await axios.get(
        `${API_BASE_URL}/api/v1/compliance/metrics`,
        { headers, params: { days: 30 } }
      );
      setMetrics(metricsResponse.data);

    } catch (err) {
      console.error('Error fetching compliance data:', err);
      setError(err.response?.data?.detail || 'Failed to load compliance data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
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

  // Calculate summary stats
  const criticalAlerts = (alerts || []).filter(a => a.severity === 'critical').length;
  const highAlerts = (alerts || []).filter(a => a.severity === 'high').length;
  const overallScore = complianceScore?.overall_score || 0;

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
          <Security sx={{ mr: 1, fontSize: 32 }} />
          HIPAA Compliance Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Organization-wide compliance monitoring and management
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Overall Compliance
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {overallScore}%
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 48, color: overallScore >= 90 ? 'success.main' : 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Critical Alerts
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: criticalAlerts > 0 ? 'error.main' : 'success.main' }}>
                    {criticalAlerts}
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 48, color: criticalAlerts > 0 ? 'error.main' : 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    High Priority
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: highAlerts > 0 ? 'warning.main' : 'success.main' }}>
                    {highAlerts}
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 48, color: highAlerts > 0 ? 'warning.main' : 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    30-Day Trend
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                    +5%
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 48, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="compliance tabs">
          <Tab label="Overview" />
          <Tab label="Alerts" />
          <Tab label="Metrics & Trends" />
          <Tab label="Ask Harper" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <HarperDashboard />
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <ComplianceAlerts />
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <ComplianceMetrics />
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Ask Harper - HIPAA Compliance Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Harper is your AI-powered HIPAA compliance assistant. Ask questions about regulations, 
                policies, procedures, or get help with compliance issues.
              </Typography>
              {/* Harper Chat will be embedded here */}
              <Box sx={{ mt: 2 }}>
                <Alert severity="info">
                  Harper chat interface will be integrated here. You can ask questions about:
                  <ul>
                    <li>HIPAA Privacy and Security Rules</li>
                    <li>Business Associate Agreements (BAAs)</li>
                    <li>Protected Health Information (PHI) handling</li>
                    <li>Breach notification procedures</li>
                    <li>Patient rights and compliance requirements</li>
                  </ul>
                </Alert>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default ComplianceDashboard;

