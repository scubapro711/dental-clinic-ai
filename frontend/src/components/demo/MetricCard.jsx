import React from 'react';
import { Card, CardContent } from '../ui/Card';
import './MetricCard.css';

/**
 * MetricCard - Display key metrics with icon, value, label, and trend
 * Optimized for dental practice dashboards
 */
const MetricCard = ({ 
  icon, 
  value, 
  label, 
  trend, 
  trendLabel,
  agentName,
  agentColor,
  onClick,
  className = ''
}) => {
  return (
    <Card 
      className={`metric-card ${className}`}
      hover={!!onClick}
      onClick={onClick}
    >
      <CardContent>
        <div className="metric-card__header">
          <div className="metric-card__icon" style={{ color: agentColor }}>
            {icon}
          </div>
          {trend && (
            <div className={`metric-card__trend metric-card__trend--${trend > 0 ? 'up' : 'down'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </div>
          )}
        </div>
        
        <div className="metric-card__value">{value}</div>
        <div className="metric-card__label">{label}</div>
        
        {trendLabel && (
          <div className="metric-card__trend-label">{trendLabel}</div>
        )}
        
        {agentName && (
          <div className="metric-card__agent" style={{ color: agentColor }}>
            🤖 {agentName}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;

