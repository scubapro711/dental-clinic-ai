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
  MenuItem,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Email as EmailIcon,
  Download as DownloadIcon,
  CheckCircle as SignedIcon,
  Warning as PendingIcon,
  Error as ExpiredIcon
} from '@mui/icons-material';
import { api } from '../../services/api';

const BAAManagementPage = () => {
  const [baaData, setBaaData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sending, setSending] = useState({});

  useEffect(() => {
    fetchBAAStatus();
  }, []);

  const fetchBAAStatus = async () => {
    try {
      setLoading(true);
      const response = await api.get('/super-admin/baa-status');
      setBaaData(response.data.organizations || []);
      setError(null);
    } catch (err) {
      setError('Failed to load BAA status. Please try again.');
      console.error('Error fetching BAA status:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendReminder = async (orgId, orgName) => {
    if (!window.confirm(`Send BAA reminder to ${orgName}?`)) {
      return;
    }

    try {
      setSending({ ...sending, [orgId]: true });
      await api.post(`/super-admin/baa-reminder/${orgId}`);
      alert(`Reminder sent successfully to ${orgName}`);
      await fetchBAAStatus(); // Refresh data
    } catch (err) {
      alert(`Failed to send reminder: ${err.message}`);
    } finally {
      setSending({ ...sending, [orgId]: false });
    }
  };

  const handleDownloadBAA = async (orgId, orgName) => {
    try {
      const response = await api.get(`/baa/${orgId}/pdf`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `BAA_${orgName.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert(`Failed to download BAA: ${err.message}`);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'signed':
        return <SignedIcon sx={{ color: 'success.main' }} />;
      case 'pending':
        return <PendingIcon sx={{ color: 'warning.main' }} />;
      case 'expired':
        return <ExpiredIcon sx={{ color: 'error.main' }} />;
      default:
        return null;
    }
  };

  const getStatusChip = (status) => {
    const configs = {
      signed: { label: 'Signed', color: 'success' },
      pending: { label: 'Pending', color: 'warning' },
      expired: { label: 'Expired', color: 'error' }
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

  const filteredData = baaData
    .filter(org => {
      if (filter !== 'all' && org.baa_status !== filter) return false;
      if (searchTerm && !org.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    });

  const stats = {
    total: baaData.length,
    signed: baaData.filter(o => o.baa_status === 'signed').length,
    pending: baaData.filter(o => o.baa_status === 'pending').length,
    expired: baaData.filter(o => o.baa_status === 'expired').length
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
          BAA Management
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage Business Associate Agreements for all organizations
        </Typography>
      </Box>

      {/* Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Paper sx={{ p: 2, flex: 1 }}>
          <Typography variant="h6">{stats.total}</Typography>
          <Typography variant="body2" color="text.secondary">Total Organizations</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, bgcolor: 'success.light' }}>
          <Typography variant="h6">{stats.signed}</Typography>
          <Typography variant="body2">Signed BAAs</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, bgcolor: 'warning.light' }}>
          <Typography variant="h6">{stats.pending}</Typography>
          <Typography variant="body2">Pending BAAs</Typography>
        </Paper>
        <Paper sx={{ p: 2, flex: 1, bgcolor: 'error.light' }}>
          <Typography variant="h6">{stats.expired}</Typography>
          <Typography variant="body2">Expired BAAs</Typography>
        </Paper>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
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
          <TextField
            select
            label="Filter by Status"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="signed">Signed</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="expired">Expired</MenuItem>
          </TextField>
          <Button variant="outlined" onClick={fetchBAAStatus}>
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
              <TableCell>Status</TableCell>
              <TableCell>Signed Date</TableCell>
              <TableCell>Signed By</TableCell>
              <TableCell>Expires Date</TableCell>
              <TableCell>Reminder Count</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography color="text.secondary">
                    No organizations found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredData.map((org) => (
                <TableRow key={org.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {org.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getStatusChip(org.baa_status)}
                  </TableCell>
                  <TableCell>
                    {org.signed_date || '-'}
                  </TableCell>
                  <TableCell>
                    {org.signed_by || '-'}
                  </TableCell>
                  <TableCell>
                    {org.expires_date || '-'}
                  </TableCell>
                  <TableCell>
                    {org.reminder_count || 0}
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                      {org.baa_status === 'signed' && (
                        <>
                          <Tooltip title="View BAA">
                            <IconButton size="small" color="primary">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download BAA">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleDownloadBAA(org.id, org.name)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                      {org.baa_status === 'pending' && (
                        <Tooltip title="Send Reminder">
                          <IconButton
                            size="small"
                            color="warning"
                            onClick={() => handleSendReminder(org.id, org.name)}
                            disabled={sending[org.id]}
                          >
                            {sending[org.id] ? (
                              <CircularProgress size={20} />
                            ) : (
                              <EmailIcon />
                            )}
                          </IconButton>
                        </Tooltip>
                      )}
                      {org.baa_status === 'expired' && (
                        <Tooltip title="Send Renewal Reminder">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleSendReminder(org.id, org.name)}
                            disabled={sending[org.id]}
                          >
                            {sending[org.id] ? (
                              <CircularProgress size={20} />
                            ) : (
                              <EmailIcon />
                            )}
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default BAAManagementPage;

