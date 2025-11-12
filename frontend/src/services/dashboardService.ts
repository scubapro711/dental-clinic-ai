/**
 * Dashboard Service
 * 
 * Centralized service for all dashboard-related API calls.
 * Uses the API client for consistent error handling, auth, and organization context.
 * 
 * Updated to use real data from backend with proper error handling.
 */

import { api } from '../api/client';
import { AxiosResponse } from 'axios';

// ========== TYPE DEFINITIONS ==========

/**
 * Dashboard metrics matching backend schema (14 fields)
 * Source: backend/app/api/v1/endpoints/dashboard_metrics.py
 */
export interface DashboardMetrics {
  // Alex Agent metrics (conversations from checkpoints)
  active_conversations: number;
  total_conversations_today: number;
  avg_response_time_seconds: number;
  escalations_pending: number;
  
  // Sophia (Admin) metrics (appointments from Odoo)
  appointments_today: number;
  appointments_completed: number;
  appointments_upcoming: number;
  scheduling_conflicts: number;
  
  // Marcus (CFO) metrics (financial from Odoo)
  revenue_today: number;
  revenue_this_month: number;
  outstanding_payments: number;
  payment_success_rate: number;
  
  // System metrics
  uptime_hours: number;
  last_updated: string;
}

/**
 * Agent metrics matching backend schema (7 fields)
 * Source: backend/app/api/v1/endpoints/dashboard_metrics.py
 */
export interface AgentMetrics {
  agent_name: string;
  status: string; // online, offline, paused
  uptime_seconds: number;
  requests_handled: number;
  avg_response_time: number;
  success_rate: number;
  last_active: string;
}

// Legacy types (kept for backward compatibility)

export interface RevenueData {
  thisMonth: number;
  lastMonth: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  insight: string;
  recommendation: string;
  breakdown?: {
    treatments: number;
    consultations: number;
    other: number;
  };
}

export interface AppointmentData {
  id: string;
  patient_name: string;
  patient_id: string;
  time: string;
  treatment_type: string;
  status: 'scheduled' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  doctor?: string;
  notes?: string;
}

export interface DecisionQueueItem {
  id: string;
  agent: 'alex' | 'marcus' | 'sarah' | 'sophia' | 'harper';
  title: string;
  description: string;
  priority: 'urgent' | 'high' | 'medium' | 'low';
  created_at: string;
  suggested_action: string;
  confidence: number;
  status: 'pending' | 'approved' | 'rejected' | 'executed';
}

/**
 * Enhanced Decision model matching backend schema
 * Source: backend/app/api/v1/endpoints/decisions.py
 */
export interface Decision {
  // Core fields
  id: string;
  thread_id: string;
  agent: 'alex' | 'sarah' | 'marcus' | 'sophia' | 'harper' | 'system';
  
  // Content
  title: string;
  description: string;
  action: string;
  
  // Classification
  priority: 'critical' | 'high' | 'medium' | 'low';
  category?: 'clinical' | 'operational' | 'financial' | 'compliance';
  
  // AI Metadata
  confidence?: number; // 0-100
  reasoning?: string;
  
  // Context
  patient_id?: string;
  patient_name?: string;
  
  // Impact
  impact_level?: 'high' | 'medium' | 'low';
  compliance_risk?: boolean;
  
  // Timing
  timestamp: string;
  due_by?: string;
}

export interface ClinicalInsight {
  id: string;
  patient_id: string;
  patient_name: string;
  insight_type: 'treatment_plan' | 'diagnosis' | 'follow_up' | 'risk_alert';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  recommended_action: string;
  created_by: 'sarah' | 'alex';
  created_at: string;
}

export interface ComplianceStatus {
  overall_score: number;
  hipaa_compliant: boolean;
  last_audit_date: string;
  issues: Array<{
    id: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    status: 'open' | 'in_progress' | 'resolved';
  }>;
  recommendations: string[];
}

export interface AgentActivity {
  agent: 'alex' | 'marcus' | 'sarah' | 'sophia' | 'harper';
  name: string;
  status: 'active' | 'idle' | 'offline';
  last_action: string;
  last_action_time: string;
  tasks_completed_today: number;
  current_task?: string;
}

export interface FineTuningMetrics {
  total_feedback: number;
  average_rating: number;
  training_data_ready: boolean;
  last_training_date?: string;
  model_performance: {
    accuracy: number;
    response_quality: number;
    user_satisfaction: number;
  };
}

// ========== DASHBOARD SERVICE ==========

class DashboardService {
  /**
   * Get overall dashboard metrics (REAL DATA)
   * Endpoint: GET /api/v1/dashboard-metrics/metrics
   */
  async getMetrics(): Promise<DashboardMetrics> {
    try {
      const response: AxiosResponse<DashboardMetrics> = await api.get('/dashboard-metrics/metrics');
      console.log('[DashboardService] Metrics fetched successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch metrics:', error);
      // Return empty/zero metrics instead of mock data
      return this.getEmptyMetrics();
    }
  }

  /**
   * Get agent metrics (REAL DATA)
   * Endpoint: GET /api/v1/dashboard-metrics/metrics/agents
   */
  async getAgentMetrics(): Promise<AgentMetrics[]> {
    try {
      const response: AxiosResponse<AgentMetrics[]> = await api.get('/dashboard-metrics/metrics/agents');
      console.log('[DashboardService] Agent metrics fetched successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch agent metrics:', error);
      // Return empty array instead of mock data
      return [];
    }
  }

  /**
   * Get revenue data (LEGACY - uses old endpoint)
   */
  async getRevenue(organizationId: string): Promise<RevenueData> {
    try {
      const response: AxiosResponse<RevenueData> = await api.get(`/dashboard/revenue`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch revenue:', error);
      // Try to construct from metrics
      try {
        const metrics = await this.getMetrics();
        return {
          thisMonth: metrics.revenue_this_month,
          lastMonth: 0, // Not available
          change: 0,
          trend: 'stable',
          insight: `הכנסות החודש: ₪${metrics.revenue_this_month.toLocaleString()}`,
          recommendation: 'נתונים מלאים זמינים בדשבורד הראשי',
        };
      } catch {
        return this.getMockRevenue();
      }
    }
  }

  /**
   * Get today's appointments (LEGACY - uses old endpoint)
   */
  async getTodaysAppointments(organizationId: string): Promise<AppointmentData[]> {
    try {
      const response: AxiosResponse<AppointmentData[]> = await api.get(`/appointments/today`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch appointments:', error);
      return [];
    }
  }

  /**
   * Get decision queue items (REAL DATA)
   * Endpoint: GET /api/v1/decisions/pending
   */
  async getDecisionQueue(organizationId: string, limit: number = 10): Promise<Decision[]> {
    try {
      const response: AxiosResponse<Decision[]> = await api.get(`/decisions/pending`, {
        params: { limit }
      });
      console.log('[DashboardService] Decision queue fetched successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch decision queue:', error);
      return [];
    }
  }

  /**
   * Approve a decision
   * Endpoint: POST /api/v1/decisions/{decision_id}/approve
   */
  async approveDecision(decisionId: string, reason?: string): Promise<void> {
    try {
      await api.post(`/decisions/${decisionId}/approve`, {
        execute: true,
        reason: reason || "Approved by user"
      });
      console.log('[DashboardService] Decision approved:', decisionId);
    } catch (error) {
      console.error('[DashboardService] Failed to approve decision:', error);
      throw error;
    }
  }

  /**
   * Reject a decision
   * Endpoint: POST /api/v1/decisions/{decision_id}/reject
   */
  async rejectDecision(decisionId: string, reason?: string): Promise<void> {
    try {
      await api.post(`/decisions/${decisionId}/reject`, {
        reason: reason || "Rejected by user"
      });
      console.log('[DashboardService] Decision rejected:', decisionId);
    } catch (error) {
      console.error('[DashboardService] Failed to reject decision:', error);
      throw error;
    }
  }

  /**
   * Get clinical insights
   */
  async getClinicalInsights(organizationId: string): Promise<ClinicalInsight[]> {
    try {
      const response: AxiosResponse<ClinicalInsight[]> = await api.get(`/clinical/insights`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch clinical insights:', error);
      return [];
    }
  }

  /**
   * Get compliance status
   */
  async getComplianceStatus(organizationId: string): Promise<ComplianceStatus> {
    try {
      const response: AxiosResponse<ComplianceStatus> = await api.get(`/compliance/status`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch compliance status:', error);
      return this.getMockComplianceStatus();
    }
  }

  /**
   * Get agent activity (LEGACY - uses old format)
   * Consider using getAgentMetrics() instead for real data
   */
  async getAgentActivity(organizationId: string): Promise<AgentActivity[]> {
    try {
      // Try new endpoint first
      const agentMetrics = await this.getAgentMetrics();
      
      // Convert to legacy format
      return agentMetrics.map(metric => ({
        agent: metric.agent_name.toLowerCase() as any,
        name: metric.agent_name,
        status: metric.status === 'online' ? 'active' : 'offline',
        last_action: 'Activity tracked',
        last_action_time: metric.last_active,
        tasks_completed_today: metric.requests_handled,
      }));
    } catch (error) {
      console.error('[DashboardService] Failed to fetch agent activity:', error);
      return [];
    }
  }

  /**
   * Get fine-tuning metrics
   */
  async getFineTuningMetrics(organizationId: string): Promise<FineTuningMetrics> {
    try {
      const response: AxiosResponse<FineTuningMetrics> = await api.get(`/fine-tuning/metrics`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch fine-tuning metrics:', error);
      return this.getMockFineTuningMetrics();
    }
  }

  // ========== FALLBACK METHODS ==========

  /**
   * Return empty metrics (no mock data)
   */
  private getEmptyMetrics(): DashboardMetrics {
    return {
      active_conversations: 0,
      total_conversations_today: 0,
      avg_response_time_seconds: 0,
      escalations_pending: 0,
      appointments_today: 0,
      appointments_completed: 0,
      appointments_upcoming: 0,
      scheduling_conflicts: 0,
      revenue_today: 0,
      revenue_this_month: 0,
      outstanding_payments: 0,
      payment_success_rate: 0,
      uptime_hours: 0,
      last_updated: new Date().toISOString(),
    };
  }

  /**
   * Mock revenue data (fallback only)
   */
  private getMockRevenue(): RevenueData {
    return {
      thisMonth: 0,
      lastMonth: 0,
      change: 0,
      trend: 'stable',
      insight: 'נתונים לא זמינים',
      recommendation: 'אנא בדוק את חיבור המערכת',
    };
  }

  /**
   * Mock compliance status (fallback only)
   */
  private getMockComplianceStatus(): ComplianceStatus {
    return {
      overall_score: 0,
      hipaa_compliant: false,
      last_audit_date: new Date().toISOString().split('T')[0],
      issues: [],
      recommendations: ['נתונים לא זמינים'],
    };
  }

  /**
   * Mock fine-tuning metrics (fallback only)
   */
  private getMockFineTuningMetrics(): FineTuningMetrics {
    return {
      total_feedback: 0,
      average_rating: 0,
      training_data_ready: false,
      model_performance: {
        accuracy: 0,
        response_quality: 0,
        user_satisfaction: 0,
      },
    };
  }
}

// Export singleton instance
export const dashboardService = new DashboardService();
export default dashboardService;
