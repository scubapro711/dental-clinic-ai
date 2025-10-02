// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://8000-inz49vfnpwjnjv1qy37ft-3b63ca47.manusvm.computer';

export const API_ENDPOINTS = {
  auth: {
    register: `${API_BASE_URL}/api/v1/auth/register`,
    login: `${API_BASE_URL}/api/v1/auth/login`,
    me: `${API_BASE_URL}/api/v1/auth/me`,
    refresh: `${API_BASE_URL}/api/v1/auth/refresh`,
  },
  chat: {
    send: `${API_BASE_URL}/api/v1/chat/`,
    conversations: `${API_BASE_URL}/api/v1/chat/conversations`,
    conversation: (id) => `${API_BASE_URL}/api/v1/chat/conversations/${id}`,
  },
};
