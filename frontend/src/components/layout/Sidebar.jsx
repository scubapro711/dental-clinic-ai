import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  BookOpen,
  Settings,
  LogOut
} from 'lucide-react';

/**
 * Sidebar Component - סרגל ניווט צדדי
 * 
 * Width: 64px (collapsed) or 240px (expanded)
 * Background: #001529 (dark blue)
 * 
 * Navigation items:
 * - לוח מחוונים (Dashboard)
 * - שיחות (Conversations)
 * - ניתוח ביצועים (Performance)
 * - ניהול ידע (Knowledge)
 * - הגדרות (Settings)
 */
export default function Sidebar() {
  const location = useLocation();
  const [isExpanded, setIsExpanded] = React.useState(false);
  
  const navItems = [
    {
      path: '/mission-control',
      icon: LayoutDashboard,
      label: 'לוח מחוונים',
      labelEn: 'Dashboard'
    },
    {
      path: '/conversations',
      icon: MessageSquare,
      label: 'שיחות',
      labelEn: 'Conversations'
    },
    {
      path: '/performance',
      icon: BarChart3,
      label: 'ניתוח ביצועים',
      labelEn: 'Performance'
    },
    {
      path: '/knowledge',
      icon: BookOpen,
      label: 'ניהול ידע',
      labelEn: 'Knowledge'
    },
    {
      path: '/settings',
      icon: Settings,
      label: 'הגדרות',
      labelEn: 'Settings'
    }
  ];
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('organization_id');
    window.location.href = '/login';
  };
  
  return (
    <div
      className={`bg-[#001529] text-white transition-all duration-300 flex flex-col ${
        isExpanded ? 'w-60' : 'w-16'
      }`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-gray-700">
        <div className="text-2xl font-bold">
          {isExpanded ? 'DentaFlow' : '🦷'}
        </div>
      </div>
      
      {/* Navigation Items */}
      <nav className="flex-1 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-4 py-3 transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <Icon className="w-6 h-6 flex-shrink-0" />
              {isExpanded && (
                <span className="mr-3 whitespace-nowrap">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>
      
      {/* Logout Button */}
      <div className="border-t border-gray-700">
        <button
          onClick={handleLogout}
          className="flex items-center w-full px-4 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
        >
          <LogOut className="w-6 h-6 flex-shrink-0" />
          {isExpanded && <span className="mr-3">יציאה</span>}
        </button>
      </div>
    </div>
  );
}
