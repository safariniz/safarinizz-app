import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Logo from '@/components/Logo';
import LanguageSwitcher from '@/components/LanguageSwitcher';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AuthPage({ onLogin }) {
  const { t } = useTranslation();
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email: loginEmail,
        password: loginPassword
      });
      toast.success(t('auth.loginSuccess'));
      onLogin(response.data.access_token, response.data.user_id);
    } catch (error) {
      toast.error(error.response?.data?.detail || t('auth.loginError'));
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email: registerEmail,
        password: registerPassword
      });
      toast.success(t('auth.registerSuccess'));
      onLogin(response.data.access_token, response.data.user_id);
    } catch (error) {
      toast.error(error.response?.data?.detail || t('auth.registerError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-blue-200 rounded-full opacity-20 blur-3xl float"></div>
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-pink-200 rounded-full opacity-20 blur-3xl float" style={{animationDelay: '2s'}}></div>
      </div>

      <div className="absolute top-4 right-4 z-20">
        <LanguageSwitcher variant="outline" />
      </div>

      <Card className="w-full max-w-md glass border-none shadow-2xl relative z-10" data-testid="auth-card">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <Logo size="lg" showText={false} />
          </div>
          <CardTitle className="text-3xl font-bold">
            <span style={{
              background: 'linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              CogitoSync
            </span>
          </CardTitle>
          <CardDescription className="text-base text-gray-600 dark:text-gray-400">
            {t('auth.tagline')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="login" data-testid="login-tab">{t('auth.loginTab')}</TabsTrigger>
              <TabsTrigger value="register" data-testid="register-tab">{t('auth.registerTab')}</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Input
                    type="email"
                    placeholder={t('auth.email')}
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                    className="bg-white/50"
                    data-testid="login-email-input"
                  />
                </div>
                <div>
                  <Input
                    type="password"
                    placeholder={t('auth.password')}
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                    className="bg-white/50"
                    data-testid="login-password-input"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                  disabled={loading}
                  data-testid="login-submit-button"
                >
                  {loading ? t('auth.loggingIn') : t('auth.loginButton')}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <Input
                    type="email"
                    placeholder={t('auth.email')}
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    required
                    className="bg-white/50"
                    data-testid="register-email-input"
                  />
                </div>
                <div>
                  <Input
                    type="password"
                    placeholder={t('auth.passwordHint')}
                    value={registerPassword}
                    onChange={(e) => setRegisterPassword(e.target.value)}
                    required
                    minLength={6}
                    className="bg-white/50"
                    data-testid="register-password-input"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600"
                  disabled={loading}
                  data-testid="register-submit-button"
                >
                  {loading ? t('auth.registering') : t('auth.registerButton')}
                </Button>
              </form>
            </TabsContent>
          </Tabs>

          <p className="text-xs text-center text-gray-500 mt-6">
            {t('auth.privacyNote')}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
