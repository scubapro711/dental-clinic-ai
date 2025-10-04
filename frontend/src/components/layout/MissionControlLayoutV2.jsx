import React from 'react';
import { cn } from '@/lib/utils';
import { Bell, Settings, Search } from 'lucide-react';
import { LiveIndicator } from '../ui/LiveIndicator';

const MissionControlLayoutV2 = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between max-w-[1920px] mx-auto">
            {/* Left: Logo & Title */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-cyan-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-xl font-bold">D</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">
                    DentalDesk AI
                  </h1>
                  <p className="text-xs text-gray-500">Mission Control v2.0</p>
                </div>
              </div>
              
              <LiveIndicator active={true} label="System Online" />
            </div>
            
            {/* Center: Search */}
            <div className="hidden md:flex flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search conversations, patients..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            {/* Right: Actions & User */}
            <div className="flex items-center gap-3">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative">
                <Bell className="w-5 h-5 text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Settings className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center gap-2 pl-3 border-l border-gray-200">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 text-white flex items-center justify-center text-sm font-semibold">
                  U
                </div>
                <span className="text-sm font-medium text-gray-700 hidden sm:inline">Dr. User</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Grid */}
      <div className="px-6 py-6 max-w-[1920px] mx-auto">
        <div className="grid grid-cols-12 gap-6">
          {children}
        </div>
      </div>
    </div>
  );
};

const LeftPanel = ({ children, className }) => {
  return (
    <aside className={cn(
      'col-span-12 lg:col-span-2',
      'space-y-4',
      className
    )}>
      {children}
    </aside>
  );
};

const CenterStage = ({ children, className }) => {
  return (
    <main className={cn(
      'col-span-12 lg:col-span-6',
      'space-y-6',
      className
    )}>
      {children}
    </main>
  );
};

const RightSidebar = ({ children, className }) => {
  return (
    <aside className={cn(
      'col-span-12 lg:col-span-4',
      'space-y-4',
      className
    )}>
      {children}
    </aside>
  );
};

export { MissionControlLayoutV2, LeftPanel, CenterStage, RightSidebar };
