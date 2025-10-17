import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useDemoContext } from '../contexts/DemoContext';
import DemoChatButton from '../components/DemoChatButton';
import {t("landing.demo.clinical")}Dashboard from '../components/clinical/{t("landing.demo.clinical")}Dashboard';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './DemoPortalEnhanced.css';/**
 * Enhanced Demo Portal - Showcases AI {t("landing.demo.age")}nt Features
 * 
 * This demo portal includes all the AI agent features from production:
 * - Pending Decisions Widget
 * - {t("landing.demo.age")}nt Activity Monitor
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
    if (window.confirm(t('landing.demo.exitConfirm'))) {
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
          <div className="demo-badge">{t("landing.demo.demoMode")}</div>
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
          <{t("landing.demo.age")}ntActivityWidget />
          <FineTuningWidget />
        </div>

        {/* Center - Dashboard Content */}
        <div className="demo-center-content">
          <div className="demo-nav">
            <button
              className={`demo-nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 {t("landing.demo.dashboard")}
            </button>
            <button
              className={`demo-nav-btn ${currentPage === 'patients' ? 'active' : ''}`}
              onClick={() => setCurrentPage('patients')}
            >
              👥 {t("landing.demo.patients")}
            </button>
            <button
              className={`demo-nav-btn ${currentPage === 'appointments' ? 'active' : ''}`}
              onClick={() => setCurrentPage('appointments')}
            >
              📅 {t("landing.demo.appointments")}
            </button>
            <button
              className={`demo-nav-btn ${currentPage === 'financial' ? 'active' : ''}`}
              onClick={() => setCurrentPage('financial')}
            >
              💰 {t("landing.demo.financial")}
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
      title: t('landing.demo.rescheduleAppointment'),
      description: 'Patient Sarah Johnson requested to move appointment from Oct 25 to Oct 27',
      priority: t('landing.demo.medium'),
      timestamp: '10 {t("landing.demo.minutesAgo")}'
    },
    {
      id: 2,
      agent: 'Marcus',
      type: 'payment_plan',
      title: t('landing.demo.paymentPlanApproval'),
      description: 'Suggested 3-month payment plan for Rachel Levi (₪2,400 total)',
      priority: t('landing.demo.high'),
      timestamp: '25 {t("landing.demo.minutesAgo")}'
    },
    {
      id: 3,
      agent: 'Sarah',
      type: 'treatment_plan',
      title: t('landing.demo.treatmentPlanApproval'),
      description: 'Complex treatment plan for David Cohen: Root canal + crown. Estimated cost: ₪3,200',
      priority: t('landing.demo.high'),
      timestamp: '15 {t("landing.demo.minutesAgo")}'
    },
    {
      id: 4,
      agent: 'Sophia',
      type: 'inventory_order',
      title: t('landing.demo.inventoryReorder'),
      description: 'Dental gloves stock low (12 boxes {t("landing.demo.remaining")}). Recommend ordering 50 boxes.',
      priority: t('landing.demo.low'),
      timestamp: '1 {t("landing.demo.hourAgo")}'
    }
  ]);

  const handleApprove = (id) => {
    setDecisions(decisions.filter(d => d.id !== id));
    alert(t('landing.demo.decisionApproved'));
  };

  const handleReject = (id) => {
    setDecisions(decisions.filter(d => d.id !== id));
    alert(t('landing.demo.decisionRejected'));
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case t('landing.demo.high'): return '#ff4444';
      case t('landing.demo.medium'): return '#ffaa00';
      case t('landing.demo.low'): return '#00aa00';
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
                      ✓ {t("landing.demo.approve")}
                    </button>
                    <button 
                      className="btn-reject"
                      onClick={() => handleReject(decision.id)}
                    >
                      ✗ {t("landing.demo.reject")}
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
 * {t("landing.demo.age")}nt Activity Widget
 * Shows real-time AI agent activity
 */
const {t("landing.demo.age")}ntActivityWidget = () => {
  const [activities, setActivities] = useState([
    {
      id: 1,
      agent: 'Alex',
      action: t('landing.demo.sentAppointmentReminder'),
      {t("landing.demo.patient")}: 'David Cohen',
      status: t('landing.demo.completed'),
      timestamp: '2 min ago'
    },
    {
      id: 2,
      agent: 'Marcus',
      action: t('landing.demo.generatedInvoice'),
      {t("landing.demo.patient")}: 'Rachel Levi',
      status: t('landing.demo.completed'),
      timestamp: '5 min ago'
    },
    {
      id: 3,
      agent: 'Sarah',
      action: t('landing.demo.reviewingTreatmentPlan'),
      {t("landing.demo.patient")}: 'Tamar Shapiro',
      status: t('landing.demo.inProgress'),
      timestamp: '{t("landing.demo.justNow")}'
    },
    {
      id: 4,
      agent: 'Sophia',
      action: t('landing.demo.checkingInventory'),
      {t("landing.demo.patient")}: null,
      status: t('landing.demo.inProgress'),
      timestamp: '{t("landing.demo.justNow")}'
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
          'Updated {t("landing.demo.patient")} record',
          'Processed payment',
          'Scheduled follow-up'
        ][Math.floor(Math.random() * 4)],
        {t("landing.demo.patient")}: ['David Cohen', 'Rachel Levi', 'Sarah Johnson'][Math.floor(Math.random() * 3)],
        status: t('landing.demo.completed'),
        timestamp: '{t("landing.demo.justNow")}'
      };
      
      setActivities(prev => [newActivity, ...prev.slice(0, 9)]);
    }, 15000); // New activity every 15 seconds

    return () => clearInterval(interval);
  }, []);

  const get{t("landing.demo.age")}ntColor = (agent) => {
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
        <span className="live-indicator">● {t("landing.demo.live")}</span>
      </div>
      <div className="widget-content">
        <div className="activity-stream">
          {activities.map(activity => (
            <div key={activity.id} className="activity-item">
              <div 
                className="activity-dot"
                style={{ backgroundColor: get{t("landing.demo.age")}ntColor(activity.agent) }}
              />
              <div className="activity-details">
                <div className="activity-agent">{activity.agent}</div>
                <div className="activity-action">{activity.action}</div>
                {activity.patient && (
                  <div className="activity-patient">Patient: {activity.patient}</div>
                )}
                <div className="activity-timestamp">{activity.timestamp}</div>
              </div>
              {activity.status === t('landing.demo.inProgress') && (
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
  const [agents, set{t("landing.demo.age")}nts] = useState([
    {
      name: 'Alex',
      role: '{t("landing.demo.patientExperience")}',
      performance: 94,
      conversations: 1247,
      satisfaction: 4.8,
      enabled: true
    },
    {
      name: 'Marcus',
      role: '{t("landing.demo.financialIntelligence")}',
      performance: 91,
      conversations: 856,
      satisfaction: 4.7,
      enabled: true
    },
    {
      name: 'Sarah',
      role: '{t("landing.demo.clinicalSupport")}',
      performance: 96,
      conversations: 623,
      satisfaction: 4.9,
      enabled: true
    },
    {
      name: 'Sophia',
      role: '{t("landing.demo.operations")}',
      performance: 89,
      conversations: 445,
      satisfaction: 4.6,
      enabled: true
    }
  ]);

  const toggle{t("landing.demo.age")}nt = (name) => {
    set{t("landing.demo.age")}nts(agents.map(agent => 
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
                    onChange={() => toggle{t("landing.demo.age")}nt(agent.name)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
              <div className="agent-metrics">
                <div className="metric">
                  <span className="metric-label">{t("landing.demo.performance")}</span>
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
                    <span className="metric-label">{t("landing.demo.conversations")}</span>
                    <span className="metric-value">{agent.conversations}</span>
                  </div>
                  <div className="metric-small">
                    <span className="metric-label">{t("landing.demo.satisfaction")}</span>
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
      timestamp: '10 {t("landing.demo.minutesAgo")}',
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
          thought: 'Recommended approval based on availability and {t("landing.demo.patient")} preference',
          confidence: 92
        }
      ],
      tools_used: ['check_availability', 'get_patient_history', 'send_notification'],
      outcome: 'Pending approval'
    },
    {
      title: 'Payment Plan Creation',
      agent: 'Marcus',
      timestamp: '25 {t("landing.demo.minutesAgo")}',
      reasoning: [
        {
          step: 1,
          thought: 'Patient has outstanding balance of ₪2,400',
          confidence: 100
        },
        {
          step: 2,
          thought: 'Analyzed {t("landing.demo.patient")} payment history - consistent on-time payments',
          confidence: 94
        },
        {
          step: 3,
          thought: 'Calculated 3-month plan: ₪800/month based on {t("landing.demo.patient")} income estimate',
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
      timestamp: '15 {t("landing.demo.minutesAgo")}',
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
      <p className="panel-subtitle">{t("landing.demo.seeHowAI")}</p>
      
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

        <h4>{t("landing.demo.reasoningProcess")}</h4>
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

        <h4>{t("landing.demo.toolsUsed")}</h4>
        <div className="tools-used">
          {decision.tools_used.map((tool, index) => (
            <span key={index} className="tool-badge">{tool}</span>
          ))}
        </div>

        <div className="decision-outcome">
          <strong>{t("landing.demo.outcome")}:</strong> {decision.outcome}
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

  const { financialSummary, {t("landing.demo.patient")}s, appointments } = demoData;
  const activePatients = {t("landing.demo.patient")}s.filter(p => p.status === '{t("landing.demo.active")}').length;
  const upcomingAppointments = appointments.length;

  return (
    <div className="demo-dashboard-enhanced">
      <h2>{t("landing.demo.aiPoweredDashboard")}</h2>
      <p className="dashboard-subtitle">{t("landing.demo.realTimeInsights")}</p>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-label">{t("landing.demo.totalRevenue")}</div>
            <div className="metric-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
            <div className="metric-change positive">+12% {t("landing.demo.fromLastMonth")}</div>
            <div className="metric-agent">{t("landing.demo.trackedBy")} Marcus 🤖</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <div className="metric-label">{t("landing.demo.activePatients")}</div>
            <div className="metric-value">{activePatients}</div>
            <div className="metric-change positive">+2 {t("landing.demo.newThisWeek")}</div>
            <div className="metric-agent">{t("landing.demo.managedBy")} Alex 🤖</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📅</div>
          <div className="metric-content">
            <div className="metric-label">{t("landing.demo.upcomingAppointments")}</div>
            <div className="metric-value">{upcomingAppointments}</div>
            <div className="metric-change neutral">Next 7 days</div>
            <div className="metric-agent">{t("landing.demo.scheduledBy")} Alex 🤖</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⚠️</div>
          <div className="metric-content">
            <div className="metric-label">{t("landing.demo.outstanding{t("landing.demo.balance")}")}</div>
            <div className="metric-value">₪{financialSummary.outstanding{t("landing.demo.balance")}.toLocaleString()}</div>
            <div className="metric-change negative">{financialSummary.unpaidInvoices} {t("landing.demo.unpaidInvoices")}</div>
            <div className="metric-agent">{t("landing.demo.monitoredBy")} Marcus 🤖</div>
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
              <span className="insight-priority high">{t("landing.demo.highPriority")}</span>
            </div>
            <h4>Revenue Opportunity Detected</h4>
            <p>3 {t("landing.demo.patient")}s are due for routine checkups. Estimated revenue: ₪1,800</p>
            <button className="insight-action">{t("landing.demo.contactPatients")}</button>
          </div>

          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Sarah</span>
              <span className="insight-priority high">{t("landing.demo.highPriority")}</span>
            </div>
            <h4>Urgent Treatment Required</h4>
            <p>Patient David Cohen needs immediate root canal treatment. Delay may cause complications.</p>
            <button className="insight-action">{t("landing.demo.scheduleTreatment")}</button>
          </div>

          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Sophia</span>
              <span className="insight-priority medium">{t("landing.demo.mediumPriority")}</span>
            </div>
            <h4>Inventory Alert</h4>
            <p>Dental gloves running low (12 boxes left). Recommend reordering soon.</p>
            <button className="insight-action">{t("landing.demo.createOrder")}</button>
          </div>

          <div className="insight-card">
            <div className="insight-header">
              <span className="agent-badge">Alex</span>
              <span className="insight-priority low">{t("landing.demo.lowPriority")}</span>
            </div>
            <h4>Patient {t("landing.demo.satisfaction")}</h4>
            <p>Average satisfaction score increased to 4.8/5 this month (+0.3)</p>
            <button className="insight-action">{t("landing.demo.viewDetails")}</button>
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
  const [filter{t("landing.demo.status")}, setFilter{t("landing.demo.status")}] = useState('all');
  const [activeTab, set{t("landing.demo.active")}Tab] = useState('overview');

  if (!demoData) {
    return <div className="demo-loading">Loading {t("landing.demo.patient")}s...</div>;
  }

  const { {t("landing.demo.patient")}s } = demoData;

  // Filter {t("landing.demo.patient")}s based on search query and status
  const filteredPatients = {t("landing.demo.patient")}s.filter(patient => {
    const matchesSearch = 
      {t("landing.demo.patient")}.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      {t("landing.demo.patient")}.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      {t("landing.demo.patient")}.phone.includes(searchQuery);
    
    const matches{t("landing.demo.status")} = 
      filter{t("landing.demo.status")} === 'all' || 
      {t("landing.demo.patient")}.status.toLowerCase() === filter{t("landing.demo.status")}.toLowerCase();
    
    return matchesSearch && matches{t("landing.demo.status")};
  });

  return (
    <div className="demo-patients-enhanced">
      <h2>AI-Assisted Patient Management</h2>
      <p className="page-subtitle">{t("landing.demo.alexMonitors")}</p>

      {/* Search and Filter Bar */}
      <div className="patients-search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder="{t("landing.demo.searchByName")}"
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
            className={`filter-btn ${filter{t("landing.demo.status")} === 'all' ? 'active' : ''}`}
            onClick={() => setFilter{t("landing.demo.status")}('all')}
          >
            {t("landing.demo.all")} ({patients.length})
          </button>
          <button
            className={`filter-btn ${filter{t("landing.demo.status")} === 'active' ? 'active' : ''}`}
            onClick={() => setFilter{t("landing.demo.status")}('active')}
          >
            {t("landing.demo.active")} ({patients.filter(p => p.status === '{t("landing.demo.active")}').length})
          </button>
          <button
            className={`filter-btn ${filter{t("landing.demo.status")} === 'inactive' ? 'active' : ''}`}
            onClick={() => setFilter{t("landing.demo.status")}('inactive')}
          >
            {t("landing.demo.inactive")} ({patients.filter(p => p.status === '{t("landing.demo.inactive")}').length})
          </button>
        </div>
      </div>

      {/* Results count */}
      {searchQuery && (
        <div className="search-results-info">
          Found {filteredPatients.length} {t("landing.demo.patient")}{filteredPatients.length !== 1 ? 's' : ''}
        </div>
      )}

      <div className="patients-container">
        <div className="patients-list">
          {filteredPatients.length === 0 ? (
            <div className="no-results">
              <p>No {t("landing.demo.patient")}s {t("landing.demo.found")} matching your search.</p>
              <button onClick={() => { setSearchQuery(''); setFilter{t("landing.demo.status")}('all'); }}>Clear filters</button>
            </div>
          ) : (
            filteredPatients.map((patient) => (
            <div
              key={patient.id}
              className={`patient-card ${selectedPatient?.id === {t("landing.demo.patient")}.id ? 'selected' : ''}`}
              onClick={() => setSelectedPatient(patient)}
            >
              <div className="patient-avatar">{patient.name.charAt(0)}</div>
              <div className="patient-info">
                <div className="patient-name">{patient.name}</div>
                <div className="patient-details">
                  Last visit: {patient.lastVisit || '{t("landing.demo.never")}'}
                </div>
                {patient.balance > 0 && (
                  <div className="patient-balance">{t("landing.demo.balance")}: ₪{patient.balance}</div>
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
                  <p className="patient-meta">{t("landing.demo.age")}: {selectedPatient.age || 'N/A'} | {t("landing.demo.lastVisit")}: {selectedPatient.lastVisit}</p>
                </div>
              </div>
              <button className="close-profile" onClick={() => setSelectedPatient(null)}>✕</button>
            </div>

            {/* Profile Tabs */}
            <div className="profile-tabs">
              <button 
                className={`profile-tab ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => set{t("landing.demo.active")}Tab('overview')}
              >
                📋 {t("landing.demo.overview")}
              </button>
              <button 
                className={`profile-tab ${activeTab === 'clinical' ? 'active' : ''}`}
                onClick={() => set{t("landing.demo.active")}Tab('clinical')}
              >
                🦷 {t("landing.demo.clinical")}
              </button>
              <button 
                className={`profile-tab ${activeTab === 'appointments' ? 'active' : ''}`}
                onClick={() => set{t("landing.demo.active")}Tab('appointments')}
              >
                📅 {t("landing.demo.appointments")}
              </button>
              <button 
                className={`profile-tab ${activeTab === 'billing' ? 'active' : ''}`}
                onClick={() => set{t("landing.demo.active")}Tab('billing')}
              >
                💰 {t("landing.demo.billing")}
              </button>
            </div>

            {/* Tab Content */}
            <div className="profile-tab-content">
              {activeTab === 'overview' && (
                <div className="profile-overview">
                  <div className="ai-summary">
                    <h4>🤖 {t("landing.demo.aiSummary")}</h4>
                    <p>Alex has sent 3 appointment reminders and 2 follow-up messages this month.</p>
                    <p>Last interaction: Confirmed appointment for Oct 25</p>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("landing.demo.email")}:</span>
                    <span className="detail-value">{selectedPatient.email}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("landing.demo.phone")}:</span>
                    <span className="detail-value">{selectedPatient.phone}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("landing.demo.status")}:</span>
                    <span className="detail-value">{selectedPatient.status}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("landing.demo.balance")}:</span>
                    <span className="detail-value">₪{selectedPatient.balance}</span>
                  </div>
                  <div className="detail-actions">
                    <button className="btn-primary">💬 {t("landing.demo.chatWithAlex")}</button>
                    <button className="btn-secondary">📅 {t("landing.demo.scheduleAppointment")}</button>
                  </div>
                </div>
              )}

              {activeTab === 'clinical' && (
                <div className="profile-clinical">
                  <{t("landing.demo.clinical")}Dashboard {t("landing.demo.patient")}={selectedPatient} />
                </div>
              )}

              {activeTab === 'appointments' && (
                <div className="profile-appointments">
                  <h4>{t("landing.demo.upcomingAppointments")}</h4>
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
                  <h4>{t("landing.demo.billing")} History</h4>
                  <div className="billing-summary">
                    <div className="billing-stat">
                      <span className="billing-label">{t("landing.demo.totalBilled")}:</span>
                      <span className="billing-value">₪{selectedPatient.totalBilled || 5200}</span>
                    </div>
                    <div className="billing-stat">
                      <span className="billing-label">{t("landing.demo.total{t("landing.demo.paid")}")}:</span>
                      <span className="billing-value">₪{(selectedPatient.totalBilled || 5200) - selectedPatient.balance}</span>
                    </div>
                    <div className="billing-stat">
                      <span className="billing-label">{t("landing.demo.outstanding")}:</span>
                      <span className="billing-value">₪{selectedPatient.balance}</span>
                    </div>
                  </div>
                  <h4>{t("landing.demo.recentInvoices")}</h4>
                  <div className="invoice-item">
                    <div className="invoice-date">Sep 15, 2025</div>
                    <div className="invoice-desc">Root Canal Treatment</div>
                    <div className="invoice-amount">₪2,400</div>
                    <div className="invoice-status paid">{t("landing.demo.paid")}</div>
                  </div>
                  <div className="invoice-item">
                    <div className="invoice-date">Aug 10, 2025</div>
                    <div className="invoice-desc">Regular Checkup</div>
                    <div className="invoice-amount">₪{selectedPatient.balance}</div>
                    <div className="invoice-status unpaid">{t("landing.demo.unpaid")}</div>
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
      <h2>AI {t("landing.demo.financialIntelligence")}</h2>
      <p className="page-subtitle">Marcus provides real-time financial insights</p>

      <div className="financial-summary">
        <div className="summary-card">
          <h3>Monthly Revenue</h3>
          <div className="summary-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
          <div className="summary-trend positive">+12% vs last month</div>
          <p className="ai-insight">🤖 Marcus predicts ₪48,000 next month based on scheduled appointments</p>
        </div>

        <div className="summary-card">
          <h3>{t("landing.demo.outstanding{t("landing.demo.balance")}")}</h3>
          <div className="summary-value">₪{financialSummary.outstanding{t("landing.demo.balance")}.toLocaleString()}</div>
          <div className="summary-trend negative">{financialSummary.unpaidInvoices} {t("landing.demo.unpaidInvoices")}</div>
          <p className="ai-insight">🤖 Marcus recommends sending payment reminders to 3 {t("landing.demo.patient")}s</p>
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

const Demo{t("landing.demo.clinical")}Enhanced = () => {
  const [selectedPatient] = useState({
    id: 1,
    name: 'David Cohen',
    age: 45,
    lastVisit: '2025-09-15'
  });

  return (
    <div className="demo-clinical-enhanced">
      <h2>🩺 AI-Powered {t("landing.demo.clinical")} System</h2>
      <p className="page-subtitle">Sarah provides intelligent clinical analysis and recommendations</p>
      
      <div className="clinical-patient-header">
        <div className="patient-info">
          <h3>{selectedPatient.name}</h3>
          <p>{t("landing.demo.age")}: {selectedPatient.age} | {t("landing.demo.lastVisit")}: {selectedPatient.lastVisit}</p>
        </div>
      </div>

      <{t("landing.demo.clinical")}Dashboard {t("landing.demo.patient")}={selectedPatient} />
    </div>
  );
};

export default DemoPortalEnhanced;

