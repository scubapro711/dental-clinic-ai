/**
 * Harper Compliance Dashboard
 * 
 * Main dashboard for HIPAA compliance monitoring and management.
 * Shows compliance score, alerts, recent activity, and quick actions.
 * 
 * Only accessible to clinic_admin and super_admin roles.
 */

import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  FileText,
  Users,
  Lock,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import HarperChat from './HarperChat';
import ComplianceAlerts from './ComplianceAlerts';
import ComplianceMetrics from './ComplianceMetrics';

const HarperDashboard = () => {
  const [complianceScore, setComplianceScore] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch compliance score
      const scoreResponse = await fetch('/api/compliance/score');
      const scoreData = await scoreResponse.json();
      setComplianceScore(scoreData);

      // Fetch active alerts
      const alertsResponse = await fetch('/api/compliance/alerts?status=open');
      const alertsData = await alertsResponse.json();
      setAlerts(alertsData);

      // Fetch metrics
      const metricsResponse = await fetch('/api/compliance/metrics');
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'destructive',
      high: 'destructive',
      medium: 'warning',
      low: 'secondary',
      info: 'default'
    };
    return colors[severity] || 'default';
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    if (score >= 70) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreStatus = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Good';
    if (score >= 70) return 'Fair';
    return 'Needs Improvement';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <Shield className="w-16 h-16 mx-auto mb-4 animate-pulse text-blue-600" />
          <p className="text-lg text-gray-600">Loading compliance dashboard...</p>
        </div>
      </div>
    );
  }

  const criticalAlerts = alerts.filter(a => a.severity === 'critical');
  const highAlerts = alerts.filter(a => a.severity === 'high');

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="w-8 h-8 text-blue-600" />
            Harper - HIPAA Compliance
          </h1>
          <p className="text-gray-600 mt-1">
            Comprehensive compliance monitoring and management
          </p>
        </div>
        <Button onClick={() => setShowChat(true)} size="lg">
          <Activity className="w-4 h-4 mr-2" />
          Ask Harper
        </Button>
      </div>

      {/* Critical Alerts Banner */}
      {criticalAlerts.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Critical Compliance Issues</AlertTitle>
          <AlertDescription>
            You have {criticalAlerts.length} critical alert{criticalAlerts.length !== 1 ? 's' : ''} requiring immediate attention.
            <Button variant="link" className="ml-2 p-0 h-auto" onClick={() => document.getElementById('alerts-section').scrollIntoView({ behavior: 'smooth' })}>
              View Alerts →
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Compliance Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Overall Score */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Overall Compliance Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold mb-2 flex items-baseline">
              <span className={getScoreColor(complianceScore?.overall || 0)}>
                {complianceScore?.overall || 0}%
              </span>
              <span className="text-sm font-normal text-gray-500 ml-2">
                {getScoreStatus(complianceScore?.overall || 0)}
              </span>
            </div>
            <Progress value={complianceScore?.overall || 0} className="h-2" />
            <p className="text-xs text-gray-500 mt-2">
              Target: 85%+
            </p>
          </CardContent>
        </Card>

        {/* PHI Compliance */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              PHI Compliance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {complianceScore?.phi || 0}%
            </div>
            <Progress value={complianceScore?.phi || 0} className="h-2" />
            <p className="text-xs text-gray-500 mt-2">
              {complianceScore?.phi_findings || 0} findings
            </p>
          </CardContent>
        </Card>

        {/* Security Controls */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Security Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {complianceScore?.security || 0}%
            </div>
            <Progress value={complianceScore?.security || 0} className="h-2" />
            <p className="text-xs text-gray-500 mt-2">
              {complianceScore?.security_gaps || 0} gaps identified
            </p>
          </CardContent>
        </Card>

        {/* Active Alerts */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Active Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-2">
              {alerts.length}
            </div>
            <div className="flex gap-2 mt-2">
              {criticalAlerts.length > 0 && (
                <Badge variant="destructive" className="text-xs">
                  {criticalAlerts.length} Critical
                </Badge>
              )}
              {highAlerts.length > 0 && (
                <Badge variant="warning" className="text-xs">
                  {highAlerts.length} High
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common compliance tasks and checks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-auto py-4 flex-col gap-2">
              <FileText className="w-6 h-6" />
              <span>Generate Report</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2">
              <Users className="w-6 h-6" />
              <span>Review BAAs</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2">
              <Activity className="w-6 h-6" />
              <span>Audit Logs</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2">
              <TrendingUp className="w-6 h-6" />
              <span>Risk Assessment</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Alerts Section */}
      <div id="alerts-section">
        <ComplianceAlerts alerts={alerts} onRefresh={fetchDashboardData} />
      </div>

      {/* Metrics Section */}
      <ComplianceMetrics metrics={metrics} />

      {/* Harper Chat Modal */}
      {showChat && (
        <HarperChat onClose={() => setShowChat(false)} />
      )}
    </div>
  );
};

export default HarperDashboard;

