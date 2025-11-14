import React, { useState, useEffect } from 'react';
import './SuperAdminPilotApplications.css';
import API_CONFIG from '@/config/api';

/**
 * Super Admin Pilot Applications Dashboard
 * 
 * Manage pilot program applications with scoring and status management
 */
const SuperAdminPilotApplications = () => {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('score');

  useEffect(() => {
    fetchApplications();
    fetchStats();
  }, [filterStatus]);

  const fetchApplications = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const url = filterStatus === 'all' 
        ? '/api/v1/pilot-applications/'
        : `/api/v1/pilot-applications/?status_filter=${filterStatus}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setApplications(data);
      }
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(API_CONFIG.endpoint('pilot-applications/stats/summary'), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const updateApplicationStatus = async (appId, status, notes = '') => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(API_CONFIG.endpoint('pilot-applications/${appId}'), {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status, notes })
      });
      
      if (response.ok) {
        fetchApplications();
        fetchStats();
        setSelectedApp(null);
      }
    } catch (error) {
      console.error('Error updating application:', error);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: '#ff9800',
      reviewing: '#2196f3',
      approved: '#4caf50',
      rejected: '#f44336',
      waitlist: '#9c27b0'
    };
    return colors[status] || '#757575';
  };

  const sortedApplications = [...applications].sort((a, b) => {
    if (sortBy === 'score') return (b.score || 0) - (a.score || 0);
    if (sortBy === 'date') return new Date(b.created_at) - new Date(a.created_at);
    return 0;
  });

  if (loading) {
    return <div className="loading">Loading applications...</div>;
  }

  return (
    <div className="super-admin-pilot">
      <div className="pilot-header">
        <h1>🚀 Pilot Applications</h1>
        <p>Manage and review pilot program applications</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Applications</div>
            </div>
          </div>
          
          <div className="stat-card pending">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <div className="stat-value">{stats.pending}</div>
              <div className="stat-label">Pending Review</div>
            </div>
          </div>
          
          <div className="stat-card approved">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-value">{stats.approved}</div>
              <div className="stat-label">Approved</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-content">
              <div className="stat-value">{stats.average_score}</div>
              <div className="stat-label">Avg Score</div>
            </div>
          </div>
          
          <div className="stat-card top">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <div className="stat-value">{stats.top_applicants}</div>
              <div className="stat-label">Top Applicants (80+)</div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="pilot-controls">
        <div className="filter-group">
          <label>Status:</label>
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="reviewing">Reviewing</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="waitlist">Waitlist</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="score">Score (High to Low)</option>
            <option value="date">Date (Newest First)</option>
          </select>
        </div>
      </div>

      {/* Applications List */}
      <div className="applications-grid">
        {sortedApplications.length === 0 ? (
          <div className="no-applications">
            <p>No applications found</p>
          </div>
        ) : (
          sortedApplications.map((app) => (
            <div 
              key={app.id} 
              className="application-card"
              onClick={() => setSelectedApp(app)}
            >
              <div className="app-header">
                <div>
                  <h3>{app.clinic_name}</h3>
                  <p className="contact-name">{app.contact_name}</p>
                </div>
                <div 
                  className="score-badge"
                  style={{ background: getScoreColor(app.score) }}
                >
                  {app.score}
                </div>
              </div>

              <div className="app-details">
                <div className="detail-row">
                  <span className="label">📧</span>
                  <span>{app.email}</span>
                </div>
                <div className="detail-row">
                  <span className="label">📞</span>
                  <span>{app.phone}</span>
                </div>
                <div className="detail-row">
                  <span className="label">🏥</span>
                  <span>{app.clinic_size} | {app.team_size} team</span>
                </div>
                <div className="detail-row">
                  <span className="label">👥</span>
                  <span>{app.monthly_patients} patients/month</span>
                </div>
                <div className="detail-row">
                  <span className="label">🤖</span>
                  <span>AI: {app.ai_experience}</span>
                </div>
                <div className="detail-row">
                  <span className="label">🎯</span>
                  <span>{app.primary_goal}</span>
                </div>
                <div className="detail-row">
                  <span className="label">⏰</span>
                  <span>{app.timeline}</span>
                </div>
              </div>

              <div className="app-footer">
                <span 
                  className="status-badge"
                  style={{ background: getStatusBadge(app.status) }}
                >
                  {app.status}
                </span>
                <span className="app-date">
                  {new Date(app.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Application Detail Modal */}
      {selectedApp && (
        <div className="modal-overlay" onClick={() => setSelectedApp(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedApp(null)}>✕</button>
            
            <div className="modal-header">
              <div>
                <h2>{selectedApp.clinic_name}</h2>
                <p>{selectedApp.contact_name}</p>
              </div>
              <div 
                className="score-badge-large"
                style={{ background: getScoreColor(selectedApp.score) }}
              >
                {selectedApp.score}
              </div>
            </div>

            <div className="modal-body">
              <div className="info-section">
                <h3>Contact Information</h3>
                <p><strong>Email:</strong> {selectedApp.email}</p>
                <p><strong>Phone:</strong> {selectedApp.phone}</p>
              </div>

              <div className="info-section">
                <h3>Clinic Details</h3>
                <p><strong>Size:</strong> {selectedApp.clinic_size}</p>
                <p><strong>Monthly Patients:</strong> {selectedApp.monthly_patients}</p>
                <p><strong>Team Size:</strong> {selectedApp.team_size}</p>
                {selectedApp.current_software && (
                  <p><strong>Current Software:</strong> {selectedApp.current_software}</p>
                )}
              </div>

              <div className="info-section">
                <h3>AI Readiness</h3>
                <p><strong>Experience:</strong> {selectedApp.ai_experience}</p>
                <p><strong>Primary Goal:</strong> {selectedApp.primary_goal}</p>
                <p><strong>Timeline:</strong> {selectedApp.timeline}</p>
                {selectedApp.budget && (
                  <p><strong>Budget:</strong> ${selectedApp.budget}</p>
                )}
              </div>

              <div className="info-section">
                <h3>Commitment</h3>
                <p>✅ Provide Feedback: {selectedApp.willing_to_provide_feedback ? 'Yes' : 'No'}</p>
                <p>✅ Be Referenced: {selectedApp.willing_to_be_referenced ? 'Yes' : 'No'}</p>
                <p>✅ Agreed to Terms: {selectedApp.agreed_to_terms ? 'Yes' : 'No'}</p>
              </div>

              {selectedApp.notes && (
                <div className="info-section">
                  <h3>Admin Notes</h3>
                  <p>{selectedApp.notes}</p>
                </div>
              )}
            </div>

            <div className="modal-actions">
              {selectedApp.status === 'pending' && (
                <>
                  <button 
                    className="btn-approve"
                    onClick={() => updateApplicationStatus(selectedApp.id, 'approved', 'Approved for pilot program')}
                  >
                    ✅ Approve
                  </button>
                  <button 
                    className="btn-waitlist"
                    onClick={() => updateApplicationStatus(selectedApp.id, 'waitlist', 'Added to waitlist')}
                  >
                    ⏸️ Waitlist
                  </button>
                  <button 
                    className="btn-reject"
                    onClick={() => updateApplicationStatus(selectedApp.id, 'rejected', 'Not a good fit at this time')}
                  >
                    ❌ Reject
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuperAdminPilotApplications;

