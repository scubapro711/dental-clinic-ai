import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Mock Login Page - דף התחברות מזויף לצורך הדגמה
 * 
 * Bypasses authentication to show Mission Control Dashboard
 * 
 * TODO: Replace with real authentication in Phase 2
 */
export default function MockLoginPage({ onLogin }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const handleMockLogin = () => {
    setLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      // Create mock token and user data
      const mockToken = 'mock-jwt-token-' + Date.now();
      const mockUser = {
        id: 1,
        name: 'Dr. Rachel Cohen',
        email: 'rachel@dentaflow.ai',
        role: 'org_admin',
        organization_id: 1,
        organization_name: 'DentaFlow Clinic',
        avatar: null
      };
      
      // Store in localStorage
      localStorage.setItem('token', mockToken);
      localStorage.setItem('access_token', mockToken);
      localStorage.setItem('organization_id', '1');
      localStorage.setItem('user_profile', JSON.stringify(mockUser));
      
      // Call onLogin callback if provided
      if (onLogin) {
        onLogin(mockToken, mockUser);
      }
      
      // Navigate to Clinic Dashboard (since role is org_admin)
      navigate('/clinic/dashboard');
      
      setLoading(false);
    }, 500);
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🦷</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">DentaFlow</h1>
          <p className="text-gray-600">מרכז פיקוד - גרסת הדגמה</p>
        </div>
        
        {/* Mock Login Info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800">
            <strong>⚠️ מצב הדגמה</strong>
            <br />
            זוהי גרסת הדגמה ללא אימות אמיתי.
            <br />
            לחץ על הכפתור למטה כדי להיכנס למערכת.
          </p>
        </div>
        
        {/* Mock User Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800 mb-2">
            <strong>👤 משתמש לדוגמה:</strong>
          </p>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• שם: Dr. Rachel Cohen</li>
            <li>• תפקיד: מנהל מערכת</li>
            <li>• מרפאה: DentaFlow Clinic</li>
          </ul>
        </div>
        
        {/* Mock Login Button */}
        <button
          onClick={handleMockLogin}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? '🔄 נכנס למערכת...' : '🚀 כניסה למרכז פיקוד'}
        </button>
        
        {/* Note */}
        <p className="text-xs text-gray-500 text-center mt-6">
          גרסה: v18.0.0 (Mock Authentication)
          <br />
          <span className="text-red-500">
            ⚠️ לא לשימוש בפרודקשן - לצורך הדגמה בלבד
          </span>
        </p>
      </div>
    </div>
  );
}
