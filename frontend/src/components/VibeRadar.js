import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapPin } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function VibeRadar() {
  const [vibes, setVibes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);

  const getLocation = () => {
    setLoading(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const loc = {
            lat: position.coords.latitude,
            lon: position.coords.longitude
          };
          setLocation(loc);
          await fetchNearbyVibes(loc);
        },
        (error) => {
          toast.error('Konum erişimi reddedildi');
          setLoading(false);
        }
      );
    } else {
      toast.error('Tarayıcınız konum desteği vermiyor');
      setLoading(false);
    }
  };

  const fetchNearbyVibes = async (loc) => {
    try {
      const response = await axios.post(
        `${API}/vibe-radar/nearby`,
        loc,
        getAuthHeader()
      );
      setVibes(response.data.vibes);
      toast.success(`${response.data.count} yakın vibe bulundu`);
    } catch (error) {
      toast.error('Vibelar yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="glass border-none shadow-xl" data-testid="vibe-radar-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MapPin className="w-5 h-5" />
          Vibe Radar
        </CardTitle>
      </CardHeader>
      <CardContent>
        {!location ? (
          <div className="text-center py-8">
            <Button
              onClick={getLocation}
              disabled={loading}
              data-testid="enable-radar-button"
            >
              {loading ? 'Radar Açılıyor...' : 'Radar'ı Aç'}
            </Button>
            <p className="text-xs text-gray-500 mt-2">
              100m çevredeki anonim CSS sinyalleri
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {vibes.slice(0, 8).map((vibe, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg glass"
                  style={{ backgroundColor: vibe.color + '30' }}
                  data-testid={`vibe-pulse-${i}`}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full light-glow"
                      style={{ backgroundColor: vibe.color }}
                    ></div>
                    <span className="text-xs font-medium">
                      {vibe.emotion_label}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    {vibe.sound_texture}
                  </p>
                </div>
              ))}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchNearbyVibes(location)}
              className="w-full"
              data-testid="refresh-radar-button"
            >
              Yenile
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}