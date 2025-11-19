import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

/**
 * Real Login - Authenticates with backend API
 * Uses /api/v1/auth/login endpoint
 * Stores real JWT tokens
 */
export default function RealLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('sarah@example.com');
  const [password, setPassword] = useState('demo123');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app/api/v1';

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Call backend login API
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email: email.trim(),
        password: password
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });

      const { access_token, refresh_token } = response.data;

      if (!access_token) {
        throw new Error('No access token received');
      }

      // Decode JWT to get user info (simple base64 decode, no verification needed here)
      const tokenParts = access_token.split('.');
      if (tokenParts.length !== 3) {
        throw new Error('Invalid token format');
      }

      const payload = JSON.parse(atob(tokenParts[1]));
      
      // Extract user info from token
      const userId = payload.sub;
      const userEmail = payload.email;
      const userRole = payload.role;
      const organizationId = payload.organization_id;
      const odooPartnerId = payload.odoo_partner_id;

      // Create user profile object
      const userProfile = {
        id: userId,
        email: userEmail,
        role: userRole,
        organization_id: organizationId,
        odoo_partner_id: odooPartnerId,
        name: email === 'rachel@dentaflow.ai' ? 'Dr. Rachel Cohen' : email === 'sarah@example.com' ? 'Sarah Johnson' : userEmail,
        organization_name: 'DentaFlow Clinic'
      };

      // Store tokens and user info in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('current_organization_id', organizationId || '1');
      localStorage.setItem('user_profile', JSON.stringify(userProfile));

      // Navigate based on role
      const redirectPath = userRole === 'patient' 
        ? '/patient/dashboard'
        : '/clinic/dashboard';

      navigate(redirectPath, { replace: true });
      
    } catch (err) {
      console.error('Login error:', err);
      
      let errorMessage = 'Login failed. Please try again.';
      
      if (err.response) {
        // Backend returned an error
        if (err.response.status === 401) {
          errorMessage = 'Incorrect email or password';
        } else if (err.response.status === 403) {
          errorMessage = 'Account is inactive';
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        }
      } else if (err.request) {
        // Network error
        errorMessage = 'Cannot connect to server. Please check your connection.';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4" role="img" aria-label="Tooth icon">🦷</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">DentaFlow</h1>
          <p className="text-gray-600">Clinic Portal Login</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4" role="alert">
              <p className="text-sm text-red-800">
                <strong>⚠️ Error:</strong> {error}
              </p>
            </div>
          )}

          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="your.email@example.com"
              disabled={isLoading}
            />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                placeholder="Enter your password"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Logging in...
              </span>
            ) : (
              <>🚀 Login to Mission Control</>
            )}
          </button>
        </form>

        {/* Demo Credentials Info */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>💡 Demo Credentials:</strong>
            <br />
            <strong>Patient Portal:</strong> sarah@example.com / demo123
            <br />
            <strong>Clinic Admin:</strong> rachel@dentaflow.ai / demo123
          </p>
        </div>

        {/* Version Info */}
        <p className="text-xs text-gray-500 text-center mt-6">
          Version: v20.2.0 (Real Authentication)
          <br />
          <span className="text-green-600">
            ✅ Connected to backend API
          </span>
        </p>
      </div>
    </div>
  );
}
