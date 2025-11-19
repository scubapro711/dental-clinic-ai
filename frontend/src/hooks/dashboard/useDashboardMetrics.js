/**
 * useDashboardMetrics Hook
 * 
 * Fetches dashboard metrics from the backend.
 */

import { useState, useEffect } from 'react';
import { dashboardApiClient } from '../../utils/dashboardApiClient';

export const useDashboardMetrics = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await dashboardApiClient.get('/dashboard/stats');
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch dashboard metrics:', err);
      setError(err.response?.data?.detail || 'שגיאה בטעינת נתונים');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return {
    stats,
    isLoading,
    error,
    refetch: fetchMetrics
  };
};
