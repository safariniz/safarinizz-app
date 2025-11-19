import React from 'react';
import { Menu, Crown, LogOut, Settings, Moon, Sun } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/context/ThemeContext';
import Logo from '@/components/Logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function MobileHeaderV3({ isPremium, onLogout }) {
  const navigate = useNavigate();
  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <header 
      className="fixed top-0 left-0 right-0 bg-white/90 dark:bg-gray-900/90 backdrop-blur-lg border-b border-gray-200 dark:border-gray-800 z-50"
      style={{
        paddingTop: 'env(safe-area-inset-top)',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
      }}
      data-testid="mobile-header-v3"
    >
      <div className="flex items-center justify-between h-14 px-4">
        <div className="flex items-center gap-2">
          <Logo size="sm" showText={false} />
          <span className="text-lg font-bold" style={{
            background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            CogitoSync
          </span>
          {isPremium && <Crown className="w-4 h-4 text-amber-500" />}
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={toggleDarkMode}>
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" data-testid="menu-button">
                <Menu className="w-5 h-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={() => navigate('/settings')}>
                <Settings className="w-4 h-4 mr-2" />
                Ayarlar
              </DropdownMenuItem>
              {!isPremium && (
                <DropdownMenuItem onClick={() => navigate('/premium')}>
                  <Crown className="w-4 h-4 mr-2" />
                  Go Premium
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={onLogout} className="text-red-600">
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}