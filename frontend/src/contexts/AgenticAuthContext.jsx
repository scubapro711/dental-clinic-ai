import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { useAuth as useAuthHook } from '../hooks/useAuth';
import { useToast } from './ToastContext';
import { SubscriptionProvider } from './SubscriptionContext';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const authHook = useAuthHook();
  const [organization, setOrganization] = useState(null);
  const { addToast } = useToast();

  useEffect(() => {
    const initOrganization = async () => {
      // Migration Logic (Spec Phase 1)
      const oldKey = localStorage.getItem('organization_id');
      if (oldKey && !localStorage.getItem('current_organization_id')) {
        localStorage.setItem('current_organization_id', oldKey);
      }
      
      // Get organization from localStorage
      const orgId = localStorage.getItem('current_organization_id');
      if (orgId && authHook.isAuthenticated) {
        // TODO: Fetch organization details from API
        // For now, use mock data
        setOrganization({
          id: orgId,
          name: 'מרפאת שניידר - תל אביב',
          plan: 'professional' // TODO: Get from API
        });
      } else {
        setOrganization(null);
      }
    };

    if (!authHook.isLoading) {
      initOrganization();
    }
  }, [authHook.isAuthenticated, authHook.isLoading]);

  const login = async (email, password) => {
    const result = await authHook.login(email, password);
    if (result.success) {
      // Organization will be set by useEffect when isAuthenticated changes
      return true;
    } else {
      addToast(result.error || 'שגיאה בהתחברות', 'error');
      return false;
    }
  };

  const logout = () => {
    authHook.logout();
    localStorage.removeItem('current_organization_id');
    setOrganization(null);
  };

  const value = useMemo(() => ({
    user: authHook.user,
    organization,
    isLoading: authHook.isLoading,
    login,
    logout
  }), [authHook.user, organization, authHook.isLoading]);

  return (
    <AuthContext.Provider value={value}>
      {organization ? (
         <SubscriptionProvider organization={organization}>
            {children}
         </SubscriptionProvider>
      ) : (
         children
      )}
    </AuthContext.Provider>
  );
};
