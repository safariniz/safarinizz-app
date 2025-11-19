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
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fallback, setFallback] = useState(false);

  const loadInsights = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/v3/ai-coach/insights`, getAuthHeader());
      setInsights(response.data.insights || []);
      setFallback(response.data.fallback || false);
      
      if (response.data.insights && response.data.insights.length > 0) {
        toast.success('Insights loaded!');
      }
    } catch (error) {
      console.error('Insights error:', error);
      toast.error('Could not load AI insights');
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
        {insights.length === 0 && !loading ? (
          <div className="text-center py-8">
            <Button
              onClick={loadInsights}
              disabled={loading}
              data-testid="load-insights-button"
              className="bg-gradient-to-r from-purple-500 to-blue-500"
            >
              {loading ? 'Loading Insights...' : 'Get AI Insights'}
            </Button>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Based on your recent emotional patterns
            </p>
          </div>
        ) : loading ? (
          <div className="text-center py-8">
            <p className="text-gray-500">Analyzing your patterns...</p>
          </div>
        ) : (
          <div className="space-y-3">
            {fallback && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-xs text-blue-800 dark:text-blue-300">
                  💡 AI analysis temporarily limited. Showing basic insights.
                </p>
              </div>
            )}
            {insights.map((insight, idx) => (
              <div
                key={idx}
                className="p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
                data-testid={`insight-${idx}`}
              >
                <p className="text-sm text-gray-800 dark:text-gray-200">{insight}</p>
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={loadInsights}
              className="w-full"
              disabled={loading}
            >
              Refresh Insights
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}