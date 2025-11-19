import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Simple Mock Login - Bypasses all auth checks
 * Just sets localStorage and redirects using React Router
 * Supports both Clinic (org_admin) and Patient (org_viewer) roles
 */
export default function SimpleMockLogin() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState('clinic'); // 'clinic' or 'patient'
  const [statusMessage, setStatusMessage] = useState('');
  
  const handleLogin = (role) => {
    setIsLoading(true);
    setStatusMessage('Logging in...');
    
    let mockUser, redirectPath;
    
    if (role === 'clinic') {
      // Clinic Admin User
      mockUser = {
        id: 1,
        name: 'Dr. Rachel Cohen',
        email: 'rachel@dentaflow.ai',
        role: 'org_admin',
        organization_id: 1,
        organization_name: 'DentaFlow Clinic',
        avatar: null
      };
      redirectPath = '/clinic/dashboard';
      setStatusMessage('Logging in to Clinic Portal...');
    } else {
      // Patient User
      mockUser = {
        id: 101,
        name: 'Sarah Johnson',
        email: 'sarah.johnson@example.com',
        role: 'org_viewer',
        organization_id: 1,
        organization_name: 'DentaFlow Clinic',
        patient_id: 1,
        avatar: null
      };
      redirectPath = '/patient/dashboard';
      setStatusMessage('Logging in to Patient Portal...');
    }
    
    // Set mock data in localStorage
    const mockToken = 'mock-jwt-token-' + Date.now();
    localStorage.setItem('token', mockToken);
    localStorage.setItem('access_token', mockToken);
    localStorage.setItem('current_organization_id', '1');
    localStorage.setItem('user_profile', JSON.stringify(mockUser));
    localStorage.setItem('mockUser', JSON.stringify(mockUser)); // For RBAC utility
    
    // Small delay to show loading state
    setTimeout(() => {
      setStatusMessage('Login successful! Redirecting...');
      // Navigate using React Router
      navigate(redirectPath, { replace: true });
      setIsLoading(false);
    }, 500);
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        {/* ARIA Live Region for status announcements */}
        <div 
          role="status" 
          aria-live="polite" 
          aria-atomic="true" 
          className="sr-only"
        >
          {statusMessage}
        </div>
        
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4" role="img" aria-label="Tooth icon">🦷</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">DentaFlow</h1>
          <p className="text-gray-600">Portal Selection - Demo Mode</p>
        </div>
        
        {/* Mock Login Info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ Demo Mode</strong>
            <br />
            This is a demo version without real authentication.
            <br />
            Choose a portal below to test the system.
          </p>
        </div>
        
        {/* Portal Selection */}
        <fieldset className="space-y-4 mb-6">
          <legend className="sr-only">Select Portal Type</legend>
          
          {/* Clinic Portal */}
          <div 
            className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedRole === 'clinic' 
                ? 'border-blue-600 bg-blue-50' 
                : 'border-gray-200 hover:border-blue-300'
            }`}
            onClick={() => setSelectedRole('clinic')}
          >
            <div className="flex items-start gap-3">
              <input
                type="radio"
                id="portal-clinic"
                name="portal-selection"
                value="clinic"
                checked={selectedRole === 'clinic'}
                onChange={() => setSelectedRole('clinic')}
                className="mt-1"
                aria-label="Clinic Portal for staff and administrators"
              />
              <label htmlFor="portal-clinic" className="flex-1 cursor-pointer">
                <h3 className="font-semibold text-gray-900 mb-1">
                  <span role="img" aria-label="Hospital">🏥</span> Clinic Portal (Mission Control)
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  For clinic staff and administrators
                </p>
                <div className="text-xs text-gray-500 space-y-1">
                  <div>• User: Dr. Rachel Cohen</div>
                  <div>• Role: org_admin</div>
                  <div>• Clinic: DentaFlow Clinic</div>
                </div>
              </label>
            </div>
          </div>
          
          {/* Patient Portal */}
          <div 
            className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedRole === 'patient' 
                ? 'border-green-600 bg-green-50' 
                : 'border-gray-200 hover:border-green-300'
            }`}
            onClick={() => setSelectedRole('patient')}
          >
            <div className="flex items-start gap-3">
              <input
                type="radio"
                id="portal-patient"
                name="portal-selection"
                value="patient"
                checked={selectedRole === 'patient'}
                onChange={() => setSelectedRole('patient')}
                className="mt-1"
                aria-label="Patient Portal for managing appointments and records"
              />
              <label htmlFor="portal-patient" className="flex-1 cursor-pointer">
                <h3 className="font-semibold text-gray-900 mb-1">
                  <span role="img" aria-label="Person">👤</span> Patient Portal
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  For patients to manage appointments and records
                </p>
                <div className="text-xs text-gray-500 space-y-1">
                  <div>• User: Sarah Johnson</div>
                  <div>• Role: org_viewer (Patient)</div>
                  <div>• Clinic: DentaFlow Clinic</div>
                </div>
              </label>
            </div>
          </div>
        </fieldset>
        
        {/* Login Button */}
        <button
          onClick={() => handleLogin(selectedRole)}
          disabled={isLoading}
          aria-label={selectedRole === 'clinic' ? 'Enter Clinic Portal' : 'Enter Patient Portal'}
          aria-busy={isLoading}
          className={`w-full py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
            selectedRole === 'clinic'
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
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
            <>
              <span role="img" aria-hidden="true">{selectedRole === 'clinic' ? '🚀' : '🏥'}</span>
              {' '}
              {selectedRole === 'clinic' ? 'Enter Mission Control' : 'Enter Patient Portal'}
            </>
          )}
        </button>
        
        {/* Note */}
        <p className="text-xs text-gray-500 text-center mt-6">
          Version: v20.1.0 (Portal Separation Testing)
          <br />
          <span className="text-red-500">
            ⚠️ Not for production - Demo purposes only
          </span>
        </p>
      </div>
    </div>
  );
}

