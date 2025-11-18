import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import '@/App.css';
import AuthPage from '@/pages/AuthPage';
import CreatePage from '@/pages/CreatePage';
import LivePage from '@/pages/LivePage';
import InsightsPage from '@/pages/InsightsPage';
import RadarPage from '@/pages/RadarPage';
import MatchPage from '@/pages/MatchPage';
import ProfilePageV3 from '@/pages/ProfilePageV3';
import FeedPageV3 from '@/pages/FeedPageV3';
import CoachChatPageV3 from '@/pages/CoachChatPageV3';
import CommunityRoomsPageV3 from '@/pages/CommunityRoomsPageV3';
import HistoryPage from '@/pages/HistoryPage';
import RoomPage from '@/pages/RoomPage';
import PremiumPage from '@/pages/PremiumPage';
import MobileHeader from '@/components/MobileHeader';
import MobileNav from '@/components/MobileNav';
import { Toaster } from '@/components/ui/sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AppLayout({ children, onLogout, isPremium }) {
  const location = useLocation();
  const hideNavRoutes = ['/auth', '/premium', '/history', '/room'];
  const showNav = !hideNavRoutes.some(route => location.pathname.startsWith(route));

  return (
    <>
      {showNav && <MobileHeader isPremium={isPremium} onLogout={onLogout} />}
      <main 
        className={showNav ? 'mobile-main' : ''}
        style={{
          paddingTop: showNav ? 'calc(3.5rem + env(safe-area-inset-top))' : '0',
          paddingBottom: showNav ? 'calc(4rem + env(safe-area-inset-bottom))' : '0',
          minHeight: '100vh'
        }}
      >
        {children}
      </main>
      {showNav && <MobileNav />}
    </>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('cogito_token'));
  const [userId, setUserId] = useState(localStorage.getItem('cogito_user_id'));
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    if (token) {
      checkPremiumStatus();
    }
    registerServiceWorker();
  }, [token]);

  const registerServiceWorker = () => {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
          .then(reg => console.log('SW registered:', reg.scope))
          .catch(err => console.log('SW registration failed:', err));
      });
    }
  };

  const checkPremiumStatus = async () => {
    try {
      const response = await axios.get(`${API}/premium/check`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsPremium(response.data.is_premium);
    } catch (error) {
      console.error('Premium status check failed');
    }
  };

  const handleLogin = (newToken, newUserId) => {
    localStorage.setItem('cogito_token', newToken);
    localStorage.setItem('cogito_user_id', newUserId);
    setToken(newToken);
    setUserId(newUserId);
  };

  const handleLogout = () => {
    localStorage.removeItem('cogito_token');
    localStorage.removeItem('cogito_user_id');
    setToken(null);
    setUserId(null);
    setIsPremium(false);
  };

  return (
    <div className=\"App\">
      <BrowserRouter>
        <AppLayout onLogout={handleLogout} isPremium={isPremium}>
          <Routes>
            <Route 
              path=\"/auth\" 
              element={!token ? <AuthPage onLogin={handleLogin} /> : <Navigate to=\"/\" />} 
            />
            <Route 
              path=\"/\" 
              element={token ? <CreatePage /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/live\" 
              element={token ? <LivePage /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/insights\" 
              element={token ? <InsightsPage isPremium={isPremium} /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/radar\" 
              element={token ? <RadarPage /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/match\" 
              element={token ? <MatchPage /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/profile\" 
              element={token ? <ProfilePageV3 /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/feed\" 
              element={token ? <FeedPageV3 /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/coach\" 
              element={token ? <CoachChatPageV3 /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/community-rooms\" 
              element={token ? <CommunityRoomsPageV3 /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/history\" 
              element={token ? <HistoryPage onLogout={handleLogout} /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/room/:roomId?\" 
              element={token ? <RoomPage onLogout={handleLogout} /> : <Navigate to=\"/auth\" />} 
            />
            <Route 
              path=\"/premium\" 
              element={token ? <PremiumPage /> : <Navigate to=\"/auth\" />} 
            />
          </Routes>
        </AppLayout>
      </BrowserRouter>
      <Toaster position=\"top-center\" />
    </div>
  );
}

export default App;