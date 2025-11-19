/**
 * Auth Context Provider
 * 
 * Manages authentication state and user session.
 * Integrates with real DentaFlow backend API.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { useToast } from './ToastContext';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app/api/v1';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [organization, setOrganization] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Make toast optional to avoid context dependency issues
  let addToast = () => {};
  try {
    const toastContext = useToast();
    if (toastContext?.addToast) {
      addToast = toastContext.addToast;
    }
  } catch (error) {
    // Toast context not available, use no-op
    console.warn('Toast context not available in AuthProvider');
  }

  useEffect(() => {
    const initAuth = async () => {
      try {
        // Migration: Check for old organization_id key
        const oldKey = localStorage.getItem('organization_id');
        if (oldKey && !localStorage.getItem('current_organization_id')) {
          localStorage.setItem('current_organization_id', oldKey);
        }

        const token = localStorage.getItem('access_token');
        if (token) {
          try {
            const response = await axios.get(`${API_BASE_URL}/auth/me`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });

            setUser(response.data);

            const orgId = localStorage.getItem('current_organization_id');
            if (orgId) {
              // Use a default organization for now
              setOrganization({
                id: orgId,
                name: 'מרפאת שניידר - תל אביב',
                plan: 'professional'
              });
            }
          } catch (error) {
            console.error('Failed to fetch user data:', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: email.trim(),
        password: password
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });

      const { access_token, refresh_token, user: userData, organization: orgData } = response.data;

      if (!access_token) {
        throw new Error('No access token received');
      }

      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('current_organization_id', orgData.id);

      // Update state
      setUser(userData);
      setOrganization(orgData);

      addToast('התחברת בהצלחה!', 'success');
      return true;
    } catch (err) {
      console.error('Login error:', err);

      let errorMessage = 'שגיאה בהתחברות. נסה שוב.';

      if (err.response) {
        if (err.response.status === 401) {
          errorMessage = 'אימייל או סיסמה שגויים';
        } else if (err.response.status === 403) {
          errorMessage = 'החשבון לא פעיל';
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        }
      } else if (err.request) {
        errorMessage = 'לא ניתן להתחבר לשרת. בדוק את החיבור לאינטרנט.';
      }

      addToast(errorMessage, 'error');
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_organization_id');
    setUser(null);
    setOrganization(null);
    addToast('התנתקת בהצלחה', 'info');
  };

  return (
    <AuthContext.Provider value={{ user, organization, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired
};
