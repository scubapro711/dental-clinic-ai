import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const DemoContext = createContext();

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useDemoContext = () => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemoContext must be used within DemoProvider');
  }
  return context;
};

export const DemoProvider = ({ children }) => {
  const [demoMode, setDemoMode] = useState(false);
  const [demoSessionId, setDemoSessionId] = useState(null);
  const [demoData, setDemoData] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Create demo session when demo mode is activated
  const startDemoSession = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await axios.post(`${API_BASE_URL}/api/v1/demo/session/create`);
      const { session_id, expires_at } = response.data;

      setDemoSessionId(session_id);
      setDemoMode(true);

      // Calculate time remaining
      const expiresAt = new Date(expires_at);
      const now = new Date();
      const remaining = Math.floor((expiresAt - now) / 1000);
      setTimeRemaining(remaining);

      // Load demo data immediately (synchronous)
      const data = loadDemoData(session_id);
      setDemoData(data);

      // Store in sessionStorage for persistence
      sessionStorage.setItem('demoSessionId', session_id);
      sessionStorage.setItem('demoExpiresAt', expires_at);

      return session_id;
    } catch (err) {
      console.error('Error starting demo session:', err);
      setError('Failed to start demo session. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // End demo session
  const endDemoSession = async () => {
    if (!demoSessionId) return;

    try {
      await axios.delete(`${API_BASE_URL}/api/v1/demo/session/${demoSessionId}`);
    } catch (err) {
      console.error('Error ending demo session:', err);
    } finally {
      setDemoMode(false);
      setDemoSessionId(null);
      setDemoData(null);
      setTimeRemaining(null);
      sessionStorage.removeItem('demoSessionId');
      sessionStorage.removeItem('demoExpiresAt');
    }
  };

  // Load demo data (patients, appointments, etc.)
  const loadDemoData = (sessionId) => {
      // In a real implementation, this would fetch from the backend
      // For now, we'll use the demo data service directly
      return {
        patients: [
          {
            id: 'demo_patient_1',
            name: 'Sarah Johnson',
            email: 'sarah.j@example.com',
            phone: '+972-50-123-4567',
            dateOfBirth: '1985-03-15',
            lastVisit: '2025-10-10',
            nextAppointment: '2025-10-25',
            balance: 0,
            status: 'Active',
          },
          {
            id: 'demo_patient_2',
            name: 'David Cohen',
            email: 'david.c@example.com',
            phone: '+972-52-234-5678',
            dateOfBirth: '1978-07-22',
            lastVisit: '2025-09-15',
            nextAppointment: '2025-10-20',
            balance: 450,
            status: 'Active',
          },
          {
            id: 'demo_patient_3',
            name: 'Rachel Levi',
            email: 'rachel.l@example.com',
            phone: '+972-54-345-6789',
            dateOfBirth: '1992-11-08',
            lastVisit: '2025-10-05',
            nextAppointment: '2025-11-01',
            balance: 0,
            status: 'Active',
          },
          {
            id: 'demo_patient_4',
            name: 'Michael Green',
            email: 'michael.g@example.com',
            phone: '+972-50-456-7890',
            dateOfBirth: '1965-05-30',
            lastVisit: '2025-08-20',
            nextAppointment: null,
            balance: 1200,
            status: 'Inactive',
          },
          {
            id: 'demo_patient_5',
            name: 'Tamar Shapiro',
            email: 'tamar.s@example.com',
            phone: '+972-52-567-8901',
            dateOfBirth: '2000-09-12',
            lastVisit: '2025-10-12',
            nextAppointment: '2025-10-28',
            balance: 0,
            status: 'Active',
          },
        ],
        appointments: [
          {
            id: 'demo_appt_1',
            patientId: 'demo_patient_1',
            patientName: 'Sarah Johnson',
            date: '2025-10-25',
            time: '10:00',
            type: 'Cleaning',
            doctor: 'Dr. Rachel Cohen',
            status: 'Scheduled',
            duration: 30,
          },
          {
            id: 'demo_appt_2',
            patientId: 'demo_patient_2',
            patientName: 'David Cohen',
            date: '2025-10-20',
            time: '14:00',
            type: 'Check-up',
            doctor: 'Dr. Yossi Mizrahi',
            status: 'Scheduled',
            duration: 30,
          },
          {
            id: 'demo_appt_3',
            patientId: 'demo_patient_3',
            patientName: 'Rachel Levi',
            date: '2025-11-01',
            time: '09:00',
            type: 'Root Canal',
            doctor: 'Dr. Rachel Cohen',
            status: 'Scheduled',
            duration: 60,
          },
          {
            id: 'demo_appt_4',
            patientId: 'demo_patient_5',
            patientName: 'Tamar Shapiro',
            date: '2025-10-28',
            time: '11:00',
            type: 'Filling',
            doctor: 'Dr. Maya Goldstein',
            status: 'Scheduled',
            duration: 45,
          },
        ],
        invoices: [
          {
            id: 'demo_inv_1',
            patientId: 'demo_patient_2',
            patientName: 'David Cohen',
            date: '2025-09-15',
            amount: 450,
            status: 'Unpaid',
            dueDate: '2025-10-15',
          },
          {
            id: 'demo_inv_2',
            patientId: 'demo_patient_4',
            patientName: 'Michael Green',
            date: '2025-08-20',
            amount: 1200,
            status: 'Overdue',
            dueDate: '2025-09-20',
          },
        ],
        financialSummary: {
          totalRevenue: 15600,
          outstandingBalance: 1650,
          paidInvoices: 12,
          unpaidInvoices: 2,
          monthlyRevenue: [
            { month: 'Jan', revenue: 12000 },
            { month: 'Feb', revenue: 13500 },
            { month: 'Mar', revenue: 14200 },
            { month: 'Apr', revenue: 15100 },
            { month: 'May', revenue: 14800 },
            { month: 'Jun', revenue: 15600 },
          ],
        },
        clinicInfo: {
          name: 'DentaFlow Demo Clinic',
          address: '123 Dental Street, Tel Aviv, Israel',
          phone: '+972-3-123-4567',
          email: 'info@dentaflow-demo.com',
          hours: 'Sun-Thu: 9:00-18:00, Fri: 9:00-13:00',
          doctors: [
            { id: 1, name: 'Dr. Rachel Cohen', specialty: 'General Dentistry' },
            { id: 2, name: 'Dr. Yossi Mizrahi', specialty: 'Orthodontics' },
            { id: 3, name: 'Dr. Maya Goldstein', specialty: 'Endodontics' },
          ],
        },
      };
  };

  // Update time remaining every second
  useEffect(() => {
    if (!demoMode || timeRemaining === null) return;

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 0) {
          clearInterval(interval);
          endDemoSession();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [demoMode, timeRemaining]);

  // Restore demo session from sessionStorage on mount
  useEffect(() => {
    const storedSessionId = sessionStorage.getItem('demoSessionId');
    const storedExpiresAt = sessionStorage.getItem('demoExpiresAt');

    if (storedSessionId && storedExpiresAt) {
      const expiresAt = new Date(storedExpiresAt);
      const now = new Date();

      if (expiresAt > now) {
        // Session still valid
        const remaining = Math.floor((expiresAt - now) / 1000);
        setDemoSessionId(storedSessionId);
        setDemoMode(true);
        setTimeRemaining(remaining);
        loadDemoData(storedSessionId);
      } else {
        // Session expired
        sessionStorage.removeItem('demoSessionId');
        sessionStorage.removeItem('demoExpiresAt');
      }
    }
  }, []);

  const value = {
    demoMode,
    demoSessionId,
    demoData,
    timeRemaining,
    isLoading,
    error,
    startDemoSession,
    endDemoSession,
  };

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
};

export default DemoContext;

