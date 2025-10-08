/**
 * API Client for DentaFlow Backend
 * 
 * Handles all HTTP requests with:
 * - JWT authentication
 * - Error handling
 * - Request/response interceptors
 * - TypeScript types
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

/**
 * Request Interceptor
 * Adds JWT token to all requests
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add organization context if available
    const organizationId = localStorage.getItem('current_organization_id');
    if (organizationId) {
      config.headers['X-Organization-ID'] = organizationId;
    }
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles errors and token refresh
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API] Response ${response.status}:`, response.data);
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    
    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('[API] Access forbidden:', error.response.data);
      // Could show a toast notification here
    }
    
    // Handle 429 Too Many Requests
    if (error.response?.status === 429) {
      console.error('[API] Rate limit exceeded');
      // Could show a toast notification here
    }
    
    // Handle 500 Server Error
    if (error.response?.status === 500) {
      console.error('[API] Server error:', error.response.data);
      // Could show a toast notification here
    }
    
    // Log error in development
    if (import.meta.env.DEV) {
      console.error('[API] Error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
    }
    
    return Promise.reject(error);
  }
);

/**
 * API Client Methods
 */
export const api = {
  // Generic methods
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.get<T>(url, config),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.post<T>(url, data, config),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.put<T>(url, data, config),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.patch<T>(url, data, config),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.delete<T>(url, config),
  
  // Auth endpoints
  auth: {
    login: (email: string, password: string) =>
      apiClient.post('/auth/login', { email, password }),
    
    register: (data: { email: string; password: string; name: string }) =>
      apiClient.post('/auth/register', data),
    
    logout: () =>
      apiClient.post('/auth/logout'),
    
    refresh: (refreshToken: string) =>
      apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
    
    me: () =>
      apiClient.get('/auth/me'),
    
    googleLogin: (token: string) =>
      apiClient.post('/auth/google', { token }),
  },
  
  // Conversations endpoints
  conversations: {
    list: (params?: { organization_id?: string; limit?: number; offset?: number }) =>
      apiClient.get('/conversations', { params }),
    
    get: (id: string) =>
      apiClient.get(`/conversations/${id}`),
    
    create: (data: { patient_phone?: string; channel?: string }) =>
      apiClient.post('/conversations', data),
    
    sendMessage: (id: string, message: string) =>
      apiClient.post(`/conversations/${id}/messages`, { message }),
    
    getMessages: (id: string) =>
      apiClient.get(`/conversations/${id}/messages`),
  },
  
  // Organizations endpoints
  organizations: {
    list: () =>
      apiClient.get('/organizations'),
    
    get: (id: string) =>
      apiClient.get(`/organizations/${id}`),
    
    create: (data: { name: string; type: string }) =>
      apiClient.post('/organizations', data),
    
    update: (id: string, data: Partial<{ name: string; type: string }>) =>
      apiClient.put(`/organizations/${id}`, data),
    
    delete: (id: string) =>
      apiClient.delete(`/organizations/${id}`),
    
    // Memberships
    getMembers: (id: string) =>
      apiClient.get(`/organizations/${id}/members`),
    
    addMember: (id: string, data: { user_id: string; role: string }) =>
      apiClient.post(`/organizations/${id}/members`, data),
    
    removeMember: (id: string, userId: string) =>
      apiClient.delete(`/organizations/${id}/members/${userId}`),
  },
  
  // Clinic Settings endpoints
  clinicSettings: {
    get: (organizationId: string) =>
      apiClient.get(`/clinic-settings/${organizationId}`),
    
    update: (organizationId: string, data: any) =>
      apiClient.put(`/clinic-settings/${organizationId}`, data),
    
    reset: (organizationId: string) =>
      apiClient.post(`/clinic-settings/${organizationId}/reset`),
  },
  
  // Treatment Prices endpoints
  treatmentPrices: {
    list: (organizationId: string) =>
      apiClient.get(`/treatment-prices`, { params: { organization_id: organizationId } }),
    
    get: (id: string) =>
      apiClient.get(`/treatment-prices/${id}`),
    
    create: (data: any) =>
      apiClient.post(`/treatment-prices`, data),
    
    update: (id: string, data: any) =>
      apiClient.put(`/treatment-prices/${id}`, data),
    
    delete: (id: string) =>
      apiClient.delete(`/treatment-prices/${id}`),
    
    bulkCreate: (organizationId: string) =>
      apiClient.post(`/treatment-prices/bulk`, { organization_id: organizationId }),
  },
  
  // Dashboard endpoints
  dashboard: {
    getMetrics: (organizationId: string) =>
      apiClient.get(`/dashboard/metrics`, { params: { organization_id: organizationId } }),
    
    getStatistics: (organizationId: string, params?: { start_date?: string; end_date?: string }) =>
      apiClient.get(`/dashboard/statistics`, { params: { organization_id: organizationId, ...params } }),
  },
  
  // Proactive Suggestions endpoints
  proactiveSuggestions: {
    list: (organizationId: string) =>
      apiClient.get(`/proactive-suggestions`, { params: { organization_id: organizationId } }),
    
    execute: (id: string) =>
      apiClient.post(`/proactive-suggestions/${id}/execute`),
    
    dismiss: (id: string) =>
      apiClient.post(`/proactive-suggestions/${id}/dismiss`),
  },
  
  // Audit Logs endpoints
  auditLogs: {
    list: (params?: { organization_id?: string; user_id?: string; action?: string; limit?: number }) =>
      apiClient.get(`/audit-logs`, { params }),
    
    get: (id: string) =>
      apiClient.get(`/audit-logs/${id}`),
  },
};

export default apiClient;
