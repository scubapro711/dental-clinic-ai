// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002/api/v1';

export const API_ENDPOINTS = {
  auth: {
    register: `${API_BASE_URL}/auth/register`,
    login: `${API_BASE_URL}/auth/login`,
    me: `${API_BASE_URL}/auth/me`,
    refresh: `${API_BASE_URL}/auth/refresh`,
  },
  chat: {
    send: `${API_BASE_URL}/chat/`,
    conversations: `${API_BASE_URL}/chat/conversations`,
    conversation: (id) => `${API_BASE_URL}/chat/conversations/${id}`,
  },
};
