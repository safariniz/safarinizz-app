import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Activity, TrendingUp, Radar, Heart } from 'lucide-react';

export default function MobileNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'create', label: 'CSS', icon: Sparkles, path: '/' },
    { id: 'live', label: 'Canlı', icon: Activity, path: '/live' },
    { id: 'insights', label: 'İçgörü', icon: TrendingUp, path: '/insights' },
    { id: 'radar', label: 'Radar', icon: Radar, path: '/radar' },
    { id: 'match', label: 'Eşleş', icon: Heart, path: '/match' }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom z-50"
      style={{
        paddingBottom: 'env(safe-area-inset-bottom)',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.08)'
      }}
      data-testid="mobile-nav"
    >
      <div className="flex justify-around items-center h-16 px-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = isActive(tab.path);
          return (
            <button
              key={tab.id}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                active ? 'text-purple-600' : 'text-gray-500'
              }`}
              data-testid={`nav-${tab.id}`}
              style={{ minWidth: '60px' }}
            >
              <Icon 
                className={`w-6 h-6 mb-1 ${
                  active ? 'stroke-[2.5]' : 'stroke-[2]'
                }`} 
              />
              <span className={`text-xs font-medium ${
                active ? 'font-semibold' : ''
              }`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}