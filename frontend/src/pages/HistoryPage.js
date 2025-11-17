import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function HistoryPage({ onLogout }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API}/css/my-history`, getAuthHeader());
      setHistory(response.data);
    } catch (error) {
      toast.error('Geçmiş yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <header className="max-w-6xl mx-auto mb-8 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/')}
            data-testid="back-button"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Geri
          </Button>
          <h1 className="text-3xl font-bold gradient-text" data-testid="history-title">CSS Geçmişim</h1>
        </div>
      </header>

      <div className="max-w-6xl mx-auto">
        {loading ? (
          <p className="text-center text-gray-500" data-testid="loading-text">Yükleniyor...</p>
        ) : history.length === 0 ? (
          <Card className="glass border-none shadow-xl" data-testid="empty-history-card">
            <CardContent className="p-12 text-center">
              <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-600">Henüz CSS oluşturmadınız.</p>
              <Button
                className="mt-4"
                onClick={() => navigate('/')}
                data-testid="create-first-css-button"
              >
                İlk CSS'inizi Oluşturun
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {history.map((css, index) => (
              <Card
                key={css.id}
                className="glass border-none shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
                data-testid={`css-history-card-${index}`}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-center mb-4">
                    <div
                      className="css-orb w-24 h-24 light-glow"
                      style={{
                        backgroundColor: css.color,
                        opacity: css.light_frequency
                      }}
                      data-testid={`css-orb-${index}`}
                    ></div>
                  </div>
                  <h3 className="font-semibold text-lg mb-2 text-center" data-testid={`css-label-${index}`}>
                    {css.emotion_label}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4 text-center" data-testid={`css-desc-${index}`}>
                    {css.description}
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                    <div>
                      <span className="block">Renk</span>
                      <span className="font-mono" data-testid={`css-color-${index}`}>{css.color}</span>
                    </div>
                    <div>
                      <span className="block">Frekans</span>
                      <span data-testid={`css-freq-${index}`}>{(css.light_frequency * 100).toFixed(0)}%</span>
                    </div>
                    <div className="col-span-2">
                      <span className="block">Ses Dokusu</span>
                      <span className="capitalize" data-testid={`css-texture-${index}`}>{css.sound_texture}</span>
                    </div>
                    <div className="col-span-2 mt-2">
                      <span className="block">Tarih</span>
                      <span data-testid={`css-date-${index}`}>
                        {new Date(css.timestamp).toLocaleDateString('tr-TR', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}