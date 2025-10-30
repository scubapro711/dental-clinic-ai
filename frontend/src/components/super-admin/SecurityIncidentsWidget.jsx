import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import {
  Error as CriticalIcon,
  Warning as HighIcon,
  Info as MediumIcon,
  CheckCircle as LowIcon,
  Visibility as ViewIcon,
  Check as ResolveIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import api from '../../services/api';

const SecurityIncidentsWidget = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [resolving, setResolving] = useState(false);

  useEffect(() => {
    fetchIncidents();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchIncidents, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchIncidents = async () => {
    try {
      const response = await api.get('/super-admin/security-incidents', {
        params: { days: 7, limit: 10 }
      });
      setIncidents(response.data.incidents || []);
      setError(null);
    } catch (err) {
      setError('Failed to load security incidents');
      console.error('Error fetching incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (incident) => {
    setSelectedIncident(incident);
    setDialogOpen(true);
  };

  const handleResolve = async (incidentId) => {
    if (!window.confirm('Mark this incident as resolved?')) {
      return;
    }

    try {
      setResolving(true);
      await api.put(`/super-admin/incidents/${incidentId}/resolve`);
      setDialogOpen(false);
      await fetchIncidents();
    } catch (err) {
      alert(`Failed to resolve incident: ${err.message}`);
    } finally {
      setResolving(false);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <CriticalIcon sx={{ color: 'error.main' }} />;
      case 'high':
        return <HighIcon sx={{ color: 'warning.main' }} />;
      case 'medium':
        return <MediumIcon sx={{ color: 'info.main' }} />;
      case 'low':
        return <LowIcon sx={{ color: 'success.main' }} />;
      default:
        return <MediumIcon />;
    }
  };

  const getSeverityChip = (severity) => {
    const configs = {
      critical: { label: 'Critical', color: 'error' },
      high: { label: 'High', color: 'warning' },
      medium: { label: 'Medium', color: 'info' },
      low: { label: 'Low', color: 'success' }
    };
    
    const config = configs[severity] || { label: severity, color: 'default' };
    
    return (
      <Chip
        label={config.label}
        color={config.color}
        size="small"
      />
    );
  };

  const getIncidentTypeLabel = (type) => {
    const labels = {
      failed_login_attempts: 'Failed Login Attempts',
      unauthorized_phi_access: 'Unauthorized PHI Access',
      bulk_phi_export: 'Bulk PHI Export',
      database_connection_failures: 'Database Failures',
      encryption_errors: 'Encryption Errors',
      high_error_rate: 'High Error Rate'
    };
    return labels[type] || type;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  const activeIncidents = (incidents || []).filter(i => i.status === 'active');
  const criticalCount = activeIncidents.filter(i => i.severity === 'critical').length;
  const highCount = activeIncidents.filter(i => i.severity === 'high').length;

  return (
    <Paper sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h6" gutterBottom>
            Security Incidents
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last 7 days • Auto-refreshes every 30s
          </Typography>
        </Box>
        <IconButton onClick={fetchIncidents} disabled={loading}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Paper sx={{ p: 1.5, flex: 1, bgcolor: 'error.lighter' }}>
          <Typography variant="h5" color="error.main">{criticalCount}</Typography>
          <Typography variant="caption">Critical</Typography>
        </Paper>
        <Paper sx={{ p: 1.5, flex: 1, bgcolor: 'warning.lighter' }}>
          <Typography variant="h5" color="warning.main">{highCount}</Typography>
          <Typography variant="caption">High</Typography>
        </Paper>
        <Paper sx={{ p: 1.5, flex: 1 }}>
          <Typography variant="h5">{activeIncidents.length}</Typography>
          <Typography variant="caption">Active</Typography>
        </Paper>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (incidents || []).length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Incidents List */}
          {activeIncidents.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
              <Typography variant="body1" color="success.main">
                No active security incidents
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All systems operating normally
              </Typography>
            </Box>
          ) : (
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {activeIncidents.map((incident, index) => (
                <React.Fragment key={incident.id}>
                  <ListItem
                    sx={{
                      '&:hover': { bgcolor: 'action.hover' },
                      cursor: 'pointer'
                    }}
                    onClick={() => handleViewDetails(incident)}
                  >
                    <ListItemIcon>
                      {getSeverityIcon(incident.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight="medium">
                            {getIncidentTypeLabel(incident.type)}
                          </Typography>
                          {getSeverityChip(incident.severity)}
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="caption" display="block">
                            {incident.organization} • {formatDate(incident.date)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {incident.description}
                          </Typography>
                        </>
                      }
                    />
                    <IconButton size="small" onClick={(e) => {
                      e.stopPropagation();
                      handleViewDetails(incident);
                    }}>
                      <ViewIcon />
                    </IconButton>
                  </ListItem>
                  {index < activeIncidents.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}

          {/* View All Button */}
          {activeIncidents.length > 0 && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Button variant="outlined" size="small">
                View All Incidents
              </Button>
            </Box>
          )}
        </>
      )}

      {/* Incident Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        {selectedIncident && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getSeverityIcon(selectedIncident.severity)}
                {getIncidentTypeLabel(selectedIncident.type)}
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                {getSeverityChip(selectedIncident.severity)}
                <Chip
                  label={selectedIncident.status}
                  size="small"
                  sx={{ ml: 1 }}
                />
              </Box>

              <Typography variant="body2" paragraph>
                <strong>Organization:</strong> {selectedIncident.organization}
              </Typography>

              <Typography variant="body2" paragraph>
                <strong>Date:</strong> {new Date(selectedIncident.date).toLocaleString()}
              </Typography>

              <Typography variant="body2" paragraph>
                <strong>Description:</strong><br />
                {selectedIncident.description}
              </Typography>

              {selectedIncident.details && (
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(selectedIncident.details, null, 2)}
                  </Typography>
                </Paper>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>
                Close
              </Button>
              {selectedIncident.status === 'active' && (
                <Button
                  variant="contained"
                  color="success"
                  onClick={() => handleResolve(selectedIncident.id)}
                  disabled={resolving}
                  startIcon={resolving ? <CircularProgress size={20} /> : <ResolveIcon />}
                >
                  {resolving ? 'Resolving...' : 'Mark Resolved'}
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Paper>
  );
};

export default SecurityIncidentsWidget;

