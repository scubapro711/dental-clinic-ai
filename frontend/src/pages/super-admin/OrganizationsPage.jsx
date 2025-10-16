import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Button,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Visibility,
  Block,
  Delete,
  CalendarToday,
  TrendingUp,
} from '@mui/icons-material';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Organizations Page - Manage All Clinics
 * 
 * Features:
 * - List all organizations with filtering
 * - Search by name or email
 * - Filter by status and plan
 * - View organization details
 * - Suspend/delete organizations
 * - Extend trial
 * - Change plan
 */
const OrganizationsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [organizations, setOrganizations] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  
  // Dialogs
  const [suspendDialog, setSuspendDialog] = useState({ open: false, org: null });
  const [deleteDialog, setDeleteDialog] = useState({ open: false, org: null });
  const [extendTrialDialog, setExtendTrialDialog] = useState({ open: false, org: null, days: 7 });
  const [changePlanDialog, setChangePlanDialog] = useState({ open: false, org: null, newPlan: '' });

  useEffect(() => {
    fetchOrganizations();
  }, [page, rowsPerPage, statusFilter, planFilter]);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      const params = {
        page: page + 1,
        limit: rowsPerPage,
      };

      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      if (planFilter) params.plan = planFilter;

      const response = await axios.get(
        `${API_BASE_URL}/api/v1/super-admin/organizations`,
        {
          headers: { Authorization: `Bearer ${token}` },
          params,
        }
      );

      setOrganizations(response.data.organizations);
      setTotal(response.data.total);
    } catch (err) {
      console.error('Error fetching organizations:', err);
      setError(err.response?.data?.detail || 'Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(0);
    fetchOrganizations();
  };

  const handleSuspend = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/v1/super-admin/organizations/${suspendDialog.org.id}/suspend`,
        { reason: 'Suspended by admin' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuspendDialog({ open: false, org: null });
      fetchOrganizations();
    } catch (err) {
      console.error('Error suspending organization:', err);
      setError(err.response?.data?.detail || 'Failed to suspend organization');
    }
  };

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${API_BASE_URL}/api/v1/super-admin/organizations/${deleteDialog.org.id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { hard_delete: false },
        }
      );
      setDeleteDialog({ open: false, org: null });
      fetchOrganizations();
    } catch (err) {
      console.error('Error deleting organization:', err);
      setError(err.response?.data?.detail || 'Failed to delete organization');
    }
  };

  const handleExtendTrial = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/v1/super-admin/organizations/${extendTrialDialog.org.id}/extend-trial`,
        { days: extendTrialDialog.days },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setExtendTrialDialog({ open: false, org: null, days: 7 });
      fetchOrganizations();
    } catch (err) {
      console.error('Error extending trial:', err);
      setError(err.response?.data?.detail || 'Failed to extend trial');
    }
  };

  const handleChangePlan = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/api/v1/super-admin/organizations/${changePlanDialog.org.id}/change-plan`,
        { plan_tier: changePlanDialog.newPlan },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setChangePlanDialog({ open: false, org: null, newPlan: '' });
      fetchOrganizations();
    } catch (err) {
      console.error('Error changing plan:', err);
      setError(err.response?.data?.detail || 'Failed to change plan');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'trialing':
        return 'info';
      case 'past_due':
        return 'warning';
      case 'canceled':
      case 'suspended':
        return 'error';
      default:
        return 'default';
    }
  };

  const getPlanColor = (plan) => {
    switch (plan) {
      case 'basic':
        return 'default';
      case 'professional':
        return 'primary';
      case 'enterprise':
        return 'secondary';
      default:
        return 'default';
    }
  };

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Organizations Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage all clinics in the platform
        </Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} flexWrap="wrap">
          <TextField
            label="Search"
            variant="outlined"
            size="small"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            sx={{ flexGrow: 1, minWidth: 200 }}
            placeholder="Search by name or email"
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="trialing">Trial</MenuItem>
              <MenuItem value="past_due">Past Due</MenuItem>
              <MenuItem value="canceled">Canceled</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Plan</InputLabel>
            <Select
              value={planFilter}
              label="Plan"
              onChange={(e) => setPlanFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="basic">Basic</MenuItem>
              <MenuItem value="professional">Professional</MenuItem>
              <MenuItem value="enterprise">Enterprise</MenuItem>
            </Select>
          </FormControl>

          <Button variant="contained" onClick={handleSearch}>
            Search
          </Button>
        </Box>
      </Paper>

      {/* Organizations Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Organization</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Plan</TableCell>
                <TableCell>Users</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : organizations.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No organizations found
                  </TableCell>
                </TableRow>
              ) : (
                organizations.map((org) => (
                  <TableRow key={org.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {org.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{org.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={org.subscription_status}
                        color={getStatusColor(org.subscription_status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={org.subscription_tier}
                        color={getPlanColor(org.subscription_tier)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{org.user_count}</TableCell>
                    <TableCell>
                      {new Date(org.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/super-admin/organizations/${org.id}`)}
                        title="View Details"
                      >
                        <Visibility />
                      </IconButton>
                      
                      {org.trial_end && (
                        <IconButton
                          size="small"
                          onClick={() => setExtendTrialDialog({ open: true, org, days: 7 })}
                          title="Extend Trial"
                        >
                          <CalendarToday />
                        </IconButton>
                      )}
                      
                      <IconButton
                        size="small"
                        onClick={() => setChangePlanDialog({ open: true, org, newPlan: org.subscription_tier })}
                        title="Change Plan"
                      >
                        <TrendingUp />
                      </IconButton>
                      
                      <IconButton
                        size="small"
                        onClick={() => setSuspendDialog({ open: true, org })}
                        title="Suspend"
                        color="warning"
                      >
                        <Block />
                      </IconButton>
                      
                      <IconButton
                        size="small"
                        onClick={() => setDeleteDialog({ open: true, org })}
                        title="Delete"
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[10, 20, 50, 100]}
        />
      </Paper>

      {/* Suspend Dialog */}
      <Dialog open={suspendDialog.open} onClose={() => setSuspendDialog({ open: false, org: null })}>
        <DialogTitle>Suspend Organization</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to suspend <strong>{suspendDialog.org?.name}</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={2}>
            The organization will be deactivated and users will not be able to access the system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSuspendDialog({ open: false, org: null })}>Cancel</Button>
          <Button onClick={handleSuspend} color="warning" variant="contained">
            Suspend
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={deleteDialog.open} onClose={() => setDeleteDialog({ open: false, org: null })}>
        <DialogTitle>Delete Organization</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{deleteDialog.org?.name}</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={2}>
            This will soft-delete the organization. Data will be retained but the organization will be marked as deleted.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, org: null })}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Extend Trial Dialog */}
      <Dialog open={extendTrialDialog.open} onClose={() => setExtendTrialDialog({ open: false, org: null, days: 7 })}>
        <DialogTitle>Extend Trial Period</DialogTitle>
        <DialogContent>
          <Typography mb={2}>
            Extend trial for <strong>{extendTrialDialog.org?.name}</strong>
          </Typography>
          <TextField
            label="Days to extend"
            type="number"
            value={extendTrialDialog.days}
            onChange={(e) => setExtendTrialDialog({ ...extendTrialDialog, days: parseInt(e.target.value) })}
            fullWidth
            inputProps={{ min: 1, max: 90 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExtendTrialDialog({ open: false, org: null, days: 7 })}>Cancel</Button>
          <Button onClick={handleExtendTrial} color="primary" variant="contained">
            Extend Trial
          </Button>
        </DialogActions>
      </Dialog>

      {/* Change Plan Dialog */}
      <Dialog open={changePlanDialog.open} onClose={() => setChangePlanDialog({ open: false, org: null, newPlan: '' })}>
        <DialogTitle>Change Subscription Plan</DialogTitle>
        <DialogContent>
          <Typography mb={2}>
            Change plan for <strong>{changePlanDialog.org?.name}</strong>
          </Typography>
          <FormControl fullWidth>
            <InputLabel>New Plan</InputLabel>
            <Select
              value={changePlanDialog.newPlan}
              label="New Plan"
              onChange={(e) => setChangePlanDialog({ ...changePlanDialog, newPlan: e.target.value })}
            >
              <MenuItem value="basic">Basic</MenuItem>
              <MenuItem value="professional">Professional</MenuItem>
              <MenuItem value="enterprise">Enterprise</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChangePlanDialog({ open: false, org: null, newPlan: '' })}>Cancel</Button>
          <Button onClick={handleChangePlan} color="primary" variant="contained">
            Change Plan
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default OrganizationsPage;

