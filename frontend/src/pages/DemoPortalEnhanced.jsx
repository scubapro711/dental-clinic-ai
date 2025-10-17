import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useDemoContext } from '../contexts/DemoContext';
import DemoChatButton from '../components/DemoChatButton';
import ClinicalDashboard from '../components/clinical/ClinicalDashboard';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import './DemoPortalEnhanced.css';/**
 * Enhanced Demo Portal - Showcases AI Agent Features
 * 
 * This demo portal includes all the AI agent features from production:
 * - Pending Decisions Widget
 * - Agent Activity Monitor
 * - AI Chat Interface
 * - Fine-Tuning Section
 * - Transparency Panel
 */
const DemoPortalEnhanced = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { demoMode, startDemoSession, endDemoSession, timeRemaining, isLoading, error } = useDemoContext();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [showTransparency, setShowTransparency] = useState(true);

  useEffect(() => {
    // Start demo session if not already started
    if (!demoMode) {
      startDemoSession().catch((err) => {
        console.error('Failed to start demo session:', err);
        navigate('/');
      });
    }
  }, [demoMode, startDemoSession, navigate]);

  const handleExitDemo = () => {
    if (window.confirm(t("landing.demo.exitConfirm"))) {
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
        <p>{t("landing.demo.startingDemo")}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="demo-portal-error">
        <h2>⚠️ {t("landing.demo.demoError")}</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')}>{t("landing.demo.returnHome")}</button>
      </div>
    );
  }

  return (
    <div className="demo-portal-enhanced">
      {/* Demo Header */}
      <div className="demo-header">
        <div className="demo-header-left">
          <div className="demo-badge">🤖 {t("landing.demo.demoMode")}</div>
          <h1>{t("landing.demo.title")}</h1>
          <p className="demo-subtitle">{t("landing.demo.subtitle")}</p>
        </div>
        <div className="demo-header-right">
          <LanguageSwitcher />
          {timeRemaining !== null && (
            <div className={`demo-timer ${timeRemaining < 300 ? 'warning' : ''}`}>
              ⏰ {formatTime(timeRemaining)} {t("landing.demo.remaining")}
            </div>
          )}
          <button className="toggle-btn" onClick={() => setShowTransparency(!showTransparency)}>
            {showTransparency ? `🔍 ${t("landing.demo.hideTransparency")}` : `🔍 ${t("landing.demo.showTransparency")}`}
          </button>
          <button className="exit-demo-btn" onClick={handleExitDemo}>
            {t("landing.demo.exitDemo")}
          </button>
        </div>
      </div>

      {/* Main Layout */}
      <div className="demo-main-layout">
        {/* Left Sidebar - Widgets */}
        <div className="demo-left-sidebar">
          <PendingDecisionsWidget />
          <AgentActivityWidget />
          <FineTuningWidget />
        </div>

        {/* Center - Dashboard Content */}
        <div className="demo-center-content">
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

          <div className="demo-content">
            {currentPage === 'dashboard' && <DemoDashboardEnhanced />}
            {currentPage === 'patients' && <DemoPatientsEnhanced />}
            {currentPage === 'appointments' && <DemoAppointmentsEnhanced />}
            {currentPage === 'financial' && <DemoFinancialEnhanced />}
          </div>
        </div>

        {/* Right Sidebar - Transparency */}
        <div className="demo-right-sidebar">
          {showTransparency && (
            <div className="demo-transparency-panel">
              <TransparencyPanelDemo />
            </div>
          )}
        </div>
      </div>

      {/* Demo Footer */}
      <div className="demo-footer">
        <p>
          ⚠️ {t("landing.demo.demoEnvironment")} 
          <a href="/register" className="cta-link">{t("landing.demo.startFreeTrial")}</a> {t("landing.demo.toUseWithReal")}
        </p>
      </div>

      {/* Floating AI Chat Button */}
      <DemoChatButton />
    </div>
  );
};

// ==================== WIDGETS ====================

/**
 * Pending Decisions Widget
 * Shows AI agent decisions waiting for approval
 */
const PendingDecisionsWidget = () => {
  const [decisions, setDecisions] = useState([
    {
      id: 1,
      agent: 'Alex',
      type: 'appointment_reschedule',
      title: 'Reschedule Appointment',
      description: 'Patient Sarah Johnson requested to move appointment from Oct 25 to Oct 27',
      priority: 'medium',
      timestamp: '10 minutes ago'
    },
    {
      id: 2,
      agent: 'Marcus',
      type: 'payment_plan',
      title: 'Payment Plan Approval',
      description: 'Suggested 3-month payment plan for Rachel Levi (₪2,400 total)',
      priority: 'high',
      timestamp: '25 minutes ago'
    },
    {
      id: 3,
      agent: 'Sarah',
      type: 'treatment_plan',
      title: 'Treatment Plan Approval',
      description: 'Complex treatment plan for David Cohen: Root canal + crown. Estimated cost: ₪3,200',
      priority: 'high',
      timestamp: '15 minutes ago'
    },
    {
      id: 4,
      agent: 'Sophia',
      type: 'inventory_order',
      title: 'Inventory Reorder',
      description: 'Dental gloves stock low (12 boxes remaining). Recommend ordering 50 boxes.',
      priority: 'low',
      timestamp: '1 hour ago'
    }
  ]);

  const handleApprove = (id) => {
    setDecisions(decisions.filter(d => d.id !== id));
    alert(t("landing.demo.decisionApproved"));
  };

  const handleReject = (id) => {
    setDecisions(decisions.filter(d => d.id !== id));
    alert(t("landing.demo.decisionRejected"));
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff4444';
      case 'medium': return '#ffaa00';
      case 'low': return '#00aa00';
      default: return '#888';
    }
  };

  return (
    <div className="widget pending-decisions-widget">
      <div className="widget-header">
        <h3>⏳ {t("landing.demo.pendingDecisions")}</h3>
        <span className="badge">{decisions.length}</span>
      </div>
      <div className="widget-content">
        {decisions.length === 0 ? (
          <div className="empty-state">
            <p>✅ {t("landing.demo.noPendingDecisions")}</p>
            <p className="text-sm">{t("landing.demo.allReviewed")}</p>
          </div>
        ) : (
          <div className="decisions-list">
            {decisions.map(decision => (
              <div key={decision.id} className="decision-card">
                <div className="decision-header">
                  <span className="agent-badge">{decision.agent}</span>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(decision.priority) }}
                  >
                    {decision.priority}
                  </span>
                </div>
                <h4>{decision.title}</h4>
                <p>{decision.description}</p>
                <div className="decision-footer">
                  <span className="timestamp">{decision.timestamp}</span>
                  <div className="decision-actions">
                    <button 
                      className="btn-approve"
                      onClick={() => handleApprove(decision.id)}
                    >
                      ✓ Approve
                    </button>
                    <button 
                      className="btn-reject"
                      onClick={() => handleReject(decision.id)}
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Agent Activity Widget
 * Shows real-time AI agent activity
 */
const AgentActivityWidget = () => {
  const [activities, setActivities] = useState([
    {
      id: 1,
      agent: 'Alex',
      action: 'Sent appointment reminder',
      patient: 'David Cohen',
      status: 'completed',
      timestamp: '2 min ago'
    },
    {
      id: 2,
      agent: 'Marcus',
      action: 'Generated invoice',
      patient: 'Rachel Levi',
      status: 'completed',
      timestamp: '5 min ago'
    },
    {
      id: 3,
      agent: 'Sarah',
      action: 'Reviewing treatment plan',
      patient: 'Tamar Shapiro',
      status: 'in_progress',
      timestamp: 'Just now'
    },
    {
      id: 4,
      agent: 'Sophia',
      action: 'Checking inventory levels',
      patient: null,
      status: 'in_progress',
      timestamp: 'Just now'
    }
  ]);

  useEffect(() => {
    // Simulate real-time activity updates
    const interval = setInterval(() => {
      const newActivity = {
        id: Date.now(),
        agent: ['Alex', 'Marcus', 'Sarah', 'Sophia'][Math.floor(Math.random() * 4)],
        action: [
          'Sent SMS reminder',
          'Updated patient record',
          'Processed payment',
          'Scheduled follow-up'
        ][Math.floor(Math.random() * 4)],
        patient: ['David Cohen', 'Rachel Levi', 'Sarah Johnson'][Math.floor(Math.random() * 3)],
        status: 'completed',
        timestamp: 'Just now'
      };
      
      setActivities(prev => [newActivity, ...prev.slice(0, 9)]);
    }, 15000); // New activity every 15 seconds

    return () => clearInterval(interval);
  }, []);

  const getAgentColor = (agent) => {
    const colors = {
      'Alex': '#3b82f6',
      'Marcus': '#10b981',
      'Sarah': '#f59e0b',
      'Sophia': '#8b5cf6'
    };
    return colors[agent] || '#888';
  };

  return (
    <div className="widget agent-activity-widget">
      <div className="widget-header">
        <h3>🤖 {t("landing.demo.agentActivity")}</h3>
        <span className="live-indicator">● LIVE</span>
      </div>
      <div className="widget-content">
        <div className="activity-stream">
          {activities.map(activity => (
            <div key={activity.id} className="activity-item">
              <div 
                className="activity-dot"
                style={{ backgroundColor: getAgentColor(activity.agent) }}
              />
              <div className="activity-details">
                <div className="activity-agent">{activity.agent}</div>
                <div className="activity-action">{activity.action}</div>
                {activity.patient && (
                  <div className="activity-patient">Patient: {activity.patient}</div>
                )}
                <div className="activity-timestamp">{activity.timestamp}</div>
              </div>
              {activity.status === 'in_progress' && (
                <div className="activity-status">
                  <div className="spinner-small"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Fine-Tuning Widget
 * Shows AI agent configuration and performance
 */
const FineTuningWidget = () => {
  const [agents, setAgents] = useState([
    {
      name: 'Alex',
      role: 'Patient Experience',
      performance: 94,
      conversations: 1247,
      satisfaction: 4.8,
      enabled: true
    },
    {
      name: 'Marcus',
      role: 'Financial Intelligence',
      performance: 91,
      conversations: 856,
      satisfaction: 4.7,
      enabled: true
    },
    {
      name: 'Sarah',
      role: 'Clinical Support',
      performance: 96,
      conversations: 623,
      satisfaction: 4.9,
      enabled: true
    },
    {
      name: 'Sophia',
      role: 'Operations',
      performance: 89,
      conversations: 445,
      satisfaction: 4.6,
      enabled: true
    }
  ]);

  const toggleAgent = (name) => {
    setAgents(agents.map(agent => 
      agent.name === name 
        ? { ...agent, enabled: !agent.enabled }
        : agent
    ));
  };

  return (
    <div className="widget fine-tuning-widget">
      <div className="widget-header">
        <h3>⚙️ AI Fine-Tuning</h3>
      </div>
      <div className="widget-content">
        <div className="agents-grid">
          {agents.map(agent => (
            <div key={agent.name} className={`agent-card ${!agent.enabled ? 'disabled' : ''}`}>
              <div className="agent-card-header">
                <div>
                  <h4>{agent.name}</h4>
                  <p className="agent-role">{agent.role}</p>
                </div>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={agent.enabled}
                    onChange={() => toggleAgent(agent.name)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
              <div className="agent-metrics">
                <div className="metric">
                  <span className="metric-label">Performance</span>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${agent.performance}%` }}
                    />
                  </div>
                  <span className="metric-value">{agent.performance}%</span>
                </div>
                <div className="metric-row">
                  <div className="metric-small">
                    <span className="metric-label">Conversations</span>
                    <span className="metric-value">{agent.conversations}</span>
                  </div>
                  <div className="metric-small">
                    <span className="metric-label">Satisfaction</span>
                    <span className="metric-value">⭐ {agent.satisfaction}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Transparency Panel Demo
 * Shows AI decision-making process
 */
const TransparencyPanelDemo = () => {
  const [selectedDecision, setSelectedDecision] = useState(0);
  
  const decisions = [
    {
      title: 'Appointment Rescheduling',
      agent: 'Alex',
      timestamp: '10 minutes ago',
      reasoning: [
        {
          step: 1,
          thought: 'Patient requested to reschedule from Oct 25 to Oct 27',
          confidence: 100
        },
        {
          step: 2,
          thought: 'Checked doctor availability for Oct 27 at 10:00 AM',
          confidence: 95
        },
        {
          step: 3,
          thought: 'Verified no conflicts with existing appointments',
          confidence: 98
        },
        {
          step: 4,
          thought: 'Recommended approval based on availability and patient preference',
          confidence: 92
        }
      ],
      tools_used: ['check_availability', 'get_patient_history', 'send_notification'],
      outcome: 'Pending approval'
    },
    {
      title: 'Payment Plan Creation',
      agent: 'Marcus',
      timestamp: '25 minutes ago',
      reasoning: [
        {
          step: 1,
          thought: 'Patient has outstanding balance of ₪2,400',
          confidence: 100
        },
        {
          step: 2,
          thought: 'Analyzed patient payment history - consistent on-time payments',
          confidence: 94
        },
        {
          step: 3,
          thought: 'Calculated 3-month plan: ₪800/month based on patient income estimate',
          confidence: 88
        },
        {
          step: 4,
          thought: 'Recommended approval with standard terms',
          confidence: 91
        }
      ],
      tools_used: ['get_patient_balance', 'analyze_payment_history', 'create_payment_plan'],
      outcome: 'Pending approval'
    },
    {
      title: 'Treatment Plan Analysis',
      agent: 'Sarah',
      timestamp: '15 minutes ago',
      reasoning: [
        {
          step: 1,
          thought: 'Patient David Cohen reports severe tooth pain in lower right molar',
          confidence: 100
        },
        {
          step: 2,
          thought: 'Reviewed X-rays: Deep cavity reaching pulp chamber - root canal required',
          confidence: 97
        },
        {
          step: 3,
          thought: 'Assessed tooth structure: Crown needed post-treatment to prevent fracture',
          confidence: 95
        },
        {
          step: 4,
          thought: 'Recommended immediate treatment: Root canal + crown. Total cost: ₪3,200',
          confidence: 93
        }
      ],
      tools_used: ['review_xrays', 'analyze_symptoms', 'estimate_treatment_cost'],
      outcome: 'Pending approval'
    }
  ];

  const decision = decisions[selectedDecision];

  return (
    <div className="transparency-panel-demo">
      <h3>🔍 {t("landing.demo.aiTransparency")}</h3>
      <p className="panel-subtitle">See how AI agents make decisions</p>
      
      <div className="decision-selector">
        {decisions.map((d, index) => (
          <button
            key={index}
            className={`decision-tab ${selectedDecision === index ? 'active' : ''}`}
            onClick={() => setSelectedDecision(index)}
          >
            {d.title}
          </button>
        ))}
      </div>

      <div className="decision-details">
        <div className="decision-meta">
          <span className="agent-badge">{decision.agent}</span>
          <span className="timestamp">{decision.timestamp}</span>
        </div>

        <h4>Reasoning Process</h4>
        <div className="reasoning-steps">
          {decision.reasoning.map((step) => (
            <div key={step.step} className="reasoning-step">
              <div className="step-number">{step.step}</div>
              <div className="step-content">
                <p>{step.thought}</p>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${step.confidence}%` }}
                  />
                  <span className="confidence-label">{step.confidence}% confidence</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <h4>Tools Used</h4>
        <div className="tools-used">
          {decision.tools_used.map((tool, index) => (
            <span key={index} className="tool-badge">{tool}</span>
          ))}
        </div>

        <div className="decision-outcome">
          <strong>Outcome:</strong> {decision.outcome}
        </div>
      </div>
    </div>
  );
};

// ==================== DASHBOARD PAGES ====================

const DemoDashboardEnhanced = () => {
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">Loading dashboard...</div>;
  }

  const { financialSummary, patients, appointments } = demoData;
  const activePatients = patients.filter(p => p.status === 'Active').length;
  const upcomingAppointments = appointments.length;

  return (
    <div className="demo-dashboard-enhanced">
      <h2>AI-Powered Dashboard</h2>
      <p className="dashboard-subtitle">Real-time insights powered by 4 AI agents</p>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-label">Total Revenue</div>
            <div className="metric-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
            <div className="metric-change positive">+12% from last month</div>
            <div className="metric-agent">Tracked by Marcus 🤖</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <div className="metric-label">Active Patients</div>
            <div className="metric-value">{activePatients}</div>
            <div className="metric-change positive">+2 new this week</div>
            <div className="metric-agent">Managed by Alex 🤖</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📅</div>
          <div className="metric-content">
            <div className="metric-label">Upcoming Appointments</div>
            <div className="metric-value">{upcomingAppointments}</div>
            <div className="metric-change neutral">Next 7 days</div>
            <div className="metric-agent">Scheduled by Alex 🤖</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <div className="metric-label">Outstanding Balance</div>
            <div className="metric-value">₪{financialSummary.outstandingBalance.toLocaleString()}</div>
            <div className="metric-change negative">{financialSummary.unpaidInvoices} unpaid invoices</div>
            <div className="metric-agent">Monitored by Marcus 🤖</div>
          </div>
        </div>
      </div>

      {/* AI Insights */}
      <div className="ai-insights-section">
        <h3>🤖 AI Insights & Recommendations</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Marcus</span>
              <span className="insight-priority high">High Priority</span>
            </div>
            <h4>Revenue Opportunity Detected</h4>
            <p>3 patients are due for routine checkups. Estimated revenue: ₪1,800</p>
            <button className="insight-action">Contact Patients</button>
          </div>

          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Sarah</span>
              <span className="insight-priority high">High Priority</span>
            </div>
            <h4>Urgent Treatment Required</h4>
            <p>Patient David Cohen needs immediate root canal treatment. Delay may cause complications.</p>
            <button className="insight-action">Schedule Treatment</button>
          </div>

          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Sophia</span>
              <span className="insight-priority medium">Medium Priority</span>
            </div>
            <h4>Inventory Alert</h4>
            <p>Dental gloves running low (12 boxes left). Recommend reordering soon.</p>
            <button className="insight-action">Create Order</button>
          </div>

          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Alex</span>
              <span className="insight-priority low">Low Priority</span>
            </div>
            <h4>Patient Satisfaction</h4>
            <p>Average satisfaction score increased to 4.8/5 this month (+0.3)</p>
            <button className="insight-action">View Details</button>
          </div>
        </div>
      </div>
    </div>
  );
};

const DemoPatientsEnhanced = () => {
  const { demoData } = useDemoContext();
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [activeTab, setActiveTab] = useState('overview');

  if (!demoData) {
    return <div className="demo-loading">Loading patients...</div>;
  }

  const { patients } = demoData;

  // Filter patients based on search query and status
  const filteredPatients = patients.filter(patient => {
    const matchesSearch = 
      patient.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.phone.includes(searchQuery);
    
    const matchesStatus = 
      filterStatus === 'all' || 
      patient.status.toLowerCase() === filterStatus.toLowerCase();
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="demo-patients-enhanced">
      <h2>AI-Assisted Patient Management</h2>
      <p className="page-subtitle">Alex monitors all patient interactions</p>

      {/* Search and Filter Bar */}
      <div className="patients-search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="Search by name, phone, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button 
              className="clear-search"
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
            onClick={() => setFilterStatus('all')}
          >
            All ({patients.length})
          </button>
          <button
            className={`filter-btn ${filterStatus === 'active' ? 'active' : ''}`}
            onClick={() => setFilterStatus('active')}
          >
            Active ({patients.filter(p => p.status === 'Active').length})
          </button>
          <button
            className={`filter-btn ${filterStatus === 'inactive' ? 'active' : ''}`}
            onClick={() => setFilterStatus('inactive')}
          >
            Inactive ({patients.filter(p => p.status === 'Inactive').length})
          </button>
        </div>
      </div>

      {/* Results count */}
      {searchQuery && (
        <div className="search-results-info">
          Found {filteredPatients.length} patient{filteredPatients.length !== 1 ? 's' : ''}
        </div>
      )}

      <div className="patients-container">
        <div className="patients-list">
          {filteredPatients.length === 0 ? (
            <div className="no-results">
              <p>No patients found matching your search.</p>
              <button onClick={() => { setSearchQuery(''); setFilterStatus('all'); }}>Clear filters</button>
            </div>
          ) : (
            filteredPatients.map((patient) => (
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
          ))
          )}
        </div>

        {selectedPatient && (
          <div className="patient-profile">
            <div className="patient-profile-header">
              <div className="patient-profile-info">
                <div className="patient-avatar-large">{selectedPatient.name.charAt(0)}</div>
                <div>
                  <h3>{selectedPatient.name}</h3>
                  <p className="patient-meta">Age: {selectedPatient.age || 'N/A'} | Last Visit: {selectedPatient.lastVisit}</p>
                </div>
              </div>
              <button className="close-profile" onClick={() => setSelectedPatient(null)}>✕</button>
            </div>

            {/* Profile Tabs */}
            <div className="profile-tabs">
              <button 
                className={`profile-tab ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                📋 Overview
              </button>
              <button 
                className={`profile-tab ${activeTab === 'clinical' ? 'active' : ''}`}
                onClick={() => setActiveTab('clinical')}
              >
                🦷 Clinical
              </button>
              <button 
                className={`profile-tab ${activeTab === 'appointments' ? 'active' : ''}`}
                onClick={() => setActiveTab('appointments')}
              >
                📅 Appointments
              </button>
              <button 
                className={`profile-tab ${activeTab === 'billing' ? 'active' : ''}`}
                onClick={() => setActiveTab('billing')}
              >
                💰 Billing
              </button>
            </div>

            {/* Tab Content */}
            <div className="profile-tab-content">
              {activeTab === 'overview' && (
                <div className="profile-overview">
                  <div className="ai-summary">
                    <h4>🤖 AI Summary</h4>
                    <p>Alex has sent 3 appointment reminders and 2 follow-up messages this month.</p>
                    <p>Last interaction: Confirmed appointment for Oct 25</p>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Email:</span>
                    <span className="detail-value">{selectedPatient.email}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Phone:</span>
                    <span className="detail-value">{selectedPatient.phone}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Status:</span>
                    <span className="detail-value">{selectedPatient.status}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Balance:</span>
                    <span className="detail-value">₪{selectedPatient.balance}</span>
                  </div>
                  <div className="detail-actions">
                    <button className="btn-primary">💬 Chat with Alex</button>
                    <button className="btn-secondary">📅 Schedule Appointment</button>
                  </div>
                </div>
              )}

              {activeTab === 'clinical' && (
                <div className="profile-clinical">
                  <ClinicalDashboard patient={selectedPatient} />
                </div>
              )}

              {activeTab === 'appointments' && (
                <div className="profile-appointments">
                  <h4>Upcoming Appointments</h4>
                  <div className="appointment-item">
                    <div className="appointment-date">Oct 25, 2025 - 10:00 AM</div>
                    <div className="appointment-type">Regular Checkup</div>
                    <div className="appointment-status">Confirmed</div>
                  </div>
                  <div className="appointment-item">
                    <div className="appointment-date">Nov 15, 2025 - 2:00 PM</div>
                    <div className="appointment-type">Cleaning</div>
                    <div className="appointment-status">Scheduled</div>
                  </div>
                </div>
              )}

              {activeTab === 'billing' && (
                <div className="profile-billing">
                  <h4>Billing History</h4>
                  <div className="billing-summary">
                    <div className="billing-stat">
                      <span className="billing-label">Total Billed:</span>
                      <span className="billing-value">₪{selectedPatient.totalBilled || 5200}</span>
                    </div>
                    <div className="billing-stat">
                      <span className="billing-label">Total Paid:</span>
                      <span className="billing-value">₪{(selectedPatient.totalBilled || 5200) - selectedPatient.balance}</span>
                    </div>
                    <div className="billing-stat">
                      <span className="billing-label">Outstanding:</span>
                      <span className="billing-value">₪{selectedPatient.balance}</span>
                    </div>
                  </div>
                  <h4>Recent Invoices</h4>
                  <div className="invoice-item">
                    <div className="invoice-date">Sep 15, 2025</div>
                    <div className="invoice-desc">Root Canal Treatment</div>
                    <div className="invoice-amount">₪2,400</div>
                    <div className="invoice-status paid">Paid</div>
                  </div>
                  <div className="invoice-item">
                    <div className="invoice-date">Aug 10, 2025</div>
                    <div className="invoice-desc">Regular Checkup</div>
                    <div className="invoice-amount">₪{selectedPatient.balance}</div>
                    <div className="invoice-status unpaid">Unpaid</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const DemoAppointmentsEnhanced = () => {
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">Loading appointments...</div>;
  }

  const { appointments } = demoData;

  return (
    <div className="demo-appointments-enhanced">
      <h2>AI-Managed Appointments</h2>
      <p className="page-subtitle">Alex handles all scheduling and reminders automatically</p>

      <div className="appointments-list">
        {appointments.map((apt, index) => (
          <div key={index} className="appointment-card">
            <div className="appointment-time">
              <div className="time-label">{apt.time}</div>
              <div className="date-label">{apt.date}</div>
            </div>
            <div className="appointment-details">
              <h4>{apt.patientName}</h4>
              <p>{apt.treatmentType}</p>
              <p className="doctor">Dr. {apt.doctor}</p>
            </div>
            <div className="appointment-ai-status">
              <span className="ai-badge">✅ Reminder sent by Alex</span>
              <span className="ai-badge">📧 Confirmed via email</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const DemoFinancialEnhanced = () => {
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">Loading financial data...</div>;
  }

  const { financialSummary } = demoData;

  return (
    <div className="demo-financial-enhanced">
      <h2>AI Financial Intelligence</h2>
      <p className="page-subtitle">Marcus provides real-time financial insights</p>

      <div className="financial-summary">
        <div className="summary-card">
          <h3>Monthly Revenue</h3>
          <div className="summary-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
          <div className="summary-trend positive">+12% vs last month</div>
          <p className="ai-insight">🤖 Marcus predicts ₪48,000 next month based on scheduled appointments</p>
        </div>

        <div className="summary-card">
          <h3>Outstanding Balance</h3>
          <div className="summary-value">₪{financialSummary.outstandingBalance.toLocaleString()}</div>
          <div className="summary-trend negative">{financialSummary.unpaidInvoices} unpaid invoices</div>
          <p className="ai-insight">🤖 Marcus recommends sending payment reminders to 3 patients</p>
        </div>

        <div className="summary-card">
          <h3>Collection Rate</h3>
          <div className="summary-value">87%</div>
          <div className="summary-trend positive">+3% vs last month</div>
          <p className="ai-insight">🤖 Marcus automated 15 payment reminders this month</p>
        </div>
      </div>
    </div>
  );
};

const DemoClinicalEnhanced = () => {
  const [selectedPatient] = useState({
    id: 1,
    name: 'David Cohen',
    age: 45,
    lastVisit: '2025-09-15'
  });

  return (
    <div className="demo-clinical-enhanced">
      <h2>🩺 AI-Powered Clinical System</h2>
      <p className="page-subtitle">Sarah provides intelligent clinical analysis and recommendations</p>
      
      <div className="clinical-patient-header">
        <div className="patient-info">
          <h3>{selectedPatient.name}</h3>
          <p>Age: {selectedPatient.age} | Last Visit: {selectedPatient.lastVisit}</p>
        </div>
      </div>

      <ClinicalDashboard patient={selectedPatient} />
    </div>
  );
};

export default DemoPortalEnhanced;

