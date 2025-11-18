import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import '@/App.css';
import { ThemeProvider } from '@/context/ThemeContext';
import AuthPage from '@/pages/AuthPage';
import CreatePage from '@/pages/CreatePage';
import LivePage from '@/pages/LivePage';
import ProfilePageV3 from '@/pages/ProfilePageV3';
import FeedPageV3 from '@/pages/FeedPageV3';
import CoachChatPageV3 from '@/pages/CoachChatPageV3';
import RadarPage from '@/pages/RadarPage';
import CommunityRoomsPageV3 from '@/pages/CommunityRoomsPageV3';
import PremiumPage from '@/pages/PremiumPage';
import MobileHeaderV3 from '@/components/MobileHeaderV3';
import MobileNavV3 from '@/components/MobileNavV3';
import { Toaster } from '@/components/ui/sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AppLayout({ children, onLogout, isPremium }) {
  const location = useLocation();
  const hideNavRoutes = ['/auth', '/premium'];
  const showNav = !hideNavRoutes.some(route => location.pathname.startsWith(route));

  return (
    <>
      {showNav && <MobileHeaderV3 isPremium={isPremium} onLogout={onLogout} />}
      <main 
        className={`${showNav ? 'mobile-main' : ''} dark:bg-gray-950 min-h-screen transition-colors`}
        style={{
          paddingTop: showNav ? 'calc(3.5rem + env(safe-area-inset-top))' : '0',
          paddingBottom: showNav ? 'calc(4rem + env(safe-area-inset-bottom))' : '0'
        }}
      >
        {children}
      </main>
      {showNav && <MobileNavV3 />}
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
          .then(() => console.log('SW registered'))
          .catch(() => console.log('SW registration failed'));
      });
    }
  };

  const checkPremiumStatus = async () => {
    try {
      const response = await axios.get(`${API}/v3/premium/check`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsPremium(response.data.is_premium);
    } catch (error) {
      console.error('Premium check failed');
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
    <ThemeProvider>
      <div className="App">
        <BrowserRouter>
          <AppLayout onLogout={handleLogout} isPremium={isPremium}>
            <Routes>
              <Route 
                path="/auth" 
                element={!token ? <AuthPage onLogin={handleLogin} /> : <Navigate to="/" />} 
              />
              <Route 
                path="/" 
                element={token ? <CreatePage /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/live" 
                element={token ? <LivePage /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/feed" 
                element={token ? <FeedPageV3 /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/coach" 
                element={token ? <CoachChatPageV3 /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/radar" 
                element={token ? <RadarPage /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/profile" 
                element={token ? <ProfilePageV3 /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/community-rooms" 
                element={token ? <CommunityRoomsPageV3 /> : <Navigate to="/auth" />} 
              />
              <Route 
                path="/premium" 
                element={token ? <PremiumPage /> : <Navigate to="/auth" />} 
              />
            </Routes>
          </AppLayout>
        </BrowserRouter>
        <Toaster position="top-center" />
      </div>
    </ThemeProvider>
  );
}

export default App;
