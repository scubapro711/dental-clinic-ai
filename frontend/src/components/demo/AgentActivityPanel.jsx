import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import './AgentActivityPanel.css';

/**
 * AgentActivityPanel - Display recent agent activities with filtering
 * Implements async agentic pattern with activity monitoring
 */
const AgentActivityPanel = ({ 
  activities = [],
  maxVisible = 5,
  collapsible = true
}) => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('all');
  
  const getAgentConfig = (agentName) => {
    const configs = {
      'Alex': { color: '#3B82F6', icon: '📞', label: t('demo.agents.alex') },
      'Sarah': { color: '#10B981', icon: '🦷', label: t('demo.agents.sarah'), badge: t('demo.clinical.in_development') },
      'Marcus': { color: '#8B5CF6', icon: '💼', label: t('demo.agents.marcus') },
      'Sophia': { color: '#F59E0B', icon: '📋', label: t('demo.agents.sophia') }
    };
    return configs[agentName] || { color: '#6B7280', icon: '🤖', label: agentName };
  };
  
  const agents = ['all', 'Alex', 'Sarah', 'Marcus', 'Sophia'];
  
  const filteredActivities = selectedAgent === 'all' 
    ? activities 
    : (activities || []).filter(a => a.agent === selectedAgent);
    
  const visibleActivities = expanded 
    ? filteredActivities 
    : filteredActivities.slice(0, maxVisible);

  return (
    <Card className="agent-activity-panel">
      <CardHeader>
        <CardTitle>
          🤖 {t('demo.activity.title')}
        </CardTitle>
        <div className="agent-activity-panel__filters">
          {agents.map(agent => {
            const config = agent === 'all' 
              ? { color: '#6B7280', label: t('demo.activity.all') }
              : getAgentConfig(agent);
            
            return (
              <button
                key={agent}
                className={`filter-btn ${selectedAgent === agent ? 'filter-btn--active' : ''}`}
                style={selectedAgent === agent ? { 
                  backgroundColor: config.color,
                  color: 'white'
                } : {}}
                onClick={() => setSelectedAgent(agent)}
              >
                {agent === 'all' ? config.label : `${config.icon} ${agent}`}
              </button>
            );
          })}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="activity-list">
          {visibleActivities.length === 0 ? (
            <div className="activity-empty">
              {t('demo.activity.no_activities')}
            </div>
          ) : (
            visibleActivities.map((activity, idx) => {
              const config = getAgentConfig(activity.agent);
              
              return (
                <div key={idx} className="activity-item">
                  <div className="activity-item__icon" style={{ backgroundColor: config.color }}>
                    {config.icon}
                  </div>
                  <div className="activity-item__content">
                    <div className="activity-item__header">
                      <span className="activity-item__agent" style={{ color: config.color }}>
                        {activity.agent}
                        {config.badge && (
                          <span className="agent-badge">{config.badge}</span>
                        )}
                      </span>
                      <span className="activity-item__time">{activity.timestamp}</span>
                    </div>
                    <div className="activity-item__description">
                      {activity.description}
                    </div>
                    {activity.status && (
                      <div className={`activity-item__status activity-item__status--${activity.status}`}>
                        {activity.status === 'success' && '✓'}
                        {activity.status === 'pending' && '⏳'}
                        {activity.status === 'error' && '✕'}
                        {' '}
                        {t(`demo.activity.status.${activity.status}`)}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
        
        {collapsible && filteredActivities.length > maxVisible && (
          <button 
            className="expand-btn"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded 
              ? `▲ ${t('demo.activity.show_less')}` 
              : `▼ ${t('demo.activity.show_more')} (${filteredActivities.length - maxVisible})`
            }
          </button>
        )}
      </CardContent>
    </Card>
  );
};

export default AgentActivityPanel;

