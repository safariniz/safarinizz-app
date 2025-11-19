import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Sparkles, AlertCircle } from 'lucide-react';
import CSSReactionPicker from '@/components/CSSReactionPicker';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function CreatePage() {
  const [emotionInput, setEmotionInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentCSS, setCurrentCSS] = useState(null);

  const handleCreateCSS = async () => {
    if (!emotionInput.trim()) {
      toast.error('Lütfen ruh halinizi tanımlayın');
      return;
    }

    setLoading(true);
    try {
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
      
      const css = response.data;
      
      // Check for AI errors
      if (css.error === 'quota_exceeded') {
        toast.error('⚠️ OpenAI kotası doldu. Lütfen biraz bekleyin.');
      } else if (css.error === 'api_error') {
        toast.warning('AI servisi geçici olarak erişilemiyor');
      } else if (!css.error) {
        toast.success('CSS oluşturuldu!');
      }
      
      setCurrentCSS(css);
      setEmotionInput('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'CSS oluşturulamadı');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-4 space-y-4 animate-fade-in">
      {/* Input Card */}
      <Card className="glass border-none shadow-xl hover-lift">
        <CardContent className="p-5 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-2 bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 rounded-lg">
              <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <h2 className="font-semibold text-lg gradient-text">Ruh Halini Paylaş</h2>
          </div>
          <Textarea
            placeholder="Şu an nasıl hissediyorsun? Dürüst ol, soyut ol... 'İçimde sessiz bir fırtına büyüyor...'"
            value={emotionInput}
            onChange={(e) => setEmotionInput(e.target.value)}
            className="min-h-32 glass-strong resize-none text-base focus:ring-2 focus:ring-purple-400 transition-all"
            data-testid="emotion-input"
          />
          <Button
            onClick={handleCreateCSS}
            disabled={loading}
            className="w-full h-12 gradient-bg hover:opacity-90 text-base font-medium shadow-lg hover:shadow-xl transition-all"
            data-testid="create-css-button"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                CSS Oluşturuluyor...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                CSS Oluştur
              </span>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* CSS Display */}
      {currentCSS && (
        <Card className="glass border-none shadow-xl animate-scale-in">
          <CardContent className="p-5">
            {currentCSS.error && (
              <div className="mb-4 p-3 glass-strong border-l-4 border-amber-500 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-amber-800 dark:text-amber-300">{currentCSS.description}</p>
              </div>
            )}
            
            <div className="flex justify-center mb-6">
              <div
                className="css-orb-enhanced w-36 h-36"
                style={{
                  backgroundColor: currentCSS.color,
                  filter: `brightness(${currentCSS.light_frequency * 1.2})`
                }}
                data-testid="css-orb"
              ></div>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-600 mb-1">Duygusal Etiket</p>
                <p className="text-lg font-semibold" data-testid="css-emotion-label">
                  {currentCSS.emotion_label}
                </p>
              </div>
              
              {!currentCSS.error && (
                <>
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Açıklama</p>
                    <p className="text-sm" data-testid="css-description">
                      {currentCSS.description}
                    </p>
                  </div>
                  
                  <div className="pt-3 border-t">
                    <p className="text-xs text-gray-600 mb-2">Reaksiyonlar</p>
                    <CSSReactionPicker cssId={currentCSS.id} />
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}