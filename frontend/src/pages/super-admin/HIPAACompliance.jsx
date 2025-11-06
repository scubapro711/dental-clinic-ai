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
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security,
  PrivacyTip,
  Assignment,
  Warning,
  CheckCircle,
  Edit,
  Visibility,
  Download,
  Refresh,
} from '@mui/icons-material';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * HIPAA Compliance Management Component
 * 
 * Allows Super Admin to:
 * - View and update Security/Privacy Officers
 * - Monitor compliance status
 * - View incident reports
 * - Access audit logs
 * - Download compliance reports
 */
const HIPAACompliance = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Officers
  const [officers, setOfficers] = useState({
    security_officer: {
      name: 'Eran Sarfaty',
      title: 'CTO & Lead Developer',
      email: 'eran@dentaflow.co.il',
      phone: '+972-XX-XXX-XXXX',
      assigned_date: '2025-10-18',
    },
    privacy_officer: {
      name: 'Eran Sarfaty',
      title: 'CTO & Lead Developer',
      email: 'eran@dentaflow.co.il',
      phone: '+972-XX-XXX-XXXX',
      assigned_date: '2025-10-18',
    },
  });
  const [editOfficerDialog, setEditOfficerDialog] = useState(false);
  const [editingOfficer, setEditingOfficer] = useState(null);
  
  // Compliance Status
  const [complianceStatus, setComplianceStatus] = useState({
    overall_score: 85,
    technical_safeguards: 100,
    administrative_safeguards: 75,
    physical_safeguards: 100,
    breach_notification: 20,
    last_audit: '2025-10-18',
    next_audit: '2026-01-18',
  });
  
  // Incidents
  const [incidents, setIncidents] = useState([]);
  
  // Audit Logs
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch officers (mock for now)
      // const officersResponse = await axios.get(
      //   `${API_BASE_URL}/api/v1/super-admin/hipaa/officers`,
      //   { headers }
      // );
      // setOfficers(officersResponse.data);

      // Fetch compliance status (mock for now)
      // const statusResponse = await axios.get(
      //   `${API_BASE_URL}/api/v1/super-admin/hipaa/status`,
      //   { headers }
      // );
      // setComplianceStatus(statusResponse.data);

      // Fetch incidents
      const incidentsResponse = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/incidents`,
        { headers }
      ).catch(() => ({ data: [] }));
      setIncidents(incidentsResponse.data || []);

      // Fetch audit logs
      const auditResponse = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/audit-logs?limit=50`,
        { headers }
      ).catch(() => ({ data: [] }));
      setAuditLogs(auditResponse.data || []);

    } catch (err) {
      console.error('Error fetching compliance data:', err);
      setError(err.response?.data?.detail || 'Failed to load compliance data');
    } finally {
      setLoading(false);
    }
  };

  const handleEditOfficer = (type) => {
    setEditingOfficer({ type, ...officers[type] });
    setEditOfficerDialog(true);
  };

  const handleSaveOfficer = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Save to backend (mock for now)
      // await axios.put(
      //   `${API_BASE_URL}/api/v1/super-admin/hipaa/officers/${editingOfficer.type}`,
      //   editingOfficer,
      //   { headers }
      // );

      // Update local state
      setOfficers({
        ...officers,
        [editingOfficer.type]: { ...editingOfficer },
      });

      setEditOfficerDialog(false);
      setEditingOfficer(null);
    } catch (err) {
      console.error('Error saving officer:', err);
      setError(err.response?.data?.detail || 'Failed to save officer');
    }
  };

  const handleDownloadReport = (reportType) => {
    // Download compliance report
    const token = localStorage.getItem('token');
    window.open(
      `${API_BASE_URL}/api/v1/super-admin/hipaa/reports/${reportType}?token=${token}`,
      '_blank'
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
          HIPAA Compliance Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage HIPAA compliance, officers, incidents, and audit logs
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Officers" icon={<PrivacyTip />} iconPosition="start" />
          <Tab label="Compliance Status" icon={<CheckCircle />} iconPosition="start" />
          <Tab label="Incidents" icon={<Warning />} iconPosition="start" />
          <Tab label="Audit Logs" icon={<Assignment />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Tab 0: Officers */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Security Officer */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Security Officer
                  </Typography>
                  <IconButton onClick={() => handleEditOfficer('security_officer')}>
                    <Edit />
                  </IconButton>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Responsible for implementing and maintaining security safeguards
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">Name:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.security_officer.name}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Title:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.security_officer.title}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Email:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.security_officer.email}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Phone:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.security_officer.phone}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Assigned:</Typography>
                  <Typography variant="body1">{officers.security_officer.assigned_date}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Privacy Officer */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    <PrivacyTip sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Privacy Officer
                  </Typography>
                  <IconButton onClick={() => handleEditOfficer('privacy_officer')}>
                    <Edit />
                  </IconButton>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Responsible for privacy policies and breach notification
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">Name:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.privacy_officer.name}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Title:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.privacy_officer.title}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Email:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.privacy_officer.email}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Phone:</Typography>
                  <Typography variant="body1" gutterBottom>{officers.privacy_officer.phone}</Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 1 }}>Assigned:</Typography>
                  <Typography variant="body1">{officers.privacy_officer.assigned_date}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Documentation */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  HIPAA Documentation
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<Download />}
                      onClick={() => handleDownloadReport('privacy-policy')}
                    >
                      Privacy Policy
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<Download />}
                      onClick={() => handleDownloadReport('incident-response')}
                    >
                      Incident Response Plan
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<Download />}
                      onClick={() => handleDownloadReport('disaster-recovery')}
                    >
                      DR Runbook
                    </Button>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<Download />}
                      onClick={() => handleDownloadReport('baa-template')}
                    >
                      BAA Template
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 1: Compliance Status */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {/* Overall Score */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Overall Compliance Score</Typography>
                  <Chip 
                    label={`${complianceStatus.overall_score}%`} 
                    color={complianceStatus.overall_score >= 80 ? 'success' : 'warning'}
                    sx={{ fontSize: '1.2rem', fontWeight: 'bold' }}
                  />
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={complianceStatus.overall_score} 
                  sx={{ height: 10, borderRadius: 5 }}
                  color={complianceStatus.overall_score >= 80 ? 'success' : 'warning'}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                  <Typography variant="caption">Last Audit: {complianceStatus.last_audit}</Typography>
                  <Typography variant="caption">Next Audit: {complianceStatus.next_audit}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Safeguards Breakdown */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Technical Safeguards</Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Score</Typography>
                    <Typography variant="body2" fontWeight="bold">{complianceStatus.technical_safeguards}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={complianceStatus.technical_safeguards} 
                    color="success"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Encryption (at rest & in transit)<br/>
                  ✅ Access controls & authentication<br/>
                  ✅ Audit logs & monitoring<br/>
                  ✅ Transmission security
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Administrative Safeguards</Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Score</Typography>
                    <Typography variant="body2" fontWeight="bold">{complianceStatus.administrative_safeguards}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={complianceStatus.administrative_safeguards} 
                    color="warning"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Security/Privacy Officers assigned<br/>
                  ✅ Risk assessment documented<br/>
                  ⚠️ DR plan (needs testing)<br/>
                  ❌ BAA with all vendors (pending)
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Physical Safeguards</Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Score</Typography>
                    <Typography variant="body2" fontWeight="bold">{complianceStatus.physical_safeguards}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={complianceStatus.physical_safeguards} 
                    color="success"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Cloud-based (GCP data centers)<br/>
                  ✅ Physical access controls (GCP)<br/>
                  ✅ Workstation security<br/>
                  ✅ Device & media controls
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Breach Notification</Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Score</Typography>
                    <Typography variant="body2" fontWeight="bold">{complianceStatus.breach_notification}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={complianceStatus.breach_notification} 
                    color="error"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ✅ Templates created<br/>
                  ✅ Incident response plan<br/>
                  ❌ Notification procedures (needs testing)<br/>
                  ❌ HHS reporting process (needs setup)
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Action Items */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Warning sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
                  Critical Action Items
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Action</TableCell>
                        <TableCell>Priority</TableCell>
                        <TableCell>Target Date</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Complete BAA with Odoo</TableCell>
                        <TableCell><Chip label="High" color="error" size="small" /></TableCell>
                        <TableCell>2025-11-01</TableCell>
                        <TableCell><Chip label="Pending" size="small" /></TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Test DR procedures</TableCell>
                        <TableCell><Chip label="High" color="error" size="small" /></TableCell>
                        <TableCell>2025-10-25</TableCell>
                        <TableCell><Chip label="Pending" size="small" /></TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Migrate to GCP Secret Manager</TableCell>
                        <TableCell><Chip label="Medium" color="warning" size="small" /></TableCell>
                        <TableCell>2025-11-08</TableCell>
                        <TableCell><Chip label="Planned" size="small" /></TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Implement MFA for admins</TableCell>
                        <TableCell><Chip label="Medium" color="warning" size="small" /></TableCell>
                        <TableCell>2025-11-15</TableCell>
                        <TableCell><Chip label="Planned" size="small" /></TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Incidents */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Security Incidents</Typography>
                  <Button variant="contained" startIcon={<Refresh />} onClick={fetchComplianceData}>
                    Refresh
                  </Button>
                </Box>
                {(incidents || []).length === 0 ? (
                  <Alert severity="success">No security incidents reported</Alert>
                ) : (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Date</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>Severity</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {(incidents || []).map((incident) => (
                          <TableRow key={incident.id}>
                            <TableCell>{incident.id}</TableCell>
                            <TableCell>{incident.date}</TableCell>
                            <TableCell>{incident.type}</TableCell>
                            <TableCell>
                              <Chip 
                                label={incident.severity} 
                                color={incident.severity === 'P0' ? 'error' : 'warning'} 
                                size="small" 
                              />
                            </TableCell>
                            <TableCell>
                              <Chip label={incident.status} size="small" />
                            </TableCell>
                            <TableCell>
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 3: Audit Logs */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Audit Logs (Last 50)</Typography>
                  <Button variant="contained" startIcon={<Refresh />} onClick={fetchComplianceData}>
                    Refresh
                  </Button>
                </Box>
                {auditLogs.length === 0 ? (
                  <Alert severity="info">No audit logs available</Alert>
                ) : (
                  <TableContainer sx={{ maxHeight: 600 }}>
                    <Table stickyHeader size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Timestamp</TableCell>
                          <TableCell>User</TableCell>
                          <TableCell>Action</TableCell>
                          <TableCell>Resource</TableCell>
                          <TableCell>IP Address</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {auditLogs.map((log, index) => (
                          <TableRow key={index}>
                            <TableCell>{log.timestamp || log.created_at}</TableCell>
                            <TableCell>{log.user_id || log.user}</TableCell>
                            <TableCell>{log.action}</TableCell>
                            <TableCell>{log.resource_type} #{log.resource_id}</TableCell>
                            <TableCell>{log.ip_address}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Edit Officer Dialog */}
      <Dialog open={editOfficerDialog} onClose={() => setEditOfficerDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit {editingOfficer?.type === 'security_officer' ? 'Security' : 'Privacy'} Officer
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Name"
              fullWidth
              value={editingOfficer?.name || ''}
              onChange={(e) => setEditingOfficer({ ...editingOfficer, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              label="Title"
              fullWidth
              value={editingOfficer?.title || ''}
              onChange={(e) => setEditingOfficer({ ...editingOfficer, title: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              label="Email"
              fullWidth
              type="email"
              value={editingOfficer?.email || ''}
              onChange={(e) => setEditingOfficer({ ...editingOfficer, email: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              label="Phone"
              fullWidth
              value={editingOfficer?.phone || ''}
              onChange={(e) => setEditingOfficer({ ...editingOfficer, phone: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOfficerDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveOfficer} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default HIPAACompliance;

