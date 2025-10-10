/**
 * Clinical Dashboard Page
 * 
 * Main dashboard for doctors with clinical tools and שרה integration.
 * 
 * Features:
 * - Patient search and selection
 * - Clinical assistant (שרה) chat
 * - Quick access to patient records
 * - Today's appointments
 * - Recent treatments
 * 
 * Reference: MASTER_PLAN_FINAL_V2.md - Phase 1
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Chip,
  Paper,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  MedicalServices as MedicalIcon,
} from '@mui/icons-material';
import { ClinicalAssistant } from '../components/ClinicalAssistant';
import { useAuth } from '../contexts/AuthContext';

interface Patient {
  id: string;
  name: string;
  phone: string;
  lastVisit?: string;
}

interface Appointment {
  id: string;
  patientName: string;
  time: string;
  type: string;
  status: string;
}

export const ClinicalDashboard: React.FC = () => {
  const { user } = useAuth();
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [todayAppointments, setTodayAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock data - replace with real API calls
  useEffect(() => {
    // Simulate loading today's appointments
    setTodayAppointments([
      {
        id: '1',
        patientName: 'דוד כהן',
        time: '09:00',
        type: 'סתימה',
        status: 'scheduled',
      },
      {
        id: '2',
        patientName: 'שרה לוי',
        time: '10:30',
        type: 'בדיקה',
        status: 'scheduled',
      },
      {
        id: '3',
        patientName: 'משה אברהם',
        time: '14:00',
        type: 'טיפול שורש',
        status: 'scheduled',
      },
    ]);
  }, []);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.length < 2) {
      setPatients([]);
      return;
    }

    // Mock search - replace with real API call
    // const results = await searchPatients(query);
    setPatients([
      {
        id: '1',
        name: 'דוד כהן',
        phone: '050-1234567',
        lastVisit: '2025-09-15',
      },
      {
        id: '2',
        name: 'שרה לוי',
        phone: '052-9876543',
        lastVisit: '2025-10-01',
      },
    ]);
  };

  const handleSelectPatient = (patient: Patient) => {
    setSelectedPatient(patient);
    setSearchQuery('');
    setPatients([]);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        לוח בקרה קליני
      </Typography>

      <Grid container spacing={3}>
        {/* Left Column - Patient Search & Today's Schedule */}
        <Grid item xs={12} md={4}>
          {/* Patient Search */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon />
                חיפוש מטופל
              </Typography>
              <TextField
                fullWidth
                placeholder="חפש לפי שם או טלפון..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              {/* Search Results */}
              {patients.length > 0 && (
                <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                  <List>
                    {patients.map((patient) => (
                      <ListItem key={patient.id} disablePadding>
                        <ListItemButton onClick={() => handleSelectPatient(patient)}>
                          <ListItemText
                            primary={patient.name}
                            secondary={`${patient.phone} • ביקור אחרון: ${patient.lastVisit}`}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}

              {/* Selected Patient */}
              {selectedPatient && (
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    mt: 2,
                    bgcolor: 'primary.50',
                    borderColor: 'primary.main',
                  }}
                >
                  <Typography variant="subtitle2" color="primary">
                    מטופל נבחר:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {selectedPatient.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedPatient.phone}
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>

          {/* Today's Appointments */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CalendarIcon />
                תורים להיום
              </Typography>
              <List>
                {todayAppointments.map((appointment, index) => (
                  <React.Fragment key={appointment.id}>
                    {index > 0 && <Divider />}
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" fontWeight="bold">
                              {appointment.time}
                            </Typography>
                            <Typography variant="body1">
                              {appointment.patientName}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Chip
                              label={appointment.type}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Chip
                              label={appointment.status === 'scheduled' ? 'מתוזמן' : 'הושלם'}
                              size="small"
                              color={appointment.status === 'scheduled' ? 'default' : 'success'}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Clinical Assistant (שרה) */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '80vh' }}>
            <ClinicalAssistant
              patientId={selectedPatient?.id}
              patientName={selectedPatient?.name}
            />
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ClinicalDashboard;

