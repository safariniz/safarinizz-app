import React from 'react';
import { Menu, Crown, LogOut, User, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function MobileHeader({ isPremium, onLogout }) {
  const navigate = useNavigate();

  return (
    <header 
      className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50"
      style={{
        paddingTop: 'env(safe-area-inset-top)',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
      }}
      data-testid="mobile-header"
    >
      <div className="flex items-center justify-between h-14 px-4">
        <h1 className="text-xl font-bold gradient-text flex items-center gap-2">
          CogitoSync
          {isPremium && <Crown className="w-5 h-5 text-amber-500" />}
        </h1>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" data-testid="menu-button">
              <Menu className="w-5 h-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={() => navigate('/history')}>
              <User className="w-4 h-4 mr-2" />
              Geçmiş
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate('/room')}>
              <Settings className="w-4 h-4 mr-2" />
              Odalar
            </DropdownMenuItem>
            {!isPremium && (
              <DropdownMenuItem onClick={() => navigate('/premium')}>
                <Crown className="w-4 h-4 mr-2" />
                Premium
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onClick={onLogout} className="text-red-600">
              <LogOut className="w-4 h-4 mr-2" />
              Çıkış
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}