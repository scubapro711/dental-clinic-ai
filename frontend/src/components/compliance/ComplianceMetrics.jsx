/**
 * Compliance Metrics Component
 * 
 * Displays compliance metrics and trends over time.
 * Shows historical data and trend analysis.
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';

const ComplianceMetrics = ({ metrics }) => {
  if (!metrics) {
    return null;
  }

  const getTrendIcon = (trend) => {
    if (trend > 0) return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (trend < 0) return <TrendingDown className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const getTrendColor = (trend) => {
    if (trend > 0) return 'text-green-600';
    if (trend < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatTrend = (trend) => {
    const sign = trend > 0 ? '+' : '';
    return `${sign}${trend}%`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Compliance Trends</CardTitle>
        <CardDescription>
          Historical compliance metrics and trends
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Overall Compliance Trend */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Overall Compliance</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(metrics.overall_trend || 0)}
                <span className={`text-sm font-medium ${getTrendColor(metrics.overall_trend || 0)}`}>
                  {formatTrend(metrics.overall_trend || 0)}
                </span>
              </div>
            </div>
            <div className="text-2xl font-bold">{metrics.overall_score || 0}%</div>
            <p className="text-xs text-gray-500">
              vs. last month: {metrics.overall_last_month || 0}%
            </p>
          </div>

          {/* PHI Compliance Trend */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">PHI Compliance</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(metrics.phi_trend || 0)}
                <span className={`text-sm font-medium ${getTrendColor(metrics.phi_trend || 0)}`}>
                  {formatTrend(metrics.phi_trend || 0)}
                </span>
              </div>
            </div>
            <div className="text-2xl font-bold">{metrics.phi_score || 0}%</div>
            <p className="text-xs text-gray-500">
              vs. last month: {metrics.phi_last_month || 0}%
            </p>
          </div>

          {/* Security Controls Trend */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Security Controls</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(metrics.security_trend || 0)}
                <span className={`text-sm font-medium ${getTrendColor(metrics.security_trend || 0)}`}>
                  {formatTrend(metrics.security_trend || 0)}
                </span>
              </div>
            </div>
            <div className="text-2xl font-bold">{metrics.security_score || 0}%</div>
            <p className="text-xs text-gray-500">
              vs. last month: {metrics.security_last_month || 0}%
            </p>
          </div>

          {/* BAA Compliance */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">BAA Compliance</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(metrics.baa_trend || 0)}
                <span className={`text-sm font-medium ${getTrendColor(metrics.baa_trend || 0)}`}>
                  {formatTrend(metrics.baa_trend || 0)}
                </span>
              </div>
            </div>
            <div className="text-2xl font-bold">{metrics.baa_score || 0}%</div>
            <p className="text-xs text-gray-500">
              {metrics.active_baas || 0} active BAAs
            </p>
          </div>

          {/* Risk Level */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Risk Level</span>
              <Badge variant={
                metrics.risk_level === 'low' ? 'success' :
                metrics.risk_level === 'medium' ? 'warning' :
                'destructive'
              }>
                {metrics.risk_level || 'Unknown'}
              </Badge>
            </div>
            <div className="text-2xl font-bold">{metrics.total_risks || 0}</div>
            <p className="text-xs text-gray-500">
              {metrics.critical_risks || 0} critical, {metrics.high_risks || 0} high
            </p>
          </div>

          {/* Audit Findings */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Audit Findings</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(metrics.findings_trend || 0)}
                <span className={`text-sm font-medium ${getTrendColor(metrics.findings_trend || 0)}`}>
                  {formatTrend(metrics.findings_trend || 0)}
                </span>
              </div>
            </div>
            <div className="text-2xl font-bold">{metrics.total_findings || 0}</div>
            <p className="text-xs text-gray-500">
              {metrics.resolved_findings || 0} resolved this month
            </p>
          </div>
        </div>

        {/* Recent Activity */}
        {metrics.recent_activity && metrics.recent_activity.length > 0 && (
          <div className="mt-6 pt-6 border-t">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Recent Activity</h4>
            <div className="space-y-2">
              {metrics.recent_activity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{activity.description}</span>
                  <span className="text-gray-400 text-xs">{activity.timestamp}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ComplianceMetrics;

