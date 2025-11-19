/**
 * useDecisions Hook
 * 
 * Manages decision queue operations.
 */

import { useState, useEffect, useCallback } from 'react';
import { dashboardApiClient } from '../../utils/dashboardApiClient';
import { useToast } from '../../contexts/dashboard/ToastContext';

export const useDecisions = () => {
  const [decisions, setDecisions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { addToast } = useToast();

  const fetchDecisions = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await dashboardApiClient.get('/decisions/pending');
      setDecisions(data.decisions || []);
    } catch (err) {
      console.error('Failed to fetch decisions:', err);
      setError(err.response?.data?.detail || 'שגיאה בטעינת החלטות');
    } finally {
      setIsLoading(false);
    }
  };

  const approveDecision = useCallback(async (id) => {
    try {
      await dashboardApiClient.post(`/decisions/${id}/approve`);
      addToast('ההחלטה אושרה בהצלחה', 'success');
      // Remove from list
      setDecisions(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      console.error('Failed to approve decision:', err);
      addToast('שגיאה באישור ההחלטה', 'error');
    }
  }, [addToast]);

  const rejectDecision = useCallback(async (id) => {
    try {
      await dashboardApiClient.post(`/decisions/${id}/reject`);
      addToast('ההחלטה נדחתה', 'info');
      // Remove from list
      setDecisions(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      console.error('Failed to reject decision:', err);
      addToast('שגיאה בדחיית ההחלטה', 'error');
    }
  }, [addToast]);

  useEffect(() => {
    fetchDecisions();
  }, []);

  return {
    decisions,
    isLoading,
    error,
    approveDecision,
    rejectDecision,
    refetch: fetchDecisions
  };
};
