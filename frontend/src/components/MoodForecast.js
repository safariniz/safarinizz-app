import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingUp, Lock } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function MoodForecast({ isPremium }) {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [premiumRequired, setPremiumRequired] = useState(false);

  const loadForecast = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/ai-forecast/predict`, getAuthHeader());
      setForecast(response.data.forecast);
      setPremiumRequired(response.data.premium_required);
    } catch (error) {
      toast.error('Tahmin yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const chartData = forecast
    ? forecast.hours.map((h, i) => ({
        hour: `${h}:00`,
        value: forecast.predictions[i] * 100
      }))
    : [];

  return (
    <Card className="glass border-none shadow-xl" data-testid="mood-forecast-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            24 Saat Tahmin
          </div>
          {premiumRequired && (
            <Lock className="w-4 h-4 text-amber-500" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {premiumRequired ? (
          <div className="text-center py-8">
            <Lock className="w-12 h-12 mx-auto mb-4 text-amber-500" />
            <p className="text-sm text-gray-600">Premium özelliği</p>
            <p className="text-xs text-gray-500 mt-2">
              24 saatlik AI tahminleri için yükselt
            </p>
          </div>
        ) : !forecast ? (
          <div className="text-center py-8">
            <Button
              onClick={loadForecast}
              disabled={loading}
              data-testid="load-forecast-button"
            >
              {loading ? 'Tahmin Hazırlanıyor...' : 'Tahmin Al'}
            </Button>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <XAxis dataKey="hour" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  border: 'none',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="value" fill="#667eea" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}