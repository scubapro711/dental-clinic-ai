/**
 * Organization Context Hooks
 * 
 * Custom hooks for managing organization context in components.
 * 
 * Features:
 * - useOrganizationContext() - Full context with loading/error states
 * - useOrganizationId() - Simple ID getter with change listener
 * 
 * @example
 * ```jsx
 * import { useOrganizationContext, useOrganizationId } from '@/hooks/useOrganizationContext';
 * 
 * // Full context
 * const { context, loading, error, refetch } = useOrganizationContext();
 * 
 * // Just the ID
 * const organizationId = useOrganizationId();
 * ```
 */

import { useState, useEffect, useCallback } from 'react';
import { organizationService } from '../services/organizationService';

/**
 * Hook to get and manage organization context
 * 
 * Features:
 * - Fetches current organization context
 * - Listens for organization changes
 * - Provides loading and error states
 * - Validates organization context exists
 * - Refetch function for manual refresh
 * 
 * @returns {Object} Organization context, loading, error, and refetch function
 * 
 * @example
 * ```jsx
 * const { context, loading, error, refetch } = useOrganizationContext();
 * 
 * if (loading) return <Spinner />;
 * if (error) return <Error message={error} />;
 * if (!context) return <NoOrganization />;
 * 
 * return <div>Current org: {context.organization.name}</div>;
 * ```
 */
export function useOrganizationContext() {
  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch organization context
  const fetchContext = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const ctx = await organizationService.getCurrentOrganizationContext();
      
      if (!ctx) {
        setError('No organization selected');
        setContext(null);
      } else {
        setContext(ctx);
      }
    } catch (err) {
      console.error('Failed to fetch organization context:', err);
      setError('Failed to load organization');
      setContext(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchContext();
  }, [fetchContext]);

  // Listen for organization changes
  useEffect(() => {
    const handleOrganizationChanged = () => {
      fetchContext();
    };

    window.addEventListener('organizationChanged', handleOrganizationChanged);
    
    return () => {
      window.removeEventListener('organizationChanged', handleOrganizationChanged);
    };
  }, [fetchContext]);

  return {
    context,
    loading,
    error,
    refetch: fetchContext,
  };
}

/**
 * Hook to get current organization ID
 * 
 * Simpler version that only returns the ID.
 * Listens for organization changes and updates automatically.
 * 
 * @returns {string|null} Current organization ID or null
 * 
 * @example
 * ```jsx
 * const organizationId = useOrganizationId();
 * 
 * if (!organizationId) {
 *   return <Error message="No organization selected" />;
 * }
 * 
 * // Use organizationId in API calls
 * const data = await fetchData(organizationId);
 * ```
 */
export function useOrganizationId() {
  const [organizationId, setOrganizationId] = useState(
    organizationService.getCurrentOrganizationId()
  );

  useEffect(() => {
    const handleOrganizationChanged = (event) => {
      setOrganizationId(event.detail.organizationId);
    };

    window.addEventListener('organizationChanged', handleOrganizationChanged);
    
    return () => {
      window.removeEventListener('organizationChanged', handleOrganizationChanged);
    };
  }, []);

  return organizationId;
}

export default useOrganizationContext;
