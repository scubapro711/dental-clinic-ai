/**
 * API Configuration
 * 
 * Centralized configuration for all API endpoints and URLs.
 * Uses environment variables with sensible defaults for staging.
 */

// Get API URL from environment variable
// Vite exposes env vars prefixed with VITE_ as import.meta.env
const API_URL = import.meta.env.VITE_API_URL || 'https://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app/api/v1';

// Extract base URL (without /api/v1)
const API_BASE_URL = API_URL.replace('/api/v1', '');

// WebSocket URL (replace http(s) with ws(s))
const WS_BASE_URL = API_BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://');

// Export configuration
export const API_CONFIG = {
  // Full API URL with /api/v1
  API_URL,
  
  // Base URL without /api/v1
  BASE_URL: API_BASE_URL,
  
  // WebSocket base URL
  WS_URL: WS_BASE_URL,
  
  // Environment
  ENV: import.meta.env.VITE_APP_ENV || 'production',
  
  // Helper to build full API endpoint URLs
  endpoint: (path) => {
    // Remove leading slash if present
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    
    // If path already includes /api/v1, use BASE_URL
    if (cleanPath.startsWith('api/v1/')) {
      return `${API_BASE_URL}/${cleanPath}`;
    }
    
    // Otherwise, use API_URL (which includes /api/v1)
    return `${API_URL}/${cleanPath}`;
  },
  
  // Helper to build WebSocket URLs
  ws: (path) => {
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    return `${WS_BASE_URL}/${cleanPath}`;
  },
};

// Log configuration in development
if (API_CONFIG.ENV === 'development') {
  console.log('=== API Configuration ===');
  console.log('API_URL:', API_CONFIG.API_URL);
  console.log('BASE_URL:', API_CONFIG.BASE_URL);
  console.log('WS_URL:', API_CONFIG.WS_URL);
  console.log('ENV:', API_CONFIG.ENV);
  console.log('========================');
}

export default API_CONFIG;
