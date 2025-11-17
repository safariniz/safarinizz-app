import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import '@/App.css';
import AuthPage from '@/pages/AuthPage';
import DashboardV2 from '@/pages/DashboardV2';
import HistoryPage from '@/pages/HistoryPage';
import RoomPage from '@/pages/RoomPage';
import PremiumPage from '@/pages/PremiumPage';
import { Toaster } from '@/components/ui/sonner';

function App() {
  const [token, setToken] = useState(localStorage.getItem('cogito_token'));
  const [userId, setUserId] = useState(localStorage.getItem('cogito_user_id'));

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
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/auth" 
            element={!token ? <AuthPage onLogin={handleLogin} /> : <Navigate to="/" />} 
          />
          <Route 
            path="/" 
            element={token ? <DashboardV2 onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/history" 
            element={token ? <HistoryPage onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/room/:roomId?" 
            element={token ? <RoomPage onLogout={handleLogout} /> : <Navigate to="/auth" />} 
          />
          <Route 
            path="/premium" 
            element={token ? <PremiumPage /> : <Navigate to="/auth" />} 
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" />
    </div>
  );
}

export default App;