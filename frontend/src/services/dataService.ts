/**
 * Data Service - Adapter/Orchestration Layer
 * 
 * Acts as an adapter between UI components and various data sources.
 * Follows the Adapter Pattern for clean separation of concerns.
 * 
 * Architecture:
 * - UI Components → dataService (this file) → dashboardService → API
 * 
 * Responsibilities:
 * 1. Aggregate data from multiple services
 * 2. Transform data to UI-expected formats
 * 3. Provide backward compatibility for legacy components
 * 4. Handle business logic and data orchestration
 */

import { dashboardService, DashboardMetrics, AgentMetrics } from './dashboardService';

// ========== TYPE DEFINITIONS ==========

/**
 * Agent format expected by MissionControlPage
 */
export interface Agent {
  name: string;
  role: string;
  status: 'active' | 'idle' | 'offline';
  avatar: string;
  stats: {
    tasksToday: number;
    avgResponseTime: string;
    successRate: number;
  };
  currentTask?: string;
  lastActive: string;
}

/**
 * Conversation format
 */
export interface Conversation {
  id: string;
  patient_name: string;
  agent: string;
  status: 'active' | 'pending' | 'resolved';
  started_at: string;
  last_message: string;
}

/**
 * Appointment format
 */
export interface Appointment {
  id: string;
  patient_name: string;
  time: string;
  treatment: string;
  status: 'scheduled' | 'confirmed' | 'in_progress' | 'completed';
  doctor?: string;
}

/**
 * Patient format
 */
export interface Patient {
  id: string;
  name: string;
  last_visit?: string;
  next_appointment?: string;
  status: 'active' | 'inactive';
}

/**
 * Log entry format
 */
export interface LogEntry {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  details: string;
  level: 'info' | 'warning' | 'error';
}

/**
 * Alert format
 */
export interface Alert {
  id: string;
  type: 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: string;
  agent?: string;
}

// ========== DATA SERVICE ==========

class DataService {
  /**
   * Get dashboard metrics (delegates to dashboardService)
   */
  async getMetrics(): Promise<DashboardMetrics> {
    try {
      return await dashboardService.getMetrics();
    } catch (error) {
      console.error('[DataService] Failed to fetch metrics:', error);
      // Return empty metrics
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
  }

  /**
   * Get agents with transformed format for UI
   */
  async getAgents(): Promise<Agent[]> {
    try {
      const agentMetrics = await dashboardService.getAgentMetrics();
      
      // Transform AgentMetrics[] to Agent[] format
      return agentMetrics.map(metric => this.transformAgentMetric(metric));
    } catch (error) {
      console.error('[DataService] Failed to fetch agents:', error);
      // Return mock agents for development
      return this.getMockAgents();
    }
  }

  /**
   * Transform AgentMetrics to Agent format
   */
  private transformAgentMetric(metric: AgentMetrics): Agent {
    const agentInfo = this.getAgentInfo(metric.agent_name);
    
    return {
      name: metric.agent_name,
      role: agentInfo.role,
      status: metric.status === 'online' ? 'active' : 'offline',
      avatar: agentInfo.avatar,
      stats: {
        tasksToday: metric.requests_handled,
        avgResponseTime: `${metric.avg_response_time.toFixed(1)}s`,
        successRate: metric.success_rate,
      },
      lastActive: metric.last_active,
    };
  }

  /**
   * Get agent role and avatar info
   */
  private getAgentInfo(agentName: string): { role: string; avatar: string } {
    const agentMap: Record<string, { role: string; avatar: string }> = {
      'Alex': { role: 'Front Desk & Appointments', avatar: '👨‍💼' },
      'Sarah': { role: 'Clinical Operations', avatar: '👩‍⚕️' },
      'Marcus': { role: 'Financial Officer', avatar: '💼' },
      'Sophia': { role: 'Practice Administrator', avatar: '👩‍💻' },
      'Harper': { role: 'HIPAA Compliance', avatar: '🔒' },
    };
    
    return agentMap[agentName] || { role: 'AI Agent', avatar: '🤖' };
  }

  /**
   * Get conversations (TODO: implement real endpoint)
   */
  async getConversations(): Promise<Conversation[]> {
    try {
      // TODO: Implement conversations endpoint
      // For now, return empty array
      return [];
    } catch (error) {
      console.error('[DataService] Failed to fetch conversations:', error);
      return [];
    }
  }

  /**
   * Get appointments (delegates to dashboardService)
   */
  async getAppointments(): Promise<Appointment[]> {
    try {
      const orgId = localStorage.getItem('current_organization_id') || '1';
      const appointmentsData = await dashboardService.getTodaysAppointments(orgId);
      
      // Transform to expected format
      return appointmentsData.map(apt => ({
        id: apt.id,
        patient_name: apt.patient_name,
        time: apt.time,
        treatment: apt.treatment_type,
        status: apt.status as any,
        doctor: apt.doctor,
      }));
    } catch (error) {
      console.error('[DataService] Failed to fetch appointments:', error);
      return [];
    }
  }

  /**
   * Get patients (TODO: implement real endpoint)
   */
  async getPatients(): Promise<Patient[]> {
    try {
      // TODO: Implement patients endpoint
      return [];
    } catch (error) {
      console.error('[DataService] Failed to fetch patients:', error);
      return [];
    }
  }

  /**
   * Get activity logs (TODO: implement real endpoint)
   */
  async getLogs(): Promise<LogEntry[]> {
    try {
      // TODO: Implement logs endpoint
      // For now, return empty array
      return [];
    } catch (error) {
      console.error('[DataService] Failed to fetch logs:', error);
      return [];
    }
  }

  /**
   * Get system alerts (TODO: implement real endpoint)
   */
  async getAlerts(): Promise<Alert[]> {
    try {
      // TODO: Implement alerts endpoint
      // For now, return empty array
      return [];
    } catch (error) {
      console.error('[DataService] Failed to fetch alerts:', error);
      return [];
    }
  }

  // ========== MOCK DATA (for development) ==========

  /**
   * Mock agents for development/fallback
   */
  private getMockAgents(): Agent[] {
    return [
      {
        name: 'Alex',
        role: 'Front Desk & Appointments',
        status: 'active',
        avatar: '👨‍💼',
        stats: {
          tasksToday: 24,
          avgResponseTime: '2.3s',
          successRate: 95,
        },
        currentTask: 'Scheduling appointment',
        lastActive: new Date().toISOString(),
      },
      {
        name: 'Sarah',
        role: 'Clinical Operations',
        status: 'idle',
        avatar: '👩‍⚕️',
        stats: {
          tasksToday: 12,
          avgResponseTime: '3.1s',
          successRate: 98,
        },
        lastActive: new Date(Date.now() - 15 * 60000).toISOString(),
      },
      {
        name: 'Marcus',
        role: 'Financial Officer',
        status: 'active',
        avatar: '💼',
        stats: {
          tasksToday: 18,
          avgResponseTime: '1.8s',
          successRate: 96,
        },
        currentTask: 'Analyzing revenue',
        lastActive: new Date().toISOString(),
      },
      {
        name: 'Sophia',
        role: 'Practice Administrator',
        status: 'active',
        avatar: '👩‍💻',
        stats: {
          tasksToday: 15,
          avgResponseTime: '2.5s',
          successRate: 94,
        },
        currentTask: 'Managing schedule',
        lastActive: new Date().toISOString(),
      },
      {
        name: 'Harper',
        role: 'HIPAA Compliance',
        status: 'idle',
        avatar: '🔒',
        stats: {
          tasksToday: 5,
          avgResponseTime: '4.2s',
          successRate: 100,
        },
        lastActive: new Date(Date.now() - 30 * 60000).toISOString(),
      },
    ];
  }
}

// Export singleton instance
export const dataService = new DataService();
export default dataService;
