import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Activity, MessageCircle, TrendingUp, Radar, User } from 'lucide-react';

export default function MobileNavV3() {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'create', label: 'Create', icon: Sparkles, path: '/' },
    { id: 'live', label: 'Live', icon: Activity, path: '/live' },
    { id: 'feed', label: 'Feed', icon: TrendingUp, path: '/feed' },
    { id: 'insights', label: 'Insights', icon: MessageCircle, path: '/coach' },
    { id: 'radar', label: 'Radar', icon: Radar, path: '/radar' },
    { id: 'profile', label: 'Profile', icon: User, path: '/profile' }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 z-50"
      style={{
        paddingBottom: 'env(safe-area-inset-bottom)',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.08)'
      }}
      data-testid="mobile-nav-v3"
    >
      <div className="grid grid-cols-6 h-16 px-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = isActive(tab.path);
          return (
            <button
              key={tab.id}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center transition-colors ${
                active ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'
              }`}
              data-testid={`nav-${tab.id}`}
            >
              <Icon className={`w-5 h-5 mb-0.5 ${active ? 'stroke-[2.5]' : 'stroke-[2]'}`} />
              <span className={`text-[10px] font-medium ${active ? 'font-semibold' : ''}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}