import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ToothChart from './ToothChart';
import './ClinicalDashboard.css';

/**
 * ClinicalDashboard Component
 * 
 * Hybrid Agentic Clinical System:
 * - Sarah AI analyzes X-rays and suggests treatments
 * - Doctor reviews, approves, or modifies AI recommendations
 * - Complete clinical workflow from diagnosis to treatment plan
 */
const ClinicalDashboard = ({ patientId, patientName }) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedXray, setSelectedXray] = useState(null);
  
  // Mock data - in production, this would come from backend
  const mockToothConditions = {
    14: {
      status: 'cavity',
      notes: 'Deep cavity reaching pulp chamber',
      aiRecommended: true,
      aiRecommendation: 'Root canal treatment required. Estimated cost: ₪1,800',
      aiConfidence: 97,
    },
    26: {
      status: 'filling',
      notes: 'Composite filling placed 2 years ago',
      aiRecommended: false,
    },
    36: {
      status: 'crown',
      notes: 'Porcelain crown placed 5 years ago',
      aiRecommended: false,
    },
    47: {
      status: 'ai_flagged',
      notes: 'Possible early cavity detected',
      aiRecommended: true,
      aiRecommendation: 'Monitor closely. Consider preventive treatment.',
      aiConfidence: 78,
    },
  };

  const mockXrays = [
    {
      id: 1,
      type: 'Panoramic',
      date: '2025-10-15',
      url: '/api/placeholder/400/300',
      aiAnalysis: {
        findings: [
          { tooth: 14, condition: 'Deep cavity', severity: 'high', confidence: 97 },
          { tooth: 47, condition: 'Early cavity', severity: 'medium', confidence: 78 },
        ],
        recommendations: [
          'Tooth #14: Root canal + crown recommended',
          'Tooth #47: Monitor or preventive filling',
        ],
      },
    },
    {
      id: 2,
      type: 'Bitewing',
      date: '2025-10-15',
      url: '/api/placeholder/400/300',
      aiAnalysis: {
        findings: [
          { tooth: 14, condition: 'Cavity reaching pulp', severity: 'high', confidence: 95 },
        ],
        recommendations: [
          'Immediate root canal treatment required',
        ],
      },
    },
  ];

  const mockTreatmentPlans = [
    {
      id: 1,
      tooth: 14,
      treatment: 'Root Canal + Crown',
      status: 'pending_approval',
      aiSuggested: true,
      aiReasoning: [
        'X-ray shows deep cavity reaching pulp chamber',
        'Patient reports severe pain',
        'No signs of infection yet, but high risk',
        'Crown needed post-treatment to prevent fracture',
      ],
      cost: 3200,
      estimatedTime: '2 visits, 3 hours total',
      urgency: 'high',
      doctorNotes: '',
    },
    {
      id: 2,
      tooth: 47,
      treatment: 'Preventive Filling',
      status: 'pending_review',
      aiSuggested: true,
      aiReasoning: [
        'Early cavity detected in X-ray',
        'No symptoms yet',
        'Preventive treatment can avoid root canal later',
      ],
      cost: 450,
      estimatedTime: '1 visit, 30 minutes',
      urgency: 'medium',
      doctorNotes: '',
    },
  ];

  const [treatmentPlans, setTreatmentPlans] = useState(mockTreatmentPlans);

  const handleApproveTreatment = (planId) => {
    setTreatmentPlans(plans =>
      plans.map(plan =>
        plan.id === planId ? { ...plan, status: 'approved' } : plan
      )
    );
  };

  const handleRejectTreatment = (planId) => {
    setTreatmentPlans(plans =>
      plans.map(plan =>
        plan.id === planId ? { ...plan, status: 'rejected' } : plan
      )
    );
  };

  const handleModifyTreatment = (planId) => {
    // In production, this would open a modal to edit the treatment plan
    alert('Modify treatment plan feature - coming soon!');
  };

  return (
    <div className="clinical-dashboard">
      <div className="clinical-header">
        <div>
          <h2>🩺 {t("clinical.title")}</h2>
          <p className="patient-info">
            {t("clinical.patient")}: <strong>{patientName}</strong> (ID: {patientId})
          </p>
        </div>
        <div className="ai-status">
          <span className="ai-badge-large">🤖 Sarah AI</span>
          <span className="status-text">Active & Analyzing</span>
        </div>
      </div>

      <div className="clinical-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
            📊 {t("clinical.tabs.overview")}
        </button>
        <button
          className={`tab-btn ${activeTab === 'tooth-chart' ? 'active' : ''}`}
          onClick={() => setActiveTab('tooth-chart')}
        >
            🦷 {t("clinical.tabs.toothChart")}
        </button>
        <button
          className={`tab-btn ${activeTab === 'xrays' ? 'active' : ''}`}
          onClick={() => setActiveTab('xrays')}
        >
            📸 {t("clinical.tabs.xrays")}
        </button>
        <button
          className={`tab-btn ${activeTab === 'treatment-plans' ? 'active' : ''}`}
          onClick={() => setActiveTab('treatment-plans')}
        >
            📋 {t("clinical.tabs.treatmentPlans")}
        </button>
        <button
          className={`tab-btn ${activeTab === 'notes' ? 'active' : ''}`}
          onClick={() => setActiveTab('notes')}
        >
            📝 {t("clinical.tabs.clinicalNotes")}
        </button>
      </div>

      <div className="clinical-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="overview-grid">
              <div className="overview-card">
                <div className="card-icon">🦷</div>
                <div className="card-content">
                  <h3>{t("clinical.overview.teethStatus")}</h3>
                  <div className="stat-large">28</div>
                  <p className="stat-label">{t("clinical.overview.healthyTeeth")}</p>
                  <div className="stat-details">
                    <span className="stat-item">2 {t("clinical.overview.withCavities")}</span>
                    <span className="stat-item">2 {t("clinical.overview.aiFlagged")}</span>
                  </div>
                </div>
              </div>

              <div className="overview-card">
                <div className="card-icon">📸</div>
                <div className="card-content">
                  <h3>{t("clinical.overview.recentXrays")}</h3>
                  <div className="stat-large">{mockXrays.length}</div>
                  <p className="stat-label">{t("clinical.overview.imagesAnalyzed")}</p>
                  <div className="stat-details">
                    <span className="stat-item">{t("clinical.overview.aiConfidence")}: 95%</span>
                  </div>
                </div>
              </div>

              <div className="overview-card">
                <div className="card-icon">📋</div>
                <div className="card-content">
                  <h3>{t("clinical.overview.treatmentPlans")}</h3>
                  <div className="stat-large">{treatmentPlans.length}</div>
                  <p className="stat-label">{t("clinical.overview.pendingApproval")}</p>
                  <div className="stat-details">
                    <span className="stat-item">1 {t("clinical.overview.urgent")}</span>
                    <span className="stat-item">1 {t("clinical.overview.routine")}</span>
                  </div>
                </div>
              </div>

              <div className="overview-card">
                <div className="card-icon">💰</div>
                <div className="card-content">
                  <h3>{t("clinical.overview.estimatedCost")}</h3>
                  <div className="stat-large">₪{treatmentPlans.reduce((sum, plan) => sum + plan.cost, 0).toLocaleString()}</div>
                  <p className="stat-label">{t("clinical.overview.totalTreatmentCost")}</p>
                  <div className="stat-details">
                    <span className="stat-item">2 {t("clinical.overview.procedures")}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="ai-insights-clinical">
              <h3>🤖 {t("clinical.insights.title")}</h3>
              <div className="insight-list">
                <div className="insight-item urgent">
                  <div className="insight-header">
                    <span className="insight-icon">⚠️</span>
                    <span className="insight-title">{t("clinical.insights.urgentTreatment")}</span>
                    <span className="confidence-badge">97% {t("clinical.insights.confidence")}</span>
                  </div>
                  <p>{t("clinical.insights.urgentDesc")}</p>
                  <button className="insight-action-btn">{t("clinical.insights.reviewPlan")}</button>
                </div>

                <div className="insight-item medium">
                  <div className="insight-header">
                    <span className="insight-icon">🔍</span>
                    <span className="insight-title">{t("clinical.insights.earlyCavity")}</span>
                    <span className="confidence-badge">78% {t("clinical.insights.confidence")}</span>
                  </div>
                  <p>{t("clinical.insights.earlyCavityDesc")}</p>
                  <button className="insight-action-btn">{t("clinical.insights.reviewPlan")}</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'tooth-chart' && (
          <div className="tooth-chart-tab">
            <ToothChart
              conditions={mockToothConditions}
              onToothClick={(toothNumber, condition) => {
                console.log('Tooth clicked:', toothNumber, condition);
              }}
            />
          </div>
        )}

        {activeTab === 'xrays' && (
          <div className="xrays-tab">
            <div className="xrays-grid">
              {mockXrays.map(xray => (
                <div
                  key={xray.id}
                  className={`xray-card ${selectedXray?.id === xray.id ? 'selected' : ''}`}
                  onClick={() => setSelectedXray(xray)}
                >
                  <div className="xray-image-placeholder">
                    <span className="xray-type">{xray.type}</span>
                    <span className="xray-date">{xray.date}</span>
                  </div>
                  <div className="xray-info">
                    <h4>{xray.type} {t("clinical.xrays.title")}</h4>
                    <p className="xray-findings">
                      {xray.aiAnalysis.findings.length} findings detected
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {selectedXray && (
              <div className="xray-analysis-panel">
                <div className="analysis-header">
                  <h3>🤖 {t("clinical.xrays.sarahAnalysis")}</h3>
                  <button onClick={() => setSelectedXray(null)}>✕</button>
                </div>
                
                <div className="analysis-content">
                  <h4>{t("clinical.xrays.findings")}:</h4>
                  <div className="findings-list">
                    {selectedXray.aiAnalysis.findings.map((finding, index) => (
                      <div key={index} className={`finding-item severity-${finding.severity}`}>
                        <div className="finding-header">
                          <span className="tooth-number">{t("clinical.xrays.tooth")} #{finding.tooth}</span>
                          <span className="confidence-badge">{finding.confidence}% {t("clinical.insights.confidence")}</span>
                        </div>
                        <p className="finding-condition">{finding.condition}</p>
                        <span className={`severity-badge ${finding.severity}`}>
                          {finding.severity} severity
                        </span>
                      </div>
                    ))}
                  </div>

                  <h4>{t("clinical.xrays.recommendations")}:</h4>
                  <ul className="recommendations-list">
                    {selectedXray.aiAnalysis.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'treatment-plans' && (
          <div className="treatment-plans-tab">
            <div className="treatment-plans-list">
              {treatmentPlans.map(plan => (
                <div key={plan.id} className={`treatment-plan-card ${plan.status}`}>
                  <div className="plan-header">
                    <div>
                      <h3>{t("clinical.treatment.tooth")} #{plan.tooth}: {plan.treatment}</h3>
                      {plan.aiSuggested && (
                        <span className="ai-suggested-badge">🤖 {t("clinical.treatment.aiSuggested")}</span>
                      )}
                    </div>
                    <div className="plan-meta">
                      <span className={`urgency-badge ${plan.urgency}`}>
                        {plan.urgency} urgency
                      </span>
                      <span className={`status-badge ${plan.status}`}>
                        {plan.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>

                  <div className="plan-content">
                    <div className="plan-section">
                      <h4>🤖 {t("clinical.treatment.reasoning")}:</h4>
                      <ol className="reasoning-list">
                        {plan.aiReasoning.map((reason, index) => (
                          <li key={index}>{reason}</li>
                        ))}
                      </ol>
                    </div>

                    <div className="plan-details-grid">
                      <div className="detail-item">
                        <span className="detail-label">💰 {t("clinical.treatment.cost")}:</span>
                        <span className="detail-value">₪{plan.cost.toLocaleString()}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">⏱️ {t("clinical.treatment.estimatedTime")}:</span>
                        <span className="detail-value">{plan.estimatedTime}</span>
                      </div>
                    </div>

                    {plan.status === 'pending_approval' && (
                      <div className="plan-actions">
                        <button
                          className="btn-approve"
                          onClick={() => handleApproveTreatment(plan.id)}
                        >
                          ✓ {t("clinical.treatment.approve")}
                        </button>
                        <button
                          className="btn-modify"
                          onClick={() => handleModifyTreatment(plan.id)}
                        >
                           ✎ {t("clinical.treatment.modify")}
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() => handleRejectTreatment(plan.id)}
                        >
                          ✗ {t("clinical.treatment.reject")}
                        </button>
                      </div>
                    )}

                    {plan.status === 'approved' && (
                      <div className="plan-approved">
                        <span className="approved-icon">✅</span>
                        <span>{t("clinical.treatment.approvedReady")}</span>
                      </div>
                    )}

                    {plan.status === 'rejected' && (
                      <div className="plan-rejected">
                        <span className="rejected-icon">❌</span>
                        <span>{t("clinical.treatment.rejectedPlan")}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'notes' && (
          <div className="notes-tab">
            <div className="notes-header">
              <h3>📝 {t("clinical.notes.title")}</h3>
              <button className="btn-add-note">+ Add Note</button>
            </div>
            
            <div className="soap-note-editor">
              <div className="soap-section">
                <h4>S - {t("clinical.notes.subjective")}</h4>
                <textarea
                  placeholder="Patient's chief complaint and symptoms..."
                  rows="3"
                  defaultValue="Patient reports severe pain in lower right molar (tooth #14). Pain started 3 days ago, worsens with cold/hot stimuli."
                />
              </div>

              <div className="soap-section">
                <h4>O - {t("clinical.notes.objective")}</h4>
                <textarea
                  placeholder="Clinical findings and observations..."
                  rows="3"
                  defaultValue="Visual exam: Deep cavity visible on tooth #14. Percussion test: positive. X-ray: Cavity reaching pulp chamber."
                />
                <div className="ai-assist">
                  <span className="ai-badge">🤖 Sarah's Observations</span>
                  <p>X-ray analysis confirms deep cavity in tooth #14 with 97% confidence. Pulp chamber involvement detected.</p>
                </div>
              </div>

              <div className="soap-section">
                <h4>A - {t("clinical.notes.assessment")}</h4>
                <textarea
                  placeholder="Diagnosis and clinical assessment..."
                  rows="3"
                  defaultValue="Diagnosis: Irreversible pulpitis, tooth #14. Deep carious lesion with pulp exposure."
                />
                <div className="ai-assist">
                  <span className="ai-badge">🤖 Sarah's Assessment</span>
                  <p>Diagnosis consistent with AI analysis. Root canal treatment indicated. High urgency due to pain and risk of infection.</p>
                </div>
              </div>

              <div className="soap-section">
                <h4>P - {t("clinical.notes.plan")}</h4>
                <textarea
                  placeholder="Treatment plan and follow-up..."
                  rows="3"
                  defaultValue="Plan: Root canal treatment + crown for tooth #14. Schedule within 1 week. Prescribe pain medication and antibiotics if needed."
                />
                <div className="ai-assist">
                  <span className="ai-badge">🤖 Sarah's Recommendations</span>
                  <ul>
                    <li>Root canal treatment (estimated cost: ₪1,800)</li>
                    <li>Crown placement post-treatment (estimated cost: ₪1,400)</li>
                    <li>Total estimated cost: ₪3,200</li>
                    <li>Schedule 2 appointments, 3 hours total</li>
                  </ul>
                </div>
              </div>

              <div className="note-actions">
                <button className="btn-save-note">💾 Save Note</button>
                <button className="btn-cancel">Cancel</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClinicalDashboard;

