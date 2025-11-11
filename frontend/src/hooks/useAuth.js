import { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '../config';

/**
 * useAuth Hook
 * 
 * Manages authentication state and user information
 * 
 * @returns {Object} Auth state and methods
 */
export function useAuth() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  /**
   * Check if user is authenticated
   */
  const checkAuth = async () => {
    setIsLoading(true);
    
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      setIsAuthenticated(false);
      setUser(null);
      setIsLoading(false);
      return;
    }

    // Check if this is a mock token (for demo purposes)
    if (token.startsWith('mock-jwt-token-')) {
      // Use user profile from localStorage instead of API call
      const userProfileStr = localStorage.getItem('user_profile');
      if (userProfileStr) {
        try {
          const userData = JSON.parse(userProfileStr);
          setUser(userData);
          setIsAuthenticated(true);
          setIsLoading(false);
          return;
        } catch (error) {
          console.error('Failed to parse user profile:', error);
        }
      }
      // If no user profile, treat as unauthenticated
      setIsAuthenticated(false);
      setUser(null);
      setIsLoading(false);
      return;
    }

    // Real token - fetch from backend
    try {
      const response = await fetch(API_ENDPOINTS.auth.me, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        // Save user data to localStorage for RBAC utilities
        localStorage.setItem('user_data', JSON.stringify(userData));
      } else {
        // Token invalid
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Don't remove token on network error - might be temporary
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Login user
   */
  const login = useCallback(async (email, password) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.login, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        await checkAuth();
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error' };
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    setIsAuthenticated(false);
    setUser(null);
  }, []);

  /**
   * Register new user
   */
  const register = useCallback(async (userData) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.register, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        await checkAuth();
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error' };
    }
  }, []);

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
    checkAuth,
  };
}

