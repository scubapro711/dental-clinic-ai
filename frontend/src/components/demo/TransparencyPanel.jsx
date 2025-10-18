import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import './TransparencyPanel.css';

/**
 * TransparencyPanel - Display AI decision-making transparency
 * Shows reasoning process, tools used, and outcome
 */
const TransparencyPanel = ({ 
  title,
  agent,
  agentColor,
  reasoningSteps = [],
  toolsUsed = [],
  outcome,
  confidence,
  status = 'pending', // 'pending', 'approved', 'rejected'
  className = ''
}) => {
  const getStatusConfig = (status) => {
    const configs = {
      pending: { color: '#ffaa00', label: 'Pending Approval', icon: '⏳' },
      approved: { color: '#10b981', label: 'Approved', icon: '✓' },
      rejected: { color: '#ef4444', label: 'Rejected', icon: '✗' }
    };
    return configs[status] || configs.pending;
  };

  const statusConfig = getStatusConfig(status);

  return (
    <Card className={`transparency-panel ${className}`}>
      <CardHeader>
        <div className="transparency-panel__header">
          <CardTitle>{title}</CardTitle>
          {agent && (
            <div className="transparency-panel__agent" style={{ color: agentColor }}>
              🤖 {agent}
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* Reasoning Process */}
        {reasoningSteps.length > 0 && (
          <div className="transparency-panel__section">
            <h4 className="transparency-panel__section-title">
              🧠 Reasoning Process
            </h4>
            <div className="transparency-panel__steps">
              {reasoningSteps.map((step, index) => (
                <div key={index} className="transparency-panel__step">
                  <div className="transparency-panel__step-number">{index + 1}</div>
                  <div className="transparency-panel__step-text">{step}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tools Used */}
        {toolsUsed.length > 0 && (
          <div className="transparency-panel__section">
            <h4 className="transparency-panel__section-title">
              🛠️ Tools Used
            </h4>
            <div className="transparency-panel__tools">
              {toolsUsed.map((tool, index) => (
                <div key={index} className="transparency-panel__tool">
                  {tool}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Outcome */}
        {outcome && (
          <div className="transparency-panel__section">
            <h4 className="transparency-panel__section-title">
              📊 Outcome
            </h4>
            <div className="transparency-panel__outcome">
              <div 
                className="transparency-panel__status"
                style={{ 
                  backgroundColor: `${statusConfig.color}15`,
                  color: statusConfig.color,
                  borderColor: statusConfig.color
                }}
              >
                {statusConfig.icon} {statusConfig.label}
              </div>
              <p className="transparency-panel__outcome-text">{outcome}</p>
            </div>
          </div>
        )}

        {/* Confidence */}
        {confidence !== undefined && (
          <div className="transparency-panel__section">
            <h4 className="transparency-panel__section-title">
              📈 Confidence
            </h4>
            <div className="transparency-panel__confidence">
              <div className="transparency-panel__confidence-bar">
                <div 
                  className="transparency-panel__confidence-fill"
                  style={{ 
                    width: `${confidence}%`,
                    backgroundColor: confidence >= 80 ? '#10b981' : confidence >= 60 ? '#ffaa00' : '#ef4444'
                  }}
                />
              </div>
              <span className="transparency-panel__confidence-value">{confidence}%</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TransparencyPanel;

