import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '@/components/ui/card';
import { Activity } from 'lucide-react';
import WebSocketService from '@/services/websocket';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function LivePage() {
  const { t, i18n } = useTranslation();
  const [liveCSS, setLiveCSS] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    WebSocketService.connect(BACKEND_URL, 'global');
    setConnected(true);
    
    WebSocketService.on('message', (data) => {
      if (data.type === 'new_css') {
        setLiveCSS(prev => [data.data, ...prev].slice(0, 20));
      }
    });

    return () => {
      WebSocketService.disconnect();
      setConnected(false);
    };
  }, []);

  return (
    <div className="px-4 py-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-semibold">{t('live.title', 'Live CSS Stream')}</h2>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${
          connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
        }`}>
          {connected ? t('live.connected', 'LIVE') : t('live.connecting', 'CONNECTING')}
        </span>
      </div>

      {liveCSS.length === 0 ? (
        <Card className="glass border-none shadow-lg">
          <CardContent className="p-8 text-center">
            <Activity className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="text-gray-600">{t('live.waiting', 'Live CSS will appear here...')}</p>
            <p className="text-xs text-gray-500 mt-1">{t('live.streamActive', 'Real-time stream active')}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {liveCSS.map((css, i) => (
            <Card
              key={i}
              className="glass border-none shadow-md animate-fade-in"
              style={{ backgroundColor: css.color + '15' }}
              data-testid={`live-css-${i}`}
            >
              <CardContent className="p-4 flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-full flex-shrink-0 light-glow"
                  style={{ backgroundColor: css.color }}
                ></div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm truncate">
                    {css.emotion_label}
                  </p>
                  <p className="text-xs text-gray-600 capitalize">
                    {css.sound_texture} • {(css.light_frequency * 100).toFixed(0)}%
                  </p>
                </div>
                <span className="text-xs text-gray-500 flex-shrink-0">
                  {new Date(css.timestamp).toLocaleTimeString(i18n.language === 'tr' ? 'tr-TR' : 'en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
