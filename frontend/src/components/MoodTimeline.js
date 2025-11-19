import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function MoodTimeline() {
  const [period, setPeriod] = useState('daily');
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTimeline();
  }, [period]);

  const loadTimeline = async () => {
    setLoading(true);
    try {
      const days = period === 'daily' ? 1 : period === 'weekly' ? 7 : 30;
      const response = await axios.get(
        `${API}/v3/mood-journal/timeline?days=${days}`,
        getAuthHeader()
      );
      
      const timeline = response.data.timeline || {};
      
      // Transform timeline data for chart
      const chartData = [];
      Object.keys(timeline).sort().forEach(date => {
        const cssEntries = timeline[date];
        if (cssEntries.length > 0) {
          // Calculate average frequency for the day
          const avgFreq = cssEntries.reduce((sum, css) => sum + (css.light_frequency || 0.5), 0) / cssEntries.length;
          const dominantEmotion = cssEntries[0].emotion_label || 'Unknown';
          
          chartData.push({
            time: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            frequency: avgFreq * 100,
            label: dominantEmotion,
            count: cssEntries.length
          });
        }
      });
      
      setTimelineData(chartData);
      
      if (chartData.length === 0) {
        toast.info('No mood data for this period');
      }
    } catch (error) {
      console.error('Timeline error:', error);
      toast.error('Could not load timeline');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="glass border-none shadow-xl" data-testid="mood-timeline-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Ruh Hali Zaman Çizelgesi
          </div>
          <div className="flex gap-2">
            {['daily', 'weekly', 'monthly'].map((p) => (
              <Button
                key={p}
                size="sm"
                variant={period === p ? 'default' : 'outline'}
                onClick={() => setPeriod(p)}
                data-testid={`period-${p}-button`}
              >
                {p === 'daily' ? 'Günlük' : p === 'weekly' ? 'Haftalık' : 'Aylık'}
              </Button>
            ))}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">Yükleniyor...</p>
          </div>
        ) : timelineData.length === 0 ? (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">Henüz veri yok</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="time" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  border: 'none',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
              />
              <Line
                type="monotone"
                dataKey="frequency"
                stroke="#667eea"
                strokeWidth={3}
                dot={{ fill: '#667eea', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}