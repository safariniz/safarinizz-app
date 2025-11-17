import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Crown, Check, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

const premiumFeatures = [
  'Sınırsız AI Koç İçgörüleri',
  'Avatar Yenileme (Sınırsız)',
  'Gelişmiş Oda Analitikleri',
  'Detaylı Ruh Hali Grafikleri',
  'AI 24 Saat Tahmin',
  'Öncelikli Empati Eşleşmesi',
  'CSS Reaction Filtreler',
  'Canlı Akış Premium Özellikleri'
];

export default function PremiumPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/premium/subscribe`,
        {},
        getAuthHeader()
      );
      toast.success('🎉 Premium aktif edildi!');
      setTimeout(() => {
        navigate('/');
        window.location.reload();
      }, 1500);
    } catch (error) {
      toast.error('Premium aktivasyonu başarısız');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6 flex items-center justify-center">
      <div className="max-w-4xl w-full">
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate('/')}
          className="mb-6"
          data-testid="back-button"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Geri
        </Button>

        <div className="text-center mb-12">
          <Crown className="w-16 h-16 mx-auto mb-4 text-amber-500" />
          <h1 className="text-4xl font-bold mb-2 gradient-text">
            CogitoSync Premium
          </h1>
          <p className="text-gray-600">
            Tüm AI gücünü açığa çıkar
          </p>
        </div>

        <Card className="glass border-none shadow-2xl" data-testid="premium-card">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl">
              <span className="text-5xl font-bold">$9.99</span>
              <span className="text-lg text-gray-600">/ay</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              {premiumFeatures.map((feature, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 bg-white/30 rounded-lg"
                  data-testid={`feature-${i}`}
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm font-medium">{feature}</span>
                </div>
              ))}
            </div>

            <Button
              onClick={handleSubscribe}
              disabled={loading}
              className="w-full h-14 text-lg bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
              data-testid="subscribe-button"
            >
              {loading ? 'Aktive Ediliyor...' : '🚀 Premium’a Yükselt'}
            </Button>

            <p className="text-xs text-center text-gray-500">
              Demo mod: Gerçek ödeme entegrasyonu eklenmemiştir
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}