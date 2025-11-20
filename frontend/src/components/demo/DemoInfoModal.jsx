/**
 * Demo Info Modal
 * 
 * Collects lead information before starting dashboard demo session.
 * Creates demo token and navigates to dashboard.
 */

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { X, Loader2, Sparkles } from 'lucide-react';

const DemoInfoModal = ({ isOpen, onClose }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleStartDemo = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Call demo dashboard session API
      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/demo/dashboard-session`,
        {
          name: name.trim(),
          email: email.trim(),
          phone: phone.trim()
        }
      );

      const { demo_token, expires_at, user } = response.data;

      // Store demo token (same as regular token)
      localStorage.setItem('token', demo_token);
      localStorage.setItem('access_token', demo_token);
      localStorage.setItem('demo_mode', 'true');
      localStorage.setItem('demo_expires_at', expires_at);
      localStorage.setItem('user_profile', JSON.stringify(user));
      localStorage.setItem('current_organization_id', user.organization_id || '1');

      // Navigate to dashboard with demo flag
      navigate('/clinic/dashboard?demo=true', { replace: true });
      
    } catch (err) {
      console.error('Demo session error:', err);
      
      let errorMessage = 'Failed to start demo. Please try again.';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.request) {
        errorMessage = 'Cannot connect to server. Please check your connection.';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md relative animate-in fade-in zoom-in duration-200">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
          aria-label="Close"
        >
          <X size={24} />
        </button>

        {/* Header */}
        <div className="p-8 pb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center">
              <Sparkles className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Try DentaFlow Demo
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                30 minutes • Full access
              </p>
            </div>
          </div>
          
          <p className="text-gray-600 dark:text-gray-300">
            Experience our complete platform with real clinic data. No credit card required.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleStartDemo} className="px-8 pb-8 space-y-4">
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <p className="text-sm text-red-800 dark:text-red-200">
                <strong>⚠️ Error:</strong> {error}
              </p>
            </div>
          )}

          <div>
            <label htmlFor="demo-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Full Name
            </label>
            <input
              id="demo-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              minLength={2}
              className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white transition"
              placeholder="John Doe"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="demo-email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email Address
            </label>
            <input
              id="demo-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white transition"
              placeholder="john@example.com"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="demo-phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Phone Number
            </label>
            <input
              id="demo-phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              minLength={7}
              className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white transition"
              placeholder="+1 (555) 123-4567"
              disabled={isLoading}
            />
          </div>

          <div className="flex gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 transition disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={18} />
                  Starting...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Start Demo
                </>
              )}
            </button>
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-4">
            Demo session expires after 30 minutes. No credit card required.
          </p>
        </form>
      </div>
    </div>
  );
};

export default DemoInfoModal;
