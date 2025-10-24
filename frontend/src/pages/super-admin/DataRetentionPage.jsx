import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Visibility as ViewIcon,
  DeleteSweep as CleanupIcon,
  CheckCircle as OkIcon,
  Warning as WarningIcon,
  Error as CriticalIcon
} from '@mui/icons-material';
import api from '../../services/api';

const DataRetentionPage = () => {
  const [retentionData, setRetentionData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [expiredRecords, setExpiredRecords] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [cleanupLoading, setCleanupLoading] = useState(false);

  useEffect(() => {
    fetchRetentionStatus();
  }, []);

  const fetchRetentionStatus = async () => {
    try {
      setLoading(true);
      const response = await api.get('/super-admin/data-retention-status');
      setRetentionData(response.data.organizations || []);
      setError(null);
    } catch (err) {
      setError('Failed to load data retention status. Please try again.');
      console.error('Error fetching retention status:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewExpired = async (org) => {
    try {
      setSelectedOrg(org);
      setDialogOpen(true);
      const response = await api.get(`/data-retention/expired/${org.id}`);
      setExpiredRecords(response.data.expired_records || []);
    } catch (err) {
      alert(`Failed to load expired records: ${err.message}`);
    }
  };

  const handleTriggerCleanup = async (orgId, orgName) => {
    if (!window.confirm(
      `Are you sure you want to trigger data cleanup for ${orgName}?\n\n` +
      `This will permanently delete expired patient records according to the retention policy.`
    )) {
      return;
    }

    try {
      setCleanupLoading(true);
      await api.post(`/data-retention/cleanup/${orgId}`);
      alert(`Cleanup triggered successfully for ${orgName}`);
      setDialogOpen(false);
      await fetchRetentionStatus(); // Refresh data
    } catch (err) {
      alert(`Failed to trigger cleanup: ${err.message}`);
    } finally {
      setCleanupLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ok':
        return <OkIcon sx={{ color: 'success.main' }} />;
      case 'action_needed':
        return <WarningIcon sx={{ color: 'warning.main' }} />;
      case 'critical':
        return <CriticalIcon sx={{ color: 'error.main' }} />;
      default:
        return null;
    }
  };

  const getStatusChip = (status, expiredCount) => {
    const configs = {
      ok: { label: 'OK', color: 'success' },
      action_needed: { label: `${expiredCount} Expired`, color: 'warning' },
      critical: { label: `${expiredCount} Expired (Critical)`, color: 'error' }
    };
    
    const config = configs[status] || { label: status, color: 'default' };
    
    return (
      <Chip
        icon={getStatusIcon(status)}
        label={config.label}
        color={config.color}
        size="small"
      />
    );
  };

  const filteredData = retentionData.filter(org =>
    searchTerm === '' || org.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    total: retentionData.length,
    ok: retentionData.filter(o => o.status === 'ok').length,
    action_needed: retentionData.filter(o => o.status === 'action_needed').length,
    critical: retentionData.filter(o => o.status === 'critical').length,
    total_expired: retentionData.reduce((sum, o) => sum + (o.expired_records || 0), 0)
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Data Retention Status
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Monitor data retention compliance across all organizations
        </Typography>
      </Box>

      {/* Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">{stats.total}</Typography>
          <Typography variant="body2" color="text.secondary">Total Organizations</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, bgcolor: 'success.light' }}>
          <Typography variant="h6">{stats.ok}</Typography>
          <Typography variant="body2">Compliant</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, bgcolor: 'warning.light' }}>
          <Typography variant="h6">{stats.action_needed}</Typography>
          <Typography variant="body2">Action Needed</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, bgcolor: 'error.light' }}>
          <Typography variant="h6">{stats.critical}</Typography>
          <Typography variant="body2">Critical</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">{stats.total_expired}</Typography>
          <Typography variant="body2" color="text.secondary">Total Expired Records</Typography>
        </Paper>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Search Organizations"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ flex: 1 }}
          />
          <Button variant="outlined" onClick={fetchRetentionStatus}>
            Refresh
          </Button>
        </Box>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Organization</TableCell>
              <TableCell align="right">Total Patients</TableCell>
              <TableCell align="right">Expired Records</TableCell>
              <TableCell>Last Cleanup</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="text.secondary">
                    No organizations found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredData.map((org) => (
                <TableRow 
                  key={org.id} 
                  hover
                  sx={{
                    bgcolor: org.status === 'critical' ? 'error.lighter' : 
                            org.status === 'action_needed' ? 'warning.lighter' : 
                            'inherit'
                  }}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {org.name}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {org.total_patients?.toLocaleString() || 0}
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={org.expired_records > 0 ? 'error.main' : 'text.secondary'}
                    >
                      {org.expired_records || 0}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {org.last_cleanup || 'Never'}
                  </TableCell>
                  <TableCell>
                    {getStatusChip(org.status, org.expired_records)}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      {org.expired_records > 0 && (
                        <>
                          <Tooltip title="View Expired Records">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewExpired(org)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Trigger Cleanup">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleTriggerCleanup(org.id, org.name)}
                            >
                              <CleanupIcon />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Expired Records Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Expired Patient Records - {selectedOrg?.name}
        </DialogTitle>
        <DialogContent>
          {expiredRecords.length === 0 ? (
            <Typography color="text.secondary">
              No expired records found
            </Typography>
          ) : (
            <List>
              {expiredRecords.map((record, index) => (
                <ListItem key={index} divider>
                  <ListItemText
                    primary={`Patient ID: ${record.patient_id}`}
                    secondary={
                      <>
                        Last Visit: {record.last_visit_date} | 
                        Retention End: {record.retention_period_end} | 
                        Expired: {record.days_expired} days ago
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Close
          </Button>
          {expiredRecords.length > 0 && (
            <Button
              variant="contained"
              color="error"
              onClick={() => handleTriggerCleanup(selectedOrg.id, selectedOrg.name)}
              disabled={cleanupLoading}
              startIcon={cleanupLoading ? <CircularProgress size={20} /> : <CleanupIcon />}
            >
              {cleanupLoading ? 'Cleaning...' : 'Trigger Cleanup'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataRetentionPage;

