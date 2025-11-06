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
      
      // Fetch metrics summary from new HIPAA API
      const summaryResponse = await fetch('/api/v1/hipaa/metrics/summary');
      const summaryData = await summaryResponse.json();
      
      // Transform to match existing component structure
      setComplianceScore({
        overall: calculateOverallScore(summaryData),
        phi: calculatePHIScore(summaryData),
        security: calculateSecurityScore(summaryData),
        phi_findings: summaryData.phi_access?.unauthorized_count || 0,
        security_gaps: summaryData.breaches?.total_count || 0
      });

      // Transform metrics for alerts
      const transformedAlerts = transformMetricsToAlerts(summaryData);
      setAlerts(transformedAlerts);

      // Set raw metrics
      setMetrics(summaryData);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to calculate overall compliance score
  const calculateOverallScore = (data) => {
    if (!data) return 0;
    
    const phiScore = data.phi_access?.authorized_count || 0;
    const totalPHI = (data.phi_access?.authorized_count || 0) + (data.phi_access?.unauthorized_count || 0);
    const phiCompliance = totalPHI > 0 ? (phiScore / totalPHI) * 100 : 100;
    
    const authSuccess = data.authentication?.successful_logins || 0;
    const totalAuth = (data.authentication?.successful_logins || 0) + (data.authentication?.failed_attempts || 0);
    const authCompliance = totalAuth > 0 ? (authSuccess / totalAuth) * 100 : 100;
    
    const encSuccess = data.encryption?.successful_operations || 0;
    const totalEnc = (data.encryption?.successful_operations || 0) + (data.encryption?.failed_operations || 0);
    const encCompliance = totalEnc > 0 ? (encSuccess / totalEnc) * 100 : 100;
    
    const breachPenalty = (data.breaches?.total_count || 0) * 10;
    
    const overall = Math.max(0, Math.min(100, 
      (phiCompliance * 0.4 + authCompliance * 0.3 + encCompliance * 0.3) - breachPenalty
    ));
    
    return Math.round(overall);
  };

  // Helper function to calculate PHI compliance score
  const calculatePHIScore = (data) => {
    if (!data || !data.phi_access) return 100;
    
    const authorized = data.phi_access.authorized_count || 0;
    const unauthorized = data.phi_access.unauthorized_count || 0;
    const total = authorized + unauthorized;
    
    if (total === 0) return 100;
    
    return Math.round((authorized / total) * 100);
  };

  // Helper function to calculate security score
  const calculateSecurityScore = (data) => {
    if (!data) return 100;
    
    const breaches = data.breaches?.total_count || 0;
    const encFailures = data.encryption?.failed_operations || 0;
    const authFailures = data.authentication?.failed_attempts || 0;
    
    const securityIssues = breaches * 20 + encFailures * 5 + authFailures * 2;
    
    return Math.max(0, Math.min(100, 100 - securityIssues));
  };

  // Helper function to transform metrics to alerts
  const transformMetricsToAlerts = (data) => {
    const alerts = [];
    
    // Unauthorized PHI access alerts
    if (data.phi_access?.unauthorized_count > 0) {
      alerts.push({
        id: 'phi-unauthorized',
        severity: 'critical',
        title: 'Unauthorized PHI Access Detected',
        description: `${data.phi_access.unauthorized_count} unauthorized PHI access attempt(s) detected`,
        timestamp: new Date().toISOString()
      });
    }
    
    // Failed login attempts
    if (data.authentication?.failed_attempts > 5) {
      alerts.push({
        id: 'auth-failures',
        severity: 'high',
        title: 'Multiple Failed Login Attempts',
        description: `${data.authentication.failed_attempts} failed login attempts detected`,
        timestamp: new Date().toISOString()
      });
    }
    
    // Encryption failures
    if (data.encryption?.failed_operations > 0) {
      alerts.push({
        id: 'enc-failures',
        severity: 'high',
        title: 'Encryption Failures',
        description: `${data.encryption.failed_operations} encryption operation(s) failed`,
        timestamp: new Date().toISOString()
      });
    }
    
    // Security breaches
    if (data.breaches?.total_count > 0) {
      alerts.push({
        id: 'breaches',
        severity: 'critical',
        title: 'Security Breach Incidents',
        description: `${data.breaches.total_count} security breach incident(s) reported`,
        timestamp: new Date().toISOString()
      });
    }
    
    // Expired BAAs
    if (data.baa_status?.expired > 0) {
      alerts.push({
        id: 'baa-expired',
        severity: 'high',
        title: 'Expired BAA Agreements',
        description: `${data.baa_status.expired} BAA agreement(s) have expired`,
        timestamp: new Date().toISOString()
      });
    }
    
    return alerts;
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

  const criticalAlerts = (alerts || []).filter(a => a.severity === 'critical');
  const highAlerts = (alerts || []).filter(a => a.severity === 'high');

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
      {(criticalAlerts || []).length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Critical Compliance Issues</AlertTitle>
          <AlertDescription>
            You have {(criticalAlerts || []).length} critical alert{(criticalAlerts || []).length !== 1 ? 's' : ''} requiring immediate attention.
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
              {(alerts || []).length}
            </div>
            <div className="flex gap-2 mt-2">
              {(criticalAlerts || []).length > 0 && (
                <Badge variant="destructive" className="text-xs">
                  {(criticalAlerts || []).length} Critical
                </Badge>
              )}
              {(highAlerts || []).length > 0 && (
                <Badge variant="warning" className="text-xs">
                  {(highAlerts || []).length} High
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

