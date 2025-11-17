import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles, History, Users, LogOut } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function Dashboard({ onLogout }) {
  const [emotionInput, setEmotionInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentCSS, setCurrentCSS] = useState(null);
  const navigate = useNavigate();

  const handleCreateCSS = async () => {
    if (!emotionInput.trim()) {
      toast.error('Lütfen ruh halinizi tanımlayın');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/css/create`,
        { emotion_input: emotionInput },
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
      <header className="max-w-6xl mx-auto mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold gradient-text" data-testid="dashboard-title">CogitoSync</h1>
        <div className="flex gap-2">
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
      <div className="max-w-4xl mx-auto">
        {/* CSS Creation */}
        <Card className="glass border-none shadow-xl mb-8" data-testid="css-creation-card">
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
              <CardDescription>Anlık duygusal görselleştirme</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                {/* Visual */}
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

                {/* Details */}
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Duygusal Etiket</p>
                    <p className="text-xl font-semibold" data-testid="css-emotion-label">{currentCSS.emotion_label}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Açıklama</p>
                    <p className="text-sm" data-testid="css-description">{currentCSS.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div>
                      <p className="text-xs text-gray-500">Renk</p>
                      <p className="text-sm font-mono" data-testid="css-color">{currentCSS.color}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Işık Frekansı</p>
                      <p className="text-sm" data-testid="css-light-frequency">{(currentCSS.light_frequency * 100).toFixed(0)}%</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-xs text-gray-500">Ses Dokusu</p>
                      <p className="text-sm capitalize" data-testid="css-sound-texture">{currentCSS.sound_texture}</p>
                    </div>
                  </div>

                  {currentCSS.image_url && (
                    <div className="pt-4">
                      <img 
                        src={currentCSS.image_url} 
                        alt="CSS Visual" 
                        className="w-full rounded-lg shadow-md"
                        data-testid="css-image"
                      />
                    </div>
                  )}

                  <div className="pt-4 space-y-2">
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
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}