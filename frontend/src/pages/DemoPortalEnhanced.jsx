import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useDemoContext } from '../contexts/DemoContext';
import DemoChatButton from '../components/DemoChatButton';
import ClinicalDashboard from '../components/clinical/ClinicalDashboard';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import './DemoPortalEnhanced.css';
import MetricCard from '../components/demo/MetricCard';
import InsightCard from '../components/demo/InsightCard';
import DecisionCard from '../components/demo/DecisionCard';
import AgentCard from '../components/demo/AgentCard';
import TransparencyPanel from '../components/demo/TransparencyPanel';/**
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
      <div className={`demo-main-layout ${!showTransparency ? 'full-width' : ''}`}>
        {/* Left Sidebar - Widgets */}
        <div className="demo-left-sidebar">
          <PendingDecisionsWidget />
          <AgentActivityWidget />
        </div>

        {/* Center - Dashboard Content */}
        <div className="demo-center-content">
          <div className="demo-nav">
            <button
              className={`demo-nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 {t("demo.nav.dashboard")}
            </button>
            <button
              className={`demo-nav-btn ${currentPage === 'patients' ? 'active' : ''}`}
              onClick={() => setCurrentPage('patients')}
            >
              👥 {t("demo.nav.patients")}
            </button>
            <button
              className={`demo-nav-btn ${currentPage === 'appointments' ? 'active' : ''}`}
              onClick={() => setCurrentPage('appointments')}
            >
              📅 {t("demo.nav.appointments")}
            </button>
            <button
              className={`demo-nav-btn ${currentPage === 'financial' ? 'active' : ''}`}
              onClick={() => setCurrentPage('financial')}
            >
              💰 {t("demo.nav.financial")}
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
        {showTransparency && (
          <div className="demo-right-sidebar">
            <div className="demo-transparency-panel">
              <TransparencyPanelDemo />
            </div>
            <FineTuningWidget />
          </div>
        )}
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
  const { t } = useTranslation();
  const [decisions, setDecisions] = useState([
    {
      id: 1,
      agent: 'Alex',
      type: 'appointment_reschedule',
      title: t('demo.decisions.appointment_rescheduling'),
      description: t('demo.decisions.reschedule_sarah'),
      priority: 'medium',
      timestamp: t('demo.time.min_ago_10')
    },
    {
      id: 2,
      agent: 'Marcus',
      type: 'payment_plan',
      title: t('demo.decisions.payment_plan_creation'),
      description: t('demo.decisions.payment_rachel'),
      priority: 'high',
      timestamp: t('demo.time.min_ago_25')
    },
    {
      id: 3,
      agent: 'Sarah',
      type: 'treatment_plan',
      title: t('demo.decisions.treatment_plan_analysis'),
      description: t('demo.decisions.treatment_david'),
      priority: 'high',
      timestamp: t('demo.time.min_ago_15')
    },
    {
      id: 4,
      agent: 'Sophia',
      type: 'inventory_order',
      title: t('demo.decisions.inventory_gloves'),
      description: t('demo.decisions.inventory_gloves'),
      priority: 'low',
      timestamp: t('demo.time.hour_ago_1')
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
                      ✓ {t("demo.widgets.approve")}
                    </button>
                    <button 
                      className="btn-reject"
                      onClick={() => handleReject(decision.id)}
                    >
                      ✗ {t("demo.widgets.reject")}
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
  const { t } = useTranslation();
  const [activities, setActivities] = useState([
    {
      id: 1,
      agent: 'Alex',
      action: t('demo.activity.sent_reminder'),
      patient: 'David Cohen',
      status: 'completed',
      timestamp: t('demo.time.min_ago_2')
    },
    {
      id: 2,
      agent: 'Marcus',
      action: t('demo.activity.generated_invoice'),
      patient: 'Rachel Levi',
      status: 'completed',
      timestamp: t('demo.time.min_ago_5')
    },
    {
      id: 3,
      agent: 'Sarah',
      action: t('demo.activity.reviewing_plan'),
      patient: 'Tamar Shapiro',
      status: 'in_progress',
      timestamp: t('demo.time.just_now')
    },
    {
      id: 4,
      agent: 'Sophia',
      action: t('demo.activity.checking_inventory'),
      patient: null,
      status: 'in_progress',
      timestamp: t('demo.time.just_now')
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
        timestamp: t('demo.time.just_now')
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
                  <div className="activity-patient">{t('demo.patient')}: {activity.patient}</div>
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
  const { t } = useTranslation();
  const [selectedDecision, setSelectedDecision] = useState(0);
  
  const decisions = [
    {
      title: t('demo.decisions.appointment_rescheduling'),
      agent: 'Alex',
      timestamp: t('demo.time.min_ago_10'),
      reasoning: [
        {
          step: 1,
          thought: t('demo.reasoning.reschedule_step1'),
          confidence: 100
        },
        {
          step: 2,
          thought: t('demo.reasoning.reschedule_step2'),
          confidence: 95
        },
        {
          step: 3,
          thought: t('demo.reasoning.reschedule_step3'),
          confidence: 98
        },
        {
          step: 4,
          thought: t('demo.reasoning.reschedule_step4'),
          confidence: 92
        }
      ],
      tools_used: ['check_availability', 'get_patient_history', 'send_notification'],
      outcome: t('demo.status.pending')
    },
    {
      title: t('demo.decisions.payment_plan_creation'),
      agent: 'Marcus',
      timestamp: t('demo.time.min_ago_25'),
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
      outcome: t('demo.status.pending')
    },
    {
      title: t('demo.decisions.treatment_plan_analysis'),
      agent: 'Sarah',
      timestamp: t('demo.time.min_ago_15'),
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
      outcome: t('demo.status.pending')
    }
  ];

  const decision = decisions[selectedDecision];

  return (
    <div className="transparency-panel-demo">
      <h3>🔍 {t("landing.demo.aiTransparency")}</h3>
      <p className="panel-subtitle">{t('demo.transparency.see_how')}</p>
      
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

        <h4>{t('demo.transparency.reasoning_process')}</h4>
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
                  <span className="confidence-label">{step.confidence}% {t('demo.confidence')}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <h4>{t('demo.transparency.tools_used')}</h4>
        <div className="tools-used">
          {decision.tools_used.map((tool, index) => (
            <span key={index} className="tool-badge">{tool}</span>
          ))}
        </div>

        <div className="decision-outcome">
          <strong>{t('demo.transparency.outcome')}:</strong> {decision.outcome}
        </div>
      </div>
    </div>
  );
};

// ==================== DASHBOARD PAGES ====================

const DemoDashboardEnhanced = () => {
  const { t } = useTranslation();
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">{t("demo.dashboard.loading")}</div>;
  }

  const { financialSummary, patients, appointments } = demoData;
  const activePatients = patients.filter(p => p.status === 'Active').length;
  const upcomingAppointments = appointments.length;

  // Agent colors for consistency
  const agentColors = {
    Alex: '#3b82f6',
    Marcus: '#10b981',
    Sarah: '#f59e0b',
    Sophia: '#8b5cf6'
  };

  return (
    <div className="demo-dashboard-enhanced">
      <h2>{t("demo.dashboard.title")}</h2>
      <p className="dashboard-subtitle">{t("demo.dashboard.subtitle")}</p>

      {/* Metrics Cards - Using new MetricCard component */}
      <div className="metrics-grid">
        <MetricCard
          icon="💰"
          value={`₪${financialSummary.totalRevenue.toLocaleString()}`}
          label={t("demo.dashboard.metrics.totalRevenue")}
          trend={12}
          trendLabel={t("demo.dashboard.metrics.fromLastMonth")}
          agentName="Marcus"
          agentColor={agentColors.Marcus}
        />

        <MetricCard
          icon="👥"
          value={activePatients}
          label={t("demo.dashboard.metrics.activePatients")}
          trend={5}
          trendLabel={`+2 ${t("demo.dashboard.metrics.newThisWeek")}`}
          agentName="Alex"
          agentColor={agentColors.Alex}
        />

        <MetricCard
          icon="📅"
          value={upcomingAppointments}
          label={t("demo.dashboard.metrics.upcomingAppointments")}
          trendLabel={t("demo.dashboard.metrics.next7Days")}
          agentName="Alex"
          agentColor={agentColors.Alex}
        />

        <MetricCard
          icon="⚠️"
          value={`₪${financialSummary.outstandingBalance.toLocaleString()}`}
          label={t("demo.dashboard.metrics.outstandingBalance")}
          trend={-8}
          trendLabel={`${financialSummary.unpaidInvoices} ${t("demo.dashboard.metrics.unpaidInvoices")}`}
          agentName="Marcus"
          agentColor={agentColors.Marcus}
        />
      </div>

      {/* AI Insights - Using new InsightCard component */}
      <div className="ai-insights-section">
        <h3>🤖 {t("demo.dashboard.insights.title")}</h3>
        <div className="insights-grid">
          <InsightCard
            title={t("demo.dashboard.insights.revenueOpportunity")}
            description={t("demo.dashboard.insights.revenueOpportunityDesc")}
            priority="high"
            agent="Marcus"
            agentColor={agentColors.Marcus}
            actionLabel={t("demo.dashboard.insights.contactPatients")}
            onAction={() => alert('Contact patients feature - Demo')}
          />

          <InsightCard
            title={t("demo.dashboard.insights.urgentTreatment")}
            description={t("demo.dashboard.insights.urgentTreatmentDesc")}
            priority="high"
            agent="Sarah"
            agentColor={agentColors.Sarah}
            actionLabel={t("demo.dashboard.insights.scheduleTreatment")}
            onAction={() => alert('Schedule treatment feature - Demo')}
          />

          <InsightCard
            title={t("demo.dashboard.insights.inventoryAlert")}
            description={t("demo.dashboard.insights.inventoryAlertDesc")}
            priority="medium"
            agent="Sophia"
            agentColor={agentColors.Sophia}
            actionLabel={t("demo.dashboard.insights.createOrder")}
            onAction={() => alert('Create order feature - Demo')}
          />

          <InsightCard
            title={t("demo.dashboard.insights.patientSatisfaction")}
            description={t("demo.dashboard.insights.patientSatisfactionDesc")}
            priority="low"
            agent="Alex"
            agentColor={agentColors.Alex}
            actionLabel={t("demo.dashboard.insights.viewDetails")}
            onAction={() => alert('View details feature - Demo')}
          />
        </div>
      </div>
    </div>
  );
};

const DemoPatientsEnhanced = () => {
  const { t } = useTranslation();
  const { demoData } = useDemoContext();
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [activeTab, setActiveTab] = useState('overview');

  if (!demoData) {
    return <div className="demo-loading">{t("demo.patients.loading")}</div>;
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
      <h2>{t("demo.patients.title")}</h2>
      <p className="page-subtitle">{t("demo.patients.subtitle")}</p>

      {/* Search and Filter Bar */}
      <div className="patients-search-bar">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="search-input"
            placeholder={t("demo.patients.searchPlaceholder")}
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
            {t("demo.patients.all")} ({patients.length})
          </button>
          <button
            className={`filter-btn ${filterStatus === 'active' ? 'active' : ''}`}
            onClick={() => setFilterStatus('active')}
          >
            {t("demo.patients.active")} ({patients.filter(p => p.status === 'Active').length})
          </button>
          <button
            className={`filter-btn ${filterStatus === 'inactive' ? 'active' : ''}`}
            onClick={() => setFilterStatus('inactive')}
          >
            {t("demo.patients.inactive")} ({patients.filter(p => p.status === 'Inactive').length})
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
        {!selectedPatient && (
          <div className="patients-list">
            {filteredPatients.length === 0 ? (
              <div className="no-results">
                <p>{t("demo.patients.noResults")}</p>
                <button onClick={() => { setSearchQuery(''); setFilterStatus('all'); }}>{t("demo.patients.clearFilters")}</button>
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
        )}

        {selectedPatient && (
          <div className="patient-profile expanded">
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
                📋 {t("demo.patients.profile.overview")}
              </button>
              <button 
                className={`profile-tab ${activeTab === 'clinical' ? 'active' : ''}`}
                onClick={() => setActiveTab('clinical')}
              >
                🦷 {t("demo.patients.profile.clinical")}
              </button>
              <button 
                className={`profile-tab ${activeTab === 'appointments' ? 'active' : ''}`}
                onClick={() => setActiveTab('appointments')}
              >
                📅 {t("demo.nav.appointments")}
              </button>
              <button 
                className={`profile-tab ${activeTab === 'billing' ? 'active' : ''}`}
                onClick={() => setActiveTab('billing')}
              >
                💰 {t("demo.patients.profile.billing")}
              </button>
            </div>

            {/* Tab Content */}
            <div className="profile-tab-content">
              {activeTab === 'overview' && (
                <div className="profile-overview">
                  <div className="ai-summary">
                    <h4>🤖 {t("demo.patients.profile.aiSummary")}</h4>
                    <p>{t("demo.patients.profile.aiSummaryText")}</p>
                    <p>{t("demo.patients.profile.lastInteraction")}</p>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("demo.patients.profile.email")}</span>
                    <span className="detail-value">{selectedPatient.email}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("demo.patients.profile.phone")}</span>
                    <span className="detail-value">{selectedPatient.phone}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("demo.patients.status")}</span>
                    <span className="detail-value">{selectedPatient.status}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">{t("demo.patients.balance")}</span>
                    <span className="detail-value">₪{selectedPatient.balance}</span>
                  </div>
                  <div className="detail-actions">
                    <button className="btn-primary">💬 {t("demo.patients.profile.chatWithAlex")}</button>
                    <button className="btn-secondary">📅 {t("demo.patients.profile.scheduleAppointment")}</button>
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
                  <h4>{t("demo.patients.profile.upcomingAppointments")}</h4>
                  <div className="appointment-item">
                    <div className="appointment-date">Oct 25, 2025 - 10:00 AM</div>
                    <div className="appointment-type">{t("demo.patients.profile.regularCheckup")}</div>
                    <div className="appointment-status">{t("demo.patients.profile.confirmed")}</div>
                  </div>
                  <div className="appointment-item">
                    <div className="appointment-date">Nov 15, 2025 - 2:00 PM</div>
                    <div className="appointment-type">{t("demo.patients.profile.cleaning")}</div>
                    <div className="appointment-status">{t("demo.patients.profile.scheduled")}</div>
                  </div>
                </div>
              )}

              {activeTab === 'billing' && (
                <div className="profile-billing">
                  <h4>{t("demo.patients.profile.billingHistory")}</h4>
                  <div className="billing-summary">
                    <div className="billing-stat">
                      <span className="billing-label">{t("demo.patients.profile.totalBilled")}</span>
                      <span className="billing-value">₪{selectedPatient.totalBilled || 5200}</span>
                    </div>
                    <div className="billing-stat">
                      <span className="billing-label">{t("demo.patients.profile.totalPaid")}</span>
                      <span className="billing-value">₪{(selectedPatient.totalBilled || 5200) - selectedPatient.balance}</span>
                    </div>
                    <div className="billing-stat">
                      <span className="billing-label">{t("demo.patients.profile.outstanding")}</span>
                      <span className="billing-value">₪{selectedPatient.balance}</span>
                    </div>
                  </div>
                  <h4>{t("demo.patients.profile.recentInvoices")}</h4>
                  <div className="invoice-item">
                    <div className="invoice-date">Sep 15, 2025</div>
                    <div className="invoice-desc">{t("demo.patients.profile.rootCanalTreatment")}</div>
                    <div className="invoice-amount">₪2,400</div>
                    <div className="invoice-status paid">{t("demo.patients.profile.paid")}</div>
                  </div>
                  <div className="invoice-item">
                    <div className="invoice-date">Aug 10, 2025</div>
                    <div className="invoice-desc">{t("demo.patients.profile.regularCheckup")}</div>
                    <div className="invoice-amount">₪{selectedPatient.balance}</div>
                    <div className="invoice-status unpaid">{t("demo.patients.profile.unpaid")}</div>
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
  const { t } = useTranslation();
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">{t("demo.appointments.loading")}</div>;
  }

  const { appointments } = demoData;

  return (
    <div className="demo-appointments-enhanced">
      <h2>{t("demo.appointments.title")}</h2>
      <p className="page-subtitle">{t("demo.appointments.subtitle")}</p>

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
              <span className="ai-badge">✅ {t("demo.appointments.reminderSent")}</span>
              <span className="ai-badge">📧 {t("demo.appointments.confirmedViaEmail")}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const DemoFinancialEnhanced = () => {
  const { t } = useTranslation();
  const { demoData } = useDemoContext();

  if (!demoData) {
    return <div className="demo-loading">{t("demo.financial.loading")}</div>;
  }

  const { financialSummary } = demoData;

  return (
    <div className="demo-financial-enhanced">
      <h2>{t("demo.financial.title")}</h2>
      <p className="page-subtitle">{t("demo.financial.subtitle")}</p>

      <div className="financial-summary">
        <div className="summary-card">
          <h3>{t("demo.financial.monthlyRevenue")}</h3>
          <div className="summary-value">₪{financialSummary.totalRevenue.toLocaleString()}</div>
          <div className="summary-trend positive">+12% vs last month</div>
          <p className="ai-insight">🤖 Marcus predicts ₪48,000 next month based on scheduled appointments</p>
        </div>

        <div className="summary-card">
          <h3>{t("demo.financial.outstandingBalance")}</h3>
          <div className="summary-value">₪{financialSummary.outstandingBalance.toLocaleString()}</div>
          <div className="summary-trend negative">{financialSummary.unpaidInvoices} unpaid invoices</div>
          <p className="ai-insight">🤖 Marcus recommends sending payment reminders to 3 patients</p>
        </div>

        <div className="summary-card">
          <h3>{t("demo.financial.collectionRate")}</h3>
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

