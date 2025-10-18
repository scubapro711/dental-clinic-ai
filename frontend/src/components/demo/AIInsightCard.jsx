import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '../ui/Card';
import './AIInsightCard.css';

/**
 * AIInsightCard - Display AI-generated insights with priority and CTA
 * Optimized for quick scanning and action
 */
const AIInsightCard = ({ 
  insight,
  onAction,
  compact = false
}) => {
  const { t } = useTranslation();
  
  const getPriorityConfig = (priority) => {
    const configs = {
      high: { color: '#EF4444', icon: '🔴', label: t('demo.insights.high_priority') },
      medium: { color: '#F59E0B', icon: '🟡', label: t('demo.insights.medium_priority') },
      low: { color: '#10B981', icon: '🟢', label: t('demo.insights.low_priority') },
      info: { color: '#3B82F6', icon: '🔵', label: t('demo.insights.info') }
    };
    return configs[priority?.toLowerCase()] || configs.info;
  };
  
  const getAgentColor = (agent) => {
    const colors = {
      'Alex': '#3B82F6',
      'Sarah': '#10B981',
      'Marcus': '#8B5CF6',
      'Sophia': '#F59E0B'
    };
    return colors[agent] || '#6B7280';
  };
  
  const config = getPriorityConfig(insight.priority);

  return (
    <Card className={`ai-insight-card ${compact ? 'ai-insight-card--compact' : ''}`}>
      <CardContent>
        <div className="ai-insight-card__header">
          <div className="ai-insight-card__priority" style={{ color: config.color }}>
            <span className="priority-icon">{config.icon}</span>
            <span className="priority-label">{config.label}</span>
          </div>
          {insight.agent && (
            <div className="ai-insight-card__agent" style={{ color: getAgentColor(insight.agent) }}>
              🤖 {insight.agent}
            </div>
          )}
        </div>
        
        <h4 className="ai-insight-card__title">{insight.title}</h4>
        <p className="ai-insight-card__description">{insight.description}</p>
        
        {insight.metrics && (
          <div className="ai-insight-card__metrics">
            {insight.metrics.map((metric, idx) => (
              <div key={idx} className="metric-item">
                <span className="metric-label">{metric.label}:</span>
                <span className="metric-value">{metric.value}</span>
              </div>
            ))}
          </div>
        )}
        
        {insight.actionLabel && onAction && (
          <button 
            className="ai-insight-card__action"
            onClick={() => onAction(insight)}
            style={{ backgroundColor: config.color }}
          >
            {insight.actionLabel}
          </button>
        )}
        
        {insight.timestamp && (
          <div className="ai-insight-card__timestamp">
            {insight.timestamp}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AIInsightCard;

