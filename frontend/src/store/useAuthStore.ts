/**
 * Authentication Store
 * 
 * Manages:
 * - User authentication state
 * - Organization context
 * - Login/logout
 * - Token management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '../api/client';

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  type: string;
  created_at: string;
}

export interface OrganizationMembership {
  id: string;
  organization_id: string;
  user_id: string;
  organization_role: string;
  odoo_partner_id?: number;
  organization: Organization;
}

interface AuthState {
  // State
  user: User | null;
  organization: Organization | null;
  memberships: OrganizationMembership[];
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (token: string) => Promise<void>;
  logout: () => void;
  register: (data: { email: string; password: string; name: string }) => Promise<void>;
  switchOrganization: (organizationId: string) => void;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      organization: null,
      memberships: [],
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login with email/password
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.auth.login(email, password);
          const { user, organization, memberships, access_token, refresh_token } = response.data;

          // Store tokens
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          localStorage.setItem('current_organization_id', organization.id);

          set({
            user,
            organization,
            memberships,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      // Login with Google
      loginWithGoogle: async (token: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.auth.googleLogin(token);
          const { user, organization, memberships, access_token, refresh_token } = response.data;

          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          localStorage.setItem('current_organization_id', organization.id);

          set({
            user,
            organization,
            memberships,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Google login failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      // Logout
      logout: () => {
        try {
          api.auth.logout();
        } catch (error) {
          console.error('Logout error:', error);
        }

        // Clear storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('current_organization_id');

        // Reset state
        set({
          user: null,
          organization: null,
          memberships: [],
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
      },

      // Register new user
      register: async (data: { email: string; password: string; name: string }) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.auth.register(data);
          const { user, organization, memberships, access_token, refresh_token } = response.data;

          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          localStorage.setItem('current_organization_id', organization.id);

          set({
            user,
            organization,
            memberships,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      // Switch organization
      switchOrganization: (organizationId: string) => {
        const { memberships } = get();
        const membership = memberships.find((m) => m.organization_id === organizationId);

        if (membership) {
          localStorage.setItem('current_organization_id', organizationId);
          set({
            organization: membership.organization,
          });
        } else {
          console.error('Organization not found in memberships');
        }
      },

      // Refresh user data
      refreshUser: async () => {
        try {
          const response = await api.auth.me();
          const { user, organization, memberships } = response.data;

          set({
            user,
            organization,
            memberships,
          });
        } catch (error) {
          console.error('Failed to refresh user:', error);
          // If refresh fails, logout
          get().logout();
        }
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        organization: state.organization,
        memberships: state.memberships,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
