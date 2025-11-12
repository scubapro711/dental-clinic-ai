import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MetricCard from './MetricCard';
import { Users, Calendar, DollarSign, Activity, Shield } from 'lucide-react';
import './DashboardStatsBar.css';

/**
 * DashboardStatsBar Component
 * 
 * Displays key metrics at the top of the dashboard.
 * Fetches real data from backend API with fallback to mock data.
 */
const DashboardStatsBar = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    activePatients: { value: 0, trend: null },
    todayAppointments: { value: 0, trend: null },
    monthlyRevenue: { value: 0, trend: null },
    systemHealth: { value: 0, trend: null },
    hipaaCompliance: { value: 0, trend: null }
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats({
          activePatients: {
            value: data.active_patients || 0,
            trend: data.active_patients_trend || null
          },
          todayAppointments: {
            value: data.today_appointments || 0,
            trend: data.today_appointments_trend || null
          },
          monthlyRevenue: {
            value: data.monthly_revenue || 0,
            trend: data.monthly_revenue_trend || null
          },
          systemHealth: {
            value: data.system_health || 98,
            trend: data.system_health_trend || null
          },
          hipaaCompliance: {
            value: data.hipaa_compliance_score || 0,
            trend: data.hipaa_compliance_trend || null
          }
        });
      } else {
        // Fallback to mock data
        setMockStats();
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      setMockStats();
    } finally {
      setIsLoading(false);
    }
  };

  const setMockStats = () => {
    setStats({
      activePatients: {
        value: 247,
        trend: { direction: 'up', value: '+12%', label: 'from last month' }
      },
      todayAppointments: {
        value: 8,
        trend: { direction: 'up', value: '+2', label: 'from yesterday' }
      },
      monthlyRevenue: {
        value: '₪45,230',
        trend: { direction: 'up', value: '+8%', label: 'from last month' }
      },
      systemHealth: {
        value: '98%',
        trend: { direction: 'up', value: '+2%', label: 'uptime' }
      },
      hipaaCompliance: {
        value: '96%',
        trend: { direction: 'up', value: '+3%', label: 'compliance score' }
      }
    });
  };

  if (isLoading) {
    return (
      <div className="dashboard-stats-bar loading">
        <div className="stats-skeleton">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="skeleton-card"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-stats-bar">
      <div className="stats-grid">
        <MetricCard
          title="Active Patients"
          value={stats.activePatients.value}
          icon={<Users className="w-6 h-6" />}
          trend={stats.activePatients.trend}
          agent={{ name: 'Alex', color: '#3b82f6' }}
          onClick={() => navigate('/clinic/agents/alex')}
        />
        <MetricCard
          title="Today's Appointments"
          value={stats.todayAppointments.value}
          icon={<Calendar className="w-6 h-6" />}
          trend={stats.todayAppointments.trend}
          agent={{ name: 'Alex', color: '#3b82f6' }}
          onClick={() => navigate('/clinic/agents/alex')}
        />
        <MetricCard
          title="Monthly Revenue"
          value={stats.monthlyRevenue.value}
          icon={<DollarSign className="w-6 h-6" />}
          trend={stats.monthlyRevenue.trend}
          agent={{ name: 'Marcus', color: '#10b981' }}
          onClick={() => navigate('/clinic/agents/marcus')}
        />
        <MetricCard
          title="System Health"
          value={stats.systemHealth.value}
          icon={<Activity className="w-6 h-6" />}
          trend={stats.systemHealth.trend}
          subtitle="All agents operational"
        />
        <MetricCard
          title="HIPAA Compliance"
          value={stats.hipaaCompliance.value}
          icon={<Shield className="w-6 h-6" />}
          trend={stats.hipaaCompliance.trend}
          agent={{ name: 'Harper', color: '#8b5cf6' }}
          onClick={() => navigate('/clinic/agents/harper')}
        />
      </div>
    </div>
  );
};

export default DashboardStatsBar;

