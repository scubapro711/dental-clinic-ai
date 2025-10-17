import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDemoContext } from '../contexts/DemoContext';
import DemoChatButton from '../components/DemoChatButton';
import './DemoPortal.css';

const DemoPortal = () => {
  const navigate = useNavigate();
  const { demoMode, startDemoSession, endDemoSession, timeRemaining, isLoading, error } = useDemoContext();
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    // Start demo session if not already started
    if (!demoMode) {
      startDemoSession().catch((err) => {
        console.error('Failed to start demo session:', err);
        // Redirect to landing page on error
        navigate('/');
      });
    }
  }, []);

  const handleExitDemo = () => {
    if (window.confirm('Are you sure you want to exit the demo? Your session will be ended.')) {
      endDemoSession();
      navigate('/');
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="demo-portal-loading">
        <div className="loading-spinner"></div>
        <p>Starting your demo session...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="demo-portal-error">
        <h2>⚠️ Demo Session Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')}>Return to Home</button>
      </div>
    );
  }

  return (
    <div className="demo-portal">
      {/* Demo Header */}
      <div className="demo-header">
        <div className="demo-header-left">
          <div className="demo-badge">DEMO MODE</div>
          <h1>DentaFlow Clinic Dashboard</h1>
        </div>
        <div className="demo-header-right">
          {timeRemaining !== null && (
            <div className={`demo-timer ${timeRemaining < 300 ? 'warning' : ''}`}>
              ⏰ {formatTime(timeRemaining)} remaining
            </div>
          )}
          <button className="exit-demo-btn" onClick={handleExitDemo}>
            Exit Demo
          </button>
        </div>
      </div>

      {/* Demo Navigation */}
      <div className="demo-nav">
        <button
          className={`demo-nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentPage('dashboard')}
        >
          📊 Dashboard
        </button>
        <button
          className={`demo-nav-btn ${currentPage === 'patients' ? 'active' : ''}`}
          onClick={() => setCurrentPage('patients')}
        >
          👥 Patients
        </button>
        <button
          className={`demo-nav-btn ${currentPage === 'appointments' ? 'active' : ''}`}
          onClick={() => setCurrentPage('appointments')}
        >
          📅 Appointments
        </button>
        <button
          className={`demo-nav-btn ${currentPage === 'financial' ? 'active' : ''}`}
          onClick={() => setCurrentPage('financial')}
        >
          💰 Financial
        </button>
      </div>

      {/* Demo Content */}
      <div className="demo-content">
        {currentPage === 'dashboard' && <DemoDashboard />}
        {currentPage === 'patients' && <DemoPatients />}
        {currentPage === 'appointments' && <DemoAppointments />}
        {currentPage === 'financial' && <DemoFinancial />}
      </div>

      {/* Demo Footer */}
      <div className="demo-footer">
        <p>
          ⚠️ This is a demo environment with sample data. 
          <a href="/register" className="cta-link">Start Free Trial</a> to use with your real clinic data.
        </p>
      </div>

      {/* Alex Chat Button */}
      <DemoChatButton />
    </div>
  );
};

// Demo Dashboard Component
const DemoDashboard = () => {
  const { demoData, isLoading, error } = useDemoContext();

  if (error) {
    return (
      <div className="demo-error">
        <h3>⚠️ Unable to load dashboard</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Reload Page</button>
      </div>
    );
  }

  if (!demoData || isLoading) {
    return (
      <div className="demo-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  const { financialSummary, patients, appointments } = demoData;
  const activePatients = patients.filter(p => p.status === 'Active').length;
  const upcomingAppointments = appointments.length;

  return (
    <div className="demo-dashboard">
      <h2>Dashboard Overview</h2>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-label">Total Revenue</div>
            <div className="metric-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
            <div className="metric-change positive">+12% from last month</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <div className="metric-label">Active Patients</div>
            <div className="metric-value">{activePatients}</div>
            <div className="metric-change positive">+2 new this week</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📅</div>
          <div className="metric-content">
            <div className="metric-label">Upcoming Appointments</div>
            <div className="metric-value">{upcomingAppointments}</div>
            <div className="metric-change neutral">Next 7 days</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <div className="metric-label">Outstanding Balance</div>
            <div className="metric-value">₪{financialSummary.outstandingBalance.toLocaleString()}</div>
            <div className="metric-change negative">{financialSummary.unpaidInvoices} unpaid invoices</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon">📅</div>
            <div className="activity-content">
              <div className="activity-title">New appointment scheduled</div>
              <div className="activity-details">Sarah Johnson - Oct 25, 10:00 AM</div>
            </div>
            <div className="activity-time">2 hours ago</div>
          </div>
          <div className="activity-item">
            <div className="activity-icon">💰</div>
            <div className="activity-content">
              <div className="activity-title">Payment received</div>
              <div className="activity-details">Rachel Levi - ₪850</div>
            </div>
            <div className="activity-time">5 hours ago</div>
          </div>
          <div className="activity-item">
            <div className="activity-icon">👤</div>
            <div className="activity-content">
              <div className="activity-title">New patient registered</div>
              <div className="activity-details">Tamar Shapiro</div>
            </div>
            <div className="activity-time">Yesterday</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Demo Patients Component
const DemoPatients = () => {
  const { demoData } = useDemoContext();
  const [selectedPatient, setSelectedPatient] = useState(null);

  if (!demoData) {
    return <div className="demo-loading">Loading patients...</div>;
  }

  const { patients } = demoData;

  return (
    <div className="demo-patients">
      <h2>Patient Management</h2>

      <div className="patients-container">
        {/* Patients List */}
        <div className="patients-list">
          {patients.map((patient) => (
            <div
              key={patient.id}
              className={`patient-card ${selectedPatient?.id === patient.id ? 'selected' : ''}`}
              onClick={() => setSelectedPatient(patient)}
            >
              <div className="patient-avatar">{patient.name.charAt(0)}</div>
              <div className="patient-info">
                <div className="patient-name">{patient.name}</div>
                <div className="patient-details">
                  Last visit: {patient.lastVisit || 'Never'}
                </div>
                {patient.balance > 0 && (
                  <div className="patient-balance">Balance: ₪{patient.balance}</div>
                )}
              </div>
              <div className={`patient-status ${patient.status.toLowerCase()}`}>
                {patient.status}
              </div>
            </div>
          ))}
        </div>

        {/* Patient Details */}
        {selectedPatient && (
          <div className="patient-details">
            <h3>{selectedPatient.name}</h3>
            <div className="detail-row">
              <span className="detail-label">Email:</span>
              <span className="detail-value">{selectedPatient.email}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Phone:</span>
              <span className="detail-value">{selectedPatient.phone}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Date of Birth:</span>
              <span className="detail-value">{selectedPatient.dateOfBirth}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Last Visit:</span>
              <span className="detail-value">{selectedPatient.lastVisit || 'Never'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Next Appointment:</span>
              <span className="detail-value">{selectedPatient.nextAppointment || 'None scheduled'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Balance:</span>
              <span className="detail-value">₪{selectedPatient.balance}</span>
            </div>
            <div className="detail-actions">
              <button className="btn-primary">Schedule Appointment</button>
              <button className="btn-secondary">View History</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Demo Appointments Component
const DemoAppointments = () => {
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">Loading appointments...</div>;
  }

  const { appointments } = demoData;

  return (
    <div className="demo-appointments">
      <h2>Appointments</h2>

      <div className="appointments-list">
        {appointments.map((appointment) => (
          <div key={appointment.id} className="appointment-card">
            <div className="appointment-date">
              <div className="date-day">{new Date(appointment.date).getDate()}</div>
              <div className="date-month">
                {new Date(appointment.date).toLocaleDateString('en-US', { month: 'short' })}
              </div>
            </div>
            <div className="appointment-info">
              <div className="appointment-patient">{appointment.patientName}</div>
              <div className="appointment-details">
                {appointment.type} with {appointment.doctor}
              </div>
              <div className="appointment-time">
                {appointment.time} ({appointment.duration} min)
              </div>
            </div>
            <div className={`appointment-status ${appointment.status.toLowerCase()}`}>
              {appointment.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Demo Financial Component
const DemoFinancial = () => {
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">Loading financial data...</div>;
  }

  const { financialSummary, invoices } = demoData;

  return (
    <div className="demo-financial">
      <h2>Financial Overview</h2>

      <div className="financial-summary">
        <div className="summary-card">
          <div className="summary-label">Total Revenue</div>
          <div className="summary-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Outstanding Balance</div>
          <div className="summary-value">₪{financialSummary.outstandingBalance.toLocaleString()}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Paid Invoices</div>
          <div className="summary-value">{financialSummary.paidInvoices}</div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Unpaid Invoices</div>
          <div className="summary-value">{financialSummary.unpaidInvoices}</div>
        </div>
      </div>

      <h3>Outstanding Invoices</h3>
      <div className="invoices-list">
        {invoices.map((invoice) => (
          <div key={invoice.id} className="invoice-card">
            <div className="invoice-patient">{invoice.patientName}</div>
            <div className="invoice-details">
              <span>Date: {invoice.date}</span>
              <span>Due: {invoice.dueDate}</span>
            </div>
            <div className="invoice-amount">₪{invoice.amount}</div>
            <div className={`invoice-status ${invoice.status.toLowerCase()}`}>
              {invoice.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DemoPortal;

