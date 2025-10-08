import React from 'react';
import { Bell, User, Search } from 'lucide-react';

/**
 * Header Component - כותרת עליונה
 * 
 * Background: #f0f0f0 (light gray)
 * Height: 64px
 * 
 * Features:
 * - Title (dynamic)
 * - Search bar
 * - Notifications bell
 * - User profile
 */
export default function Header({ title = 'מרכז פיקוד' }) {
  const [notifications, setNotifications] = React.useState(3);
  const [userProfile, setUserProfile] = React.useState(null);
  
  React.useEffect(() => {
    // Load user profile from localStorage
    const profile = JSON.parse(localStorage.getItem('user_profile') || '{}');
    setUserProfile(profile);
  }, []);
  
  return (
    <header className="h-16 bg-[#f0f0f0] border-b border-gray-300 flex items-center justify-between px-6">
      {/* Title */}
      <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
      
      {/* Right Side - Search, Notifications, Profile */}
      <div className="flex items-center gap-4">
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="חיפוש..."
            className="w-64 px-4 py-2 pr-10 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
        </div>
        
        {/* Notifications */}
        <button className="relative p-2 rounded-lg hover:bg-gray-200 transition-colors">
          <Bell className="w-6 h-6 text-gray-600" />
          {notifications > 0 && (
            <span className="absolute top-0 right-0 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {notifications}
            </span>
          )}
        </button>
        
        {/* User Profile */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            {userProfile?.avatar ? (
              <img
                src={userProfile.avatar}
                alt={userProfile.name}
                className="w-full h-full rounded-full"
              />
            ) : (
              <User className="w-5 h-5 text-white" />
            )}
          </div>
          <span className="text-sm font-medium text-gray-700">
            {userProfile?.name || 'משתמש'}
          </span>
        </div>
      </div>
    </header>
  );
}
