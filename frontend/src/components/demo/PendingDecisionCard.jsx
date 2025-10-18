import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../ui/Card';
import './PendingDecisionCard.css';

/**
 * PendingDecisionCard - Display pending decisions with clear CTAs
 * Implements progressive disclosure and priority-based design
 */
const PendingDecisionCard = ({ 
  decision,
  onApprove,
  onReject,
  onModify,
  showDetails = false
}) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(showDetails);
  
  const getPriorityColor = (priority) => {
    switch(priority?.toLowerCase()) {
      case 'high': return '#EF4444';
      case 'medium': return '#F59E0B';
      case 'low': return '#10B981';
      default: return '#3B82F6';
    }
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

  return (
    <Card className="pending-decision-card" elevated>
      <CardHeader>
        <div className="pending-decision-card__header">
          <div className="pending-decision-card__priority" 
               style={{ backgroundColor: getPriorityColor(decision.priority) }}>
            {decision.priority?.toUpperCase() || 'MEDIUM'}
          </div>
          <div className="pending-decision-card__agent"
               style={{ color: getAgentColor(decision.agent) }}>
            🤖 {decision.agent}
          </div>
        </div>
        <CardTitle className="pending-decision-card__title">
          {decision.title}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <p className="pending-decision-card__description">
          {decision.description}
        </p>
        
        {decision.metadata && (
          <div className="pending-decision-card__metadata">
            {decision.metadata.patient && (
              <div className="metadata-item">
                <span className="metadata-label">👤</span>
                <span className="metadata-value">{decision.metadata.patient}</span>
              </div>
            )}
            {decision.metadata.amount && (
              <div className="metadata-item">
                <span className="metadata-label">💰</span>
                <span className="metadata-value">{decision.metadata.amount}</span>
              </div>
            )}
            {decision.metadata.date && (
              <div className="metadata-item">
                <span className="metadata-label">📅</span>
                <span className="metadata-value">{decision.metadata.date}</span>
              </div>
            )}
          </div>
        )}
        
        {expanded && decision.reasoning && (
          <div className="pending-decision-card__reasoning">
            <div className="reasoning-header">
              {t('demo.transparency.reasoning_process')}
            </div>
            <ol className="reasoning-steps">
              {decision.reasoning.steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
            <div className="reasoning-confidence">
              {t('demo.transparency.confidence')}: {decision.reasoning.confidence}%
            </div>
          </div>
        )}
      </CardContent>
      
      <CardFooter>
        <div className="pending-decision-card__actions">
          <button 
            className="btn btn--reject"
            onClick={() => onReject && onReject(decision)}
          >
            ✕ {t('demo.decisions.reject')}
          </button>
          
          {onModify && (
            <button 
              className="btn btn--modify"
              onClick={() => onModify(decision)}
            >
              ✎ {t('demo.decisions.modify')}
            </button>
          )}
          
          <button 
            className="btn btn--approve"
            onClick={() => onApprove && onApprove(decision)}
          >
            ✓ {t('demo.decisions.approve')}
          </button>
        </div>
        
        {decision.reasoning && (
          <button 
            className="btn-link"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? '▲' : '▼'} {expanded ? t('demo.transparency.hide_reasoning') : t('demo.transparency.show_reasoning')}
          </button>
        )}
      </CardFooter>
    </Card>
  );
};

export default PendingDecisionCard;

