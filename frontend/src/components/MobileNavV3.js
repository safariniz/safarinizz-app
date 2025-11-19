import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Activity, MessageCircle, TrendingUp, Radar, User } from 'lucide-react';

export default function MobileNavV3() {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'create', label: 'Oluştur', icon: Sparkles, path: '/' },
    { id: 'live', label: 'Canlı', icon: Activity, path: '/live' },
    { id: 'feed', label: 'Akış', icon: TrendingUp, path: '/feed' },
    { id: 'insights', label: 'İçgörüler', icon: MessageCircle, path: '/coach' },
    { id: 'radar', label: 'Radar', icon: Radar, path: '/radar' },
    { id: 'profile', label: 'Profil', icon: User, path: '/profile' }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 nav-blur z-50 animate-slide-up"
      style={{
        paddingBottom: 'max(env(safe-area-inset-bottom), 8px)'
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
              className={`
                flex flex-col items-center justify-center 
                transition-all duration-200 rounded-xl mx-1
                ${active 
                  ? 'text-purple-600 dark:text-purple-400 scale-105' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }
              `}
              data-testid={`nav-${tab.id}`}
            >
              <div className={`
                p-1.5 rounded-lg transition-all
                ${active ? 'bg-purple-100 dark:bg-purple-900/30' : ''}
              `}>
                <Icon className={`w-5 h-5 ${active ? 'stroke-[2.5]' : 'stroke-[2]'}`} />
              </div>
              <span className={`text-[9px] font-medium mt-0.5 ${active ? 'font-bold' : ''}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}