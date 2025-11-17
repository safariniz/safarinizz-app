import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, Lock } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function AICoachPanel({ isPremium }) {
  const [insight, setInsight] = useState(null);
  const [loading, setLoading] = useState(false);
  const [premiumRequired, setPremiumRequired] = useState(false);

  const loadInsights = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/ai-coach/insights`, getAuthHeader());
      setInsight(response.data.insight);
      setPremiumRequired(response.data.premium_required);
    } catch (error) {
      toast.error('İçgörüler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="glass border-none shadow-xl" data-testid="ai-coach-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            AI Koç
          </div>
          {premiumRequired && (
            <Lock className="w-4 h-4 text-amber-500" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {!insight ? (
          <div className="text-center py-8">
            <Button
              onClick={loadInsights}
              disabled={loading}
              data-testid="load-insights-button"
            >
              {loading ? 'İçgörüler Yükleniyor...' : 'İçgörüleri Gör'}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {premiumRequired && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-xs text-amber-800">
                  🔒 Premium özelliği: Sınırsız AI analizi için yükselt
                </p>
              </div>
            )}
            <div
              className="p-4 bg-white/30 rounded-lg"
              data-testid="insight-content"
            >
              <p className="text-sm">{insight.content}</p>
              <p className="text-xs text-gray-500 mt-2">
                {new Date(insight.created_at).toLocaleDateString('tr-TR')}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadInsights}
              className="w-full"
            >
              Yenile
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}