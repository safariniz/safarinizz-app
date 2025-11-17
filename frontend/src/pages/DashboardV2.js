import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, History, Users, LogOut, Crown, TrendingUp } from 'lucide-react';
import VibeRadar from '@/components/VibeRadar';
import MoodTimeline from '@/components/MoodTimeline';
import AICoachPanel from '@/components/AICoachPanel';
import MoodForecast from '@/components/MoodForecast';
import EmpathyMatch from '@/components/EmpathyMatch';
import CSSReactionPicker from '@/components/CSSReactionPicker';
import WebSocketService from '@/services/websocket';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function DashboardV2({ onLogout }) {
  const [emotionInput, setEmotionInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentCSS, setCurrentCSS] = useState(null);
  const [isPremium, setIsPremium] = useState(false);
  const [liveCSS, setLiveCSS] = useState([]);
  const [activeTab, setActiveTab] = useState('create');
  const navigate = useNavigate();

  useEffect(() => {
    checkPremiumStatus();
    initWebSocket();
    
    return () => {
      WebSocketService.disconnect();
    };
  }, []);

  const checkPremiumStatus = async () => {
    try {
      const response = await axios.get(`${API}/premium/check`, getAuthHeader());
      setIsPremium(response.data.is_premium);
    } catch (error) {
      console.error('Premium status check failed');
    }
  };

  const initWebSocket = () => {
    WebSocketService.connect(BACKEND_URL, 'global');
    WebSocketService.on('message', (data) => {
      if (data.type === 'new_css') {
        setLiveCSS(prev => [data.data, ...prev].slice(0, 10));
        toast.info('🌊 Yeni CSS sinyali!');
      }
    });
  };

  const handleCreateCSS = async () => {
    if (!emotionInput.trim()) {
      toast.error('Lütfen ruh halinizi tanımlayın');
      return;
    }

    setLoading(true);
    try {
      // Get location if available
      let location = null;
      if (navigator.geolocation) {
        await new Promise((resolve) => {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              location = {
                lat: position.coords.latitude,
                lon: position.coords.longitude
              };
              resolve();
            },
            () => resolve()
          );
        });
      }

      const response = await axios.post(
        `${API}/css/create`,
        { emotion_input: emotionInput, location },
        getAuthHeader()
      );
      setCurrentCSS(response.data);
      toast.success('CSS oluşturuldu');
      setEmotionInput('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'CSS oluşturulamadı');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <header className="max-w-7xl mx-auto mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold gradient-text" data-testid="dashboard-title">
          CogitoSync
          {isPremium && <Crown className="inline w-6 h-6 ml-2 text-amber-500" />}
        </h1>
        <div className="flex gap-2">
          {!isPremium && (
            <Button
              size="sm"
              className="bg-gradient-to-r from-amber-500 to-orange-500"
              onClick={() => navigate('/premium')}
              data-testid="upgrade-button"
            >
              <Crown className="w-4 h-4 mr-2" />
              Premium
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/history')}
            data-testid="history-button"
          >
            <History className="w-4 h-4 mr-2" />
            Geçmiş
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/room')}
            data-testid="room-button"
          >
            <Users className="w-4 h-4 mr-2" />
            Oda
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onLogout}
            data-testid="logout-button"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Çıkış
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-5 mb-8">
            <TabsTrigger value="create" data-testid="tab-create">CSS Oluştur</TabsTrigger>
            <TabsTrigger value="live" data-testid="tab-live">Canlı Akış</TabsTrigger>
            <TabsTrigger value="insights" data-testid="tab-insights">AI Koç</TabsTrigger>
            <TabsTrigger value="radar" data-testid="tab-radar">Vibe Radar</TabsTrigger>
            <TabsTrigger value="match" data-testid="tab-match">Empati</TabsTrigger>
          </TabsList>

          {/* CREATE TAB */}
          <TabsContent value="create">
            <div className="grid md:grid-cols-2 gap-6">
              {/* CSS Creation */}
              <Card className="glass border-none shadow-xl" data-testid="css-creation-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Ruh Halimi Paylaş
                  </CardTitle>
                  <CardDescription>
                    İçsel duygusal durumunuzu tanımlayın, AI soyut bir CSS'e dönüştürsün.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="Örn: 'Bugün hafif bir huzursuzluk var içimde, ama umut da...'"
                    value={emotionInput}
                    onChange={(e) => setEmotionInput(e.target.value)}
                    className="min-h-32 bg-white/50 resize-none"
                    data-testid="emotion-input"
                  />
                  <Button
                    onClick={handleCreateCSS}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600"
                    data-testid="create-css-button"
                  >
                    {loading ? 'CSS oluşturuluyor...' : 'CSS Oluştur'}
                  </Button>
                </CardContent>
              </Card>

              {/* Current CSS Display */}
              {currentCSS && (
                <Card className="glass border-none shadow-xl" data-testid="current-css-card">
                  <CardHeader>
                    <CardTitle>Mevcut CSS'iniz</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-center items-center p-8">
                        <div
                          className="css-orb w-48 h-48 light-glow"
                          style={{
                            backgroundColor: currentCSS.color,
                            opacity: currentCSS.light_frequency
                          }}
                          data-testid="css-orb"
                        ></div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Duygusal Etiket</p>
                        <p className="text-xl font-semibold" data-testid="css-emotion-label">
                          {currentCSS.emotion_label}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Açıklama</p>
                        <p className="text-sm" data-testid="css-description">
                          {currentCSS.description}
                        </p>
                      </div>
                      <CSSReactionPicker cssId={currentCSS.id} />
                      <Button
                        onClick={() => navigate('/room', { state: { cssId: currentCSS.id } })}
                        className="w-full"
                        variant="outline"
                        data-testid="share-in-room-button"
                      >
                        <Users className="w-4 h-4 mr-2" />
                        Odada Paylaş
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Mood Timeline */}
            <div className="mt-6">
              <MoodTimeline />
            </div>
          </TabsContent>

          {/* LIVE TAB */}
          <TabsContent value="live">
            <Card className="glass border-none shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Canlı CSS Akışı
                  <span className="text-xs bg-green-500 text-white px-2 py-1 rounded-full ml-2">
                    LIVE
                  </span>
                </CardTitle>
                <CardDescription>
                  Gerçek zamanlı CSS sinyalleri
                </CardDescription>
              </CardHeader>
              <CardContent>
                {liveCSS.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500">Canlı CSS'ler burada görünecek...</p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-3 gap-4">
                    {liveCSS.map((css, i) => (
                      <div
                        key={i}
                        className="p-4 rounded-lg glass"
                        style={{ backgroundColor: css.color + '20' }}
                        data-testid={`live-css-${i}`}
                      >
                        <div
                          className="w-16 h-16 rounded-full mx-auto mb-3 light-glow"
                          style={{ backgroundColor: css.color }}
                        ></div>
                        <p className="text-sm font-semibold text-center">{css.emotion_label}</p>
                        <p className="text-xs text-gray-600 text-center mt-1">
                          {css.sound_texture}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* INSIGHTS TAB */}
          <TabsContent value="insights">
            <div className="grid md:grid-cols-2 gap-6">
              <AICoachPanel isPremium={isPremium} />
              <MoodForecast isPremium={isPremium} />
            </div>
          </TabsContent>

          {/* RADAR TAB */}
          <TabsContent value="radar">
            <VibeRadar />
          </TabsContent>

          {/* MATCH TAB */}
          <TabsContent value="match">
            <EmpathyMatch />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}