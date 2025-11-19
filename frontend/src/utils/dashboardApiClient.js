/**
 * Dashboard API Client Utility
 * 
 * Centralized API client with authentication and error handling.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app/api/v1';

class DashboardApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor: Add auth token and organization ID
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        const orgId = localStorage.getItem('current_organization_id');
        if (orgId && !config.url?.includes('/auth')) {
          config.headers['X-Organization-ID'] = orgId;
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor: Handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // If 401 and we haven't tried to refresh yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken
              });

              const { access_token, refresh_token: new_refresh } = response.data;

              // Update tokens
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', new_refresh);

              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            } catch (refreshError) {
              // Refresh failed, logout user
              localStorage.clear();
              window.location.href = '/login';
              return Promise.reject(refreshError);
            }
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async get(url, params) {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  async post(url, data) {
    const response = await this.client.post(url, data);
    return response.data;
  }

  async put(url, data) {
    const response = await this.client.put(url, data);
    return response.data;
  }

  async delete(url) {
    const response = await this.client.delete(url);
    return response.data;
  }

  async patch(url, data) {
    const response = await this.client.patch(url, data);
    return response.data;
  }
}

export const dashboardApiClient = new DashboardApiClient();
