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
    <div className="px-4 py-4 space-y-4">
      {/* Input Card */}
      <Card className="glass border-none shadow-lg">
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <h2 className="font-semibold text-lg">Ruh Halimi Paylaş</h2>
          </div>
          <Textarea
            placeholder="Bugün nasıl hissediyorsun? Örn: 'Hafif bir huzursuzluk var içimde...'"
            value={emotionInput}
            onChange={(e) => setEmotionInput(e.target.value)}
            className="min-h-32 bg-white/50 resize-none text-base"
            data-testid="emotion-input"
          />
          <Button
            onClick={handleCreateCSS}
            disabled={loading}
            className="w-full h-12 bg-gradient-to-r from-blue-500 to-purple-500 text-base font-medium"
            data-testid="create-css-button"
          >
            {loading ? 'CSS Oluşturuluyor...' : 'CSS Oluştur'}
          </Button>
        </CardContent>
      </Card>

      {/* CSS Display */}
      {currentCSS && (
        <Card className="glass border-none shadow-lg">
          <CardContent className="p-4">
            {currentCSS.error && (
              <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-amber-800">{currentCSS.description}</p>
              </div>
            )}
            
            <div className="flex justify-center mb-4">
              <div
                className="css-orb w-32 h-32 light-glow"
                style={{
                  backgroundColor: currentCSS.color,
                  opacity: currentCSS.light_frequency
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