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
  const [confidence, setConfidence] = useState('low');
  const [fallback, setFallback] = useState(false);

  const loadForecast = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/v3/ai-forecast/predict`, getAuthHeader());
      setForecast(response.data.forecast);
      setConfidence(response.data.confidence || 'low');
      setFallback(response.data.fallback || false);
      
      if (response.data.forecast) {
        toast.success('Forecast ready!');
      }
    } catch (error) {
      console.error('Forecast error:', error);
      toast.error('Could not generate forecast');
    } finally {
      setLoading(false);
    }
  };

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
        {!forecast ? (
          <div className="text-center py-8">
            <Button
              onClick={loadForecast}
              disabled={loading}
              data-testid="load-forecast-button"
              className="bg-gradient-to-r from-blue-500 to-teal-500"
            >
              {loading ? 'Analyzing Patterns...' : 'Get 24h Forecast'}
            </Button>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              AI-powered mood prediction
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {fallback && (
              <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded text-xs text-yellow-800 dark:text-yellow-300">
                ⚠️ AI forecast limited. Showing basic prediction.
              </div>
            )}
            <div className="p-4 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-800 rounded-lg">
              <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">
                {forecast}
              </p>
              <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-400">
                <span className={`px-2 py-1 rounded ${
                  confidence === 'high' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  confidence === 'medium' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {confidence} confidence
                </span>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadForecast}
              className="w-full"
              disabled={loading}
            >
              Refresh Forecast
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}