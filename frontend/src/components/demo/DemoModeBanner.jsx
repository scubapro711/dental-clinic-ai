/**
 * Demo Mode Banner
 * 
 * Displays at the top of dashboard during demo session.
 * Shows countdown timer and upgrade CTA.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Sparkles, ArrowRight } from 'lucide-react';

const DemoModeBanner = ({ expiresAt }) => {
  const [timeLeft, setTimeLeft] = useState('');
  const [isExpired, setIsExpired] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const expires = new Date(expiresAt);
      const diff = expires - now;

      if (diff <= 0) {
        setTimeLeft('Expired');
        setIsExpired(true);
        clearInterval(interval);
        
        // Redirect to register after 2 seconds
        setTimeout(() => {
          localStorage.clear();
          navigate('/register', { 
            state: { message: 'Demo session expired. Sign up to continue!' }
          });
        }, 2000);
      } else {
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        setTimeLeft(`${minutes}:${seconds.toString().padStart(2, '0')}`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt, navigate]);

  const handleSignUp = () => {
    navigate('/register', {
      state: { source: 'demo', message: 'Love what you see? Sign up now!' }
    });
  };

  return (
    <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white px-6 py-3 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Sparkles className="animate-pulse" size={24} />
          <div>
            <p className="font-semibold text-sm">Demo Mode</p>
            <p className="text-xs opacity-90">
              Exploring DentaFlow with real clinic data
            </p>
          </div>
        </div>
        
        <div className="hidden md:flex items-center gap-2 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-lg">
          <Clock size={16} />
          <span className="font-mono font-semibold">
            {isExpired ? '⏰ Expired' : timeLeft}
          </span>
        </div>
      </div>

      <button
        onClick={handleSignUp}
        className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2 shadow-lg hover:shadow-xl"
      >
        {isExpired ? 'Sign Up' : 'Upgrade Now'}
        <ArrowRight size={18} />
      </button>
    </div>
  );
};

export default DemoModeBanner;
