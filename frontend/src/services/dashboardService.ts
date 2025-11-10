/**
 * Dashboard Service
 * 
 * Centralized service for all dashboard-related API calls.
 * Uses the API client for consistent error handling, auth, and organization context.
 */

import { api } from '../api/client';
import { AxiosResponse } from 'axios';

// ========== TYPE DEFINITIONS ==========

export interface DashboardMetrics {
  appointments_today: number;
  revenue_this_month: number;
  pending_decisions: number;
  active_conversations: number;
  patient_satisfaction: number;
  compliance_score: number;
}

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
   * Get overall dashboard metrics
   */
  async getMetrics(organizationId: string): Promise<DashboardMetrics> {
    try {
      const response: AxiosResponse<DashboardMetrics> = await api.dashboard.getMetrics(organizationId);
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch metrics:', error);
      // Return mock data as fallback
      return this.getMockMetrics();
    }
  }

  /**
   * Get revenue data
   */
  async getRevenue(organizationId: string): Promise<RevenueData> {
    try {
      const response: AxiosResponse<RevenueData> = await api.get(`/dashboard/revenue`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch revenue:', error);
      return this.getMockRevenue();
    }
  }

  /**
   * Get today's appointments
   */
  async getTodaysAppointments(organizationId: string): Promise<AppointmentData[]> {
    try {
      const response: AxiosResponse<AppointmentData[]> = await api.get(`/appointments/today`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch appointments:', error);
      return this.getMockAppointments();
    }
  }

  /**
   * Get decision queue items
   */
  async getDecisionQueue(organizationId: string, status?: string): Promise<DecisionQueueItem[]> {
    try {
      const response: AxiosResponse<DecisionQueueItem[]> = await api.get(`/decision-queue`, {
        params: { organization_id: organizationId, status }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch decision queue:', error);
      return this.getMockDecisionQueue();
    }
  }

  /**
   * Approve a decision queue item
   */
  async approveDecision(decisionId: string): Promise<void> {
    try {
      await api.post(`/decision-queue/${decisionId}/approve`);
    } catch (error) {
      console.error('[DashboardService] Failed to approve decision:', error);
      throw error;
    }
  }

  /**
   * Reject a decision queue item
   */
  async rejectDecision(decisionId: string, reason?: string): Promise<void> {
    try {
      await api.post(`/decision-queue/${decisionId}/reject`, { reason });
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
      return this.getMockClinicalInsights();
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
   * Get agent activity
   */
  async getAgentActivity(organizationId: string): Promise<AgentActivity[]> {
    try {
      const response: AxiosResponse<AgentActivity[]> = await api.get(`/agents/activity`, {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      console.error('[DashboardService] Failed to fetch agent activity:', error);
      return this.getMockAgentActivity();
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

  // ========== MOCK DATA METHODS (Fallback) ==========

  private getMockMetrics(): DashboardMetrics {
    return {
      appointments_today: 12,
      revenue_this_month: 45000,
      pending_decisions: 5,
      active_conversations: 8,
      patient_satisfaction: 4.7,
      compliance_score: 95,
    };
  }

  private getMockRevenue(): RevenueData {
    return {
      thisMonth: 45000,
      lastMonth: 39000,
      change: 15.4,
      trend: 'up',
      insight: 'הכנסות עלו ב-15% לעומת החודש הקודם',
      recommendation: 'מרקוס ממליץ: התמקדו בטיפולים מורכבים - הם מניבים 40% מההכנסות',
      breakdown: {
        treatments: 30000,
        consultations: 10000,
        other: 5000,
      },
    };
  }

  private getMockAppointments(): AppointmentData[] {
    return [
      {
        id: '1',
        patient_name: 'יוסי כהן',
        patient_id: 'p001',
        time: '09:00',
        treatment_type: 'ניקוי אבנית',
        status: 'confirmed',
        doctor: 'ד"ר לוי',
      },
      {
        id: '2',
        patient_name: 'שרה לוי',
        patient_id: 'p002',
        time: '10:30',
        treatment_type: 'סתימה',
        status: 'scheduled',
        doctor: 'ד"ר כהן',
      },
      {
        id: '3',
        patient_name: 'דוד מזרחי',
        patient_id: 'p003',
        time: '14:00',
        treatment_type: 'שורש',
        status: 'confirmed',
        doctor: 'ד"ר לוי',
      },
    ];
  }

  private getMockDecisionQueue(): DecisionQueueItem[] {
    return [
      {
        id: 'd1',
        agent: 'alex',
        title: 'תזכורת לפגישה',
        description: 'שלח תזכורת SMS למטופל יוסי כהן לפגישה מחר',
        priority: 'high',
        created_at: new Date().toISOString(),
        suggested_action: 'שלח SMS',
        confidence: 0.92,
        status: 'pending',
      },
      {
        id: 'd2',
        agent: 'marcus',
        title: 'חשבונית ממתינה',
        description: 'שלח תזכורת לתשלום לשרה לוי (₪800)',
        priority: 'medium',
        created_at: new Date().toISOString(),
        suggested_action: 'שלח תזכורת',
        confidence: 0.85,
        status: 'pending',
      },
    ];
  }

  private getMockClinicalInsights(): ClinicalInsight[] {
    return [
      {
        id: 'ci1',
        patient_id: 'p001',
        patient_name: 'יוסי כהן',
        insight_type: 'follow_up',
        title: 'נדרש מעקב',
        description: 'מטופל זקוק לבדיקת המשך לאחר טיפול שורש',
        severity: 'medium',
        recommended_action: 'קבע פגישת המשך בעוד שבועיים',
        created_by: 'sarah',
        created_at: new Date().toISOString(),
      },
    ];
  }

  private getMockComplianceStatus(): ComplianceStatus {
    return {
      overall_score: 95,
      hipaa_compliant: true,
      last_audit_date: '2025-11-01',
      issues: [],
      recommendations: [
        'המשך לעדכן מדיניות פרטיות',
        'בצע הדרכת צוות רבעונית',
      ],
    };
  }

  private getMockAgentActivity(): AgentActivity[] {
    return [
      {
        agent: 'alex',
        name: 'אלכס - קבלת קהל',
        status: 'active',
        last_action: 'שלח תזכורת SMS',
        last_action_time: '2 דקות',
        tasks_completed_today: 24,
        current_task: 'מתאם פגישה חדשה',
      },
      {
        agent: 'marcus',
        name: 'מרקוס - CFO',
        status: 'active',
        last_action: 'ניתח הכנסות',
        last_action_time: '5 דקות',
        tasks_completed_today: 12,
      },
      {
        agent: 'sarah',
        name: 'שרה - קלינית',
        status: 'idle',
        last_action: 'סקר תיק רפואי',
        last_action_time: '15 דקות',
        tasks_completed_today: 8,
      },
      {
        agent: 'sophia',
        name: 'סופיה - ניהול',
        status: 'active',
        last_action: 'עדכן לוח זמנים',
        last_action_time: '1 דקה',
        tasks_completed_today: 18,
      },
      {
        agent: 'harper',
        name: 'הארפר - HIPAA',
        status: 'idle',
        last_action: 'בדק לוגים',
        last_action_time: '30 דקות',
        tasks_completed_today: 5,
      },
    ];
  }

  private getMockFineTuningMetrics(): FineTuningMetrics {
    return {
      total_feedback: 156,
      average_rating: 4.6,
      training_data_ready: true,
      last_training_date: '2025-10-15',
      model_performance: {
        accuracy: 0.92,
        response_quality: 0.89,
        user_satisfaction: 0.94,
      },
    };
  }
}

// Export singleton instance
export const dashboardService = new DashboardService();
export default dashboardService;
